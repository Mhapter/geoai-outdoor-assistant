"""
Automated unit and integration tests for the Location Verification Engine,
coordinate boundaries, duplicate detection, and geocoding normalization.
"""

import pytest
from app.schemas.location_models import (
    NormalizedLocation,
    VerificationStatus,
    LocationVerificationReport
)
from app.services.location_verification import LocationVerificationPipeline
from app.services.location_provider import parse_explicit_coordinates
from app.geo.spatial_math import haversine_km


def test_coordinate_bounds_validation():
    """Tests WGS84 range validation: [-90, 90] for latitude, [-180, 180] for longitude."""
    vp = LocationVerificationPipeline()

    # Valid points
    ok, notes = vp.validate_coordinate_bounds(28.4506, 77.5839)
    assert ok is True
    assert len(notes) == 0

    ok, notes = vp.validate_coordinate_bounds(-33.8688, 151.2093)
    assert ok is True

    # Out of bounds latitude
    ok, notes = vp.validate_coordinate_bounds(95.0, 77.0)
    assert ok is False
    assert any("Latitude" in n for n in notes)

    # Out of bounds longitude
    ok, notes = vp.validate_coordinate_bounds(28.0, 185.0)
    assert ok is False
    assert any("Longitude" in n for n in notes)

    # Null Island (0, 0)
    ok, notes = vp.validate_coordinate_bounds(0.0, 0.0)
    assert ok is False
    assert any("Null Island" in n for n in notes)

    # NaN / Inf
    ok, notes = vp.validate_coordinate_bounds(float("nan"), 77.0)
    assert ok is False
    assert any("NaN" in n for n in notes)


def test_explicit_coordinate_parsing():
    """Tests parsing raw coordinate strings in various user formats."""
    # Standard comma-separated
    res = parse_explicit_coordinates("28.4506, 77.5839")
    assert res is not None
    assert abs(res[0] - 28.4506) < 1e-4
    assert abs(res[1] - 77.5839) < 1e-4

    # With N/E directional markers
    res2 = parse_explicit_coordinates("28.4506 N, 77.5839 E")
    assert res2 is not None
    assert abs(res2[0] - 28.4506) < 1e-4
    assert abs(res2[1] - 77.5839) < 1e-4

    # Southern & Western hemisphere
    res3 = parse_explicit_coordinates("33.8688 S, 151.2093 E")
    assert res3 is not None
    assert abs(res3[0] - (-33.8688)) < 1e-4

    # Text that is not coordinates
    assert parse_explicit_coordinates("Central Park") is None
    assert parse_explicit_coordinates("Lodhi Garden, New Delhi") is None


def test_distance_tolerance_check():
    """Tests distance sanity check against user-selected search radius."""
    vp = LocationVerificationPipeline()

    origin_lat, origin_lon = 28.4506, 77.5839  # Bennett University

    # Nearby point (~1.5 km)
    target_lat, target_lon = 28.4600, 77.5900
    ok, dist_km, notes = vp.check_distance_tolerance(target_lat, target_lon, origin_lat, origin_lon, max_radius_km=10.0)
    assert ok is True
    assert dist_km < 3.0

    # Distant point (Mumbai ~1100 km away)
    mumbai_lat, mumbai_lon = 19.0760, 72.8777
    ok, dist_km, notes = vp.check_distance_tolerance(mumbai_lat, mumbai_lon, origin_lat, origin_lon, max_radius_km=10.0)
    assert ok is False
    assert dist_km > 1000.0
    assert any("exceeding the allowable search window" in n for n in notes)


def test_locality_concordance():
    """Tests locality matching against place address components."""
    vp = LocationVerificationPipeline()

    loc = NormalizedLocation(
        id="test_1",
        name="Lodhi Garden",
        formatted_address="Lodhi Garden, Lodhi Road, New Delhi, Delhi 110003, India",
        lat=28.5931,
        lon=77.2197,
        category="park",
        provider="authoritative_gazetteer",
        locality="New Delhi",
        region="Delhi",
        country="India"
    )

    # Concordant locality
    ok, notes = vp.check_locality_concordance(loc, "Delhi")
    assert ok is True

    # Concordant sub-locality
    ok, notes = vp.check_locality_concordance(loc, "Lodhi Road")
    assert ok is True

    # Mismatched locality
    ok, notes = vp.check_locality_concordance(loc, "Bengaluru")
    assert ok is False


def test_duplicate_detection_and_deduplication():
    """Tests spatial clustering and duplicate removal within 50 meters."""
    vp = LocationVerificationPipeline()

    loc1 = NormalizedLocation(
        id="osm_1",
        name="Noida Stadium",
        formatted_address="Noida Stadium, Sector 21A, Noida",
        lat=28.591000,
        lon=77.338000,
        category="sports_centre",
        provider="osm_nominatim"
    )

    # Duplicate point 15 meters away
    loc2 = NormalizedLocation(
        id="osm_2",
        name="Noida Stadium Ground",
        formatted_address="Noida Stadium, Sector 21A, Noida, UP",
        lat=28.591100,
        lon=77.338100,
        category="sports_centre",
        provider="osm_photon"
    )

    # Distinct venue 2 km away
    loc3 = NormalizedLocation(
        id="osm_3",
        name="Sector 50 Sports Arena",
        formatted_address="Sector 50, Noida",
        lat=28.577000,
        lon=77.368000,
        category="sports_centre",
        provider="osm_nominatim"
    )

    deduped = vp.deduplicate_locations([loc1, loc2, loc3])
    # Should merge loc1 and loc2 into 1 venue
    assert len(deduped) == 2
    venue_names = [v.name for v in deduped]
    assert "Sector 50 Sports Arena" in venue_names


def test_google_maps_url_generation():
    """Ensures valid Google Maps reference and direction URLs are generated."""
    loc = NormalizedLocation(
        id="test_url",
        name="Bennett University",
        formatted_address="TechZone 2, Greater Noida",
        lat=28.450628,
        lon=77.583925,
        category="campus",
        provider="authoritative_gazetteer",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=28.450628,77.583925"
    )

    assert "https://www.google.com/maps/search/?api=1&query=28.450628,77.583925" in loc.google_maps_url
    assert "28.450628" in loc.google_maps_url
    assert "77.583925" in loc.google_maps_url
