from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime paths for the local Amharic DBpedia automation workspace."""

    model_config = SettingsConfigDict(env_prefix="AMDB_", env_file=".env", extra="ignore")

    project_root: Path = Path(__file__).resolve().parents[3]
    def_dir: Path | None = None

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def sanitized_dir(self) -> Path:
        return self.data_dir / "sanitized"

    @property
    def reports_dir(self) -> Path:
        return self.data_dir / "reports"

    @property
    def def_runs_dir(self) -> Path:
        return self.data_dir / "def-runs"

    @property
    def extraction_dir(self) -> Path:
        return self.project_root / "extraction"

    @property
    def def_runner_script(self) -> Path:
        return self.extraction_dir / "scripts" / "run_def.sh"

    @property
    def statistics_runner_script(self) -> Path:
        return self.extraction_dir / "scripts" / "run_statistics.sh"

    @property
    def latest_statistics_report(self) -> Path:
        return self.reports_dir / "statistics-latest.json"

    @property
    def default_def_config(self) -> Path:
        return self.extraction_dir / "config" / "extraction.am.properties"

    @property
    def resolved_def_dir(self) -> Path:
        return self.def_dir or self.project_root.parent / "extraction-framework"

    @property
    def def_ontology_xml(self) -> Path:
        return self.resolved_def_dir / "ontology.xml"

    @property
    def amharic_mapping_xml(self) -> Path:
        return self.resolved_def_dir / "mappings" / "Mapping_am.xml"

    wikidata_api_url: str = "https://www.wikidata.org/w/api.php"
    wikidata_timeout_seconds: float = 12.0
    wikidata_user_agent: str = (
        "AmharicDBpediaChapter/0.1 "
        "(https://github.com/dbpedia/AmharicDBpediaChapter; research prototype)"
    )
    afro_xlmr_model_name: str = "dice-research/amharic-property-retriever-afro-xlmr-base"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
