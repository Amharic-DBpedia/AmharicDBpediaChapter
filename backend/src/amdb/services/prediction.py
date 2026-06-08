from __future__ import annotations

import importlib
import re
from dataclasses import dataclass
from typing import Any, cast

from amdb.config import settings
from amdb.core.logging import get_logger, log_step
from amdb.services.ontology import AmharicMappingIndex, DbpediaOntologyCatalog, OntologyProperty


@dataclass(frozen=True, slots=True)
class MappingPrediction:
    target_property: str
    target_uri: str
    label: str
    confidence: float
    source: str
    model_name: str


class AfroXlmrPropertyPredictor:
    TOKEN_RE = re.compile(r"[A-Za-z0-9]+")
    PREFIX_URIS = {
        "dbo": "http://dbpedia.org/ontology/",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    }

    def __init__(
        self,
        catalog: DbpediaOntologyCatalog,
        mapping_index: AmharicMappingIndex | None = None,
        model_name: str | None = None,
    ) -> None:
        self._catalog = catalog
        self._mapping_index = mapping_index or AmharicMappingIndex({})
        self._model_name = model_name or settings.afro_xlmr_model_name
        self._logger = get_logger(__name__)
        self._model: Any | None = None
        self._sentence_util: Any | None = None
        self._property_embeddings: Any | None = None

    @classmethod
    def from_default_def_checkout(cls) -> AfroXlmrPropertyPredictor:
        return cls(
            catalog=DbpediaOntologyCatalog.from_default_def_checkout(),
            mapping_index=AmharicMappingIndex.from_default_def_checkout(),
        )

    def predict(
        self,
        parameter_name: str,
        template_name: str,
        wikidata_hints: list[str],
        value_sample: str | None = None,
        top_k: int = 5,
        use_existing_mappings: bool = True,
        use_ml_model: bool = True,
    ) -> list[MappingPrediction]:
        if use_existing_mappings:
            existing = self._predict_from_existing_mapping(parameter_name)
            if existing is not None:
                log_step(
                    self._logger,
                    "predictor.existing_mapping_hit",
                    "Matched parameter against existing Amharic DEF mapping",
                    {
                        "parameter": parameter_name,
                        "target_property": existing.target_property,
                        "confidence": existing.confidence,
                    },
                )
                return [existing]

        query_text = self._build_query_text(
            parameter_name=parameter_name,
            template_name=template_name,
            wikidata_hints=wikidata_hints,
            value_sample=value_sample,
        )

        if use_ml_model:
            predictions = self._predict_with_model(query_text=query_text, top_k=top_k)
        else:
            predictions = self._predict_with_lexical_fallback(query_text=query_text, top_k=top_k)

        best = predictions[0] if predictions else None
        log_step(
            self._logger,
            "predictor.prediction_completed",
            "Predicted DBpedia ontology property",
            {
                "parameter": parameter_name,
                "best": best.target_property if best else None,
                "confidence": f"{best.confidence:.3f}" if best else None,
                "source": best.source if best else None,
            },
        )
        return predictions

    def _predict_from_existing_mapping(self, parameter_name: str) -> MappingPrediction | None:
        existing = self._mapping_index.lookup(parameter_name)
        if existing is None:
            return None

        ontology_property = existing.ontology_property
        catalog_property = self._catalog.find(ontology_property)
        if catalog_property is not None:
            return self._prediction_for_property(
                prop=catalog_property,
                confidence=1.0,
                source="existing-def-mapping",
                model_name="Mapping_am.xml",
            )

        target_property = self._as_curie(ontology_property)
        return MappingPrediction(
            target_property=target_property,
            target_uri=self._expand_curie(target_property),
            label=ontology_property,
            confidence=1.0,
            source="existing-def-mapping",
            model_name="Mapping_am.xml",
        )

    def _predict_with_model(self, query_text: str, top_k: int) -> list[MappingPrediction]:
        try:
            self._ensure_model_loaded()
        except (ModuleNotFoundError, OSError, RuntimeError) as exc:
            log_step(
                self._logger,
                "predictor.ml_fallback",
                "Could not load Afro-XLM-R model; using lexical fallback",
                {"model": self._model_name, "reason": exc},
            )
            return self._predict_with_lexical_fallback(query_text=query_text, top_k=top_k)

        model = self._model
        sentence_util = self._sentence_util
        property_embeddings = self._property_embeddings
        if model is None or sentence_util is None or property_embeddings is None:
            return self._predict_with_lexical_fallback(query_text=query_text, top_k=top_k)

        query_embedding = model.encode(
            query_text,
            convert_to_tensor=True,
            normalize_embeddings=True,
        )
        scores = sentence_util.cos_sim(query_embedding, property_embeddings)[0]
        top_k_result = scores.topk(k=min(top_k, len(self._catalog.properties)))
        indices = [int(index) for index in top_k_result.indices.tolist()]
        values = [float(value) for value in top_k_result.values.tolist()]

        predictions: list[MappingPrediction] = []
        for index, score in zip(indices, values, strict=False):
            prop = self._catalog.properties[index]
            predictions.append(
                self._prediction_for_property(
                    prop=prop,
                    confidence=self._clip_confidence(score),
                    source="afro-xlmr-embedding",
                    model_name=self._model_name,
                )
            )

        return predictions

    def _predict_with_lexical_fallback(
        self,
        query_text: str,
        top_k: int,
    ) -> list[MappingPrediction]:
        query_tokens = self._tokens(query_text)
        scored: list[tuple[float, OntologyProperty]] = []

        for prop in self._catalog.properties:
            prop_tokens = self._tokens(prop.search_text)
            if not prop_tokens:
                score = 0.0
            else:
                score = len(query_tokens.intersection(prop_tokens)) / len(prop_tokens)
            scored.append((score, prop))

        scored.sort(key=lambda item: item[0], reverse=True)
        best = scored[: max(top_k, 1)]

        return [
            self._prediction_for_property(
                prop=prop,
                confidence=max(0.01, min(score, 1.0)),
                source="lexical-fallback",
                model_name="lexical-fallback",
            )
            for score, prop in best
        ]

    def _ensure_model_loaded(self) -> None:
        if self._model is not None and self._property_embeddings is not None:
            return

        log_step(
            self._logger,
            "predictor.model_loading",
            "Loading Afro-XLM-R sentence transformer",
            {"model": self._model_name, "properties": len(self._catalog.properties)},
        )

        sentence_transformers = cast(Any, importlib.import_module("sentence_transformers"))
        sentence_util = sentence_transformers.util
        sentence_transformer = sentence_transformers.SentenceTransformer
        model = sentence_transformer(self._model_name)
        property_texts = [prop.search_text for prop in self._catalog.properties]
        property_embeddings = model.encode(
            property_texts,
            convert_to_tensor=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        self._model = model
        self._sentence_util = sentence_util
        self._property_embeddings = property_embeddings
        log_step(
            self._logger,
            "predictor.model_loaded",
            "Afro-XLM-R sentence transformer is ready",
            {"model": self._model_name},
        )

    def _build_query_text(
        self,
        parameter_name: str,
        template_name: str,
        wikidata_hints: list[str],
        value_sample: str | None,
    ) -> str:
        hints = ", ".join(wikidata_hints[:25])
        pieces = [
            f"template: {template_name}",
            f"parameter: {parameter_name}",
            f"value: {value_sample or ''}",
            f"wikidata hints: {hints}",
        ]
        return " | ".join(pieces)

    def _prediction_for_property(
        self,
        prop: OntologyProperty,
        confidence: float,
        source: str,
        model_name: str,
    ) -> MappingPrediction:
        return MappingPrediction(
            target_property=prop.curie,
            target_uri=prop.uri,
            label=prop.label,
            confidence=self._clip_confidence(confidence),
            source=source,
            model_name=model_name,
        )

    def _tokens(self, text: str) -> set[str]:
        return {match.group(0).casefold() for match in self.TOKEN_RE.finditer(text)}

    def _as_curie(self, property_name: str) -> str:
        if ":" in property_name:
            return property_name
        return f"dbo:{property_name}"

    def _expand_curie(self, curie: str) -> str:
        if curie.startswith("http://") or curie.startswith("https://"):
            return curie
        if ":" not in curie:
            return f"http://dbpedia.org/ontology/{curie}"

        prefix, local_name = curie.split(":", 1)
        base_uri = self.PREFIX_URIS.get(prefix)
        return f"{base_uri}{local_name}" if base_uri else curie

    def _clip_confidence(self, value: float) -> float:
        return max(0.0, min(value, 1.0))
