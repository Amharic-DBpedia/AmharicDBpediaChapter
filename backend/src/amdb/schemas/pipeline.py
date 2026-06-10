from pydantic import BaseModel, Field


class PipelineRunRequest(BaseModel):
    input_path: str = Field(..., description="Path to raw or sanitized Amharic Wikipedia XML dump")
    run_name: str | None = Field(default=None, description="Stable run id/report prefix")
    max_pages: int = Field(default=10, ge=1, le=10_000)
    top_k: int = Field(default=5, ge=1, le=20)
    use_wikidata: bool = Field(default=True)
    use_existing_mappings: bool = Field(default=True)
    use_ml_model: bool = Field(default=True)


class MappingPredictionResponse(BaseModel):
    target_property: str
    target_uri: str
    label: str
    confidence: float
    source: str
    model_name: str


class MappingCandidateResponse(BaseModel):
    page_title: str
    page_id: str | None
    template_name: str
    parameter_name: str
    value_sample: str
    wikidata_entity_id: str | None
    wikidata_entity_label: str | None
    wikidata_hints: list[str]
    predictions: list[MappingPredictionResponse]


class PipelineRunResponse(BaseModel):
    run_id: str
    input_path: str
    report_path: str
    pages_seen: int
    templates_seen: int
    parameters_seen: int
    candidates_count: int
    candidates_sample: list[MappingCandidateResponse]


class PipelineJobResponse(BaseModel):
    job_id: str
    status: str
    input_path: str
    report_path: str | None
    error: str | None
