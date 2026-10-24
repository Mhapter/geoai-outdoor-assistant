"""
Tests for newly added /api/locations endpoints:
- GET /api/locations/search
- GET /api/locations/autocomplete
- POST /api/locations/verify
- POST /api/locations/report
- GET /api/locations/reports
"""

import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_locations_search_endpoint():
    resp = client.get("/api/locations/search?q=Cubbon Park")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["count"] > 0
    primary = data["primary_result"]
    assert "Cubbon Park" in primary["name"]
    assert abs(primary["lat"] - 12.9763) < 0.05
    assert primary["verification_status"] == "verified"


def test_locations_autocomplete_endpoint():
    resp = client.get("/api/locations/autocomplete?q=Bennett")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert len(data["suggestions"]) > 0
    assert any("Bennett" in s["name"] for s in data["suggestions"])


def test_locations_verify_endpoint():
    candidate = {
        "id": "test_verify_cand",
        "name": "Lodhi Garden",
        "formatted_address": "Lodhi Garden, New Delhi, Delhi, India",
        "lat": 28.5931,
        "lon": 77.2197,
        "category": "park",
        "provider": "osm_nominatim",
        "verification_status": "unverified"
    }
    resp = client.post("/api/locations/verify?expected_locality=Delhi&origin_lat=28.5900&origin_lon=77.2100", json=candidate)
    assert resp.status_code == 200
    report = resp.json()
    assert report["is_valid_coordinate"] is True
    assert report["is_within_locality"] is True
    assert report["distance_within_tolerance"] is True


def test_locations_report_and_retrieve():
    payload = {
        "location_id": "test_loc_123",
        "location_name": "Sample Test Park",
        "reported_lat": 28.5000,
        "reported_lon": 77.2000,
        "issue_type": "wrong_coordinates",
        "suggested_correction": "Move pin 100m east",
        "notes": "Entrance is on the east road."
    }
    resp = client.post("/api/locations/report", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "report_id" in data

    # Check retrieval
    r_resp = client.get("/api/locations/reports")
    assert r_resp.status_code == 200
    r_data = r_resp.json()
    assert r_data["total_reports"] >= 1
