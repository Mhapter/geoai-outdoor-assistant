"""
Unit tests for activity profiles and personal constraints.
Verifies all 10 hackathon-mandated activities are supported with distinct thresholds.
"""

import pytest
from app.recommendations.activity_profiles import ACTIVITY_PROFILES
from app.recommendations.personal_profiles import PROFILE_MODIFIERS

MANDATORY_ACTIVITIES = [
    "running",
    "cycling",
    "golf",
    "cricket",
    "football",
    "tennis",
    "hiking",
    "picnic",
    "event",
    "photography",
]


def test_mandatory_activities_exist():
    for act in MANDATORY_ACTIVITIES:
        assert act in ACTIVITY_PROFILES, f"Mandatory activity '{act}' missing from ACTIVITY_PROFILES"


def test_activity_profiles_schema():
    for act_key, p in ACTIVITY_PROFILES.items():
        assert "label" in p
        assert "icon" in p
        assert "ideal_temp" in p
        assert len(p["ideal_temp"]) == 2
        assert p["ideal_temp"][0] < p["ideal_temp"][1]
        assert "max_temp" in p
        assert "max_aqi" in p
        assert "max_wind_kmh" in p
        assert "max_rain_prob" in p
        assert "carry" in p
        assert len(p["carry"]) >= 2
        assert "osm_filters" in p
        assert len(p["osm_filters"]) >= 1


def test_activity_sensitivity_distinction():
    # Tennis and badminton should be more wind-sensitive than football
    assert ACTIVITY_PROFILES["tennis"]["max_wind_kmh"] < ACTIVITY_PROFILES["football"]["max_wind_kmh"]
    assert ACTIVITY_PROFILES["badminton"]["max_wind_kmh"] < ACTIVITY_PROFILES["football"]["max_wind_kmh"]

    # Golf and photography should require daylight
    assert ACTIVITY_PROFILES["golf"]["needs_daylight"] is True
    assert ACTIVITY_PROFILES["photography"]["needs_daylight"] is True


def test_personal_profiles_exist():
    required_profiles = ["asthma", "senior", "child", "pregnancy"]
    for prof in required_profiles:
        assert prof in PROFILE_MODIFIERS
        p = PROFILE_MODIFIERS[prof]
        assert "max_aqi" in p
        assert p["max_aqi"] <= 95  # Must tighten AQI limits
        assert "extra_carry" in p
        assert len(p["extra_carry"]) >= 1
        assert "watch_note" in p
