"""
Routing and travel duration service for Fieldwise.
Uses OSRM (Open Source Routing Machine) public routing API to calculate driving distance and duration.
Includes sensible haversine urban velocity fallback when OSRM is unreachable.
"""

from typing import Dict, Any, Tuple
import httpx
import diskcache
from app.geo.spatial_context import haversine_km

from app.cache import cache
CACHE_TTL = 3600  # 1 hour cache for routes

USER_AGENT = "Fieldwise-Outdoor-Intelligence/1.0 (https://csre.iitb.ac.in; geoai@csre.iitb.ac.in)"


async def calculate_route(orig_lat: float, orig_lon: float, dest_lat: float, dest_lon: float) -> Tuple[float, float, str]:
    """
    Returns (distance_km, duration_mins, provider).
    Does NOT claim real-time live traffic; explicitly states estimated driving duration under standard flow.
    """
    cache_key = f"osrm_route_v5:{round(orig_lat, 3)}:{round(orig_lon, 3)}:{round(dest_lat, 3)}:{round(dest_lon, 3)}"
    if cache_key in cache:
        return cache[cache_key]

    crow_dist = haversine_km(orig_lat, orig_lon, dest_lat, dest_lon)
    # Average urban/suburban road network routing factor ~ 1.25x crow flies, 26 km/h speed
    fallback_dist = round(crow_dist * 1.25, 2)
    fallback_mins = round(max(3.0, (fallback_dist / 26.0) * 60.0), 1)

    url = f"https://router.project-osrm.org/route/v1/driving/{orig_lon},{orig_lat};{dest_lon},{dest_lat}?overview=false"
    try:
        t_cfg = httpx.Timeout(2.0, connect=1.0)
        async with httpx.AsyncClient(timeout=t_cfg) as client:
            resp = await client.get(url, headers={"User-Agent": USER_AGENT})
            if resp.status_code == 200:
                data = resp.json()
                routes = data.get("routes", [])
                if routes:
                    r_dist = round(routes[0]["distance"] / 1000.0, 2)
                    r_mins = round(routes[0]["duration"] / 60.0, 1)
                    res = (r_dist, r_mins, "OSRM Open Source Routing Machine (Free Flow Estimate)")
                    cache.set(cache_key, res, expire=CACHE_TTL)
                    return res
    except Exception:
        pass

    res = (fallback_dist, fallback_mins, "Haversine Urban Transit Model (OSRM Unavailable)")
    cache.set(cache_key, res, expire=CACHE_TTL)
    return res
