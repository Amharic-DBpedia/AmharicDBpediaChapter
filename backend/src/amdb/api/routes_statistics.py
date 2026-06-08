from fastapi import APIRouter, HTTPException

from amdb.core.paths import ensure_data_dirs, resolve_user_path
from amdb.schemas.statistics import (
    StatisticsRunListResponse,
    StatisticsRunRequest,
    StatisticsRunResponse,
    StatisticsRunSummaryResponse,
)
from amdb.services.statistics import StatisticsService

router = APIRouter()


@router.post("/generate", response_model=StatisticsRunResponse)
def generate_statistics(request: StatisticsRunRequest) -> StatisticsRunResponse:
    ensure_data_dirs()
    source_dir = resolve_user_path(request.source_dir)
    if not source_dir.exists():
        raise HTTPException(status_code=404, detail=f"Statistics source not found: {source_dir}")

    service = StatisticsService()
    result = service.generate(
        source_dir=source_dir,
        run_id=request.run_name,
        dump_date=request.dump_date,
        extraction_run_id=request.extraction_run_id,
        use_native_def_stats=request.use_native_def_stats,
        max_files=request.max_files,
    )
    return StatisticsRunResponse.model_validate(service.to_payload(result))


@router.get("/latest", response_model=StatisticsRunResponse)
def latest_statistics() -> StatisticsRunResponse:
    try:
        payload = StatisticsService().load_latest()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return StatisticsRunResponse.model_validate(payload)


@router.get("/runs", response_model=StatisticsRunListResponse)
def list_statistics_runs() -> StatisticsRunListResponse:
    runs = [
        StatisticsRunSummaryResponse.model_validate(summary)
        for summary in StatisticsService().list_runs()
    ]
    return StatisticsRunListResponse(runs=runs)


@router.get("/runs/{run_id}", response_model=StatisticsRunResponse)
def statistics_run(run_id: str) -> StatisticsRunResponse:
    try:
        payload = StatisticsService().load_run(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return StatisticsRunResponse.model_validate(payload)
