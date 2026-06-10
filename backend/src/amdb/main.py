from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from amdb.api.routes_extraction import router as extraction_router
from amdb.api.routes_health import router as health_router
from amdb.api.routes_pipeline import router as pipeline_router
from amdb.api.routes_sanitizer import router as sanitizer_router
from amdb.api.routes_statistics import router as statistics_router
from amdb.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title="Amharic DBpedia Automation API",
    version="0.1.0",
    description=(
        "Backend for Amharic DBpedia sanitization, mapping-candidate prediction, "
        "extraction, and validation workflows."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/health", tags=["health"])
app.include_router(sanitizer_router, prefix="/api/sanitizer", tags=["sanitizer"])
app.include_router(extraction_router, prefix="/api/extraction", tags=["extraction"])
app.include_router(pipeline_router, prefix="/api/pipeline", tags=["pipeline"])
app.include_router(statistics_router, prefix="/api/statistics", tags=["statistics"])
