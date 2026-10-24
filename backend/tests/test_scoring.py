"""
Unit tests for the multi-venue, multi-hour scoring engine.
"""

import pytest
from app.recommendations.scoring import evaluate_candidate_slots


def test_scoring_with_downwind_penalty():
    venues = [
        {
            "name": "Lakeside Park",
            "lat": 28.45,
            "lon": 77.50,
            "distance_km": 2.0,
            "env_context": {
                "green_cover_nearby": True,
                "water_body_nearby": True,
                "water_name": "Lake",
                "major_road": {
                    "name": "Expressway",
                    "dist_km": 0.5,
                    "wind_from_hazard_deg": 90,  # Road is east of venue; wind from 90 means downwind
                    "direction_from_venue": "E"
                }
            }
        }
    ]

    weather_bundle = [
        {
            "hourly": {
                "time": [f"2026-10-24T{h:02d}:00" for h in range(24)],
                "temperature_2m": [22.0] * 24,
                "apparent_temperature": [22.0] * 24,
                "relative_humidity_2m": [50] * 24,
                "precipitation_probability": [0] * 24,
                "precipitation": [0.0] * 24,
                "wind_speed_10m": [8.0] * 24,
                "wind_direction_10m": [90.0] * 24,  # Exact downwind angle
                "uv_index": [2.0] * 24,
                "cloud_cover": [10] * 24,
                "is_day": [1] * 24
            },
            "aqi_hourly": {
                "us_aqi": [45] * 24,
                "pm2_5": [12.0] * 24,
                "pm10": [25.0] * 24
            }
        }
    ]

    travel_data = [(2.0, 5.0, "OSRM")]

    # Evaluate standard running
    res_normal = evaluate_candidate_slots(
        venues=venues,
        weather_data_by_venue=weather_bundle,
        travel_data_by_venue=travel_data,
        activity_key="running",
        personal_profiles=[],
        target_hours_filter=[7]
    )

    # Evaluate with asthma profile (higher downwind penalty)
    res_asthma = evaluate_candidate_slots(
        venues=venues,
        weather_data_by_venue=weather_bundle,
        travel_data_by_venue=travel_data,
        activity_key="running",
        personal_profiles=["asthma"],
        target_hours_filter=[7]
    )

    best_normal = res_normal["best_recommendation"]
    best_asthma = res_asthma["best_recommendation"]

    assert best_normal is not None
    assert best_asthma is not None
    assert "Downwind of Expressway" in best_normal["downwind_status"]
    # Asthma score should be penalized more severely due to downwind_penalty_multiplier
    assert best_asthma["score"] < best_normal["score"]
    # Asthma carry items should include inhaler
    assert any("inhaler" in c.lower() for c in res_asthma["recommended_carry"])
