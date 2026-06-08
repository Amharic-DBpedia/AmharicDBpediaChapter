from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from threading import Lock
from typing import Protocol

from amdb.config import settings
from amdb.core.errors import PipelineError, WikidataLookupError
from amdb.core.logging import get_logger, log_step
from amdb.core.paths import ensure_parent
from amdb.services.ingestion import DumpTemplateParser
from amdb.services.prediction import AfroXlmrPropertyPredictor, MappingPrediction
from amdb.services.wikidata import WikidataClient, WikidataContext


class WikidataContextProvider(Protocol):
    def get_context_for_title(self, title: str) -> WikidataContext: ...


class PropertyPredictor(Protocol):
    def predict(
        self,
        parameter_name: str,
        template_name: str,
        wikidata_hints: list[str],
        value_sample: str | None = None,
        top_k: int = 5,
        use_existing_mappings: bool = True,
        use_ml_model: bool = True,
    ) -> list[MappingPrediction]: ...


@dataclass(frozen=True, slots=True)
class MappingCandidate:
    page_title: str
    page_id: str | None
    template_name: str
    parameter_name: str
    value_sample: str
    wikidata_entity_id: str | None
    wikidata_entity_label: str | None
    wikidata_hints: list[str]
    predictions: list[MappingPrediction]


@dataclass(frozen=True, slots=True)
class MappingPipelineResult:
    run_id: str
    input_path: str
    report_path: str
    pages_seen: int
    templates_seen: int
    parameters_seen: int
    candidates_count: int
    candidates_sample: list[MappingCandidate]


class PipelineJobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class PipelineJob:
    job_id: str
    status: PipelineJobStatus
    input_path: str
    report_path: str | None = None
    error: str | None = None


class InMemoryPipelineJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, PipelineJob] = {}
        self._lock = Lock()

    def create(self, input_path: str, job_id: str | None = None) -> PipelineJob:
        job = PipelineJob(
            job_id=job_id or str(uuid.uuid4()),
            status=PipelineJobStatus.QUEUED,
            input_path=input_path,
        )
        with self._lock:
            self._jobs[job.job_id] = job
        return job

    def set_running(self, job_id: str) -> None:
        self._replace(job_id, status=PipelineJobStatus.RUNNING)

    def set_succeeded(self, job_id: str, report_path: str) -> None:
        self._replace(job_id, status=PipelineJobStatus.SUCCEEDED, report_path=report_path)

    def set_failed(self, job_id: str, error: str) -> None:
        self._replace(job_id, status=PipelineJobStatus.FAILED, error=error)

    def get(self, job_id: str) -> PipelineJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def _replace(
        self,
        job_id: str,
        status: PipelineJobStatus,
        report_path: str | None = None,
        error: str | None = None,
    ) -> None:
        with self._lock:
            current = self._jobs[job_id]
            self._jobs[job_id] = PipelineJob(
                job_id=current.job_id,
                status=status,
                input_path=current.input_path,
                report_path=report_path if report_path is not None else current.report_path,
                error=error,
            )


class MappingPipelineService:
    def __init__(
        self,
        parser: DumpTemplateParser | None = None,
        wikidata_client: WikidataContextProvider | None = None,
        predictor: PropertyPredictor | None = None,
    ) -> None:
        self._parser = parser or DumpTemplateParser()
        self._wikidata_client = wikidata_client or WikidataClient()
        self._predictor = predictor or AfroXlmrPropertyPredictor.from_default_def_checkout()
        self._logger = get_logger(__name__)

    def run(
        self,
        input_path: Path,
        run_id: str | None = None,
        max_pages: int | None = 10,
        top_k: int = 5,
        use_wikidata: bool = True,
        use_existing_mappings: bool = True,
        use_ml_model: bool = True,
    ) -> MappingPipelineResult:
        resolved_run_id = run_id or str(uuid.uuid4())
        report_path = settings.reports_dir / f"{resolved_run_id}.mapping-pipeline-report.json"
        ensure_parent(report_path)

        log_step(
            self._logger,
            "pipeline.started",
            "Running mapping candidate pipeline",
            {
                "run_id": resolved_run_id,
                "input_path": input_path,
                "max_pages": max_pages,
                "use_wikidata": use_wikidata,
                "use_ml_model": use_ml_model,
            },
        )

        pages_seen = 0
        templates_seen = 0
        parameters_seen = 0
        candidates: list[MappingCandidate] = []
        wikidata_cache: dict[str, WikidataContext] = {}

        try:
            for page in self._parser.iter_pages(input_path=input_path, max_pages=max_pages):
                pages_seen += 1
                if not page.templates:
                    continue

                wikidata_context = self._wikidata_context_for_page(
                    page.title,
                    enabled=use_wikidata,
                    cache=wikidata_cache,
                )

                for template in page.templates:
                    templates_seen += 1
                    for parameter in template.parameters:
                        parameters_seen += 1
                        predictions = self._predictor.predict(
                            parameter_name=parameter.name,
                            template_name=template.name,
                            wikidata_hints=wikidata_context.hint_labels,
                            value_sample=self._value_sample(parameter.value),
                            top_k=top_k,
                            use_existing_mappings=use_existing_mappings,
                            use_ml_model=use_ml_model,
                        )

                        candidate = MappingCandidate(
                            page_title=page.title,
                            page_id=page.page_id,
                            template_name=template.name,
                            parameter_name=parameter.name,
                            value_sample=self._value_sample(parameter.value),
                            wikidata_entity_id=wikidata_context.entity_id,
                            wikidata_entity_label=wikidata_context.entity_label,
                            wikidata_hints=wikidata_context.hint_labels,
                            predictions=predictions,
                        )
                        candidates.append(candidate)

                        best = predictions[0] if predictions else None
                        log_step(
                            self._logger,
                            "pipeline.candidate_predicted",
                            "Generated mapping candidate",
                            {
                                "page": page.title,
                                "template": template.name,
                                "parameter": parameter.name,
                                "best": best.target_property if best else None,
                                "confidence": f"{best.confidence:.3f}" if best else None,
                            },
                        )
        except PipelineError:
            raise
        except Exception as exc:
            raise PipelineError(f"Mapping pipeline failed: {exc}") from exc

        result = MappingPipelineResult(
            run_id=resolved_run_id,
            input_path=str(input_path),
            report_path=str(report_path),
            pages_seen=pages_seen,
            templates_seen=templates_seen,
            parameters_seen=parameters_seen,
            candidates_count=len(candidates),
            candidates_sample=candidates[:50],
        )
        self._write_report(result=result, candidates=candidates)

        log_step(
            self._logger,
            "pipeline.completed",
            "Mapping candidate pipeline completed",
            {
                "run_id": resolved_run_id,
                "pages_seen": pages_seen,
                "templates_seen": templates_seen,
                "parameters_seen": parameters_seen,
                "candidates": len(candidates),
                "report_path": report_path,
            },
        )
        return result

    def _wikidata_context_for_page(
        self,
        title: str,
        enabled: bool,
        cache: dict[str, WikidataContext],
    ) -> WikidataContext:
        if not enabled:
            return WikidataContext(entity_id=None, entity_label=None, property_hints=[])

        if title in cache:
            return cache[title]

        try:
            context = self._wikidata_client.get_context_for_title(title)
        except WikidataLookupError as exc:
            log_step(
                self._logger,
                "wikidata.lookup_failed",
                "Continuing without Wikidata hints",
                {"title": title, "reason": exc},
            )
            context = WikidataContext(entity_id=None, entity_label=None, property_hints=[])

        cache[title] = context
        return context

    def _write_report(
        self,
        result: MappingPipelineResult,
        candidates: list[MappingCandidate],
    ) -> None:
        payload = {
            "run_id": result.run_id,
            "input_path": result.input_path,
            "pages_seen": result.pages_seen,
            "templates_seen": result.templates_seen,
            "parameters_seen": result.parameters_seen,
            "candidates_count": result.candidates_count,
            "candidates": [asdict(candidate) for candidate in candidates],
        }
        Path(result.report_path).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _value_sample(self, value: str, limit: int = 160) -> str:
        compact = " ".join(value.split())
        return compact if len(compact) <= limit else f"{compact[: limit - 3]}..."


pipeline_job_store = InMemoryPipelineJobStore()
