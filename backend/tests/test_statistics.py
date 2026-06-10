import bz2
from pathlib import Path

from amdb.services.statistics import StatisticsService


def test_statistics_service_counts_rdf_outputs(tmp_path: Path) -> None:
    source_dir = tmp_path / "rdf"
    source_dir.mkdir()

    mapping_file = source_dir / "amwiki-20250820-mappingbased-literals.ttl.bz2"
    with bz2.open(mapping_file, "wt", encoding="utf-8") as file:
        file.write(
            "\n".join(
                [
                    '<http://am.dbpedia.org/resource/Entity_1> '
                    '<http://dbpedia.org/ontology/birthDate> "1900" .',
                    '<http://am.dbpedia.org/resource/Entity_1> '
                    '<http://xmlns.com/foaf/0.1/name> "ሙከራ"@am .',
                ]
            )
        )

    raw_infobox_file = source_dir / "amwiki-20250820-infobox-properties.ttl"
    raw_infobox_file.write_text(
        '<http://am.dbpedia.org/resource/Entity_2> '
        '<http://am.dbpedia.org/property/ስም> "ሌላ"@am .\n',
        encoding="utf-8",
    )

    result = StatisticsService().generate(
        source_dir=source_dir,
        run_id="unit-statistics",
        extraction_run_id="unit-def-run",
    )

    assert result.success is True
    assert result.file_count == 2
    assert result.total_triples == 3
    assert result.unique_subjects == 2
    assert result.unique_predicates == 3
    assert result.mapping_based_triples == 2
    assert result.raw_infobox_triples == 1
    assert Path(result.report_path).exists()


def test_statistics_service_reports_no_rdf_files(tmp_path: Path) -> None:
    result = StatisticsService().generate(source_dir=tmp_path, run_id="empty-statistics")

    assert result.success is False
    assert result.file_count == 0
    assert result.error is not None


def test_statistics_service_can_load_latest(tmp_path: Path) -> None:
    rdf_file = tmp_path / "sample.ttl"
    rdf_file.write_text(
        '<http://am.dbpedia.org/resource/A> <http://dbpedia.org/ontology/wikiPageID> "1" .\n',
        encoding="utf-8",
    )

    service = StatisticsService()
    result = service.generate(source_dir=tmp_path, run_id="latest-statistics")
    latest = service.load_latest()

    assert latest["run_id"] == result.run_id
    assert latest["total_triples"] == 1
