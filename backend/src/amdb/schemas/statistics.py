from pydantic import BaseModel, Field


class StatisticsRunRequest(BaseModel):
    source_dir: str = Field(
        ...,
        description=(
            "Directory or file containing DEF RDF outputs. Supports .ttl, .ttl.bz2, "
            ".nt, .nt.bz2, .ntriples, and .ntriples.bz2."
        ),
    )
    run_name: str | None = Field(default=None, description="Optional stable statistics run ID.")
    dump_date: str | None = Field(
        default=None,
        description="Optional Wikipedia dump date metadata.",
    )
    extraction_run_id: str | None = Field(
        default=None,
        description="Optional DEF run ID that produced the RDF files.",
    )
    use_native_def_stats: bool = Field(
        default=False,
        description=(
            "Also invoke DEF collectStats.sh. This requires DEF's release-style core-i18n "
            "layout and the correct Java runtime."
        ),
    )
    max_files: int | None = Field(
        default=None,
        ge=1,
        le=1000,
        description="Optional cap for smoke tests or demos.",
    )


class PredicateCountResponse(BaseModel):
    predicate: str
    count: int


class DatasetStatisticResponse(BaseModel):
    dataset_name: str
    file_path: str
    triple_count: int
    subject_count: int
    predicate_count: int
    object_count: int
    skipped_lines: int
    sample_predicates: list[PredicateCountResponse]


class NativeDefStatsResponse(BaseModel):
    attempted: bool
    success: bool
    exit_code: int | None
    stdout_path: str | None
    stderr_path: str | None
    statistics_dir: str | None
    error: str | None


class StatisticsRunResponse(BaseModel):
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
    dataset_statistics: list[DatasetStatisticResponse]
    native_def_stats: NativeDefStatsResponse
    error: str | None


class StatisticsRunSummaryResponse(BaseModel):
    run_id: str
    generated_at: str
    source_dir: str
    report_path: str
    success: bool
    total_triples: int
    file_count: int
    extraction_run_id: str | None


class StatisticsRunListResponse(BaseModel):
    runs: list[StatisticsRunSummaryResponse]
