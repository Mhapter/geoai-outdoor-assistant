"""
Unit tests for the Natural Language Query Parser.
Verifies parsing of the 10 reference queries from the hackathon specification.
"""

import pytest
from app.services.slm_service import SmallLanguageModelService

slm = SmallLanguageModelService()


def test_parse_koregaon_running():
    q = "Where can I go running tomorrow evening near Koregaon Park?"
    parsed = slm.parse_query(q)
    assert parsed["status"] == "ok"
    assert parsed["activity"] == "running"
    assert "Koregaon Park" in parsed["location"]
    assert parsed["day_offset"] == 1
    assert parsed["target_hours"] == [17, 18, 19, 20]


def test_parse_whitefield_cricket():
    q = "Best time this weekend for a kids' cricket match within 15 km of Whitefield?"
    parsed = slm.parse_query(q)
    assert parsed["status"] == "ok"
    assert parsed["activity"] == "cricket"
    assert "child" in parsed["personal_profiles"]
    assert parsed["radius_km"] == 15.0
    assert "Whitefield" in parsed["location"]


def test_parse_powai_asthma():
    q = "I have mild asthma, where's good for a morning walk near Powai in the next two days?"
    parsed = slm.parse_query(q)
    assert parsed["status"] == "ok"
    assert "asthma" in parsed["personal_profiles"]
    assert "Powai" in parsed["location"]
    assert parsed["target_hours"] == [6, 7, 8, 9, 10, 11]


def test_parse_cycle_commute():
    q = "Is it okay to cycle to work at 8 AM near Bennett University?"
    parsed = slm.parse_query(q)
    assert parsed["status"] == "ok"
    assert parsed["activity"] == "cycling"
    assert parsed["target_hours"] == [8]
    assert "Bennett University" in parsed["location"]


def test_parse_pune_event():
    q = "Planning an outdoor birthday party on Sunday afternoon in Pune, what should I keep in mind?"
    parsed = slm.parse_query(q)
    assert parsed["status"] == "ok"
    assert parsed["activity"] == "event"
    assert parsed["day_label"] == "Sunday"
    assert parsed["target_hours"] == [12, 13, 14, 15, 16]
    assert "Pune" in parsed["location"]


def test_parse_andheri_golf():
    q = "Good place and time for golf on Saturday within 40 km of Andheri?"
    parsed = slm.parse_query(q)
    assert parsed["status"] == "ok"
    assert parsed["activity"] == "golf"
    assert parsed["radius_km"] == 40.0
    assert "Andheri" in parsed["location"]


def test_parse_bandra_sunset():
    q = "Where can I take sunset photos this evening around Bandra?"
    parsed = slm.parse_query(q)
    assert parsed["status"] == "ok"
    assert parsed["activity"] == "photography"
    assert "Bandra" in parsed["location"]
    assert 17 in parsed["target_hours"]


def test_parse_lonavala_hike_comparison():
    q = "Is Saturday or Sunday better for a hike near Lonavala?"
    parsed = slm.parse_query(q)
    assert parsed["status"] == "ok"
    assert parsed["activity"] == "hiking"
    assert parsed["compare_mode"] == "sat_vs_sun"
    assert "Lonavala" in parsed["location"]


def test_parse_parents_bengaluru():
    q = "When is it safe for my parents to walk outdoors tomorrow in Bengaluru?"
    parsed = slm.parse_query(q)
    assert parsed["status"] == "ok"
    assert "senior" in parsed["personal_profiles"]
    assert parsed["day_offset"] == 1
    assert "Bengaluru" in parsed["location"]


def test_parse_missing_location():
    q = "Where can I run tomorrow morning?"
    parsed = slm.parse_query(q)
    assert parsed["status"] == "missing_location"
    assert "location" not in parsed or not parsed.get("location")
