"""
Fieldwise — Your Outdoor Intelligence Assistant
GeoAI Hackathon @ CSRE, IIT Bombay 2026

FastAPI backend pairing deterministic spatio-temporal reasoning
with an open-weights <= 3B parameter Small Language Model.
"""

import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure terminal handles UTF-8 safely
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from app.api.health import router as health_router
from app.api.activities import router as activities_router
from app.api.sources import router as sources_router
from app.api.recommendations import router as recommendations_router
from app.api.locations import router as locations_router
from app.schemas.contracts import QueryRequest

app = FastAPI(
    title="Fieldwise — Outdoor Intelligence Assistant",
    description="Live, evidence-grounded outdoor spatio-temporal reasoning engine powered by an open-weights <=3B Small Language Model (Qwen2.5-1.5B-Instruct).",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes under /api
app.include_router(health_router, prefix="/api")
app.include_router(activities_router, prefix="/api")
app.include_router(sources_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")
app.include_router(locations_router, prefix="/api")

# Also register top-level routes for backward compatibility with judging scripts
app.include_router(health_router)
app.include_router(activities_router)
app.include_router(sources_router)


@app.post("/ask", tags=["Compatibility"])
async def ask_compatibility(req: QueryRequest):
    """Backward-compatible endpoint for POST /ask."""
    from app.api.recommendations import create_recommendation
    res = await create_recommendation(req)
    # Also adapt to older response keys if callers expect them
    res_dict = res.model_dump()
    res_dict["answer"] = res.recommendation_markdown
    res_dict["top_venue_slots"] = [res.best_recommendation.model_dump()] if res.best_recommendation else []
    res_dict["alternatives_compared"] = [a.model_dump() for a in res.alternative_venues]
    return res_dict


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": "Fieldwise — Outdoor Intelligence Assistant",
        "event": "GeoAI Hackathon @ CSRE, IIT Bombay 2026",
        "status": "online",
        "documentation": "/docs",
        "endpoints": {
            "health": "/api/health",
            "activities": "/api/activities",
            "sources": "/api/sources",
            "recommendations": "/api/recommendations"
        },
        "attribution": "© OpenStreetMap contributors, Open-Meteo, OSRM"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
