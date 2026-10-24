"""
Unit tests for spatial math functions in Fieldwise.
"""

import pytest
from app.geo.spatial_context import haversine_km, calculate_bearing, angle_diff, compass_dir


def test_haversine_known_distance():
    # Bennett University (28.4506, 77.5839) to Greater Noida City Center (28.4744, 77.5040) ~ 8.2 km
    dist = haversine_km(28.4506, 77.5839, 28.4744, 77.5040)
    assert 7.5 < dist < 9.0


def test_calculate_bearing():
    # From origin directly north
    bearing = calculate_bearing(0.0, 0.0, 1.0, 0.0)
    assert 0 <= bearing < 5 or 355 < bearing <= 360

    # From origin directly east
    bearing_e = calculate_bearing(0.0, 0.0, 0.0, 1.0)
    assert 85 < bearing_e < 95


def test_angle_diff():
    assert angle_diff(10, 20) == 10
    assert angle_diff(350, 10) == 20
    assert angle_diff(180, 0) == 180


def test_compass_dir():
    assert compass_dir(0) == "N"
    assert compass_dir(90) == "E"
    assert compass_dir(180) == "S"
    assert compass_dir(270) == "W"
    assert compass_dir(45) == "NE"
