from pathlib import Path

from amdb.services.ingestion import DumpTemplateParser


def test_dump_template_parser_streams_infobox_parameters(tmp_path: Path) -> None:
    input_path = tmp_path / "sample.xml"
    input_path.write_text(
        """
<mediawiki>
  <page>
    <title>አበበ ቢቂላ</title>
    <id>42</id>
    <revision>
      <text>{{የሰው_መረጃ
| ስም = አበበ ቢቂላ
| የትውልድ_ቦታ = ጃቶ
| የልደት_ቀን = 1932
}}</text>
    </revision>
  </page>
</mediawiki>
""",
        encoding="utf-8",
    )

    pages = list(DumpTemplateParser().iter_pages(input_path))

    assert len(pages) == 1
    assert pages[0].title == "አበበ ቢቂላ"
    assert pages[0].page_id == "42"
    assert pages[0].templates[0].name == "የሰው_መረጃ"
    params = {param.name: param.value for param in pages[0].templates[0].parameters}
    assert params["የትውልድ_ቦታ"] == "ጃቶ"
