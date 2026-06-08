from pathlib import Path

from amdb.services.ontology import AmharicMappingIndex, DbpediaOntologyCatalog


def test_ontology_catalog_loads_dbpedia_property_labels(tmp_path: Path) -> None:
    ontology_path = tmp_path / "ontology.xml"
    ontology_path.write_text(
        """
<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.8/">
  <page>
    <title>OntologyProperty:BirthPlace</title>
    <revision>
      <text>{{ObjectProperty
{{label|en|birth place}}
}}</text>
    </revision>
  </page>
  <page>
    <title>OntologyProperty:Foaf:name</title>
    <revision>
      <text>{{DatatypeProperty
{{label|en|name}}
}}</text>
    </revision>
  </page>
</mediawiki>
""",
        encoding="utf-8",
    )

    catalog = DbpediaOntologyCatalog.from_ontology_xml(ontology_path)
    prop = catalog.find("birthPlace")

    assert prop is not None
    assert prop.curie == "dbo:birthPlace"
    assert prop.label == "birth place"
    assert prop.property_type == "ObjectProperty"

    prefixed = catalog.find("foaf:name")
    assert prefixed is not None
    assert prefixed.curie == "foaf:name"
    assert prefixed.uri == "http://xmlns.com/foaf/0.1/name"


def test_amharic_mapping_index_loads_existing_template_property(tmp_path: Path) -> None:
    mapping_path = tmp_path / "Mapping_am.xml"
    mapping_path.write_text(
        """
<mediawiki>
  <page>
    <title>Mapping am:መረጃሳጥን ሰው</title>
    <revision>
      <text>{{TemplateMapping
| mappings =
{{PropertyMapping | templateProperty = የትውልድ_ቦታ | ontologyProperty = birthPlace }}
}}</text>
    </revision>
  </page>
</mediawiki>
""",
        encoding="utf-8",
    )

    index = AmharicMappingIndex.from_mapping_xml(mapping_path)
    mapping = index.lookup("የትውልድ_ቦታ")

    assert mapping is not None
    assert mapping.ontology_property == "birthPlace"
