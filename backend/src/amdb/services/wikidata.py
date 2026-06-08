from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from amdb.config import settings
from amdb.core.errors import WikidataLookupError
from amdb.core.logging import get_logger, log_step


@dataclass(frozen=True, slots=True)
class WikidataPropertyHint:
    property_id: str
    label: str


@dataclass(frozen=True, slots=True)
class WikidataContext:
    entity_id: str | None
    entity_label: str | None
    property_hints: list[WikidataPropertyHint]

    @property
    def hint_labels(self) -> list[str]:
        return [hint.label for hint in self.property_hints]


class WikidataClient:
    """Resolve an Amharic Wikipedia page title to Wikidata property-label hints."""

    def __init__(
        self,
        api_url: str | None = None,
        timeout_seconds: float | None = None,
        user_agent: str | None = None,
    ) -> None:
        self._api_url = api_url or settings.wikidata_api_url
        self._timeout_seconds = timeout_seconds or settings.wikidata_timeout_seconds
        self._user_agent = user_agent or settings.wikidata_user_agent
        self._logger = get_logger(__name__)

    def get_context_for_title(self, title: str) -> WikidataContext:
        log_step(
            self._logger,
            "wikidata.lookup_started",
            "Resolving Amharic Wikipedia title in Wikidata",
            {"title": title},
        )

        entity = self._fetch_entity_for_title(title)
        if entity is None:
            log_step(
                self._logger,
                "wikidata.lookup_missing",
                "No Wikidata entity found for page title",
                {"title": title},
            )
            return WikidataContext(entity_id=None, entity_label=None, property_hints=[])

        entity_id = self._string_or_none(entity.get("id"))
        entity_label = self._extract_entity_label(entity)
        property_ids = self._extract_claim_property_ids(entity)
        hints = self._fetch_property_hints(property_ids)

        log_step(
            self._logger,
            "wikidata.hints_loaded",
            "Loaded Wikidata property hints",
            {"title": title, "entity_id": entity_id, "hints": len(hints)},
        )

        return WikidataContext(
            entity_id=entity_id,
            entity_label=entity_label,
            property_hints=hints,
        )

    def _fetch_entity_for_title(self, title: str) -> dict[str, Any] | None:
        payload = self._request_json(
            {
                "action": "wbgetentities",
                "format": "json",
                "sites": "amwiki",
                "titles": title,
                "props": "labels|claims",
                "languages": "en",
            }
        )

        entities = payload.get("entities")
        if not isinstance(entities, dict):
            return None

        for raw_entity in entities.values():
            if isinstance(raw_entity, dict) and not raw_entity.get("missing"):
                return raw_entity
        return None

    def _fetch_property_hints(self, property_ids: list[str]) -> list[WikidataPropertyHint]:
        if not property_ids:
            return []

        payload = self._request_json(
            {
                "action": "wbgetentities",
                "format": "json",
                "ids": "|".join(property_ids[:50]),
                "props": "labels",
                "languages": "en",
            }
        )

        entities = payload.get("entities")
        if not isinstance(entities, dict):
            return []

        hints: list[WikidataPropertyHint] = []
        for property_id in property_ids:
            raw_property = entities.get(property_id)
            if not isinstance(raw_property, dict):
                continue

            label = self._extract_entity_label(raw_property)
            if label:
                hints.append(WikidataPropertyHint(property_id=property_id, label=label))

        return hints

    def _request_json(self, params: dict[str, str]) -> dict[str, Any]:
        query = urlencode(params)
        request = Request(
            f"{self._api_url}?{query}",
            headers={"User-Agent": self._user_agent},
        )

        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                payload = json.load(response)
        except (HTTPError, URLError, OSError, TimeoutError, json.JSONDecodeError) as exc:
            raise WikidataLookupError(f"Wikidata request failed: {exc}") from exc

        if not isinstance(payload, dict):
            raise WikidataLookupError("Wikidata returned a non-object JSON payload")
        return payload

    def _extract_claim_property_ids(self, entity: dict[str, Any]) -> list[str]:
        claims = entity.get("claims")
        if not isinstance(claims, dict):
            return []

        property_ids = [key for key in claims if isinstance(key, str) and key.startswith("P")]
        return sorted(property_ids)

    def _extract_entity_label(self, entity: dict[str, Any]) -> str | None:
        labels = entity.get("labels")
        if not isinstance(labels, dict):
            return None

        english = labels.get("en")
        if not isinstance(english, dict):
            return None

        return self._string_or_none(english.get("value"))

    def _string_or_none(self, value: object) -> str | None:
        return value if isinstance(value, str) and value else None
