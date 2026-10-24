"""
Recommendation endpoint for Fieldwise Outdoor Intelligence.
Pairs deterministic spatial & meteorological evaluation with open-weights SLM synthesis.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Query

from app.schemas.contracts import QueryRequest, RecommendationResponse, SourceProvenance
from app.services.slm_service import SmallLanguageModelService, DEFAULT_MODEL_ID
from app.services.geocoding_service import geocode_location, get_location_autocomplete_suggestions
from app.services.weather_service import fetch_weather_forecast
from app.services.air_quality_service import fetch_air_quality
from app.services.routing_service import calculate_route
from app.geo.spatial_context import fetch_overpass_context
from app.recommendations.scoring import evaluate_candidate_slots
from app.recommendations.activity_profiles import ACTIVITY_PROFILES
from app.services.image_service import get_venue_photos

router = APIRouter(tags=["Recommendations"])
slm = SmallLanguageModelService(model_id=DEFAULT_MODEL_ID)


@router.get("/places/autocomplete")
async def autocomplete_places(q: str = Query(..., min_length=1, description="Place or city prefix to suggest")):
    """
    Instant Google Suggest-style location autocomplete endpoint.
    Returns matched cities, landmarks, and districts with exact GPS coordinates.
    """
    suggestions = await get_location_autocomplete_suggestions(q, limit=6)
    return {"status": "ok", "query": q, "suggestions": suggestions}


@router.get("/recommendations")
async def get_recommendations_info():
    """
    Provides usage guidance and interactive links when accessed via HTTP GET in web browsers.
    """
    return {
        "status": "online",
        "endpoint": "/api/recommendations",
        "method": "POST",
        "description": "Fieldwise Spatio-Temporal Outdoor Decision Recommendation Engine (CSRE IIT Bombay GeoAI Hackathon 2026).",
        "interactive_docs": "/docs",
        "sample_post_body": {
            "question": "Where can I go running tomorrow morning near Powai?"
        },
        "sample_curl": 'curl -X POST "/api/recommendations" -H "Content-Type: application/json" -d \'{"question": "Where can I go running tomorrow morning near Powai?"}\''
    }


@router.post("/recommendations", response_model=RecommendationResponse)
async def create_recommendation(req: QueryRequest):
    """
    Main recommendation endpoint.
    Accepts natural-language queries or structured parameter overrides.
    Retrieves live geospatial, weather, AQI, and routing data,
    evaluates multiple candidate venues and time windows,
    and returns evidence-grounded recommendations.
    """
    raw_question = (req.question or req.query or "").strip()

    # 1. Natural Language Intent Parsing
    parsed = {}
    if raw_question:
        parsed = slm.parse_query(raw_question)
    else:
        parsed = {
            "status": "ok",
            "activity": req.activity or "general_outdoor",
            "location": req.location or "",
            "radius_km": req.radius_km or 10.0,
            "target_hours": None,
            "time_window_label": req.time_window or "All Day",
            "day_offset": 0,
            "day_label": "Today",
            "personal_profiles": req.personal_profiles or []
        }

    # 2. Apply explicit user structured controls if provided
    # Only override activity if raw_question did not detect a distinct activity
    if req.activity and (not raw_question or parsed.get("activity") in ("general_outdoor", None)):
        parsed["activity"] = req.activity
    elif not parsed.get("activity") and req.activity:
        parsed["activity"] = req.activity
    if req.location:
        parsed["location"] = req.location
    if req.radius_km is not None:
        parsed["radius_km"] = float(req.radius_km)
    if req.personal_profiles:
        # Merge unique personal profiles
        existing_p = set(parsed.get("personal_profiles", []))
        for p in req.personal_profiles:
            existing_p.add(p)
        parsed["personal_profiles"] = list(existing_p)

    if req.time_window:
        tw = req.time_window.lower()
        if tw == "morning":
            parsed["target_hours"] = [6, 7, 8, 9, 10, 11]
            parsed["time_window_label"] = "Morning (06:00 AM - 11:00 AM)"
        elif tw == "afternoon":
            parsed["target_hours"] = [12, 13, 14, 15, 16]
            parsed["time_window_label"] = "Afternoon (12:00 PM - 04:00 PM)"
        elif tw == "evening":
            parsed["target_hours"] = [17, 18, 19, 20]
            parsed["time_window_label"] = "Evening (05:00 PM - 08:00 PM)"
        elif tw == "golden_hour":
            parsed["target_hours"] = [17, 18]
            parsed["time_window_label"] = "Golden Hour (05:00 PM - 06:30 PM)"
        elif tw == "all_day":
            parsed["target_hours"] = None
            parsed["time_window_label"] = "All Day"

    if req.date_window:
        dw = req.date_window.lower()
        if dw == "today":
            parsed["day_offset"] = 0
            parsed["day_label"] = "Today"
        elif dw == "tomorrow":
            parsed["day_offset"] = 1
            parsed["day_label"] = "Tomorrow"
        elif dw in ("weekend", "saturday or sunday"):
            now = datetime.now()
            days_to_sat = (5 - now.weekday()) % 7
            parsed["day_offset"] = days_to_sat if days_to_sat > 0 else 7
            parsed["day_label"] = "This Weekend"

    # 3. Handle GPS and missing location
    is_near_me = any(w in raw_question.lower() for w in ["near me", "current location", "my location", "here", "around me"])
    origin = None
    origin_type = "query_location"

    if req.user_lat is not None and req.user_lon is not None and (is_near_me or not parsed.get("location")):
        origin = {
            "name": f"Current Device Location ({req.user_lat:.4f}° N, {req.user_lon:.4f}° E)",
            "short_name": "My Device GPS",
            "lat": req.user_lat,
            "lon": req.user_lon,
            "geocoder": "Browser Device GPS Telemetry"
        }
        origin_type = "device_gps"
        parsed["location"] = "Current GPS Location"
        parsed["status"] = "ok"

    if parsed.get("status") == "missing_location":
        return RecommendationResponse(
            status="missing_location",
            question=raw_question,
            message=parsed.get("message"),
            parsed_intent=parsed,
            origin={"name": "Unknown", "short_name": "Unknown", "lat": 0.0, "lon": 0.0},
            origin_type="none",
            recommendation_markdown=f"### 📍 Location Required\n\n{parsed.get('message')}",
            model_used=DEFAULT_MODEL_ID,
            is_fallback=True,
            sources=[],
            warnings=["Location missing from request. Please specify a campus, city, or click '📍 Use GPS'."]
        )

    # 4. Resolve Origin Coordinates
    if not origin and parsed.get("location"):
        origin = await geocode_location(parsed["location"])
        origin_type = "geocoded"

    if not origin:
        return RecommendationResponse(
            status="location_not_found",
            question=raw_question,
            message=(
                f"Could not locate '{parsed.get('location')}' via Open-Meteo & OpenStreetMap. "
                f"Please specify a known city, campus, or landmark, or click '📍 Use GPS' to detect your current position."
            ),
            parsed_intent=parsed,
            origin={"name": parsed.get("location", "Unknown"), "short_name": "Unknown", "lat": 0.0, "lon": 0.0},
            origin_type="failed",
            recommendation_markdown=f"### 🔍 Location Not Found\n\nCould not resolve **{parsed.get('location')}**. Please try a nearby city or campus.",
            model_used=DEFAULT_MODEL_ID,
            is_fallback=True,
            sources=[],
            warnings=[f"Geocoding failed for {parsed.get('location')}."]
        )

    # 5. Retrieve Candidate Venues & Features from OpenStreetMap
    activity_key = parsed.get("activity", "general_outdoor")
    act_profile = ACTIVITY_PROFILES.get(activity_key, ACTIVITY_PROFILES["general_outdoor"])

    venues = await fetch_overpass_context(
        lat=origin["lat"],
        lon=origin["lon"],
        radius_km=parsed.get("radius_km", 10.0),
        activity_key=activity_key,
        osm_filters=act_profile["osm_filters"],
        activity_label=act_profile["label"],
        origin_short_name=origin.get("short_name", parsed.get("location", "Area"))
    )

    if not venues:
        return RecommendationResponse(
            status="no_venues",
            question=raw_question,
            message=f"No suitable venues found for {act_profile['label']} within {parsed.get('radius_km')} km of {origin['name']}.",
            parsed_intent=parsed,
            origin=origin,
            origin_type=origin_type,
            recommendation_markdown=f"No venues found in OpenStreetMap within {parsed.get('radius_km')} km.",
            model_used=DEFAULT_MODEL_ID,
            is_fallback=True,
            sources=[],
            warnings=["No candidate venues discovered."]
        )

    # 6. Concurrently Fetch Weather and Air Quality (deduplicating by grid)
    weather_cache_grid: Dict[str, Any] = {}

    async def get_regional_telemetry(v_lat: float, v_lon: float):
        k = f"{round(v_lat, 2)}_{round(v_lon, 2)}"
        if k not in weather_cache_grid:
            w_fut = fetch_weather_forecast(v_lat, v_lon, days=4)
            a_fut = fetch_air_quality(v_lat, v_lon, days=4)
            w_res, a_res = await asyncio.gather(w_fut, a_fut)
            weather_cache_grid[k] = {
                "hourly": w_res.get("hourly", {}),
                "daily": w_res.get("daily", {}),
                "aqi_hourly": a_res.get("hourly", {}),
                "aqi_scale": a_res.get("scale", "US AQI"),
                "is_simulated": w_res.get("is_simulated", False) or a_res.get("is_simulated", False)
            }
        return weather_cache_grid[k]

    weather_tasks = [get_regional_telemetry(v["lat"], v["lon"]) for v in venues]
    travel_tasks = [calculate_route(origin["lat"], origin["lon"], v["lat"], v["lon"]) for v in venues]

    weather_results, travel_results = await asyncio.gather(
        asyncio.gather(*weather_tasks),
        asyncio.gather(*travel_tasks)
    )

    # 7. Evaluate and Score Candidates across Hours
    evaluation = evaluate_candidate_slots(
        venues=venues,
        weather_data_by_venue=weather_results,
        travel_data_by_venue=travel_results,
        activity_key=activity_key,
        personal_profiles=parsed.get("personal_profiles", []),
        target_hours_filter=parsed.get("target_hours"),
        day_offset=parsed.get("day_offset", 0),
        compare_mode=parsed.get("compare_mode"),
        radius_km=parsed.get("radius_km", 10.0)
    )

    # 7b. Attach Verified Imagery for Preview Galleries (Exact Venue Only)
    best_slot = evaluation.get("best_recommendation")
    alt_slots = evaluation.get("alternative_venues", [])
    slots_to_hydrate = [best_slot] if best_slot else []
    slots_to_hydrate.extend(alt_slots)

    locality_name = origin.get("locality") or origin.get("short_name")
    photo_tasks = [
        get_venue_photos(
            venue_name=s["venue_name"],
            venue_lat=s.get("lat"),
            venue_lon=s.get("lon"),
            locality=locality_name
        )
        for s in slots_to_hydrate
    ]
    if photo_tasks:
        photo_results = await asyncio.gather(*photo_tasks)
        for s, photos in zip(slots_to_hydrate, photo_results):
            s["images"] = photos
            s["has_verified_photos"] = len(photos) > 0

    # 8. Synthesize Grounded Recommendation
    explanation_md = slm.synthesize_explanation(
        user_query=raw_question or f"Outdoor {activity_key} near {parsed.get('location')}",
        parsed=parsed,
        evaluation=evaluation
    )

    now_iso = datetime.now().isoformat()
    sources = [
        SourceProvenance(
            name="OpenStreetMap Overpass API & POIs",
            type="Geospatial Vector Polygons & Points",
            url="https://overpass-api.de/api/interpreter",
            fetched_at=now_iso,
            attribution="© OpenStreetMap contributors",
            freshness="Live query (30m cache)",
            details="Extracted parks, sports facilities, water bodies, road corridors, and industrial zones."
        ),
        SourceProvenance(
            name="Open-Meteo Weather Forecast API",
            type="Meteorological Telemetry",
            url="https://api.open-meteo.com/v1/forecast",
            fetched_at=now_iso,
            attribution="Open-Meteo (CC-BY 4.0)",
            freshness="Hourly atmospheric forecasts",
            details="Fetched temperature, apparent temp, rain probability, wind speed/direction, and UV index."
        ),
        SourceProvenance(
            name="Open-Meteo Air Quality API",
            type="Atmospheric Chemistry Telemetry",
            url="https://air-quality-api.open-meteo.com/v1/air-quality",
            fetched_at=now_iso,
            attribution="Open-Meteo & Copernicus Atmosphere Monitoring Service",
            freshness="Hourly dispersion telemetry",
            details="Retrieved US Air Quality Index (EPA standard 0-500 scale), PM2.5, and PM10."
        ),
        SourceProvenance(
            name="OSRM Routing Engine",
            type="Road Network Transit Modeling",
            url="https://router.project-osrm.org",
            fetched_at=now_iso,
            attribution="OSRM / © OpenStreetMap contributors",
            freshness="Instant query",
            details="Estimated driving distance and transit duration without claiming live congestion."
        )
    ]

    warnings = []
    if any(w.get("is_simulated", False) for w in weather_results):
        warnings.append("Note: Open-Meteo was unreachable; high-fidelity meteorological fallback simulation was utilized.")

    return RecommendationResponse(
        status="ok",
        question=raw_question,
        parsed_intent=parsed,
        origin=origin,
        origin_type=origin_type,
        best_recommendation=evaluation["best_recommendation"],
        alternative_venues=evaluation["alternative_venues"],
        avoid_slots=evaluation["avoid_slots"],
        hourly_timeline=evaluation["hourly_timeline"],
        recommended_carry=evaluation["recommended_carry"],
        profile_watch_notes=evaluation["profile_watch_notes"],
        recommendation_markdown=explanation_md,
        model_used=DEFAULT_MODEL_ID,
        is_fallback=not slm.is_loaded,
        sources=sources,
        warnings=warnings
    )
