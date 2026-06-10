from pathlib import Path

from amdb.services.mapping_pipeline import MappingPipelineService
from amdb.services.prediction import MappingPrediction
from amdb.services.wikidata import WikidataContext, WikidataPropertyHint


class FakeWikidataClient:
    def get_context_for_title(self, title: str) -> WikidataContext:
        return WikidataContext(
            entity_id="Q123",
            entity_label="Abebe Bikila",
            property_hints=[WikidataPropertyHint(property_id="P19", label="place of birth")],
        )


class FakePredictor:
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
        return [
            MappingPrediction(
                target_property="dbo:birthPlace",
                target_uri="http://dbpedia.org/ontology/birthPlace",
                label="birth place",
                confidence=0.96,
                source="fake",
                model_name="fake",
            )
        ]


def test_mapping_pipeline_generates_report(tmp_path: Path) -> None:
    input_path = tmp_path / "sample.xml"
    input_path.write_text(
        """
<mediawiki>
  <page>
    <title>አበበ ቢቂላ</title>
    <id>42</id>
    <revision>
      <text>{{የሰው_መረጃ
| የትውልድ_ቦታ = ጃቶ
}}</text>
    </revision>
  </page>
</mediawiki>
""",
        encoding="utf-8",
    )

    service = MappingPipelineService(
        wikidata_client=FakeWikidataClient(),
        predictor=FakePredictor(),
    )

    result = service.run(
        input_path=input_path,
        run_id="test-pipeline",
        max_pages=1,
        top_k=1,
        use_wikidata=True,
    )

    assert Path(result.report_path).exists()
    assert result.pages_seen == 1
    assert result.templates_seen == 1
    assert result.parameters_seen == 1
    assert result.candidates_sample[0].wikidata_hints == ["place of birth"]
    assert result.candidates_sample[0].predictions[0].target_property == "dbo:birthPlace"
