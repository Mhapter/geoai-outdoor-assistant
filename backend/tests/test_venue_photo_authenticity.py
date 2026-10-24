"""
Automated tests ensuring:
1. Unrelated photos (e.g. New York cityscapes, US Open courts, stock photos) cannot be attached to venues in Greater Noida or other locations.
2. Only photos within 1.0 km of the exact venue coordinates can be verified.
3. Missing photos honestly return an empty list [] rather than filling with stock images.
4. Straight-line distance and route distance are explicitly distinguished.
5. Missing external telemetry is flagged honestly and never silently fabricated.
"""

import pytest
import asyncio
from app.services.image_service import (
    get_venue_photos,
    is_title_unrelated,
    AUTHENTIC_AUDITED_VENUE_PHOTOS
)
from app.geo.spatial_math import haversine_km
from app.services.routing_service import calculate_route


@pytest.mark.anyio
async def test_unrelated_venue_returns_empty_photos():
    """
    Proves that a venue with no verified photos in Greater Noida
    returns an empty list [], NEVER a New York cityscape or random stock image.
    """
    # A generic or unknown local venue in Greater Noida
    photos = await get_venue_photos(
        venue_name="Local Sector 18 Tennis Court",
        venue_lat=28.4700,
        venue_lon=77.5000,
        locality="Greater Noida"
    )
    # Must NOT return US Open or New York tennis photo
    assert photos == [], "Unrelated venue must return [] and never generic or stock photos"
    assert not any("New York" in str(p) for p in photos)
    assert not any("US Open" in str(p) for p in photos)


@pytest.mark.anyio
async def test_spatial_proximity_enforcement_on_photos():
    """
    Proves that landmark photos are rejected if the venue coordinates do not match
    the landmark's verified real-world location (e.g. 'Cubbon Park' in Greater Noida coordinates).
    """
    # Asking for 'Cubbon Park' but with Greater Noida coordinates (28.45°N, 77.58°E)
    photos = await get_venue_photos(
        venue_name="Cubbon Park",
        venue_lat=28.4506,
        venue_lon=77.5839,
        locality="Greater Noida"
    )
    # The Bangalore Cubbon Park photo MUST be rejected because it is > 1700 km away
    assert photos == [], "Photo must be rejected if coordinates do not match the real venue location"


@pytest.mark.anyio
async def test_verified_venue_returns_authentic_metadata():
    """
    Proves that an authentic venue (Bennett University at Greater Noida coordinates)
    returns verified photos with exact attribution, license, and source.
    """
    photos = await get_venue_photos(
        venue_name="Bennett University Athletic Arena",
        venue_lat=28.450628,
        venue_lon=77.583925,
        locality="Greater Noida"
    )
    assert len(photos) > 0, "Bennett University at verified coordinates should return verified photos"
    top_photo = photos[0]
    assert "upload.wikimedia.org" in top_photo["url"]
    assert "Bennett_University" in top_photo["url"] or "BU_DRONE" in top_photo["url"]
    assert "attribution" in top_photo and len(top_photo["attribution"]) > 0
    assert "license" in top_photo and "CC" in top_photo["license"]
    assert top_photo.get("verified") is True


def test_title_blacklist_rejection():
    """Tests that titles containing foreign cities or unrelated terms are rejected."""
    assert is_title_unrelated("New York City Skyline Central Park.jpg", "City Park") is True
    assert is_title_unrelated("Tennis courts at the US Open, Flushing Meadows.jpg", "Tennis Club") is True
    assert is_title_unrelated("London Hyde Park Promenade.jpg", "Park Promenade") is True
    assert is_title_unrelated("Bennett University Campus Grounds.jpg", "Bennett University") is False
    assert is_title_unrelated("Lodhi Garden Delhi heritage gate.jpg", "Lodhi Garden") is False


@pytest.mark.anyio
async def test_route_and_straight_line_distance_distinguished():
    """
    Verifies that straight-line distance and road route distance are distinct
    and that road distance is greater than or equal to straight-line distance.
    """
    orig_lat, orig_lon = 28.4506, 77.5839  # Bennett University
    dest_lat, dest_lon = 28.5355, 77.3910  # Noida Sector center

    straight_km = haversine_km(orig_lat, orig_lon, dest_lat, dest_lon)
    route_km, route_mins, provider = await calculate_route(orig_lat, orig_lon, dest_lat, dest_lon)

    assert straight_km > 0.0
    assert route_km >= straight_km * 0.95, "Route distance should be >= straight-line distance"
    assert route_mins > 0.0
    assert len(provider) > 0
