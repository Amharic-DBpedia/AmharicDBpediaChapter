from pydantic import BaseModel, Field


class SanitizerRuleCount(BaseModel):
    rule_id: str
    count: int


class SanitizerChangedPage(BaseModel):
    title: str
    rule_ids: list[str]
    before_hash: str
    after_hash: str


class SanitizerRequest(BaseModel):
    input_path: str = Field(..., description="Path to raw Amharic Wikipedia XML dump.")
    output_name: str | None = Field(
        default=None,
        description="Optional output file name under data/sanitized.",
    )


class SanitizerResponse(BaseModel):
    input_path: str
    output_path: str
    report_path: str
    pages_seen: int
    pages_changed: int
    rules_applied: list[SanitizerRuleCount]
    changed_pages_sample: list[SanitizerChangedPage]
