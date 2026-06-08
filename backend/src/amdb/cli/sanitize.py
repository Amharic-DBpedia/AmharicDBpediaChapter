import argparse
from pathlib import Path

from amdb.services.sanitizer import DumpSanitizer


def main() -> None:
    parser = argparse.ArgumentParser(description="Sanitize an Amharic Wikipedia XML dump.")
    parser.add_argument("--input", required=True, help="Input .xml or .xml.bz2 dump path.")
    parser.add_argument("--output", required=True, help="Output sanitized dump path.")
    args = parser.parse_args()

    result = DumpSanitizer().sanitize_dump(
        input_path=Path(args.input).expanduser().resolve(),
        output_path=Path(args.output).expanduser().resolve(),
    )

    print(f"Input: {result.input_path}")
    print(f"Output: {result.output_path}")
    print(f"Report: {result.report_path}")
    print(f"Pages seen: {result.pages_seen}")
    print(f"Pages changed: {result.pages_changed}")


if __name__ == "__main__":
    main()
