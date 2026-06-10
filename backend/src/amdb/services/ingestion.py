from __future__ import annotations

import bz2
import importlib
from collections.abc import Iterator
from contextlib import AbstractContextManager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, cast
from xml.etree import ElementTree as ET

from amdb.core.errors import InvalidDumpError
from amdb.core.logging import get_logger, log_step


@dataclass(frozen=True, slots=True)
class TemplateParameter:
    name: str
    value: str


@dataclass(frozen=True, slots=True)
class ParsedTemplate:
    name: str
    parameters: list[TemplateParameter]


@dataclass(frozen=True, slots=True)
class ParsedPage:
    title: str
    page_id: str | None
    templates: list[ParsedTemplate]


class DumpTemplateParser:
    """Stream a MediaWiki dump and extract infobox-like template parameters."""

    INFOBOX_MARKERS = ("infobox", "info box", "መረጃ", "ሳጥን")

    def __init__(self) -> None:
        self._logger = get_logger(__name__)
        self._mwparser = self._load_mwparser()

    def iter_pages(self, input_path: Path, max_pages: int | None = None) -> Iterator[ParsedPage]:
        log_step(
            self._logger,
            "ingestion.started",
            "Streaming MediaWiki dump",
            {"input_path": input_path, "max_pages": max_pages},
        )

        pages_seen = 0
        pages_with_templates = 0

        try:
            with self._open_binary(input_path) as file:
                for _event, elem in ET.iterparse(file, events=("end",)):
                    if self._local_name(elem.tag) != "page":
                        continue

                    pages_seen += 1
                    parsed_page = self._parse_page(elem)
                    elem.clear()

                    if parsed_page is not None:
                        if parsed_page.templates:
                            pages_with_templates += 1
                            log_step(
                                self._logger,
                                "ingestion.page_parsed",
                                "Extracted templates from page",
                                {
                                    "title": parsed_page.title,
                                    "templates": len(parsed_page.templates),
                                    "page_number": pages_seen,
                                },
                            )
                        yield parsed_page

                    if max_pages is not None and pages_seen >= max_pages:
                        break
        except (ET.ParseError, OSError, UnicodeDecodeError) as exc:
            raise InvalidDumpError(f"Could not stream MediaWiki dump {input_path}: {exc}") from exc
        finally:
            log_step(
                self._logger,
                "ingestion.completed",
                "Finished streaming MediaWiki dump",
                {"pages_seen": pages_seen, "pages_with_templates": pages_with_templates},
            )

    def iter_template_pages(
        self,
        input_path: Path,
        max_pages: int | None = None,
    ) -> Iterator[ParsedPage]:
        for page in self.iter_pages(input_path=input_path, max_pages=max_pages):
            if page.templates:
                yield page

    def parse_wikitext(self, text: str) -> list[ParsedTemplate]:
        if self._mwparser is not None:
            templates = self._parse_with_mwparser(text)
        else:
            templates = self._parse_with_fallback(text)

        return [template for template in templates if self._is_infobox_like(template)]

    def _parse_page(self, page_el: ET.Element[str]) -> ParsedPage | None:
        title = self._first_text(page_el, "title") or ""
        page_id = self._first_direct_text(page_el, "id")
        text = self._first_text(page_el, "text") or ""
        if not title:
            return None

        templates = self.parse_wikitext(text) if text else []
        return ParsedPage(title=title, page_id=page_id, templates=templates)

    def _parse_with_mwparser(self, text: str) -> list[ParsedTemplate]:
        mwparser = self._mwparser
        if mwparser is None:
            return self._parse_with_fallback(text)

        wikicode = mwparser.parse(text)
        templates: list[ParsedTemplate] = []

        for raw_template in wikicode.filter_templates(recursive=False):
            template_name = str(raw_template.name).strip()
            parameters: list[TemplateParameter] = []

            for raw_param in raw_template.params:
                name = str(raw_param.name).strip()
                if not name or name.isdecimal():
                    continue

                parameters.append(
                    TemplateParameter(
                        name=name,
                        value=str(raw_param.value).strip(),
                    )
                )

            if parameters:
                templates.append(ParsedTemplate(name=template_name, parameters=parameters))

        return templates

    def _parse_with_fallback(self, text: str) -> list[ParsedTemplate]:
        templates: list[ParsedTemplate] = []

        for body in self._extract_top_level_template_bodies(text):
            parts = self._split_top_level(body)
            if not parts:
                continue

            template_name = parts[0].strip()
            parameters: list[TemplateParameter] = []

            for raw_part in parts[1:]:
                if "=" not in raw_part:
                    continue

                name, value = raw_part.split("=", 1)
                name = name.strip()
                if not name or name.isdecimal():
                    continue

                parameters.append(TemplateParameter(name=name, value=value.strip()))

            if template_name and parameters:
                templates.append(ParsedTemplate(name=template_name, parameters=parameters))

        return templates

    def _extract_top_level_template_bodies(self, text: str) -> list[str]:
        bodies: list[str] = []
        depth = 0
        start: int | None = None
        index = 0

        while index < len(text) - 1:
            pair = text[index : index + 2]
            if pair == "{{":
                if depth == 0:
                    start = index + 2
                depth += 1
                index += 2
                continue

            if pair == "}}" and depth:
                depth -= 1
                if depth == 0 and start is not None:
                    bodies.append(text[start:index])
                    start = None
                index += 2
                continue

            index += 1

        return bodies

    def _split_top_level(self, body: str) -> list[str]:
        parts: list[str] = []
        depth = 0
        start = 0
        index = 0

        while index < len(body):
            pair = body[index : index + 2]
            if pair == "{{":
                depth += 1
                index += 2
                continue
            if pair == "}}" and depth:
                depth -= 1
                index += 2
                continue
            if body[index] == "|" and depth == 0:
                parts.append(body[start:index])
                start = index + 1
            index += 1

        parts.append(body[start:])
        return parts

    def _is_infobox_like(self, template: ParsedTemplate) -> bool:
        normalized_name = template.name.replace("_", " ").casefold()
        return any(marker in normalized_name for marker in self.INFOBOX_MARKERS)

    def _first_text(self, element: ET.Element[str], local_name: str) -> str | None:
        for child in element.iter():
            if self._local_name(child.tag) == local_name:
                return "".join(child.itertext())
        return None

    def _first_direct_text(self, element: ET.Element[str], local_name: str) -> str | None:
        for child in list(element):
            if self._local_name(child.tag) == local_name:
                return child.text
        return None

    def _open_binary(self, path: Path) -> AbstractContextManager[BinaryIO]:
        if path.name.endswith(".bz2"):
            return cast(AbstractContextManager[BinaryIO], bz2.open(path, "rb"))
        return cast(AbstractContextManager[BinaryIO], path.open("rb"))

    def _load_mwparser(self) -> Any | None:
        try:
            module = importlib.import_module("mwparserfromhell")
        except ModuleNotFoundError:
            log_step(
                self._logger,
                "ingestion.parser_fallback",
                "mwparserfromhell not installed; using conservative fallback parser",
            )
            return None

        log_step(
            self._logger,
            "ingestion.parser_loaded",
            "Loaded mwparserfromhell parser",
        )
        return module

    def _local_name(self, tag: str) -> str:
        return tag.rsplit("}", 1)[-1] if "}" in tag else tag
