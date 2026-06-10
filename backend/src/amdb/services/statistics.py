from __future__ import annotations

import bz2
import json
import os
import re
import subprocess
import time
import uuid
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TextIO

from amdb.config import settings
from amdb.core.logging import get_logger, log_step


@dataclass(frozen=True)
class PredicateCount:
    predicate: str
    count: int


@dataclass(frozen=True)
class DatasetStatistic:
    dataset_name: str
    file_path: str
    triple_count: int
    subject_count: int
    predicate_count: int
    object_count: int
    skipped_lines: int
    sample_predicates: list[PredicateCount]


@dataclass(frozen=True)
class NativeDefStats:
    attempted: bool
    success: bool
    exit_code: int | None
    stdout_path: str | None
    stderr_path: str | None
    statistics_dir: str | None
    error: str | None


@dataclass(frozen=True)
class StatisticsResult:
    run_id: str
    source_dir: str
    report_path: str
    generated_at: str
    success: bool
    engine: str
    dump_date: str | None
    extraction_run_id: str | None
    file_count: int
    total_triples: int
    unique_subjects: int
    unique_predicates: int
    unique_objects: int
    mapping_based_triples: int
    raw_infobox_triples: int
    dataset_statistics: list[DatasetStatistic]
    native_def_stats: NativeDefStats
    error: str | None


class StatisticsService:
    """Generate and serve precomputed RDF statistics for DEF output directories."""

    _RDF_SUFFIXES = (
        ".ttl",
        ".ttl.bz2",
        ".nt",
        ".nt.bz2",
        ".ntriples",
        ".ntriples.bz2",
    )
    _TRIPLE_RE = re.compile(
        r"^\s*(?P<subject><[^>]+>|_:[^\s]+)\s+"
        r"(?P<predicate><[^>]+>|[A-Za-z][\w-]*:[^\s]+)\s+"
        r"(?P<object>.+?)\s*\.\s*(?:#.*)?$"
    )
    _SAFE_RUN_ID_RE = re.compile(r"[^A-Za-z0-9_.-]+")

    def __init__(self) -> None:
        self._logger = get_logger(__name__)

    def generate(
        self,
        source_dir: Path,
        run_id: str | None = None,
        dump_date: str | None = None,
        extraction_run_id: str | None = None,
        use_native_def_stats: bool = False,
        max_files: int | None = None,
    ) -> StatisticsResult:
        started_at = time.monotonic()
        source_dir = source_dir.expanduser().resolve()
        safe_run_id = self._safe_run_id(run_id or f"statistics-{uuid.uuid4()}")

        log_step(
            self._logger,
            "statistics.started",
            "Generating RDF statistics",
            {
                "run_id": safe_run_id,
                "source_dir": source_dir,
                "dump_date": dump_date,
                "extraction_run_id": extraction_run_id,
                "use_native_def_stats": use_native_def_stats,
                "max_files": max_files,
            },
        )

        settings.reports_dir.mkdir(parents=True, exist_ok=True)

        native_stats = NativeDefStats(
            attempted=False,
            success=False,
            exit_code=None,
            stdout_path=None,
            stderr_path=None,
            statistics_dir=None,
            error=None,
        )
        if use_native_def_stats:
            native_stats = self._run_native_def_stats(source_dir=source_dir, run_id=safe_run_id)

        rdf_files = self._discover_rdf_files(source_dir, max_files=max_files)
        log_step(
            self._logger,
            "statistics.files_discovered",
            "Discovered RDF files for streaming statistics",
            {"file_count": len(rdf_files)},
        )

        dataset_statistics: list[DatasetStatistic] = []
        global_subjects: set[str] = set()
        global_predicates: set[str] = set()
        global_objects: set[str] = set()
        total_triples = 0
        mapping_based_triples = 0
        raw_infobox_triples = 0

        for index, rdf_file in enumerate(rdf_files, start=1):
            statistic, subjects, predicates, objects = self._scan_file(rdf_file)
            dataset_statistics.append(statistic)
            global_subjects.update(subjects)
            global_predicates.update(predicates)
            global_objects.update(objects)
            total_triples += statistic.triple_count

            category = self._dataset_category(statistic.dataset_name)
            if category == "mapping-based":
                mapping_based_triples += statistic.triple_count
            elif category == "raw-infobox":
                raw_infobox_triples += statistic.triple_count

            log_step(
                self._logger,
                "statistics.file_completed",
                "Finished RDF file statistics",
                {
                    "index": f"{index}/{len(rdf_files)}",
                    "dataset": statistic.dataset_name,
                    "triples": statistic.triple_count,
                    "subjects": statistic.subject_count,
                    "predicates": statistic.predicate_count,
                    "skipped_lines": statistic.skipped_lines,
                },
            )

        error = None
        success = True
        if not rdf_files:
            success = False
            error = f"No RDF files found under {source_dir}"

        engine = "python-streaming"
        if native_stats.attempted:
            engine = "python-streaming+def-native"

        generated_at = datetime.now(UTC).isoformat()
        report_path = settings.reports_dir / f"{safe_run_id}.statistics-report.json"

        result = StatisticsResult(
            run_id=safe_run_id,
            source_dir=str(source_dir),
            report_path=str(report_path),
            generated_at=generated_at,
            success=success,
            engine=engine,
            dump_date=dump_date,
            extraction_run_id=extraction_run_id,
            file_count=len(rdf_files),
            total_triples=total_triples,
            unique_subjects=len(global_subjects),
            unique_predicates=len(global_predicates),
            unique_objects=len(global_objects),
            mapping_based_triples=mapping_based_triples,
            raw_infobox_triples=raw_infobox_triples,
            dataset_statistics=dataset_statistics,
            native_def_stats=native_stats,
            error=error,
        )

        payload = self.to_payload(result)
        self._write_json(report_path, payload)
        self._write_json(settings.latest_statistics_report, payload)

        duration_seconds = time.monotonic() - started_at
        log_step(
            self._logger,
            "statistics.completed",
            "Statistics report generated",
            {
                "run_id": result.run_id,
                "success": result.success,
                "total_triples": result.total_triples,
                "unique_subjects": result.unique_subjects,
                "unique_predicates": result.unique_predicates,
                "report_path": result.report_path,
                "duration_seconds": f"{duration_seconds:.2f}",
            },
        )

        return result

    def load_latest(self) -> dict[str, Any]:
        return self._read_json(settings.latest_statistics_report)

    def load_run(self, run_id: str) -> dict[str, Any]:
        report_path = settings.reports_dir / f"{self._safe_run_id(run_id)}.statistics-report.json"
        return self._read_json(report_path)

    def list_runs(self) -> list[dict[str, Any]]:
        settings.reports_dir.mkdir(parents=True, exist_ok=True)
        summaries: list[dict[str, Any]] = []
        report_paths = sorted(
            settings.reports_dir.glob("*.statistics-report.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        for report_path in report_paths:
            try:
                payload = self._read_json(report_path)
            except (json.JSONDecodeError, OSError):
                continue
            summaries.append(
                {
                    "run_id": payload.get("run_id", report_path.stem),
                    "generated_at": payload.get("generated_at", ""),
                    "source_dir": payload.get("source_dir", ""),
                    "report_path": str(report_path),
                    "success": bool(payload.get("success", False)),
                    "total_triples": int(payload.get("total_triples", 0)),
                    "file_count": int(payload.get("file_count", 0)),
                    "extraction_run_id": payload.get("extraction_run_id"),
                }
            )
        return summaries

    def to_payload(self, result: StatisticsResult) -> dict[str, Any]:
        return {
            "run_id": result.run_id,
            "source_dir": result.source_dir,
            "report_path": result.report_path,
            "generated_at": result.generated_at,
            "success": result.success,
            "engine": result.engine,
            "dump_date": result.dump_date,
            "extraction_run_id": result.extraction_run_id,
            "file_count": result.file_count,
            "total_triples": result.total_triples,
            "unique_subjects": result.unique_subjects,
            "unique_predicates": result.unique_predicates,
            "unique_objects": result.unique_objects,
            "mapping_based_triples": result.mapping_based_triples,
            "raw_infobox_triples": result.raw_infobox_triples,
            "dataset_statistics": [
                {
                    **asdict(statistic),
                    "sample_predicates": [
                        asdict(predicate) for predicate in statistic.sample_predicates
                    ],
                }
                for statistic in result.dataset_statistics
            ],
            "native_def_stats": asdict(result.native_def_stats),
            "error": result.error,
        }

    def _run_native_def_stats(self, source_dir: Path, run_id: str) -> NativeDefStats:
        output_dir = settings.reports_dir / f"{run_id}.native-def-statistics"
        output_dir.mkdir(parents=True, exist_ok=True)
        stdout_path = output_dir / "stdout.log"
        stderr_path = output_dir / "stderr.log"

        if not settings.statistics_runner_script.is_file():
            missing_runner_error = (
                f"Statistics runner script not found: {settings.statistics_runner_script}"
            )
            log_step(
                self._logger,
                "statistics.native_skipped",
                "DEF native statistics wrapper is unavailable",
                {"error": missing_runner_error},
            )
            return NativeDefStats(
                attempted=True,
                success=False,
                exit_code=None,
                stdout_path=None,
                stderr_path=None,
                statistics_dir=None,
                error=missing_runner_error,
            )

        command = [
            "bash",
            str(settings.statistics_runner_script),
            str(source_dir),
            str(output_dir),
        ]

        log_step(
            self._logger,
            "statistics.native_started",
            "Running DEF native statistics wrapper",
            {"command": " ".join(command)},
        )
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "DEF_DIR": str(settings.resolved_def_dir)},
        )
        stdout_path.write_text(process.stdout, encoding="utf-8")
        stderr_path.write_text(process.stderr, encoding="utf-8")

        native_statistics_dir = output_dir / "native-statistics"
        success = process.returncode == 0
        native_error: str | None = None if success else self._tail(process.stderr or process.stdout)

        log_step(
            self._logger,
            "statistics.native_completed",
            "DEF native statistics wrapper completed",
            {
                "exit_code": process.returncode,
                "success": success,
                "stdout_path": stdout_path,
                "stderr_path": stderr_path,
                "statistics_dir": native_statistics_dir if native_statistics_dir.is_dir() else None,
            },
        )

        return NativeDefStats(
            attempted=True,
            success=success,
            exit_code=process.returncode,
            stdout_path=str(stdout_path),
            stderr_path=str(stderr_path),
            statistics_dir=str(native_statistics_dir) if native_statistics_dir.is_dir() else None,
            error=native_error,
        )

    def _discover_rdf_files(self, source_dir: Path, max_files: int | None) -> list[Path]:
        if source_dir.is_file():
            files = [source_dir] if self._is_rdf_file(source_dir) else []
        elif source_dir.is_dir():
            files = sorted(
                path
                for path in source_dir.rglob("*")
                if path.is_file() and self._is_rdf_file(path)
            )
        else:
            files = []

        if max_files is not None:
            return files[:max_files]
        return files

    def _scan_file(self, path: Path) -> tuple[DatasetStatistic, set[str], set[str], set[str]]:
        dataset_name = self._dataset_name(path)
        log_step(
            self._logger,
            "statistics.file_started",
            "Scanning RDF file",
            {"dataset": dataset_name, "file_path": path},
        )

        subjects: set[str] = set()
        predicates: Counter[str] = Counter()
        objects: set[str] = set()
        skipped_lines = 0
        triples = 0

        with self._open_rdf_text(path) as file:
            for line in file:
                parsed = self._parse_triple_line(line)
                if parsed is None:
                    if self._should_skip_line(line):
                        continue
                    skipped_lines += 1
                    continue

                subject, predicate, rdf_object = parsed
                subjects.add(subject)
                predicates[predicate] += 1
                objects.add(rdf_object)
                triples += 1

        sample_predicates = [
            PredicateCount(predicate=predicate, count=count)
            for predicate, count in predicates.most_common(20)
        ]

        return (
            DatasetStatistic(
                dataset_name=dataset_name,
                file_path=str(path),
                triple_count=triples,
                subject_count=len(subjects),
                predicate_count=len(predicates),
                object_count=len(objects),
                skipped_lines=skipped_lines,
                sample_predicates=sample_predicates,
            ),
            subjects,
            set(predicates),
            objects,
        )

    def _parse_triple_line(self, line: str) -> tuple[str, str, str] | None:
        match = self._TRIPLE_RE.match(line)
        if match is None:
            return None
        return (
            match.group("subject"),
            match.group("predicate"),
            match.group("object").strip(),
        )

    def _should_skip_line(self, line: str) -> bool:
        stripped = line.strip()
        return (
            not stripped
            or stripped.startswith("#")
            or stripped.startswith("@prefix")
            or stripped.startswith("@base")
            or stripped.upper().startswith("PREFIX ")
            or stripped.upper().startswith("BASE ")
        )

    @contextmanager
    def _open_rdf_text(self, path: Path) -> Iterator[TextIO]:
        if path.name.endswith(".bz2"):
            with bz2.open(path, mode="rt", encoding="utf-8", errors="replace") as file:
                yield file
            return

        with path.open(mode="rt", encoding="utf-8", errors="replace") as file:
            yield file

    def _dataset_category(self, dataset_name: str) -> str:
        normalized = dataset_name.lower().replace("_", "-")
        if "mappingbased" in normalized or "mapping-based" in normalized:
            return "mapping-based"
        if "infobox-properties" in normalized or "raw-infobox" in normalized:
            return "raw-infobox"
        return "other"

    def _dataset_name(self, path: Path) -> str:
        name = path.name
        for suffix in self._RDF_SUFFIXES:
            if name.endswith(suffix):
                return name[: -len(suffix)]
        return path.stem

    def _is_rdf_file(self, path: Path) -> bool:
        return any(path.name.endswith(suffix) for suffix in self._RDF_SUFFIXES)

    def _safe_run_id(self, run_id: str) -> str:
        compact = self._SAFE_RUN_ID_RE.sub("-", run_id.strip()).strip("-")
        return compact or f"statistics-{uuid.uuid4()}"

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.is_file():
            raise FileNotFoundError(f"Statistics report not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _tail(self, text: str, limit: int = 600) -> str:
        compact = " ".join(text.split())
        if len(compact) <= limit:
            return compact
        return compact[-limit:]
