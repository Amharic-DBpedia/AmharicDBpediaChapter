from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException

from amdb.config import settings
from amdb.core.errors import DefRunnerError
from amdb.core.logging import get_logger, log_step
from amdb.core.paths import assert_file_exists, ensure_data_dirs, resolve_user_path
from amdb.schemas.extraction import DefRunRequest, DefRunResponse
from amdb.services.def_runner import DefRunner
from amdb.services.statistics import StatisticsService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/run-def", response_model=DefRunResponse)
def run_def(request: DefRunRequest, background_tasks: BackgroundTasks) -> DefRunResponse:
    ensure_data_dirs()
    sanitized_dump_path = resolve_user_path(request.sanitized_dump_path)
    config_path = settings.default_def_config
    if request.config_path:
        config_path = resolve_user_path(request.config_path)

    try:
        assert_file_exists(sanitized_dump_path)
        assert_file_exists(config_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        result = DefRunner().run(
            sanitized_dump_path=sanitized_dump_path,
            config_path=config_path,
            run_name=request.run_name,
        )
    except DefRunnerError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    statistics_job_scheduled = False
    if result.success and request.generate_statistics:
        statistics_source_dir = (
            resolve_user_path(request.statistics_source_dir)
            if request.statistics_source_dir
            else Path(result.output_dir)
        )
        background_tasks.add_task(
            _generate_statistics_after_def,
            result.run_id,
            statistics_source_dir,
            request.use_native_def_statistics,
            request.statistics_max_files,
        )
        statistics_job_scheduled = True
        log_step(
            logger,
            "extraction.statistics_scheduled",
            "Scheduled post-extraction statistics generation",
            {
                "run_id": result.run_id,
                "statistics_source_dir": statistics_source_dir,
                "use_native_def_statistics": request.use_native_def_statistics,
            },
        )

    return DefRunResponse(
        run_id=result.run_id,
        sanitized_dump_path=result.sanitized_dump_path,
        output_dir=result.output_dir,
        stdout_path=result.stdout_path,
        stderr_path=result.stderr_path,
        exit_code=result.exit_code,
        success=result.success,
        statistics_job_scheduled=statistics_job_scheduled,
    )


def _generate_statistics_after_def(
    extraction_run_id: str,
    source_dir: Path,
    use_native_def_statistics: bool,
    max_files: int | None,
) -> None:
    try:
        result = StatisticsService().generate(
            source_dir=source_dir,
            run_id=f"{extraction_run_id}-statistics",
            extraction_run_id=extraction_run_id,
            use_native_def_stats=use_native_def_statistics,
            max_files=max_files,
        )
    except Exception as exc:
        log_step(
            logger,
            "extraction.statistics_failed",
            "Post-extraction statistics generation failed",
            {"extraction_run_id": extraction_run_id, "source_dir": source_dir, "error": exc},
        )
        return

    log_step(
        logger,
        "extraction.statistics_completed",
        "Post-extraction statistics generation completed",
        {
            "extraction_run_id": extraction_run_id,
            "statistics_run_id": result.run_id,
            "success": result.success,
            "report_path": result.report_path,
        },
    )
