"""
Data sources, attribution, and methodology documentation endpoint for Fieldwise.
"""

from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(tags=["Sources"])


@router.get("/sources")
async def get_data_sources() -> List[Dict[str, Any]]:
    """Returns detailed provenance and usage terms for all live data integrations."""
    return [
        {
            "name": "OpenStreetMap",
            "type": "Geospatial Vectors & Venues",
            "provider": "OpenStreetMap Foundation via Overpass API & Photon",
            "url": "https://www.openstreetmap.org",
            "endpoint": "https://overpass-api.de/api/interpreter",
            "terms": "Open Database License (ODbL) 1.0",
            "attribution": "© OpenStreetMap contributors",
            "description": "Real-time vector queries for parks, nature reserves, sports pitches, trails, roads, water bodies, and industrial zones."
        },
        {
            "name": "Open-Meteo Weather Forecast API",
            "type": "Meteorological Forecasts",
            "provider": "Open-Meteo GmbH",
            "url": "https://open-meteo.com",
            "endpoint": "https://api.open-meteo.com/v1/forecast",
            "terms": "Creative Commons Attribution 4.0 International (CC-BY 4.0)",
            "attribution": "Weather data by Open-Meteo.com",
            "description": "Hourly 2m temperature, apparent temperature, relative humidity, precipitation probability, wind speed and 10m direction, UV index, and solar daylight."
        },
        {
            "name": "Open-Meteo Air Quality API",
            "type": "Atmospheric Chemistry Telemetry",
            "provider": "Open-Meteo GmbH & Copernicus Atmosphere Monitoring Service (CAMS)",
            "url": "https://open-meteo.com/en/docs/air-quality-api",
            "endpoint": "https://air-quality-api.open-meteo.com/v1/air-quality",
            "terms": "CC-BY 4.0 & Copernicus Open Access",
            "attribution": "Air quality data by Open-Meteo.com (CAMS & SILAM models)",
            "description": "Hourly US Air Quality Index (EPA standard 0-500 scale), PM2.5, PM10, nitrogen dioxide, and ozone concentrations."
        },
        {
            "name": "OSRM (Open Source Routing Machine)",
            "type": "Road Network Transit & Travel Times",
            "provider": "Project OSRM / FOSSGIS",
            "url": "https://project-osrm.org",
            "endpoint": "https://router.project-osrm.org/route/v1/driving",
            "terms": "BSD 2-Clause / © OpenStreetMap contributors",
            "attribution": "Routing data © OpenStreetMap contributors",
            "description": "Road network route distance and free-flow driving duration estimates based on OSM road topology."
        },
        {
            "name": "Qwen2.5 Small Language Model (SLM)",
            "type": "Neuro-Symbolic Explanation Synthesis",
            "provider": "Alibaba Qwen / Hugging Face",
            "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct",
            "terms": "Apache 2.0 Open Source License",
            "attribution": "Qwen2.5 Open-weights Research Community",
            "description": "Strictly <= 3B parameter small language model running under local control to reason exclusively over structured live evidence."
        }
    ]
