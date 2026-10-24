"""
Health check and capability readiness endpoint for Fieldwise.
"""

import os
from fastapi import APIRouter
from app.schemas.contracts import HealthResponse
from app.services.slm_service import DEFAULT_MODEL_ID

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Reports system status, open-weights SLM configuration, and data sources."""
    model_loaded = os.getenv("GEOAI_LOAD_SLM", "0") == "1"
    return {
        "status": "ok",
        "version": "1.0.0",
        "app_name": "Fieldwise Outdoor Intelligence Assistant",
        "model_id": DEFAULT_MODEL_ID,
        "model_loaded": model_loaded,
        "parameters": "1.54B (Qwen2.5-1.5B-Instruct) / strictly <= 3B limit compliant",
        "data_sources": {
            "venues": "OpenStreetMap Overpass API & Photon POIs",
            "geocoding": "Curated Gazetteer, OpenStreetMap Photon, Open-Meteo & Nominatim",
            "weather": "Open-Meteo Weather Forecast API (Hourly)",
            "air_quality": "Open-Meteo Air Quality API (US AQI EPA Scale & PM2.5/PM10)",
            "routing": "OSRM Open Source Routing Machine (Driving Duration & Distance)"
        },
        "attribution": "© OpenStreetMap contributors, Open-Meteo, OSRM"
    }
