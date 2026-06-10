import argparse
from pathlib import Path

from amdb.services.statistics import StatisticsService


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate dynamic RDF statistics for DEF outputs.")
    parser.add_argument(
        "--source-dir",
        required=True,
        help="Directory or file containing RDF outputs.",
    )
    parser.add_argument("--run-name", default=None, help="Optional stable statistics run ID.")
    parser.add_argument("--dump-date", default=None, help="Optional Wikipedia dump date metadata.")
    parser.add_argument("--extraction-run-id", default=None, help="Optional DEF run ID metadata.")
    parser.add_argument(
        "--use-native-def-stats",
        action="store_true",
        help="Also run DEF collectStats.sh when the output layout supports it.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Optional file cap for smoke tests.",
    )
    args = parser.parse_args()

    result = StatisticsService().generate(
        source_dir=Path(args.source_dir).expanduser().resolve(),
        run_id=args.run_name,
        dump_date=args.dump_date,
        extraction_run_id=args.extraction_run_id,
        use_native_def_stats=args.use_native_def_stats,
        max_files=args.max_files,
    )

    print(f"Run ID: {result.run_id}")
    print(f"Source: {result.source_dir}")
    print(f"Report: {result.report_path}")
    print(f"Files: {result.file_count}")
    print(f"Triples: {result.total_triples}")
    print(f"Unique subjects: {result.unique_subjects}")
    print(f"Unique predicates: {result.unique_predicates}")
    print(f"Unique objects: {result.unique_objects}")
    print(f"Mapping-based triples: {result.mapping_based_triples}")
    print(f"Raw infobox triples: {result.raw_infobox_triples}")
    print(f"Success: {result.success}")


if __name__ == "__main__":
    main()
