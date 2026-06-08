from pathlib import Path

from amdb.config import settings


class ArtifactService:
    def sanitized_output_path(self, input_path: Path, output_name: str | None = None) -> Path:
        if output_name:
            return settings.sanitized_dir / Path(output_name).name

        suffix = (
            "".join(input_path.suffixes[-2:])
            if input_path.name.endswith(".xml.bz2")
            else input_path.suffix
        )
        stem = input_path.name.removesuffix(suffix)
        return settings.sanitized_dir / f"{stem}.sanitized{suffix}"

    def report_path_for(self, output_path: Path) -> Path:
        report_stem = output_path.name.removesuffix(".bz2").removesuffix(".xml")
        return settings.reports_dir / f"{report_stem}.sanitizer-report.json"
