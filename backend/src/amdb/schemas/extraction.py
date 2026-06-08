from pydantic import BaseModel, Field


class DefRunRequest(BaseModel):
    sanitized_dump_path: str
    config_path: str | None = None
    run_name: str | None = None
    generate_statistics: bool = Field(
        default=True,
        description="Schedule statistics generation when DEF exits successfully.",
    )
    statistics_source_dir: str | None = Field(
        default=None,
        description=(
            "Optional RDF output directory to scan for statistics. Defaults to the DEF run output "
            "directory and scans recursively."
        ),
    )
    use_native_def_statistics: bool = Field(
        default=False,
        description=(
            "Also run DEF collectStats.sh after extraction when the output layout supports it."
        ),
    )
    statistics_max_files: int | None = Field(
        default=None,
        ge=1,
        le=1000,
        description="Optional file cap for statistics smoke tests.",
    )


class DefRunResponse(BaseModel):
    run_id: str
    sanitized_dump_path: str
    output_dir: str
    stdout_path: str
    stderr_path: str
    exit_code: int
    success: bool
    statistics_job_scheduled: bool
