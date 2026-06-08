from pathlib import Path

from amdb.services.sanitizer import DumpSanitizer


def test_sanitize_wikitext_removes_known_parser_breakers() -> None:
    sanitizer = DumpSanitizer()

    raw = """
{{የሠዓሊ_መረጃ
| image = Example.jpg|thumb|250px
| ማብራሪያ = <div style="float:right;">Broken HTML</div>
}}
"""

    clean, rules = sanitizer.sanitize_wikitext(raw)

    assert "thumb" not in clean
    assert "250px" not in clean
    assert "<div" not in clean
    assert "style=" not in clean
    assert "ማብራሪያ" in clean
    assert {
        "remove-image-thumb-option",
        "remove-image-px-option",
        "remove-raw-div-tags",
        "remove-style-attributes",
    }.issubset(set(rules))


def test_sanitize_dump_generates_report(tmp_path: Path) -> None:
    input_path = tmp_path / "sample.xml"
    output_path = tmp_path / "sample.sanitized.xml"

    input_path.write_text(
        """
<mediawiki>
  <page>
    <title>ሙከራ</title>
    <revision>
      <text>{{Infobox|image=Example.jpg|thumb|250px}}</text>
    </revision>
  </page>
</mediawiki>
""",
        encoding="utf-8",
    )

    result = DumpSanitizer().sanitize_dump(input_path=input_path, output_path=output_path)

    assert output_path.exists()
    assert result.pages_seen == 1
    assert result.pages_changed == 1
    assert result.rules_applied["remove-image-thumb-option"] == 1
