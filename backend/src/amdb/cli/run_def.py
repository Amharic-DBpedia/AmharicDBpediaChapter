import argparse
from pathlib import Path

from amdb.config import settings
from amdb.services.def_runner import DefRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DEF against a sanitized Amharic dump.")
    parser.add_argument("--dump", required=True, help="Sanitized dump path.")
    parser.add_argument(
        "--config",
        default=str(settings.default_def_config),
        help="DEF config path.",
    )
    parser.add_argument("--run-name", default=None, help="Optional stable run name.")
    args = parser.parse_args()

    result = DefRunner().run(
        sanitized_dump_path=Path(args.dump).expanduser().resolve(),
        config_path=Path(args.config).expanduser().resolve(),
        run_name=args.run_name,
    )

    print(f"Run ID: {result.run_id}")
    print(f"Output dir: {result.output_dir}")
    print(f"Exit code: {result.exit_code}")
    print(f"Stdout: {result.stdout_path}")
    print(f"Stderr: {result.stderr_path}")


if __name__ == "__main__":
    main()
