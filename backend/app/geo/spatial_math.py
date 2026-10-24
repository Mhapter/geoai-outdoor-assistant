"""
Geospatial mathematical utility functions for Fieldwise.
Pure math functions for distance, bearing, and wind angles with zero external dependencies.
"""

import math


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance between two GPS coordinates in kilometers."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates forward compass bearing from point 1 to point 2 in degrees (0-360)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def angle_diff(a: float, b: float) -> float:
    """Calculates the absolute minimum angular difference between two compass bearings in degrees."""
    diff = abs(a - b) % 360
    return 360 - diff if diff > 180 else diff


def compass_dir(deg: float) -> str:
    """Converts degrees into 8-point compass direction."""
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[int((deg + 22.5) % 360 // 45)]
