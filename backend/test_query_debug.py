import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.services.slm_service import SmallLanguageModelService
from app.services.geocoding_service import geocode_location
from app.geo.spatial_context import fetch_overpass_context
from app.recommendations.activity_profiles import ACTIVITY_PROFILES
from app.recommendations.scoring import evaluate_candidate_slots

async def main():
    slm = SmallLanguageModelService()
    parsed = slm.parse_query("Cricket match within 15 km of Whitefield")
    print("Parsed intent:", json.dumps(parsed, indent=2))

    origin = await geocode_location(parsed["location"])
    print("Origin:", origin)

    activity_key = parsed.get("activity", "cricket")
    act_profile = ACTIVITY_PROFILES.get(activity_key, ACTIVITY_PROFILES["cricket"])

    venues = await fetch_overpass_context(
        lat=origin["lat"],
        lon=origin["lon"],
        radius_km=parsed.get("radius_km", 15.0),
        activity_key=activity_key,
        osm_filters=act_profile["osm_filters"],
        activity_label=act_profile["label"],
        origin_short_name=origin.get("short_name", "Whitefield")
    )
    print("\nVenues found for cricket:", len(venues))
    for v in venues:
        print(" -", v.get("name"), "lat:", v.get("lat"), "lon:", v.get("lon"), "dist:", v.get("distance_km"), "km")

    # Now let's check what happens if activity='tennis'
    print("\n--- Testing with activity='tennis' ---")
    tennis_profile = ACTIVITY_PROFILES["tennis"]
    tennis_venues = await fetch_overpass_context(
        lat=origin["lat"],
        lon=origin["lon"],
        radius_km=parsed.get("radius_km", 15.0),
        activity_key="tennis",
        osm_filters=tennis_profile["osm_filters"],
        activity_label=tennis_profile["label"],
        origin_short_name=origin.get("short_name", "Whitefield")
    )
    print("Tennis venues found:", len(tennis_venues))
    for v in tennis_venues:
        print(" -", v.get("name"), "lat:", v.get("lat"), "lon:", v.get("lon"), "dist:", v.get("distance_km"), "km")

if __name__ == "__main__":
    asyncio.run(main())
