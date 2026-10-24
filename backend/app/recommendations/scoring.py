"""
Recommendation and Scoring Engine for Fieldwise.
Transparent, deterministic multi-place and multi-hour evaluation.
Scores venues based on thermal comfort, air quality, wind aerodynamics,
downwind highway/industrial plume avoidance, green cover, and travel time.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from app.geo.spatial_context import angle_diff, compass_dir
from app.recommendations.activity_profiles import ACTIVITY_PROFILES
from app.recommendations.personal_profiles import PROFILE_MODIFIERS


def evaluate_candidate_slots(
    venues: List[Dict[str, Any]],
    weather_data_by_venue: List[Dict[str, Any]],
    travel_data_by_venue: List[Tuple[float, float, str]],
    activity_key: str,
    personal_profiles: List[str],
    target_hours_filter: Optional[List[int]] = None,
    day_offset: int = 0,
    compare_mode: Optional[str] = None,
    radius_km: float = 10.0
) -> Dict[str, Any]:
    """
    Evaluates each candidate venue across candidate hours in the specified window.
    Applies activity-specific scoring and personalized health profile constraints.
    """
    act = dict(ACTIVITY_PROFILES.get(activity_key, ACTIVITY_PROFILES["general_outdoor"]))
    downwind_mult = 1.0
    extra_carry = list(act.get("carry", []))
    watch_notes = []

    if act.get("watch_note"):
        watch_notes.append(act["watch_note"])

    # Apply personal profile adjustments
    for prof_key in personal_profiles:
        mod = PROFILE_MODIFIERS.get(prof_key)
        if mod:
            if "max_aqi" in mod:
                act["max_aqi"] = min(act["max_aqi"], mod["max_aqi"])
            if "max_temp" in mod:
                act["max_temp"] = min(act["max_temp"], mod["max_temp"])
            if "ideal_temp" in mod:
                act["ideal_temp"] = mod["ideal_temp"]
            downwind_mult = max(downwind_mult, mod.get("downwind_penalty_multiplier", 1.0))
            for item in mod.get("extra_carry", []):
                if item not in extra_carry:
                    extra_carry.append(item)
            if mod.get("watch_note"):
                watch_notes.append(mod["watch_note"])

    scored_slots = []
    avoid_slots = []
    venue_hourly_series: Dict[str, List[Dict[str, Any]]] = {}

    for idx, venue in enumerate(venues):
        w_bundle = weather_data_by_venue[idx]
        w_hourly = w_bundle.get("hourly", {})
        times = w_hourly.get("time", [])
        if not times:
            continue

        route_dist_km, route_base_mins, route_provider = travel_data_by_venue[idx] if idx < len(travel_data_by_venue) else (venue.get("distance_km", 2.0), 8.0, "OSRM")
        env = venue.get("env_context", {})
        venue_hourly_series[venue["name"]] = []

        # Determine index range for evaluation based on day_offset
        start_idx = min(day_offset * 24, max(0, len(times) - 24))
        end_idx = min(start_idx + 24, len(times))

        for h_i in range(start_idx, end_idx):
            t_str = times[h_i]
            dt = datetime.fromisoformat(t_str)
            hr = dt.hour

            # Focus outdoor recommendations between 05:00 and 22:00
            if hr < 5 or hr > 21:
                continue

            temp = w_hourly.get("temperature_2m", [24.0])[h_i] if h_i < len(w_hourly.get("temperature_2m", [])) else 24.0
            app_temp = w_hourly.get("apparent_temperature", [temp])[h_i] if h_i < len(w_hourly.get("apparent_temperature", [])) else temp
            rh = w_hourly.get("relative_humidity_2m", [50])[h_i] if h_i < len(w_hourly.get("relative_humidity_2m", [])) else 50
            rain_prob = w_hourly.get("precipitation_probability", [0])[h_i] if h_i < len(w_hourly.get("precipitation_probability", [])) else 0
            rain_mm = w_hourly.get("precipitation", [0.0])[h_i] if h_i < len(w_hourly.get("precipitation", [])) else 0.0
            wind_spd = w_hourly.get("wind_speed_10m", [6.0])[h_i] if h_i < len(w_hourly.get("wind_speed_10m", [])) else 6.0
            wind_dir = w_hourly.get("wind_direction_10m", [45.0])[h_i] if h_i < len(w_hourly.get("wind_direction_10m", [])) else 45.0
            uv = w_hourly.get("uv_index", [0.0])[h_i] if h_i < len(w_hourly.get("uv_index", [])) else 0.0
            cloud = w_hourly.get("cloud_cover", [20])[h_i] if h_i < len(w_hourly.get("cloud_cover", [])) else 20
            is_day = bool(w_hourly.get("is_day", [1])[h_i]) if h_i < len(w_hourly.get("is_day", [])) else True

            # Air quality readings
            aqi_list = w_bundle.get("aqi_hourly", {}).get("us_aqi", [])
            pm25_list = w_bundle.get("aqi_hourly", {}).get("pm2_5", [])
            pm10_list = w_bundle.get("aqi_hourly", {}).get("pm10", [])

            aqi = aqi_list[h_i] if h_i < len(aqi_list) and aqi_list[h_i] is not None else 65
            pm25 = pm25_list[h_i] if h_i < len(pm25_list) and pm25_list[h_i] is not None else 18.0
            pm10 = pm10_list[h_i] if h_i < len(pm10_list) and pm10_list[h_i] is not None else 35.0

            score = 100.0
            reasons_good = []
            reasons_bad = []
            reasons_missing = []

            # 1. Daylight Check
            if act.get("needs_daylight") and not is_day:
                score -= 42.0
                reasons_bad.append("Insufficient daylight for active outdoor visibility & safety")

            # 2. Golden-hour Bonus for creative photography / yoga
            is_golden = hr in (6, 7, 17, 18)
            if act.get("golden_hour_bonus") and is_golden:
                score += 12.0
                reasons_good.append("Low-angle golden-hour lighting ideal for photography and visual ambiance")

            # 3. Thermal Comfort Evaluation
            low_t, high_t = act["ideal_temp"]
            if low_t <= temp <= high_t:
                reasons_good.append(f"Ideal thermal comfort ({temp:.1f}°C, feels like {app_temp:.1f}°C)")
            elif temp > act["max_temp"]:
                pen = (temp - act["max_temp"]) * 6.5
                score -= pen
                reasons_bad.append(f"Excessive heat load ({temp:.1f}°C, feels like {app_temp:.1f}°C)")
            elif temp > high_t:
                score -= (temp - high_t) * 3.0
            elif temp < act.get("min_temp", 5):
                pen = (act.get("min_temp", 5) - temp) * 4.0
                score -= pen
                reasons_bad.append(f"Chilly temperatures ({temp:.1f}°C)")

            # 4. Air Quality Evaluation (EPA US AQI)
            if aqi <= 55:
                reasons_good.append(f"Clean breathable air (US AQI {int(aqi)}, PM2.5 {pm25:.1f} µg/m³)")
            elif aqi > act["max_aqi"]:
                pen = (aqi - act["max_aqi"]) * 0.60 * downwind_mult
                score -= pen
                reasons_bad.append(f"Elevated particulate pollution (US AQI {int(aqi)}, PM2.5 {pm25:.1f} µg/m³)")
            else:
                score -= (aqi - 55) * 0.20

            # 5. Rain Probability & Precipitation
            if rain_prob > act["max_rain_prob"]:
                score -= (rain_prob - act["max_rain_prob"]) * 0.85
                reasons_bad.append(f"High rain probability ({rain_prob}%, {rain_mm:.1f} mm rain expected)")
            elif rain_prob <= 10:
                reasons_good.append("Minimal precipitation risk (< 10%)")

            # 6. Wind Aerodynamics
            if wind_spd > act["max_wind_kmh"]:
                score -= (wind_spd - act["max_wind_kmh"]) * 1.5
                reasons_bad.append(f"High wind gust speed ({wind_spd:.1f} km/h from {compass_dir(wind_dir)})")
            elif wind_spd <= 12:
                reasons_good.append(f"Gentle calm breeze ({wind_spd:.1f} km/h {compass_dir(wind_dir)})")

            # 7. Downwind Highway & Industrial Plume Geospatial Analysis
            downwind_status = "Upwind / Clear Corridor"
            if env.get("major_road"):
                road = env["major_road"]
                diff = angle_diff(wind_dir, road["wind_from_hazard_deg"])
                if diff <= 45:
                    rush_factor = 1.5 if hr in (8, 9, 10, 17, 18, 19, 20) else 1.0
                    pen = 14.0 * rush_factor * downwind_mult
                    score -= pen
                    downwind_status = f"Downwind of {road['name']}"
                    reasons_bad.append(f"Downwind of {road['name']} ({road['dist_km']} km {road['direction_from_venue']}) under {compass_dir(wind_dir)} breeze")
                else:
                    reasons_good.append(f"Upwind/crosswind of {road['name']} (airflow disperses traffic exhaust away)")

            if env.get("industry"):
                ind = env["industry"]
                diff_ind = angle_diff(wind_dir, ind["wind_from_hazard_deg"])
                if diff_ind <= 50:
                    pen = 20.0 * downwind_mult
                    score -= pen
                    downwind_status = f"Downwind of {ind['name']}"
                    reasons_bad.append(f"Downwind of {ind['name']} ({ind['dist_km']} km {ind['direction_from_venue']}) under {compass_dir(wind_dir)} wind")

            # 8. Green Canopy and Water Body Micro-climate Buffering
            if env.get("green_cover_nearby"):
                score += 5.0
                reasons_good.append("Sheltered by mature tree canopies and green vegetation buffer")
            if env.get("water_body_nearby") and temp >= 27:
                score += 4.0
                reasons_good.append(f"Beneficial evaporative micro-cooling near {env.get('water_name', 'water body')}")

            # 8b. Venue-to-Activity Grounding Check
            v_acts = venue.get("activities", [])
            v_tags = venue.get("tags", {})
            is_sports_activity = activity_key in ("cricket", "football", "tennis", "golf")

            if v_acts and activity_key in v_acts:
                score += 8.0
                reasons_good.append(f"Dedicated regulation venue for {act.get('label', activity_key)}")
            elif is_sports_activity:
                sport_tag = v_tags.get("sport", "").lower()
                leisure_tag = v_tags.get("leisure", "").lower()
                if sport_tag == activity_key or activity_key in venue.get("name", "").lower():
                    score += 6.0
                    reasons_good.append(f"Verified sports pitch for {act.get('label', activity_key)}")
                elif leisure_tag in ("garden", "park", "nature_reserve") and "cricket" not in venue["name"].lower() and "tennis" not in venue["name"].lower() and "football" not in venue["name"].lower():
                    score -= 42.0
                    reasons_bad.append(f"General park lacking dedicated regulation {act.get('label', activity_key)} grounds")

            # 9. Driving Transit & Proximity to Origin
            is_rush = hr in (8, 9, 10, 17, 18, 19, 20)
            est_travel_mins = round(route_base_mins * (1.45 if is_rush else 1.0), 1)

            # Strict radius limit enforcement
            if route_dist_km > radius_km:
                dist_excess = route_dist_km - radius_km
                score -= (20.0 + dist_excess * 3.5)
                reasons_bad.append(f"Exceeds preferred radius ({route_dist_km:.1f} km > {radius_km:.0f} km search limit)")
            elif route_dist_km <= 3.0:
                score += 8.0
                reasons_good.append(f"Immediate proximity ({route_dist_km:.1f} km, ~{int(est_travel_mins)} mins away)")
            elif route_dist_km <= 6.0:
                score += 4.0
                reasons_good.append(f"Convenient local access ({route_dist_km:.1f} km)")
            elif route_dist_km > 12.0:
                score -= (route_dist_km - 10.0) * 1.2
                reasons_bad.append(f"Extended driving distance ({route_dist_km:.1f} km)")

            if est_travel_mins > 30:
                score -= (est_travel_mins - 30) * 0.5
                reasons_bad.append(f"Elevated transit time ({int(est_travel_mins)} mins {'rush hour' if is_rush else ''})")
            elif route_dist_km <= radius_km:
                reasons_good.append(f"Within {radius_km:.0f} km search radius ({route_dist_km:.1f} km transit via OSRM)")

            final_score = int(max(5, min(99, round(score))))
            if final_score >= 82:
                suitability = "Optimal"
            elif final_score >= 68:
                suitability = "Good"
            elif final_score >= 50:
                suitability = "Marginal"
            else:
                suitability = "Avoid"

            slot_record = {
                "venue_name": venue["name"],
                "lat": venue["lat"],
                "lon": venue["lon"],
                "hour_iso": t_str,
                "hour_label": dt.strftime("%a %d %b, %I:00 %p"),
                "day_name": dt.strftime("%A"),
                "day_date": dt.strftime("%Y-%m-%d"),
                "score": final_score,
                "suitability_label": suitability,
                "temp_c": round(temp, 1),
                "feels_like_c": round(app_temp, 1),
                "rain_prob_pct": int(rain_prob),
                "rain_mm": round(rain_mm, 1),
                "wind_kmh": round(wind_spd, 1),
                "wind_compass": compass_dir(wind_dir),
                "us_aqi": int(aqi),
                "pm25": round(pm25, 1),
                "pm10": round(pm10, 1),
                "uv_index": round(uv, 1),
                "distance_km": route_dist_km,
                "travel_mins": int(est_travel_mins),
                "straight_line_dist_km": round(float(venue.get("distance_km", route_dist_km)), 2),
                "route_dist_km": route_dist_km,
                "routing_provider": route_provider,
                "downwind_status": downwind_status,
                "reasons_good": reasons_good,
                "reasons_bad": reasons_bad,
                "reasons_missing": reasons_missing,
                "google_maps_url": venue.get("google_maps_url") or f"https://www.google.com/maps/search/?api=1&query={venue['lat']},{venue['lon']}",
                "verification_status": venue.get("verification_status", "verified"),
                "verification_notes": venue.get("verification_notes", []),
                "provider": venue.get("provider", "osm")
            }

            hourly_condition = {
                "hour_iso": t_str,
                "hour_label": dt.strftime("%I:00 %p").lstrip("0"),
                "day_name": dt.strftime("%A"),
                "day_date": dt.strftime("%Y-%m-%d"),
                "temp_c": round(temp, 1),
                "feels_like_c": round(app_temp, 1),
                "humidity_pct": int(rh),
                "precip_prob_pct": int(rain_prob),
                "rain_mm": round(rain_mm, 1),
                "wind_kmh": round(wind_spd, 1),
                "wind_dir_deg": int(wind_dir),
                "wind_compass": compass_dir(wind_dir),
                "us_aqi": int(aqi),
                "pm25": round(pm25, 1),
                "pm10": round(pm10, 1),
                "uv_index": round(uv, 1),
                "cloud_cover_pct": int(cloud),
                "is_daylight": is_day,
                "golden_hour": is_golden
            }
            venue_hourly_series[venue["name"]].append(hourly_condition)

            # Check if this slot passes the user's requested target hours
            if not target_hours_filter or hr in target_hours_filter:
                scored_slots.append(slot_record)
            if reasons_bad and final_score < 65:
                avoid_slots.append(slot_record)

    # Sort scored slots descending by score
    scored_slots.sort(key=lambda s: s["score"], reverse=True)
    avoid_slots.sort(key=lambda s: s["score"])

    # Extract distinct best slot per venue
    best_per_venue = []
    seen_venues = set()
    for s in scored_slots:
        if s["venue_name"] not in seen_venues:
            seen_venues.add(s["venue_name"])
            best_per_venue.append(s)

    best_recommendation = scored_slots[0] if scored_slots else None
    alternative_venues = best_per_venue[1:5] if len(best_per_venue) > 1 else []
    top_venue_name = best_recommendation["venue_name"] if best_recommendation else (venues[0]["name"] if venues else "")
    hourly_timeline = venue_hourly_series.get(top_venue_name, [])

    return {
        "best_recommendation": best_recommendation,
        "alternative_venues": alternative_venues,
        "avoid_slots": avoid_slots[:4],
        "hourly_timeline": hourly_timeline,
        "recommended_carry": extra_carry,
        "profile_watch_notes": watch_notes,
    }
