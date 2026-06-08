from pathlib import Path

from amdb.config import settings


def ensure_data_dirs() -> None:
    for path in [
        settings.raw_dir,
        settings.sanitized_dir,
        settings.reports_dir,
        settings.def_runs_dir,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def resolve_user_path(path: str) -> Path:
    return Path(path).expanduser().resolve()


def assert_file_exists(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"File does not exist: {path}")
