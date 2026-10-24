"""
Reproducible Location Accuracy Test Dataset.
Validates search and geocoding resolution against known reference places
and ground-truth coordinates within documented tolerances.
"""

import pytest
import asyncio
from app.services.location_provider import location_service
from app.geo.spatial_math import haversine_km

# Ground-truth reference places with verified coordinates and tolerances
ACCURACY_BENCHMARKS = [
    {
        "query": "Bennett University",
        "expected_name": "Bennett University",
        "ref_lat": 28.450628,
        "ref_lon": 77.583925,
        "max_tolerance_km": 0.5,
        "expected_locality": "Greater Noida",
        "category": "university_campus"
    },
    {
        "query": "IIT Bombay",
        "expected_name": "Indian Institute of Technology Bombay",
        "ref_lat": 19.133444,
        "ref_lon": 72.913333,
        "max_tolerance_km": 0.5,
        "expected_locality": "Mumbai",
        "category": "university_campus"
    },
    {
        "query": "IIT Delhi",
        "expected_name": "Indian Institute of Technology Delhi",
        "ref_lat": 28.544976,
        "ref_lon": 77.192627,
        "max_tolerance_km": 0.5,
        "expected_locality": "New Delhi",
        "category": "university_campus"
    },
    {
        "query": "Cubbon Park",
        "expected_name": "Cubbon Park",
        "ref_lat": 12.976353,
        "ref_lon": 77.592918,
        "max_tolerance_km": 0.5,
        "expected_locality": "Bengaluru",
        "category": "park"
    },
    {
        "query": "Lodhi Garden",
        "expected_name": "Lodhi Garden",
        "ref_lat": 28.593100,
        "ref_lon": 77.219700,
        "max_tolerance_km": 0.5,
        "expected_locality": "New Delhi",
        "category": "park"
    },
    {
        "query": "Marine Drive",
        "expected_name": "Marine Drive",
        "ref_lat": 18.943200,
        "ref_lon": 72.823000,
        "max_tolerance_km": 1.0,
        "expected_locality": "Mumbai",
        "category": "promenade"
    },
    {
        "query": "Koregaon Park",
        "expected_name": "Koregaon Park",
        "ref_lat": 18.536200,
        "ref_lon": 73.894000,
        "max_tolerance_km": 1.0,
        "expected_locality": "Pune",
        "category": "locality"
    },
    {
        "query": "Whitefield",
        "expected_name": "Whitefield",
        "ref_lat": 12.969800,
        "ref_lon": 77.750000,
        "max_tolerance_km": 1.0,
        "expected_locality": "Bengaluru",
        "category": "locality"
    },
    {
        "query": "Pari Chowk",
        "expected_name": "Pari Chowk",
        "ref_lat": 28.468200,
        "ref_lon": 77.514200,
        "max_tolerance_km": 0.5,
        "expected_locality": "Greater Noida",
        "category": "junction"
    },
    {
        "query": "Noida Stadium",
        "expected_name": "Noida Stadium",
        "ref_lat": 28.591000,
        "ref_lon": 77.338000,
        "max_tolerance_km": 0.5,
        "expected_locality": "Noida",
        "category": "sports_centre"
    }
]


@pytest.mark.anyio
@pytest.mark.parametrize("benchmark", ACCURACY_BENCHMARKS)
async def test_reference_places_accuracy(benchmark):
    """
    Executes geocoding against known ground truth benchmarks.
    Asserts that distance error between resolved coordinates and reference coordinates
    is strictly within documented tolerance.
    """
    results = await location_service.search_location(benchmark["query"], limit=1)
    assert len(results) > 0, f"Failed to resolve place: {benchmark['query']}"

    top = results[0]
    distance_error_km = haversine_km(top.lat, top.lon, benchmark["ref_lat"], benchmark["ref_lon"])

    assert distance_error_km <= benchmark["max_tolerance_km"], (
        f"Location discrepancy for '{benchmark['query']}': "
        f"Resolved to ({top.lat:.5f}, {top.lon:.5f}), "
        f"expected ({benchmark['ref_lat']:.5f}, {benchmark['ref_lon']:.5f}). "
        f"Distance error {distance_error_km:.2f} km exceeds tolerance {benchmark['max_tolerance_km']} km."
    )


@pytest.mark.anyio
async def test_direct_coordinate_resolution():
    """
    Tests that passing explicit GPS coordinates directly resolves to the exact coordinates.
    """
    input_str = "19.1334, 72.9133"
    results = await location_service.search_location(input_str, limit=1)
    assert len(results) > 0
    top = results[0]

    assert abs(top.lat - 19.1334) < 1e-4
    assert abs(top.lon - 72.9133) < 1e-4
