import logging
from collections.abc import Mapping
from typing import Any


def configure_logging() -> None:
    if logging.getLogger().handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)


def log_step(
    logger: logging.Logger,
    step: str,
    message: str,
    fields: Mapping[str, Any] | None = None,
) -> None:
    """Emit readable step logs without requiring a JSON logging dependency."""

    field_text = _format_fields(fields or {})
    suffix = f" {field_text}" if field_text else ""
    logger.info("[%s] %s%s", step, message, suffix)


def _format_fields(fields: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for key, value in fields.items():
        if value is None:
            continue
        text = str(value).replace("\n", "\\n")
        if len(text) > 160:
            text = f"{text[:157]}..."
        parts.append(f"{key}={text}")
    return " ".join(parts)
