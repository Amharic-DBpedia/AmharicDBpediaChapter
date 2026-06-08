from fastapi import APIRouter, HTTPException

from amdb.core.errors import InvalidDumpError
from amdb.core.paths import assert_file_exists, ensure_data_dirs, resolve_user_path
from amdb.schemas.sanitizer import (
    SanitizerChangedPage,
    SanitizerRequest,
    SanitizerResponse,
    SanitizerRuleCount,
)
from amdb.services.artifacts import ArtifactService
from amdb.services.sanitizer import DumpSanitizer

router = APIRouter()


@router.post("/run", response_model=SanitizerResponse)
def run_sanitizer(request: SanitizerRequest) -> SanitizerResponse:
    ensure_data_dirs()
    input_path = resolve_user_path(request.input_path)

    try:
        assert_file_exists(input_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    output_path = ArtifactService().sanitized_output_path(input_path, request.output_name)

    try:
        result = DumpSanitizer().sanitize_dump(input_path=input_path, output_path=output_path)
    except InvalidDumpError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return SanitizerResponse(
        input_path=result.input_path,
        output_path=result.output_path,
        report_path=result.report_path,
        pages_seen=result.pages_seen,
        pages_changed=result.pages_changed,
        rules_applied=[
            SanitizerRuleCount(rule_id=rule_id, count=count)
            for rule_id, count in sorted(result.rules_applied.items())
        ],
        changed_pages_sample=[
            SanitizerChangedPage(
                title=page.title,
                rule_ids=page.rule_ids,
                before_hash=page.before_hash,
                after_hash=page.after_hash,
            )
            for page in result.changed_pages_sample
        ],
    )
