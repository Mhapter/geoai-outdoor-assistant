"""
Weather forecast service for Fieldwise.
Retrieves live hourly and daily forecasts from Open-Meteo Forecast API.
Includes temperature, apparent temperature, precipitation probability,
precipitation amount, relative humidity, wind speed and direction, UV index, and sunrise/sunset.
"""

import math
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import httpx
import diskcache

cache = diskcache.Cache("./.geoai_cache_v5")
CACHE_TTL = 1800  # 30 minutes cache for forecasts

USER_AGENT = "Fieldwise-Outdoor-Intelligence/1.0 (https://csre.iitb.ac.in; geoai@csre.iitb.ac.in)"


async def fetch_weather_forecast(lat: float, lon: float, days: int = 3) -> Dict[str, Any]:
    """
    Fetches hourly weather forecast from Open-Meteo.
    Returns normalized dictionary with hourly parameters and provenance.
    """
    cache_key = f"weather_openmeteo_v5:{round(lat, 2)}:{round(lon, 2)}:{days}"
    if cache_key in cache:
        return cache[cache_key]

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": (
            "temperature_2m,apparent_temperature,relative_humidity_2m,"
            "precipitation_probability,precipitation,cloud_cover,"
            "wind_speed_10m,wind_direction_10m,uv_index,is_day"
        ),
        "daily": "sunrise,sunset,uv_index_max,precipitation_sum",
        "timezone": "auto",
        "forecast_days": days
    }

    try:
        t_cfg = httpx.Timeout(6.0, connect=2.5)
        async with httpx.AsyncClient(timeout=t_cfg) as client:
            resp = await client.get(url, params=params, headers={"User-Agent": USER_AGENT})
            if resp.status_code == 200:
                data = resp.json()
                if "hourly" in data:
                    result = {
                        "hourly": data["hourly"],
                        "daily": data.get("daily", {}),
                        "timezone": data.get("timezone", "UTC"),
                        "elevation": data.get("elevation", 0),
                        "source": "Open-Meteo Weather Forecast API",
                        "attribution": "Open-Meteo (CC-BY 4.0)",
                        "fetched_at": datetime.now().isoformat(),
                        "is_simulated": False
                    }
                    cache.set(cache_key, result, expire=CACHE_TTL)
                    return result
    except Exception:
        pass

    # Realistic meteorological synthetic fallback if network is blocked
    now = datetime.now()
    times = [(now + timedelta(hours=i)).strftime("%Y-%m-%dT%H:00") for i in range(days * 24)]
    temps, app_temps, rhs, rains, rain_probs, winds, dirs, uvs, days_flag, clouds = [], [], [], [], [], [], [], [], [], []

    for t_str in times:
        hr = datetime.fromisoformat(t_str).hour
        is_d = 1 if 6 <= hr <= 18 else 0
        base_t = 24.0 + 7.5 * math.sin(math.radians((hr - 8) * 15))
        uv_val = max(0.0, 7.0 * math.sin(math.radians((hr - 6) * 15))) if is_d else 0.0

        temps.append(round(base_t, 1))
        app_temps.append(round(base_t + 1.2, 1))
        rhs.append(max(40, min(85, int(65 - 20 * math.sin(math.radians((hr - 6) * 15))))))
        rain_prob = 15 if 14 <= hr <= 17 else 5
        rain_probs.append(rain_prob)
        rains.append(0.2 if rain_prob > 10 else 0.0)
        winds.append(round(9.0 + 4.5 * math.sin(math.radians(hr * 15)), 1))
        dirs.append(int((60 + hr * 10) % 360))
        uvs.append(round(uv_val, 1))
        days_flag.append(is_d)
        clouds.append(25 if is_d else 10)

    result = {
        "hourly": {
            "time": times,
            "temperature_2m": temps,
            "apparent_temperature": app_temps,
            "relative_humidity_2m": rhs,
            "precipitation_probability": rain_probs,
            "precipitation": rains,
            "wind_speed_10m": winds,
            "wind_direction_10m": dirs,
            "uv_index": uvs,
            "cloud_cover": clouds,
            "is_day": days_flag
        },
        "daily": {
            "sunrise": [f"{now.strftime('%Y-%m-%d')}T06:15:00"],
            "sunset": [f"{now.strftime('%Y-%m-%d')}T18:15:00"]
        },
        "timezone": "auto",
        "elevation": 210,
        "source": "Open-Meteo Weather Simulation Baseline (Offline Fallback)",
        "attribution": "Fieldwise Micro-climate Simulator",
        "fetched_at": datetime.now().isoformat(),
        "is_simulated": True
    }
    return result
