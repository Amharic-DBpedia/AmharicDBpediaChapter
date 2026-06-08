from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from amdb.config import settings
from amdb.core.errors import OntologyCatalogError
from amdb.core.logging import get_logger, log_step


@dataclass(frozen=True, slots=True)
class OntologyProperty:
    local_name: str
    curie: str
    uri: str
    label: str
    property_type: str

    @property
    def search_text(self) -> str:
        return f"{self.label} {self.local_name} {self.curie}"


@dataclass(frozen=True, slots=True)
class ExistingTemplateMapping:
    template_property: str
    ontology_property: str


class DbpediaOntologyCatalog:
    LABEL_RE = re.compile(r"\{\{\s*label\s*\|\s*en\s*\|\s*([^}|]+)", re.IGNORECASE)
    PREFIX_URIS = {
        "dbo": "http://dbpedia.org/ontology/",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    }

    def __init__(self, properties: list[OntologyProperty]) -> None:
        if not properties:
            raise OntologyCatalogError("DBpedia ontology catalog is empty")

        self.properties = properties
        self._by_name: dict[str, OntologyProperty] = {}
        for prop in properties:
            self._by_name[self._normalize_property_name(prop.local_name)] = prop
            self._by_name[self._normalize_property_name(prop.curie)] = prop

    @classmethod
    def from_default_def_checkout(cls) -> DbpediaOntologyCatalog:
        return cls.from_ontology_xml(settings.def_ontology_xml)

    @classmethod
    def from_ontology_xml(cls, ontology_path: Path) -> DbpediaOntologyCatalog:
        logger = get_logger(__name__)
        if not ontology_path.is_file():
            raise OntologyCatalogError(f"DBpedia ontology XML not found: {ontology_path}")

        log_step(
            logger,
            "ontology.load_started",
            "Loading DBpedia ontology properties",
            {"ontology_path": ontology_path},
        )

        properties: list[OntologyProperty] = []
        try:
            for _event, elem in ET.iterparse(ontology_path, events=("end",)):
                if cls._local_name(elem.tag) != "page":
                    continue

                prop = cls._property_from_page(elem)
                elem.clear()
                if prop is not None:
                    properties.append(prop)
        except (ET.ParseError, OSError, UnicodeDecodeError) as exc:
            message = f"Could not load ontology XML {ontology_path}: {exc}"
            raise OntologyCatalogError(message) from exc

        log_step(
            logger,
            "ontology.load_completed",
            "Loaded DBpedia ontology properties",
            {"properties": len(properties)},
        )

        return cls(properties)

    def find(self, name: str) -> OntologyProperty | None:
        return self._by_name.get(self._normalize_property_name(name))

    @classmethod
    def _property_from_page(cls, page_el: ET.Element[str]) -> OntologyProperty | None:
        title = cls._first_text(page_el, "title") or ""
        if not title.startswith("OntologyProperty:"):
            return None

        wiki_name = title.split(":", 1)[1].strip()
        local_name = cls._wiki_title_to_property_name(wiki_name)
        text = cls._first_text(page_el, "text") or ""
        label = cls._extract_english_label(text) or cls._humanize_property_name(local_name)
        property_type = cls._extract_property_type(text)

        curie = local_name if ":" in local_name else f"dbo:{local_name}"

        return OntologyProperty(
            local_name=local_name,
            curie=curie,
            uri=cls._property_uri(curie),
            label=label,
            property_type=property_type,
        )

    @classmethod
    def _extract_english_label(cls, text: str) -> str | None:
        match = cls.LABEL_RE.search(text)
        if not match:
            return None
        return re.sub(r"\s+", " ", match.group(1)).strip()

    @staticmethod
    def _extract_property_type(text: str) -> str:
        if re.search(r"\{\{\s*ObjectProperty\b", text, flags=re.IGNORECASE):
            return "ObjectProperty"
        if re.search(r"\{\{\s*DatatypeProperty\b", text, flags=re.IGNORECASE):
            return "DatatypeProperty"
        return "Property"

    @staticmethod
    def _wiki_title_to_property_name(name: str) -> str:
        if not name:
            return name
        return f"{name[0].lower()}{name[1:]}"

    @staticmethod
    def _humanize_property_name(name: str) -> str:
        spaced = re.sub(r"(?<!^)(?=[A-Z])", " ", name)
        return spaced.replace("_", " ").strip().lower()

    @staticmethod
    def _normalize_property_name(name: str) -> str:
        value = name.strip()
        if value.startswith("dbo:"):
            value = value.split(":", 1)[1]
        if value.startswith("http://dbpedia.org/ontology/"):
            value = value.rsplit("/", 1)[1]
        return value.casefold()

    @classmethod
    def _property_uri(cls, curie: str) -> str:
        if ":" not in curie:
            return f"http://dbpedia.org/ontology/{curie}"

        prefix, local_name = curie.split(":", 1)
        base_uri = cls.PREFIX_URIS.get(prefix)
        return f"{base_uri}{local_name}" if base_uri else curie

    @staticmethod
    def _first_text(element: ET.Element[str], local_name: str) -> str | None:
        for child in element.iter():
            if DbpediaOntologyCatalog._local_name(child.tag) == local_name:
                return "".join(child.itertext())
        return None

    @staticmethod
    def _local_name(tag: str) -> str:
        return tag.rsplit("}", 1)[-1] if "}" in tag else tag


class AmharicMappingIndex:
    PROPERTY_MAPPING_RE = re.compile(
        r"\{\{\s*PropertyMapping\b(?P<body>.*?)\}\}",
        re.IGNORECASE | re.DOTALL,
    )
    TEMPLATE_PROPERTY_RE = re.compile(
        r"\|\s*templateProperty\s*=\s*(?P<value>[^|}\n]+)",
        re.IGNORECASE,
    )
    ONTOLOGY_PROPERTY_RE = re.compile(
        r"\|\s*ontologyProperty\s*=\s*(?P<value>[^|}\n]+)",
        re.IGNORECASE,
    )

    def __init__(self, mappings: dict[str, ExistingTemplateMapping]) -> None:
        self._mappings = mappings

    @classmethod
    def from_default_def_checkout(cls) -> AmharicMappingIndex:
        return cls.from_mapping_xml(settings.amharic_mapping_xml)

    @classmethod
    def from_mapping_xml(cls, mapping_path: Path) -> AmharicMappingIndex:
        logger = get_logger(__name__)
        if not mapping_path.is_file():
            log_step(
                logger,
                "mapping_index.missing",
                "Amharic DEF mapping XML was not found",
                {"mapping_path": mapping_path},
            )
            return cls({})

        log_step(
            logger,
            "mapping_index.load_started",
            "Loading existing Amharic template mappings",
            {"mapping_path": mapping_path},
        )

        text = mapping_path.read_text(encoding="utf-8")
        mappings: dict[str, ExistingTemplateMapping] = {}

        for match in cls.PROPERTY_MAPPING_RE.finditer(text):
            body = match.group("body")
            template_match = cls.TEMPLATE_PROPERTY_RE.search(body)
            ontology_match = cls.ONTOLOGY_PROPERTY_RE.search(body)
            if template_match is None or ontology_match is None:
                continue

            template_property = cls._clean_mapping_value(template_match.group("value"))
            ontology_property = cls._clean_mapping_value(ontology_match.group("value"))
            if not template_property or not ontology_property:
                continue

            mappings.setdefault(
                cls._normalize_template_property(template_property),
                ExistingTemplateMapping(
                    template_property=template_property,
                    ontology_property=ontology_property,
                ),
            )

        log_step(
            logger,
            "mapping_index.load_completed",
            "Loaded existing Amharic template mappings",
            {"mappings": len(mappings)},
        )
        return cls(mappings)

    def lookup(self, template_property: str) -> ExistingTemplateMapping | None:
        return self._mappings.get(self._normalize_template_property(template_property))

    @staticmethod
    def _clean_mapping_value(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    @staticmethod
    def _normalize_template_property(value: str) -> str:
        normalized = re.sub(r"\s+", "_", value.strip())
        return normalized.strip("_").casefold()
