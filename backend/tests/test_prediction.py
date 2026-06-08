from amdb.services.ontology import (
    AmharicMappingIndex,
    DbpediaOntologyCatalog,
    ExistingTemplateMapping,
    OntologyProperty,
)
from amdb.services.prediction import AfroXlmrPropertyPredictor


def test_predictor_prefers_existing_amharic_def_mapping() -> None:
    catalog = DbpediaOntologyCatalog(
        [
            OntologyProperty(
                local_name="birthPlace",
                curie="dbo:birthPlace",
                uri="http://dbpedia.org/ontology/birthPlace",
                label="birth place",
                property_type="ObjectProperty",
            )
        ]
    )
    mapping_index = AmharicMappingIndex(
        {
            "የትውልድ_ቦታ": ExistingTemplateMapping(
                template_property="የትውልድ_ቦታ",
                ontology_property="birthPlace",
            )
        }
    )
    predictor = AfroXlmrPropertyPredictor(catalog=catalog, mapping_index=mapping_index)

    predictions = predictor.predict(
        parameter_name="የትውልድ_ቦታ",
        template_name="የሰው_መረጃ",
        wikidata_hints=["place of birth"],
        use_ml_model=False,
    )

    assert predictions[0].target_property == "dbo:birthPlace"
    assert predictions[0].confidence == 1.0
    assert predictions[0].source == "existing-def-mapping"


def test_predictor_lexical_fallback_uses_wikidata_hints() -> None:
    catalog = DbpediaOntologyCatalog(
        [
            OntologyProperty(
                local_name="deathDate",
                curie="dbo:deathDate",
                uri="http://dbpedia.org/ontology/deathDate",
                label="death date",
                property_type="DatatypeProperty",
            ),
            OntologyProperty(
                local_name="birthPlace",
                curie="dbo:birthPlace",
                uri="http://dbpedia.org/ontology/birthPlace",
                label="birth place",
                property_type="ObjectProperty",
            ),
        ]
    )
    predictor = AfroXlmrPropertyPredictor(catalog=catalog, mapping_index=AmharicMappingIndex({}))

    predictions = predictor.predict(
        parameter_name="የትውልድ_ቦታ",
        template_name="የሰው_መረጃ",
        wikidata_hints=["place of birth"],
        use_existing_mappings=False,
        use_ml_model=False,
    )

    assert predictions[0].target_property == "dbo:birthPlace"
