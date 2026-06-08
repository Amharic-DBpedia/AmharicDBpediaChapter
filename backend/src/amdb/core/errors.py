class AmdbError(Exception):
    """Base exception for expected backend failures."""


class InvalidDumpError(AmdbError):
    """Raised when a dump cannot be read or parsed as MediaWiki XML."""


class DefRunnerError(AmdbError):
    """Raised when the DEF runner is misconfigured before process execution."""


class OntologyCatalogError(AmdbError):
    """Raised when the local DBpedia ontology catalog cannot be loaded."""


class PipelineError(AmdbError):
    """Raised when the mapping-candidate pipeline cannot complete."""


class WikidataLookupError(AmdbError):
    """Raised when a Wikidata lookup fails unexpectedly."""
