from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from amdb.core.errors import AmdbError
from amdb.core.paths import assert_file_exists, ensure_data_dirs, resolve_user_path
from amdb.schemas.pipeline import (
    MappingCandidateResponse,
    MappingPredictionResponse,
    PipelineJobResponse,
    PipelineRunRequest,
    PipelineRunResponse,
)
from amdb.services.mapping_pipeline import (
    MappingCandidate,
    MappingPipelineResult,
    MappingPipelineService,
    PipelineJob,
    pipeline_job_store,
)

router = APIRouter()


@router.post("/runs", response_model=PipelineJobResponse)
def start_pipeline_run(
    request: PipelineRunRequest,
    background_tasks: BackgroundTasks,
) -> PipelineJobResponse:
    ensure_data_dirs()
    input_path = resolve_user_path(request.input_path)
    try:
        assert_file_exists(input_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    job = pipeline_job_store.create(input_path=str(input_path), job_id=request.run_name)
    background_tasks.add_task(_run_background_pipeline, job.job_id, request, str(input_path))
    return _job_response(job)


@router.get("/runs/{job_id}", response_model=PipelineJobResponse)
def get_pipeline_run(job_id: str) -> PipelineJobResponse:
    job = pipeline_job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Pipeline job not found: {job_id}")
    return _job_response(job)


@router.post("/preview", response_model=PipelineRunResponse)
def preview_pipeline_run(request: PipelineRunRequest) -> PipelineRunResponse:
    ensure_data_dirs()
    input_path = resolve_user_path(request.input_path)
    try:
        assert_file_exists(input_path)
        result = MappingPipelineService().run(
            input_path=input_path,
            run_id=request.run_name,
            max_pages=request.max_pages,
            top_k=request.top_k,
            use_wikidata=request.use_wikidata,
            use_existing_mappings=request.use_existing_mappings,
            use_ml_model=request.use_ml_model,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AmdbError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return _run_response(result)


def _run_background_pipeline(job_id: str, request: PipelineRunRequest, input_path: str) -> None:
    pipeline_job_store.set_running(job_id)
    try:
        result = MappingPipelineService().run(
            input_path=resolve_user_path(input_path),
            run_id=job_id,
            max_pages=request.max_pages,
            top_k=request.top_k,
            use_wikidata=request.use_wikidata,
            use_existing_mappings=request.use_existing_mappings,
            use_ml_model=request.use_ml_model,
        )
    except Exception as exc:
        pipeline_job_store.set_failed(job_id, str(exc))
        return

    pipeline_job_store.set_succeeded(job_id, result.report_path)


def _run_response(result: MappingPipelineResult) -> PipelineRunResponse:
    return PipelineRunResponse(
        run_id=result.run_id,
        input_path=result.input_path,
        report_path=result.report_path,
        pages_seen=result.pages_seen,
        templates_seen=result.templates_seen,
        parameters_seen=result.parameters_seen,
        candidates_count=result.candidates_count,
        candidates_sample=[
            _candidate_response(candidate) for candidate in result.candidates_sample
        ],
    )


def _candidate_response(candidate: MappingCandidate) -> MappingCandidateResponse:
    return MappingCandidateResponse(
        page_title=candidate.page_title,
        page_id=candidate.page_id,
        template_name=candidate.template_name,
        parameter_name=candidate.parameter_name,
        value_sample=candidate.value_sample,
        wikidata_entity_id=candidate.wikidata_entity_id,
        wikidata_entity_label=candidate.wikidata_entity_label,
        wikidata_hints=candidate.wikidata_hints,
        predictions=[
            MappingPredictionResponse(
                target_property=prediction.target_property,
                target_uri=prediction.target_uri,
                label=prediction.label,
                confidence=prediction.confidence,
                source=prediction.source,
                model_name=prediction.model_name,
            )
            for prediction in candidate.predictions
        ],
    )


def _job_response(job: PipelineJob) -> PipelineJobResponse:
    return PipelineJobResponse(
        job_id=job.job_id,
        status=job.status.value,
        input_path=job.input_path,
        report_path=job.report_path,
        error=job.error,
    )
