"""
Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "model_id" in data
    assert "OpenStreetMap" in data["attribution"]


def test_activities_endpoint():
    resp = client.get("/api/activities")
    assert resp.status_code == 200
    acts = resp.json()
    assert len(acts) >= 10
    act_ids = [a["id"] for a in acts]
    assert "running" in act_ids
    assert "cycling" in act_ids
    assert "golf" in act_ids
    assert "cricket" in act_ids
    assert "photography" in act_ids


def test_sources_endpoint():
    resp = client.get("/api/sources")
    assert resp.status_code == 200
    sources = resp.json()
    assert len(sources) >= 4
    names = [s["name"] for s in sources]
    assert any("OpenStreetMap" in n for n in names)
    assert any("Open-Meteo" in n for n in names)


def test_recommendation_missing_location():
    resp = client.post("/api/recommendations", json={"question": "Where can I run?"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "missing_location"
    assert "Location Required" in data["recommendation_markdown"] or "specify" in data["message"].lower()


def test_recommendation_with_known_location():
    resp = client.post("/api/recommendations", json={
        "question": "Best spot for jogging tomorrow morning near Bennett University?"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["best_recommendation"] is not None
    assert "Bennett University" in data["origin"]["name"]
    assert len(data["hourly_timeline"]) > 0
    assert len(data["sources"]) > 0
