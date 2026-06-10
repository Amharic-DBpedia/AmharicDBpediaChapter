from __future__ import annotations

import os
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from amdb.config import settings
from amdb.core.errors import DefRunnerError
from amdb.core.logging import get_logger, log_step


@dataclass(frozen=True)
class DefRunResult:
    run_id: str
    sanitized_dump_path: str
    output_dir: str
    stdout_path: str
    stderr_path: str
    exit_code: int

    @property
    def success(self) -> bool:
        return self.exit_code == 0


class DefRunner:
    def __init__(self) -> None:
        self._logger = get_logger(__name__)

    def run(
        self,
        sanitized_dump_path: Path,
        config_path: Path,
        run_name: str | None = None,
    ) -> DefRunResult:
        log_step(
            self._logger,
            "def_runner.started",
            "Starting DBpedia Extraction Framework run",
            {
                "sanitized_dump_path": sanitized_dump_path,
                "config_path": config_path,
                "run_name": run_name,
            },
        )

        if not settings.def_runner_script.is_file():
            log_step(
                self._logger,
                "def_runner.validation_failed",
                "DEF runner script was not found",
                {"def_runner_script": settings.def_runner_script},
            )
            raise DefRunnerError(f"DEF runner script not found: {settings.def_runner_script}")
        if not settings.resolved_def_dir.is_dir():
            log_step(
                self._logger,
                "def_runner.validation_failed",
                "DEF checkout was not found",
                {"def_dir": settings.resolved_def_dir},
            )
            raise DefRunnerError(f"DEF checkout not found: {settings.resolved_def_dir}")

        run_id = run_name or str(uuid.uuid4())
        output_dir = settings.def_runs_dir / run_id
        output_dir.mkdir(parents=True, exist_ok=True)

        stdout_path = output_dir / "stdout.log"
        stderr_path = output_dir / "stderr.log"

        command = [
            "bash",
            str(settings.def_runner_script),
            str(sanitized_dump_path),
            str(output_dir),
            str(config_path),
        ]

        log_step(
            self._logger,
            "def_runner.validation_completed",
            "Validated DEF inputs",
            {
                "def_runner_script": settings.def_runner_script,
                "def_dir": settings.resolved_def_dir,
                "output_dir": output_dir,
            },
        )
        log_step(
            self._logger,
            "def_runner.command_prepared",
            "Prepared DEF shell command",
            {"command": " ".join(command)},
        )

        started_at = time.monotonic()
        log_step(
            self._logger,
            "def_runner.process_started",
            "Launching DEF process",
            {"run_id": run_id},
        )
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            env={**os.environ, "DEF_DIR": str(settings.resolved_def_dir)},
        )
        duration_seconds = time.monotonic() - started_at

        log_step(
            self._logger,
            "def_runner.process_completed",
            "DEF process completed",
            {
                "run_id": run_id,
                "exit_code": process.returncode,
                "duration_seconds": f"{duration_seconds:.2f}",
            },
        )

        stdout_path.write_text(process.stdout, encoding="utf-8")
        stderr_path.write_text(process.stderr, encoding="utf-8")
        log_step(
            self._logger,
            "def_runner.logs_written",
            "Captured DEF stdout and stderr",
            {
                "stdout_path": stdout_path,
                "stderr_path": stderr_path,
                "stdout_chars": len(process.stdout),
                "stderr_chars": len(process.stderr),
            },
        )

        if process.returncode != 0:
            log_step(
                self._logger,
                "def_runner.failed",
                "DEF returned a non-zero exit code",
                {
                    "run_id": run_id,
                    "exit_code": process.returncode,
                    "stdout_tail": self._tail(process.stdout),
                    "stderr_tail": self._tail(process.stderr),
                },
            )
        else:
            log_step(
                self._logger,
                "def_runner.succeeded",
                "DEF run completed successfully",
                {"run_id": run_id, "output_dir": output_dir},
            )

        return DefRunResult(
            run_id=run_id,
            sanitized_dump_path=str(sanitized_dump_path),
            output_dir=str(output_dir),
            stdout_path=str(stdout_path),
            stderr_path=str(stderr_path),
            exit_code=process.returncode,
        )

    def _tail(self, text: str, limit: int = 600) -> str:
        compact = " ".join(text.split())
        if len(compact) <= limit:
            return compact
        return f"{compact[-limit:]}"
