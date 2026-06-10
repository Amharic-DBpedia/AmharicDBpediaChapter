from __future__ import annotations

import bz2
import hashlib
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TextIO
from xml.etree import ElementTree as ET

from amdb.config import settings
from amdb.core.errors import InvalidDumpError
from amdb.core.logging import get_logger, log_step
from amdb.core.paths import ensure_parent
from amdb.services.artifacts import ArtifactService


@dataclass(frozen=True)
class ChangedPage:
    title: str
    rule_ids: list[str]
    before_hash: str
    after_hash: str


@dataclass(frozen=True)
class SanitizerResult:
    input_path: str
    output_path: str
    report_path: str
    pages_seen: int
    pages_changed: int
    rules_applied: dict[str, int]
    changed_pages_sample: list[ChangedPage]


@dataclass(frozen=True)
class SanitizerRule:
    rule_id: str
    pattern: re.Pattern[str]
    replacement: str


class DumpSanitizer:
    """Conservative sanitizer for Amharic Wikipedia XML before DEF parsing."""

    RULES: tuple[SanitizerRule, ...] = (
        SanitizerRule(
            "remove-style-attributes",
            re.compile(r"""style\s*=\s*(['"]).*?\1""", flags=re.IGNORECASE | re.DOTALL),
            "",
        ),
        SanitizerRule(
            "remove-css-float-declarations",
            re.compile(r"""(?i)\bfloat\s*:\s*(?:left|right|none)\s*;?"""),
            "",
        ),
        SanitizerRule(
            "remove-image-thumb-option",
            re.compile(r"""(?i)\|[ \t]*thumb[ \t]*(?=\||\]|\n)"""),
            "",
        ),
        SanitizerRule(
            "remove-image-px-option",
            re.compile(r"""(?i)\|[ \t]*\d{1,5}[ \t]*px[ \t]*(?=\||\]|\n)"""),
            "",
        ),
        SanitizerRule(
            "remove-raw-div-tags",
            re.compile(r"""(?i)</?div\b[^>]*>"""),
            "",
        ),
        SanitizerRule(
            "remove-raw-span-tags",
            re.compile(r"""(?i)</?span\b[^>]*>"""),
            "",
        ),
        SanitizerRule(
            "remove-table-style-option",
            re.compile(r"""(?im)^\s*[|!]\s*style\s*=\s*(['"]).*?\1\s*\|"""),
            "|",
        ),
    )

    def __init__(self, artifact_service: ArtifactService | None = None) -> None:
        self._artifact_service = artifact_service or ArtifactService()
        self._logger = get_logger(__name__)

    def sanitize_dump(self, input_path: Path, output_path: Path) -> SanitizerResult:
        log_step(
            self._logger,
            "sanitizer.started",
            "Starting dump sanitization",
            {
                "input_path": input_path,
                "output_path": output_path,
                "rules": len(self.RULES),
            },
        )
        ensure_parent(output_path)
        settings.reports_dir.mkdir(parents=True, exist_ok=True)

        try:
            log_step(
                self._logger,
                "sanitizer.input_read_started",
                "Reading dump text",
                {"input_path": input_path},
            )
            xml_text = self._read_text(input_path)
            log_step(
                self._logger,
                "sanitizer.input_read_completed",
                "Read dump text",
                {"characters": len(xml_text), "compressed": input_path.name.endswith(".bz2")},
            )
            log_step(
                self._logger,
                "sanitizer.xml_parse_started",
                "Parsing MediaWiki XML",
            )
            root = ET.fromstring(xml_text)
        except (ET.ParseError, OSError, UnicodeDecodeError) as exc:
            log_step(
                self._logger,
                "sanitizer.failed",
                "Could not read or parse dump",
                {"input_path": input_path, "reason": exc},
            )
            raise InvalidDumpError(f"Could not parse MediaWiki dump {input_path}: {exc}") from exc

        namespace = self._detect_namespace(root.tag)
        log_step(
            self._logger,
            "sanitizer.xml_parse_completed",
            "Parsed MediaWiki XML",
            {"root_tag": root.tag, "namespace": namespace or "none"},
        )

        pages_seen = 0
        changed_pages: list[ChangedPage] = []
        rule_counter: Counter[str] = Counter()

        log_step(
            self._logger,
            "sanitizer.pages_started",
            "Scanning pages for parser-breaking markup",
        )
        for page in root.findall(f".//{namespace}page"):
            pages_seen += 1
            title_el = page.find(f"{namespace}title")
            text_el = page.find(f".//{namespace}text")

            if title_el is None or text_el is None:
                continue

            title = title_el.text or ""
            original = self._extract_text_payload(text_el)
            if not original:
                continue

            sanitized, applied_rules = self.sanitize_wikitext(original)
            if sanitized == original:
                if pages_seen % 5000 == 0:
                    self._log_progress(pages_seen, len(changed_pages), rule_counter)
                continue

            for child in list(text_el):
                text_el.remove(child)
            text_el.text = sanitized

            changed_page = ChangedPage(
                title=title,
                rule_ids=applied_rules,
                before_hash=self._sha256(original),
                after_hash=self._sha256(sanitized),
            )
            changed_pages.append(changed_page)

            if len(changed_pages) <= 50:
                log_step(
                    self._logger,
                    "sanitizer.page_changed",
                    "Sanitized page text",
                    {
                        "page_number": pages_seen,
                        "title": title,
                        "rules": ",".join(applied_rules),
                        "before_hash": changed_page.before_hash,
                        "after_hash": changed_page.after_hash,
                    },
                )

            rule_counter.update(applied_rules)
            if pages_seen % 5000 == 0:
                self._log_progress(pages_seen, len(changed_pages), rule_counter)

        log_step(
            self._logger,
            "sanitizer.pages_completed",
            "Finished scanning pages",
            {
                "pages_seen": pages_seen,
                "pages_changed": len(changed_pages),
                "rules_applied": dict(rule_counter),
            },
        )

        output_content = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        log_step(
            self._logger,
            "sanitizer.output_write_started",
            "Writing sanitized dump",
            {
                "output_path": output_path,
                "bytes": len(output_content),
                "compressed": output_path.name.endswith(".bz2"),
            },
        )
        self._write_bytes(output_path, output_content)
        log_step(
            self._logger,
            "sanitizer.output_write_completed",
            "Wrote sanitized dump",
            {"output_path": output_path},
        )

        report_path = self._artifact_service.report_path_for(output_path)
        result = SanitizerResult(
            input_path=str(input_path),
            output_path=str(output_path),
            report_path=str(report_path),
            pages_seen=pages_seen,
            pages_changed=len(changed_pages),
            rules_applied=dict(rule_counter),
            changed_pages_sample=changed_pages[:50],
        )
        self._write_report(result)
        log_step(
            self._logger,
            "sanitizer.report_written",
            "Wrote sanitizer report",
            {"report_path": report_path, "sample_size": len(result.changed_pages_sample)},
        )
        log_step(
            self._logger,
            "sanitizer.completed",
            "Dump sanitization completed",
            {
                "input_path": input_path,
                "output_path": output_path,
                "report_path": report_path,
                "pages_seen": result.pages_seen,
                "pages_changed": result.pages_changed,
            },
        )
        return result

    def sanitize_wikitext(self, text: str) -> tuple[str, list[str]]:
        current = text
        applied_rules: list[str] = []

        for rule in self.RULES:
            current, count = rule.pattern.subn(rule.replacement, current)
            if count:
                applied_rules.append(rule.rule_id)

        return current, applied_rules

    def _log_progress(
        self,
        pages_seen: int,
        pages_changed: int,
        rule_counter: Counter[str],
    ) -> None:
        log_step(
            self._logger,
            "sanitizer.progress",
            "Sanitizer progress checkpoint",
            {
                "pages_seen": pages_seen,
                "pages_changed": pages_changed,
                "rules_applied": dict(rule_counter),
            },
        )

    def _read_text(self, path: Path) -> str:
        if path.name.endswith(".bz2"):
            with bz2.open(path, "rt", encoding="utf-8") as file:
                return file.read()
        return path.read_text(encoding="utf-8")

    def _write_bytes(self, path: Path, content: bytes) -> None:
        if path.name.endswith(".bz2"):
            with bz2.open(path, "wb") as file:
                file.write(content)
            return
        path.write_bytes(content)

    def _write_report(self, result: SanitizerResult) -> None:
        Path(result.report_path).write_text(
            json.dumps(
                {
                    "input_path": result.input_path,
                    "output_path": result.output_path,
                    "pages_seen": result.pages_seen,
                    "pages_changed": result.pages_changed,
                    "rules_applied": result.rules_applied,
                    "changed_pages_sample": [
                        asdict(page) for page in result.changed_pages_sample
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def _extract_text_payload(self, text_el: ET.Element[str]) -> str:
        if len(text_el) == 0:
            return text_el.text or ""

        return "".join(text_el.itertext())

    def _detect_namespace(self, tag: str) -> str:
        if tag.startswith("{"):
            return tag.split("}")[0] + "}"
        return ""

    def _sha256(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


def open_text(path: Path) -> TextIO:
    return bz2.open(path, "rt", encoding="utf-8") if path.name.endswith(".bz2") else path.open()
