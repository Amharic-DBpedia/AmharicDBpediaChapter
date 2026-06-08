import argparse
from pathlib import Path

from amdb.core.paths import ensure_data_dirs
from amdb.services.mapping_pipeline import MappingPipelineService


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Amharic DBpedia mapping-candidate pipeline through step 3."
    )
    parser.add_argument("--input", required=True, help="Input XML or XML.BZ2 dump path")
    parser.add_argument("--run-name", default=None, help="Stable report/run id")
    parser.add_argument("--max-pages", type=int, default=10)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--no-wikidata", action="store_true")
    parser.add_argument("--no-existing-mappings", action="store_true")
    parser.add_argument("--no-ml-model", action="store_true")
    args = parser.parse_args()

    ensure_data_dirs()
    result = MappingPipelineService().run(
        input_path=Path(args.input).expanduser().resolve(),
        run_id=args.run_name,
        max_pages=args.max_pages,
        top_k=args.top_k,
        use_wikidata=not args.no_wikidata,
        use_existing_mappings=not args.no_existing_mappings,
        use_ml_model=not args.no_ml_model,
    )

    print(f"Run: {result.run_id}")
    print(f"Input: {result.input_path}")
    print(f"Report: {result.report_path}")
    print(f"Pages seen: {result.pages_seen}")
    print(f"Templates seen: {result.templates_seen}")
    print(f"Parameters seen: {result.parameters_seen}")
    print(f"Candidates: {result.candidates_count}")


if __name__ == "__main__":
    main()
