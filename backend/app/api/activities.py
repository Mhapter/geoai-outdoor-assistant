"""
Activity definitions and sensitivity profiles endpoint for Fieldwise.
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from app.schemas.contracts import ActivityInfo
from app.recommendations.activity_profiles import ACTIVITY_PROFILES
from app.recommendations.personal_profiles import PROFILE_MODIFIERS

router = APIRouter(tags=["Activities"])


@router.get("/activities", response_model=List[ActivityInfo])
async def list_activities():
    """Returns all supported outdoor activities and their environmental sensitivity thresholds."""
    results = []
    for act_id, p in ACTIVITY_PROFILES.items():
        results.append(ActivityInfo(
            id=p["id"],
            label=p["label"],
            icon=p["icon"],
            category=p["category"],
            description=p["description"],
            ideal_temp_c=p["ideal_temp"],
            max_temp_c=float(p["max_temp"]),
            max_aqi=int(p["max_aqi"]),
            max_wind_kmh=float(p["max_wind_kmh"]),
            max_rain_prob=float(p["max_rain_prob"]),
            needs_daylight=p["needs_daylight"],
            carry_items=p["carry"],
            watch_notes=p.get("watch_note", "")
        ))
    return results


@router.get("/profiles")
async def list_profiles():
    """Returns available personal vulnerability and demographic profile modifiers."""
    return PROFILE_MODIFIERS
