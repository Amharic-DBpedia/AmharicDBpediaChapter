from pathlib import Path

from amdb.services.artifacts import ArtifactService


def test_sanitized_output_path_keeps_xml_bz2_suffix() -> None:
    input_path = Path("/tmp/amwiki-20250820-pages-articles.xml.bz2")

    output_path = ArtifactService().sanitized_output_path(input_path)

    assert output_path.name == "amwiki-20250820-pages-articles.sanitized.xml.bz2"
