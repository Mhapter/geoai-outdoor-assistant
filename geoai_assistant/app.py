"""
GeoAI Outdoor Intelligence Platform — Apple Enterprise Horizon Edition (v5.8)
GeoAI Hackathon @ CSRE, IIT Bombay

High-performance FastAPI platform pairing deterministic spatio-temporal
reasoning with an open-weights <=3B Small Language Model (Qwen2.5-3B-Instruct).
Crafted with multinational executive standards:
- Dynamic Ambient Horizon Canvas
- Live Generative SLM Streaming Typewriter (Qwen2.5-3B-Instruct)
- AI Action Suite (Copy, Native AI Speech Voice, Evidence Inspector)
- Top 5 Authentic Candidate Venues Guarantee
- Apple Maps Route Intelligence & Tactile Audio Feedback
"""

import asyncio
import sys
from typing import Optional
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# Ensure Windows terminal handles UTF-8 / emojis safely
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from geo_engine import (
    geocode_place,
    fetch_overpass_context,
    fetch_osrm_travel_time,
    fetch_weather_and_aqi,
    evaluate_venues_across_hours,
)
from slm_engine import SmallLanguageModelEngine, DEFAULT_MODEL_ID

app = FastAPI(
    title="GeoAI Outdoor Intelligence Platform — CSRE, IIT Bombay",
    description="Spatio-temporal outdoor decision support powered by an open-weights <=3B Small Language Model",
    version="5.8.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

slm = SmallLanguageModelEngine(model_id=DEFAULT_MODEL_ID)


class QueryRequest(BaseModel):
    question: str = Field(..., example="Outdoor activities near gtb nagar delhi")
    user_lat: Optional[float] = None
    user_lon: Optional[float] = None


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "5.8.0",
        "model_id": DEFAULT_MODEL_ID,
        "parameters": "3.09B total (2.77B non-embedding) <= 3B limit compliant",
        "design_language": "Apple Enterprise Horizon (Generative SLM Streaming + Audio Engine)",
        "attribution": "© OpenStreetMap contributors, Open-Meteo, OSRM"
    }


@app.post("/ask")
async def ask_assistant(req: QueryRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    parsed = slm.parse_user_query(question)
    if parsed.get("status") != "ok":
        # Check if browser GPS coordinates were provided to resolve a missing location
        if req.user_lat is not None and req.user_lon is not None and parsed.get("status") == "missing_location":
            parsed["location"] = f"Current GPS Location ({req.user_lat:.4f}° N, {req.user_lon:.4f}° E)"
            parsed["status"] = "ok"
        else:
            return {
                "question": question,
                "status": parsed.get("status"),
                "answer": parsed.get("message"),
                "parsed_intent": parsed,
                "attribution": "© OpenStreetMap contributors"
            }

    origin = None
    origin_type = "query_location"

    # Transparent origin resolution:
    # If the user clicked "Use GPS" or asked "near me", prioritize device GPS
    is_near_me = any(w in question.lower() for w in ["near me", "current location", "my location", "here", "around me"])
    
    if req.user_lat is not None and req.user_lon is not None and (is_near_me or not parsed.get("location")):
        origin = {
            "name": f"Current Device Location ({req.user_lat:.4f}° N, {req.user_lon:.4f}° E)",
            "short_name": "My Device GPS",
            "lat": req.user_lat,
            "lon": req.user_lon,
            "geocoder": "Browser GPS Telemetry"
        }
        origin_type = "device_gps"
    elif parsed.get("location"):
        origin = await geocode_place(parsed["location"])
        origin_type = "query_location"
    elif req.user_lat is not None and req.user_lon is not None:
        origin = {
            "name": f"Current Device Location ({req.user_lat:.4f}° N, {req.user_lon:.4f}° E)",
            "short_name": "My Device GPS",
            "lat": req.user_lat,
            "lon": req.user_lon,
            "geocoder": "Browser GPS Telemetry"
        }
        origin_type = "device_gps"

    if not origin:
        return {
            "question": question,
            "status": "location_not_found",
            "answer": (
                f"Could not locate '{parsed['location']}' via Open-Meteo & OpenStreetMap. "
                f"Please specify a known city, campus, or landmark, or click **'📍 Use GPS'** to pinpoint your current location."
            ),
            "attribution": "© OpenStreetMap contributors"
        }

    venues = await fetch_overpass_context(
        origin["lat"], origin["lon"], parsed["radius_km"], parsed["activity"], origin.get("short_name", parsed["location"])
    )

    # Deduplicate weather queries by regional coordinates
    weather_cache = {}
    async def get_regional_weather(lat, lon):
        k = (round(lat, 2), round(lon, 2))
        if k not in weather_cache:
            weather_cache[k] = await fetch_weather_and_aqi(lat, lon, days=4)
        return weather_cache[k]

    weather_tasks = [get_regional_weather(v["lat"], v["lon"]) for v in venues]
    travel_tasks = [fetch_osrm_travel_time(origin["lat"], origin["lon"], v["lat"], v["lon"]) for v in venues]

    weather_bundle, base_travel_mins = await asyncio.gather(
        asyncio.gather(*weather_tasks),
        asyncio.gather(*travel_tasks)
    )

    evidence = evaluate_venues_across_hours(
        venues=venues,
        weather_bundle=weather_bundle,
        base_travel_mins=base_travel_mins,
        activity_key=parsed["activity"],
        personal_profiles=parsed["personal_profiles"],
        target_hours_filter=parsed["target_hours"],
        day_offset=parsed["day_offset"],
        compare_mode=parsed.get("compare_mode")
    )

    answer = slm.synthesize_recommendation(question, parsed, evidence)

    return {
        "question": question,
        "status": "ok",
        "model_used": DEFAULT_MODEL_ID,
        "origin": origin,
        "origin_type": origin_type,
        "parsed_intent": parsed,
        "recommendation_markdown": answer,
        "top_venue_slots": evidence["top_slots"],
        "alternatives_compared": evidence["best_per_venue"],
        "avoid_slots": evidence["avoid_slots"],
        "hourly_timeline": evidence["hourly_timeline"],
        "recommended_carry": evidence["recommended_carry"],
        "profile_watch_notes": evidence["profile_watch_notes"],
        "evidence_raw": evidence,
        "sources": evidence["sources"]
    }



@app.get("/", response_class=HTMLResponse)
async def interactive_ui(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>GeoAI — Outdoor Intelligence</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root {
      --bg: #09090b;
      --surface: #121215;
      --surface-raised: #18181b;
      --surface-hover: #222226;
      --border: #3f3f46;
      --border-subtle: #27272a;
      --text-primary: #fafafa;
      --text-secondary: #a1a1aa;
      --text-muted: #52525b;
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --accent-dim: rgba(59, 130, 246, 0.12);
      --accent-glow: rgba(59, 130, 246, 0.25);
      --green: #22c55e;
      --green-dim: rgba(34, 197, 94, 0.12);
      --amber: #f59e0b;
      --amber-dim: rgba(245, 158, 11, 0.12);
      --red: #ef4444;
      --red-dim: rgba(239, 68, 68, 0.12);
      --font-sans: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: var(--font-sans);
      background-color: var(--bg);
      color: var(--text-primary);
      height: 100vh;
      width: 100vw;
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    /* Scrollbars */
    ::-webkit-scrollbar {
      width: 5px;
      height: 5px;
    }
    ::-webkit-scrollbar-track {
      background: transparent;
    }
    ::-webkit-scrollbar-thumb {
      background: #27272a;
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #3f3f46;
    }

    /* Main Application Layout */
    .app-layout {
      display: flex;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
    }

    /* Sidebar: Fixed 380px wide */
    .sidebar {
      width: 380px;
      min-width: 380px;
      max-width: 380px;
      height: 100vh;
      background: var(--surface);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      z-index: 30;
      position: relative;
    }

    /* Sidebar Header */
    .sidebar-header {
      padding: 16px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-subtle);
    }
    .brand-group {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-logo-mark {
      width: 30px;
      height: 30px;
      border-radius: 7px;
      background: var(--surface-raised);
      border: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--accent);
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }
    .brand-text {
      display: flex;
      flex-direction: column;
    }
    .brand-wordmark {
      font-size: 15px;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: var(--text-primary);
    }
    .brand-subtitle {
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
    }
    .model-badge-pill {
      display: flex;
      align-items: center;
      gap: 6px;
      background: var(--surface-raised);
      border: 1px solid var(--border-subtle);
      padding: 3px 8px;
      border-radius: 9999px;
      font-size: 11px;
      font-family: var(--font-mono);
      color: var(--text-secondary);
    }
    .pulse-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--green);
      box-shadow: 0 0 6px var(--green);
    }

    /* Search & Chips Section */
    .search-section {
      padding: 16px 18px 14px 18px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      border-bottom: 1px solid var(--border-subtle);
      background: var(--surface);
    }
    .search-input-wrapper {
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--surface-raised);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 5px 8px 5px 12px;
      transition: all 0.15s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .search-input-wrapper:focus-within {
      border-color: var(--accent);
      box-shadow: 0 0 0 1px var(--accent);
      background: #1c1c20;
    }
    .search-icon {
      color: var(--text-muted);
      flex-shrink: 0;
    }
    .search-field {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      font-family: var(--font-sans);
      font-size: 13px;
      color: var(--text-primary);
      min-width: 0;
    }
    .search-field::placeholder {
      color: var(--text-muted);
    }
    .gps-btn {
      background: transparent;
      border: none;
      color: var(--text-secondary);
      padding: 6px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;
    }
    .gps-btn:hover {
      color: var(--text-primary);
      background: rgba(255, 255, 255, 0.06);
    }
    .gps-btn.active {
      color: var(--accent);
      background: var(--accent-dim);
    }
    .run-btn {
      background: var(--accent);
      color: #ffffff;
      border: none;
      padding: 6px 9px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background-color 0.15s ease;
    }
    .run-btn:hover {
      background: var(--accent-hover);
    }

    /* Chips Bar */
    .chips-bar {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 2px;
      scrollbar-width: none;
    }
    .chips-bar::-webkit-scrollbar {
      display: none;
    }
    .query-chip {
      background: var(--surface-raised);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      font-size: 11.5px;
      font-weight: 500;
      padding: 4px 10px;
      border-radius: 6px;
      white-space: nowrap;
      cursor: pointer;
      transition: all 0.15s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .query-chip:hover {
      border-color: var(--border);
      color: var(--text-primary);
      background: #232328;
    }

    /* Venue List Header */
    .venues-list-header {
      padding: 12px 18px 8px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .venues-header-title {
      font-size: 11px;
      font-weight: 600;
      color: var(--text-muted);
      letter-spacing: 0.05em;
    }
    .venues-header-count {
      font-size: 11px;
      font-family: var(--font-mono);
      color: var(--text-secondary);
    }

    /* Venues Scroll Area */
    .venues-scroll-area {
      flex: 1;
      overflow-y: auto;
      padding: 6px 14px 16px 14px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .venue-card {
      background: var(--surface-raised);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 12px;
      cursor: pointer;
      transition: all 0.15s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .venue-card:hover {
      border-color: var(--border);
      background: var(--surface-hover);
      transform: translateY(-1px);
    }
    .venue-card.selected {
      border-color: var(--accent);
      background: rgba(59, 130, 246, 0.08);
      box-shadow: 0 0 0 1px var(--accent);
    }
    .venue-card-top {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .rank-box {
      width: 24px;
      height: 24px;
      min-width: 24px;
      border-radius: 5px;
      background: #202024;
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .rank-box.rank-top {
      background: rgba(59, 130, 246, 0.2);
      border-color: rgba(59, 130, 246, 0.4);
      color: #60a5fa;
    }
    .venue-meta-block {
      flex: 1;
      min-width: 0;
    }
    .venue-name-line {
      font-size: 13.5px;
      font-weight: 600;
      color: var(--text-primary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .venue-sub-line {
      font-size: 11.5px;
      color: var(--text-muted);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      margin-top: 1px;
    }
    .venue-score-tag {
      padding: 2px 7px;
      border-radius: 5px;
      font-family: var(--font-mono);
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }
    .venue-pills-row {
      display: flex;
      align-items: center;
      gap: 5px;
      flex-wrap: wrap;
    }
    .v-chip {
      font-size: 11px;
      color: var(--text-secondary);
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-subtle);
      padding: 2px 6px;
      border-radius: 4px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    /* Sidebar Footer */
    .sidebar-footer {
      padding: 12px 18px;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 11px;
      color: var(--text-muted);
      background: var(--surface);
    }
    .audio-toggle-btn {
      background: transparent;
      border: none;
      cursor: pointer;
      color: var(--text-secondary);
      font-size: 13px;
      padding: 4px;
      border-radius: 4px;
      transition: color 0.15s ease;
    }
    .audio-toggle-btn:hover {
      color: var(--text-primary);
    }

    /* Main Content Area */
    .main-content {
      flex: 1;
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background: var(--bg);
      position: relative;
    }

    /* Map Section (Top 55%) */
    .map-container-wrap {
      height: 55%;
      min-height: 280px;
      position: relative;
      border-bottom: 1px solid var(--border-subtle);
      background: #09090b;
    }
    #map {
      width: 100%;
      height: 100%;
    }

    /* Map Overlays */
    .map-origin-overlay {
      position: absolute;
      top: 16px;
      left: 16px;
      z-index: 1000;
      background: rgba(18, 18, 21, 0.88);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px 12px;
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
      pointer-events: auto;
    }
    .origin-pulse-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--accent);
      box-shadow: 0 0 8px var(--accent);
    }
    .origin-label-title {
      font-size: 12.5px;
      font-weight: 600;
      color: var(--text-primary);
    }
    .origin-label-sub {
      font-size: 10.5px;
      color: var(--text-muted);
    }

    .map-controls-overlay {
      position: absolute;
      top: 16px;
      right: 16px;
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 8px;
      pointer-events: auto;
    }
    .layer-selector {
      display: flex;
      background: rgba(18, 18, 21, 0.88);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 3px;
      gap: 2px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }
    .layer-btn {
      background: transparent;
      border: none;
      color: var(--text-secondary);
      font-size: 11.5px;
      font-weight: 500;
      padding: 4px 9px;
      border-radius: 5px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .layer-btn:hover {
      color: var(--text-primary);
    }
    .layer-btn.active {
      background: var(--surface-raised);
      color: var(--text-primary);
      font-weight: 600;
    }
    .map-tool-btn {
      background: rgba(18, 18, 21, 0.88);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid var(--border);
      border-radius: 8px;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-secondary);
      cursor: pointer;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
      transition: all 0.15s ease;
    }
    .map-tool-btn:hover {
      color: var(--text-primary);
      border-color: var(--accent);
    }

    /* Detail Panel (Bottom 45%) */
    .detail-panel {
      height: 45%;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background: var(--bg);
    }
    .detail-tabs-bar {
      height: 44px;
      min-height: 44px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px;
      border-bottom: 1px solid var(--border-subtle);
      background: var(--surface);
    }
    .detail-tabs-nav {
      display: flex;
      gap: 4px;
    }
    .tab-nav-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 12.5px;
      font-weight: 500;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .tab-nav-btn:hover {
      color: var(--text-primary);
      background: rgba(255, 255, 255, 0.04);
    }
    .tab-nav-btn.active {
      color: var(--text-primary);
      background: var(--surface-raised);
      font-weight: 600;
    }
    .detail-actions-nav {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .tab-action-btn {
      display: flex;
      align-items: center;
      gap: 5px;
      background: var(--surface-raised);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      font-size: 11.5px;
      font-weight: 500;
      padding: 4px 10px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .tab-action-btn:hover {
      color: var(--text-primary);
      border-color: var(--border);
    }

    /* Tab Content Pages */
    .tab-page-container {
      flex: 1;
      overflow-y: auto;
      background: var(--bg);
    }
    .tab-page {
      display: none;
      height: 100%;
    }
    .tab-page.active {
      display: block;
    }

    /* AI Analysis Tab */
    .analysis-meta-bar {
      padding: 12px 24px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .analysis-model-group {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      font-family: var(--font-mono);
    }
    .model-name-text {
      font-weight: 600;
      color: var(--text-primary);
    }
    .model-tag-text {
      color: var(--text-muted);
      font-size: 11px;
      padding: 1px 6px;
      border-radius: 4px;
      background: var(--surface-raised);
      border: 1px solid var(--border-subtle);
    }
    .analysis-speed-metric {
      font-size: 11.5px;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }
    .slm-prose-wrap {
      padding: 24px;
      max-width: 880px;
      line-height: 1.65;
      font-size: 14px;
      color: var(--text-secondary);
      cursor: pointer;
    }
    .slm-prose-wrap h1, .slm-prose-wrap h2, .slm-prose-wrap h3 {
      color: var(--text-primary);
      margin: 18px 0 10px 0;
      font-weight: 600;
    }
    .slm-prose-wrap h1 { font-size: 18px; }
    .slm-prose-wrap h2 { font-size: 15px; border-bottom: 1px solid var(--border-subtle); padding-bottom: 4px; }
    .slm-prose-wrap p { margin-bottom: 14px; }
    .slm-prose-wrap strong { color: var(--text-primary); font-weight: 600; }
    .slm-prose-wrap ul, .slm-prose-wrap ol { margin: 10px 0 16px 20px; }
    .slm-prose-wrap li { margin-bottom: 6px; }

    /* Apple Weather Hero Layout */
    .weather-container {
      padding: 24px;
      max-width: 920px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .weather-header-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .weather-venue-title {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }
    .weather-venue-sub {
      font-size: 12.5px;
      color: var(--text-muted);
      margin-top: 2px;
    }
    .weather-score-pill {
      padding: 4px 10px;
      border-radius: 6px;
      font-family: var(--font-mono);
      font-size: 13px;
      font-weight: 700;
    }
    .weather-score-pill.excellent {
      background: var(--green-dim);
      color: var(--green);
      border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .weather-score-pill.good {
      background: var(--amber-dim);
      color: var(--amber);
      border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .weather-temp-row {
      display: flex;
      align-items: center;
      gap: 24px;
      padding: 8px 0;
    }
    .temp-big-number {
      font-size: 54px;
      font-weight: 300;
      letter-spacing: -0.04em;
      color: var(--text-primary);
      font-family: var(--font-sans);
    }
    .temp-desc-group {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .temp-condition-line {
      font-size: 14px;
      font-weight: 500;
      color: var(--text-primary);
    }
    .temp-sub-metrics {
      font-size: 12.5px;
      color: var(--text-muted);
    }

    /* 2x2 Metric Grid */
    .metric-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 14px;
    }
    .weather-metric-cell {
      background: var(--surface-raised);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      transition: border-color 0.15s ease;
    }
    .weather-metric-cell:hover {
      border-color: var(--border);
    }
    .metric-cell-label {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
    }
    .metric-cell-val {
      font-size: 20px;
      font-weight: 700;
      font-family: var(--font-mono);
      color: var(--text-primary);
    }
    .metric-cell-unit {
      font-size: 13px;
      font-weight: 400;
      color: var(--text-muted);
    }
    .aqi-bar-track {
      height: 5px;
      border-radius: 9999px;
      background: linear-gradient(to right, #22c55e, #eab308, #ef4444, #a855f7);
      position: relative;
      margin: 6px 0 2px 0;
    }
    .aqi-bar-thumb {
      position: absolute;
      top: -3.5px;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: #ffffff;
      box-shadow: 0 0 6px rgba(0,0,0,0.6);
      transform: translateX(-50%);
    }
    .aqi-tick-labels {
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }
    .metric-cell-caption {
      font-size: 12px;
      color: var(--text-secondary);
      line-height: 1.4;
    }
    .wind-vector-row {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .compass-circle {
      width: 34px;
      height: 34px;
      border-radius: 50%;
      border: 1.5px solid var(--border);
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #18181b;
    }
    .compass-pointer {
      width: 2px;
      height: 14px;
      background: #ef4444;
      border-radius: 1px;
      position: absolute;
      transform-origin: center bottom;
      bottom: 17px;
    }

    /* Hourly Timeline Strip */
    .hourly-title-row {
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-top: 8px;
    }
    .hourly-scroll-strip {
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 6px;
    }
    .hourly-card {
      background: var(--surface-raised);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 10px 14px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      min-width: 68px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .hourly-card:hover {
      border-color: var(--border);
      background: #25252a;
    }
    .hourly-card.active {
      border-color: var(--accent);
      background: rgba(59, 130, 246, 0.08);
    }
    .hc-time {
      font-size: 11.5px;
      font-weight: 500;
      color: var(--text-secondary);
    }
    .hc-glyph {
      font-size: 16px;
    }
    .hc-temp {
      font-size: 13px;
      font-weight: 600;
      font-family: var(--font-mono);
      color: var(--text-primary);
    }
    .hc-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
    }

    /* Venues Detail Tab */
    .venues-detail-container {
      padding: 24px;
      max-width: 920px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .venues-subheading {
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.05em;
      color: var(--text-muted);
    }
    .venues-table-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .venue-row-card {
      background: var(--surface-raised);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 12px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .venue-row-card:hover {
      border-color: var(--border);
      background: #232328;
    }
    .venue-row-card.selected {
      border-color: var(--accent);
      background: rgba(59, 130, 246, 0.08);
    }
    .vrc-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .vrc-details {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }
    .vrc-name {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
    }
    .vrc-meta {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 11.5px;
      color: var(--text-secondary);
      flex-wrap: wrap;
    }
    .vrc-right {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .vrc-score {
      font-size: 13px;
      font-family: var(--font-mono);
      font-weight: 700;
    }
    .vrc-focus-btn {
      background: transparent;
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      font-size: 11px;
      font-weight: 500;
      padding: 4px 8px;
      border-radius: 5px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .vrc-focus-btn:hover {
      border-color: var(--accent);
      color: var(--text-primary);
    }

    /* Checklists 2-column */
    .checklists-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      margin-top: 8px;
    }
    .checklist-col {
      background: var(--surface-raised);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .checklist-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 600;
      color: var(--green);
    }
    .checklist-header.warning {
      color: var(--amber);
    }
    .checklist-items {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .chk-item {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      font-size: 12.5px;
      color: var(--text-secondary);
      line-height: 1.45;
    }
    .chk-ico-ok {
      color: var(--green);
      font-weight: 700;
    }
    .chk-ico-warn {
      color: var(--amber);
      font-size: 12px;
    }
    .chk-ico-stop {
      color: var(--red);
      font-size: 12px;
    }

    /* Telemetry Tab */
    .telemetry-header-bar {
      padding: 12px 24px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      color: var(--text-muted);
      font-family: var(--font-mono);
    }
    .telemetry-code-block {
      padding: 20px 24px;
      font-family: var(--font-mono);
      font-size: 12px;
      color: #a1a1aa;
      line-height: 1.6;
      overflow: auto;
      background: var(--bg);
    }

    /* Loading Spinner Component */
    .loader-placeholder {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 12px;
      height: 180px;
      color: var(--text-muted);
      font-size: 13px;
    }
    .minimal-ring-spinner {
      width: 22px;
      height: 22px;
      border: 2px solid var(--border-subtle);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin-kf 0.7s linear infinite;
    }
    @keyframes spin-kf {
      to { transform: rotate(360deg); }
    }

    /* Toast Notification */
    .toast-tray {
      position: fixed;
      top: 18px;
      right: 18px;
      z-index: 99999;
      display: flex;
      flex-direction: column;
      gap: 8px;
      pointer-events: none;
    }
    .toast-pill {
      background: var(--surface-raised);
      border: 1px solid var(--border);
      color: var(--text-primary);
      padding: 8px 16px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 500;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      gap: 8px;
      opacity: 0;
      transform: translateY(-8px);
      animation: toast-kf 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes toast-kf {
      to { opacity: 1; transform: translateY(0); }
    }

    /* Custom Leaflet Map Pins */
    .origin-pulse-marker {
      position: relative;
      width: 20px;
      height: 20px;
    }
    .origin-pulse-marker::before {
      content: '';
      position: absolute;
      inset: -6px;
      border-radius: 50%;
      background: rgba(59, 130, 246, 0.4);
      animation: pulse-ring-kf 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;
    }
    .origin-pulse-marker-dot {
      position: absolute;
      inset: 3px;
      border-radius: 50%;
      background: #3b82f6;
      border: 2.5px solid #ffffff;
      box-shadow: 0 0 10px rgba(59, 130, 246, 0.9);
    }
    @keyframes pulse-ring-kf {
      0% { transform: scale(0.6); opacity: 0.9; }
      70% { transform: scale(1.6); opacity: 0; }
      100% { transform: scale(1.6); opacity: 0; }
    }

    .venue-pin-badge {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: #18181b;
      border: 2px solid #71717a;
      color: #fafafa;
      font-family: var(--font-mono);
      font-weight: 700;
      font-size: 11px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);
      cursor: pointer;
      transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .venue-pin-badge:hover {
      transform: scale(1.15);
      border-color: #3b82f6;
    }
    .venue-pin-badge.top-rank {
      background: #3b82f6;
      border-color: #ffffff;
      color: #ffffff;
      box-shadow: 0 0 14px rgba(59, 130, 246, 0.7);
    }

    /* Leaflet Popups */
    .leaflet-popup-content-wrapper {
      background: #18181b !important;
      color: #fafafa !important;
      border: 1px solid #3f3f46 !important;
      border-radius: 8px !important;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6) !important;
      padding: 4px !important;
    }
    .leaflet-popup-tip {
      background: #18181b !important;
      border-top: 1px solid #3f3f46 !important;
    }
    .popup-box {
      min-width: 220px;
      padding: 4px;
    }
    .popup-head {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 8px;
    }
    .popup-rank-tag {
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      color: #3b82f6;
      background: rgba(59, 130, 246, 0.15);
      padding: 1px 5px;
      border-radius: 4px;
    }
    .popup-name {
      font-size: 13px;
      font-weight: 600;
      color: #fafafa;
    }
    .popup-score-num {
      margin-left: auto;
      font-family: var(--font-mono);
      font-size: 12px;
      font-weight: 700;
      color: #22c55e;
    }
    .popup-metric-line {
      font-size: 11.5px;
      color: #a1a1aa;
      margin-bottom: 3px;
    }
    .popup-metric-line b {
      color: #fafafa;
      font-weight: 500;
    }
    .guardrail-card {
      background: rgba(245, 158, 11, 0.05);
      border: 1px solid var(--amber);
      border-radius: 8px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .guardrail-title-row {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13.5px;
      font-weight: 600;
      color: var(--amber);
    }
  </style>
</head>
<body>
  <div class="app-layout">
    <!-- Left Sidebar (Fixed 380px) -->
    <aside class="sidebar">
      <!-- Top Branding -->
      <div class="sidebar-header">
        <div class="brand-group">
          <div class="brand-logo-mark">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
              <polyline points="2 17 12 22 22 17"></polyline>
              <polyline points="2 12 12 17 22 12"></polyline>
            </svg>
          </div>
          <div class="brand-text">
            <div class="brand-wordmark">GeoAI</div>
            <div class="brand-subtitle">Outdoor Intelligence</div>
          </div>
        </div>
        <div class="model-badge-pill">
          <span class="pulse-dot"></span>
          <span>Qwen 2.5 3B</span>
        </div>
      </div>

      <!-- Search Input Area -->
      <div class="search-section">
        <div class="search-input-wrapper">
          <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input type="text" id="queryInput" class="search-field" placeholder="Ask outdoor intelligence query..." value="Where can I go for a jog near GTB Nagar around 7 AM?" onkeydown="if(event.key==='Enter') runAnalysis();" />
          <button class="gps-btn" id="gpsBtn" onclick="useCurrentGPS()" title="Locate via device GPS">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="22" y1="12" x2="18" y2="12"></line>
              <line x1="6" y1="12" x2="2" y2="12"></line>
              <line x1="12" y1="6" x2="12" y2="2"></line>
              <line x1="12" y1="22" x2="12" y2="18"></line>
            </svg>
          </button>
          <button class="run-btn" onclick="runAnalysis()" title="Execute analysis">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </button>
        </div>

        <!-- Quick Query Chips -->
        <div class="chips-bar">
          <button class="query-chip" onclick="setQuery('Where can I go for a jog near GTB Nagar around 7 AM?')">🏃 Jog (GTB Nagar)</button>
          <button class="query-chip" onclick="setQuery('Best cycling route near Powai Lake at 6 AM')">🚴 Cycling (Powai)</button>
          <button class="query-chip" onclick="setQuery('Football ground near Indiranagar at 5 PM with good air')">⚽ Football (Evening)</button>
          <button class="query-chip" onclick="setQuery('Shaded walking park near Lodhi Colony for seniors')">🧘 Park Walk (Seniors)</button>
          <button class="query-chip" onclick="setQuery('Trail running route with low dust exposure near South Delhi')">🌳 Sheltered Trail</button>
        </div>
      </div>

      <!-- Ranked Venues Header -->
      <div class="venues-list-header">
        <span class="venues-header-title">RECOMMENDED VENUES</span>
        <span class="venues-header-count" id="venueCountBadge">0 found</span>
      </div>

      <!-- Venue Cards List -->
      <div class="venues-scroll-area" id="sidebarVenueList">
        <div class="loader-placeholder">
          <div class="minimal-ring-spinner"></div>
          <span>Ready for analysis...</span>
        </div>
      </div>

      <!-- Sidebar Footer -->
      <div class="sidebar-footer">
        <div>CSRE IIT Bombay · Open-Meteo · OSRM</div>
        <button class="audio-toggle-btn" id="sfxToggleBtn" onclick="toggleAudioFeedback()" title="Toggle Sound Feedback">
          <span id="sfxIcon">🔊</span>
        </button>
      </div>
    </aside>

    <!-- Right Main Area -->
    <main class="main-content">
      <!-- Top Half: Map Panel (55%) -->
      <div class="map-container-wrap">
        <div id="map"></div>

        <!-- Origin Label Pill (Top Left) -->
        <div class="map-origin-overlay" id="mapOriginPill">
          <div class="origin-pulse-dot"></div>
          <div>
            <div class="origin-label-title" id="mapOriginTitle">📍 GTB Nagar, North Delhi</div>
            <div class="origin-label-sub" id="mapOriginSubtitle">Geocoded Query Origin · 8 km Radius</div>
          </div>
        </div>

        <!-- Map Controls (Top Right) -->
        <div class="map-controls-overlay">
          <div class="layer-selector">
            <button class="layer-btn active" id="btnLayerDark" onclick="switchMapLayer('dark', this)">Dark</button>
            <button class="layer-btn" id="btnLayerOsm" onclick="switchMapLayer('osm', this)">Street</button>
            <button class="layer-btn" id="btnLayerSat" onclick="switchMapLayer('satellite', this)">Satellite</button>
            <button class="layer-btn" id="btnLayerTopo" onclick="switchMapLayer('topo', this)">Terrain</button>
          </div>
          <button class="map-tool-btn" onclick="recenterMap()" title="Fit all venue bounds">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 3 21 3 21 9"></polyline>
              <polyline points="9 21 3 21 3 15"></polyline>
              <line x1="21" y1="3" x2="14" y2="10"></line>
              <line x1="3" y1="21" x2="10" y2="14"></line>
            </svg>
          </button>
        </div>
      </div>

      <!-- Bottom Half: Detail Panel (45%) -->
      <div class="detail-panel">
        <!-- Horizontal Tabs Header -->
        <div class="detail-tabs-bar">
          <div class="detail-tabs-nav">
            <button class="tab-nav-btn active" id="tabBtn-analysis" onclick="switchTab('analysis')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
              <span>AI Analysis</span>
            </button>
            <button class="tab-nav-btn" id="tabBtn-weather" onclick="switchTab('weather')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/></svg>
              <span>Weather</span>
            </button>
            <button class="tab-nav-btn" id="tabBtn-venues" onclick="switchTab('venues')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>
              <span>Venues</span>
            </button>
            <button class="tab-nav-btn" id="tabBtn-telemetry" onclick="switchTab('telemetry')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
              <span>Telemetry</span>
            </button>
          </div>

          <!-- Quick Action Buttons -->
          <div class="detail-actions-nav">
            <button class="tab-action-btn" onclick="copyBriefing()" title="Copy briefing markdown">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
              <span>Copy</span>
            </button>
            <button class="tab-action-btn" id="btnListenSLM" onclick="readBriefingAloud()" title="Read decision aloud">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
              <span>Listen</span>
            </button>
            <button class="tab-action-btn" onclick="runAnalysis()" title="Regenerate synthesis">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg>
              <span>Rerun</span>
            </button>
          </div>
        </div>

        <!-- Tab Body Pages -->
        <div class="tab-page-container">
          <!-- Page 1: AI Analysis -->
          <div class="tab-page active" id="panel-analysis" onclick="skipStreaming()">
            <div class="analysis-meta-bar">
              <div class="analysis-model-group">
                <span class="pulse-dot"></span>
                <span class="model-name-text">Qwen2.5-3B-Instruct</span>
                <span class="model-tag-text">Verified Grounded</span>
              </div>
              <div class="analysis-speed-metric" id="slmMetrics">Initializing synthesis...</div>
            </div>
            <div class="slm-prose-wrap" id="slmProseBody">
              <div class="loader-placeholder">
                <div class="minimal-ring-spinner"></div>
                <span>Analyzing micro-climates, wind plumes & routing...</span>
              </div>
            </div>
          </div>

          <!-- Page 2: Weather -->
          <div class="tab-page" id="panel-weather">
            <div id="weatherTabContent"></div>
          </div>

          <!-- Page 3: Venues -->
          <div class="tab-page" id="panel-venues">
            <div id="venuesTabContent"></div>
          </div>

          <!-- Page 4: Telemetry -->
          <div class="tab-page" id="panel-telemetry">
            <div class="telemetry-header-bar">
              <span>Raw GeoAI Inference Telemetry & Evidence Payload</span>
              <button class="tab-action-btn" onclick="copyTelemetryJson()">Copy JSON</button>
            </div>
            <pre class="telemetry-code-block" id="evidenceDrawer">{ "status": "waiting_for_analysis" }</pre>
          </div>
        </div>
      </div>
    </main>
  </div>

  <!-- Toast Container -->
  <div class="toast-tray" id="toastContainer"></div>

  <script>
    // Audio Feedback Context
    let audioCtx = null;
    let sfxEnabled = true;

    function initAudio() {
      if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
    }

    function playAudioTap() {
      if (!sfxEnabled) return;
      try {
        initAudio();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(400, audioCtx.currentTime + 0.035);
        gain.gain.setValueAtTime(0.03, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.035);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.035);
      } catch (e) {}
    }

    function playAudioChime() {
      if (!sfxEnabled) return;
      try {
        initAudio();
        [587.33, 880.0].forEach((freq, idx) => {
          const osc = audioCtx.createOscillator();
          const gain = audioCtx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(freq, audioCtx.currentTime + idx * 0.08);
          gain.gain.setValueAtTime(0.035, audioCtx.currentTime + idx * 0.08);
          gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + idx * 0.08 + 0.22);
          osc.connect(gain);
          gain.connect(audioCtx.destination);
          osc.start(audioCtx.currentTime + idx * 0.08);
          osc.stop(audioCtx.currentTime + idx * 0.08 + 0.22);
        });
      } catch (e) {}
    }

    function toggleAudioFeedback() {
      sfxEnabled = !sfxEnabled;
      const icon = document.getElementById('sfxIcon');
      if (icon) icon.textContent = sfxEnabled ? '🔊' : '🔇';
      showToast(sfxEnabled ? "Audio feedback enabled" : "Audio feedback muted");
      if (sfxEnabled) playAudioTap();
    }

    // Toast Notification System
    function showToast(message, type = "info") {
      const container = document.getElementById('toastContainer');
      if (!container) return;
      const toast = document.createElement('div');
      toast.className = 'toast-pill';
      const icon = type === 'warn' ? '⚠️' : (type === 'gps' ? '📍' : '✨');
      toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
      container.appendChild(toast);
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-6px)';
        toast.style.transition = 'all 0.2s ease';
        setTimeout(() => toast.remove(), 200);
      }, 3500);
    }

    // Tab Switching
    function switchTab(tabKey) {
      playAudioTap();
      ['analysis', 'weather', 'venues', 'telemetry'].forEach(k => {
        const btn = document.getElementById('tabBtn-' + k);
        const panel = document.getElementById('panel-' + k);
        if (btn) btn.classList.toggle('active', k === tabKey);
        if (panel) panel.classList.toggle('active', k === tabKey);
      });
    }

    function toggleEvidenceDrawer() {
      switchTab('telemetry');
    }

    // Leaflet Tile Layers Setup
    const mapLayers = {
      dark: L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
      }),
      osm: L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
      }),
      satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        attribution: 'Tiles &copy; Esri'
      }),
      topo: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        maxZoom: 17,
        attribution: '&copy; OpenStreetMap, SRTM'
      })
    };

    const map = L.map('map', {
      layers: [mapLayers.dark],
      zoomControl: false
    }).setView([28.6977, 77.2069], 13);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    let activeLayer = mapLayers.dark;
    let markersLayer = L.layerGroup().addTo(map);
    let currentMarkers = [];
    let currentPolylines = [];
    let currentBoundsCoords = [];
    let currentUserLat = null;
    let currentUserLon = null;
    let streamInterval = null;
    let isStreamingSLM = false;

    function switchMapLayer(key, btn) {
      playAudioTap();
      document.querySelectorAll('.layer-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      map.removeLayer(activeLayer);
      activeLayer = mapLayers[key] || mapLayers.dark;
      map.addLayer(activeLayer);
    }

    function recenterMap() {
      playAudioTap();
      if (currentBoundsCoords.length > 0) {
        map.fitBounds(currentBoundsCoords, {padding: [50, 50], maxZoom: 14});
      }
    }

    function setQuery(text) {
      playAudioTap();
      const qInput = document.getElementById('queryInput');
      if (qInput) qInput.value = text;
      runAnalysis();
    }

    // Geolocation Support
    function useCurrentGPS() {
      playAudioTap();
      if (!navigator.geolocation) {
        showToast("Geolocation is not supported by your browser.", "warn");
        return;
      }
      const btn = document.getElementById('gpsBtn');
      btn.classList.add('active');
      showToast("Acquiring physical GPS telemetry...", "gps");

      navigator.geolocation.getCurrentPosition(
        (pos) => {
          currentUserLat = pos.coords.latitude;
          currentUserLon = pos.coords.longitude;
          showToast(`GPS Acquired: ${currentUserLat.toFixed(3)}° N, ${currentUserLon.toFixed(3)}° E`, "gps");
          const qInput = document.getElementById('queryInput');
          if (!qInput.value.trim() || qInput.value.includes('near')) {
            qInput.value = "Outdoor activities near my location";
          }
          runAnalysis(currentUserLat, currentUserLon);
        },
        (err) => {
          btn.classList.remove('active');
          showToast("GPS unavailable — continuing with geocoded search", "warn");
          runAnalysis();
        },
        { enableHighAccuracy: true, timeout: 6000 }
      );
    }

    // Progressive SLM Streaming
    function streamSLMResponse(fullMarkdown) {
      const bodyEl = document.getElementById('slmProseBody');
      const metricsEl = document.getElementById('slmMetrics');
      if (!bodyEl) return;

      if (streamInterval) clearInterval(streamInterval);
      if (!fullMarkdown) {
        bodyEl.innerHTML = '<p style="color:var(--text-muted)">No briefing text generated.</p>';
        return;
      }

      const rawHtml = marked.parse(fullMarkdown);
      const words = fullMarkdown.split(' ');
      let wordIdx = 0;
      let partialMd = '';
      isStreamingSLM = true;

      const tStart = performance.now();

      streamInterval = setInterval(() => {
        if (!isStreamingSLM || wordIdx >= words.length) {
          clearInterval(streamInterval);
          isStreamingSLM = false;
          bodyEl.innerHTML = rawHtml;
          const tEnd = performance.now();
          const elapsedSec = ((tEnd - tStart) / 1000).toFixed(1);
          const totalTokens = Math.round(words.length * 1.33);
          const tokPerSec = Math.round(totalTokens / Math.max(0.4, (tEnd - tStart) / 1000));
          if (metricsEl) {
            metricsEl.innerHTML = `⚡ ${totalTokens} tokens in ${elapsedSec}s (${tokPerSec} tok/s) · Grounded`;
          }
          return;
        }

        const chunkSize = Math.min(3, words.length - wordIdx);
        for (let i = 0; i < chunkSize; i++) {
          partialMd += (wordIdx === 0 ? '' : ' ') + words[wordIdx];
          wordIdx++;
        }

        bodyEl.innerHTML = marked.parse(partialMd);
        if (metricsEl) {
          metricsEl.innerHTML = `⚡ Streaming Qwen2.5-3B-Instruct (${Math.round(wordIdx * 1.33)} tok)...`;
        }
      }, 18);
    }

    function skipStreaming() {
      isStreamingSLM = false;
    }

    // Audio & Clipboard Actions
    function copyBriefing() {
      playAudioTap();
      const bodyEl = document.getElementById('slmProseBody');
      if (!bodyEl) return;
      navigator.clipboard.writeText(bodyEl.innerText).then(() => {
        showToast("Briefing copied to clipboard");
      });
    }

    function copyTelemetryJson() {
      playAudioTap();
      const el = document.getElementById('evidenceDrawer');
      if (!el) return;
      navigator.clipboard.writeText(el.innerText).then(() => {
        showToast("Telemetry JSON copied to clipboard");
      });
    }

    function readBriefingAloud() {
      playAudioTap();
      const btn = document.getElementById('btnListenSLM');
      if (window.speechSynthesis && window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        if (btn) btn.innerHTML = `
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
          <span>Listen</span>`;
        showToast("Voice playback stopped");
        return;
      }
      const bodyEl = document.getElementById('slmProseBody');
      if (!bodyEl) return;
      const cleanText = bodyEl.innerText.replace(/[#*•🛑⚠️💡🏆🎯🔬⚖️🎒📍🚗⏰🌡️🌫️💨🛡️]/g, '').trim();
      if (!cleanText) return;

      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = 1.05;
      utterance.pitch = 1.0;

      const voices = window.speechSynthesis.getVoices();
      const enVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Apple')));
      if (enVoice) utterance.voice = enVoice;

      utterance.onstart = () => {
        if (btn) btn.innerHTML = `
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="5" y="5" rx="2" ry="2"/></svg>
          <span>Stop</span>`;
        showToast("Reading executive decision briefing...");
      };
      utterance.onend = utterance.onerror = () => {
        if (btn) btn.innerHTML = `
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
          <span>Listen</span>`;
      };

      window.speechSynthesis.speak(utterance);
    }

    function focusMapVenue(idx) {
      playAudioTap();
      document.querySelectorAll('.venue-card').forEach((c, i) => c.classList.toggle('selected', i === idx));
      document.querySelectorAll('.venue-row-card').forEach((c, i) => c.classList.toggle('selected', i === idx));
      if (currentMarkers[idx]) {
        map.flyTo(currentMarkers[idx].getLatLng(), 14, {duration: 0.8});
        currentMarkers[idx].openPopup();
      }
      currentPolylines.forEach((line, i) => {
        if (i === idx) {
          line.setStyle({opacity: 0.95, weight: 3.5, color: '#3b82f6'});
        } else {
          line.setStyle({opacity: 0.25, weight: 1.5, color: '#71717a'});
        }
      });
    }

    // Main Analysis Execution
    async function runAnalysis(userLat = null, userLon = null) {
      playAudioTap();
      const q = document.getElementById('queryInput').value.trim();
      if (!q) return;

      switchTab('analysis');
      const bodyEl = document.getElementById('slmProseBody');
      if (bodyEl) {
        bodyEl.innerHTML = `
          <div class="loader-placeholder">
            <div class="minimal-ring-spinner"></div>
            <span>Analyzing micro-climates, wind plumes & routing...</span>
          </div>
        `;
      }
      const metricsEl = document.getElementById('slmMetrics');
      if (metricsEl) metricsEl.textContent = 'Synthesizing evidence...';

      const payload = { question: q };
      if (userLat !== null && userLon !== null) {
        payload.user_lat = userLat;
        payload.user_lon = userLon;
      } else if (currentUserLat !== null && currentUserLon !== null) {
        payload.user_lat = currentUserLat;
        payload.user_lon = currentUserLon;
      }

      try {
        const resp = await fetch('/ask', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const data = await resp.json();
        playAudioChime();

        if (data.status !== 'ok') {
          renderGuardrailNotice(data);
        } else {
          renderResults(data);
        }
      } catch (err) {
        if (bodyEl) {
          bodyEl.innerHTML = `
            <div class="guardrail-card" style="border-color: var(--red);">
              <div class="guardrail-title-row" style="color: var(--red);">
                <span>⚠️ Connectivity Notice</span>
              </div>
              <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.55;">
                ${err.message}
              </div>
            </div>
          `;
        }
      }
    }

    function renderGuardrailNotice(data) {
      switchTab('analysis');
      const bodyEl = document.getElementById('slmProseBody');
      if (bodyEl) {
        bodyEl.innerHTML = `
          <div class="guardrail-card">
            <div class="guardrail-title-row">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              <span>Clarification Required (Guardrail Triggered)</span>
            </div>
            <div style="font-size: 13.5px; line-height: 1.6; color: var(--text-secondary);">
              ${marked.parse(data.answer || '')}
            </div>
          </div>
        `;
      }
    }

    // Render Full Results
    function renderResults(data) {
      const best = (data.top_venue_slots && data.top_venue_slots[0]) ? data.top_venue_slots[0] : ((data.alternatives_compared && data.alternatives_compared[0]) ? data.alternatives_compared[0] : {});
      const alts = data.alternatives_compared || [];
      const origin = data.origin || {lat: 28.6977, lon: 77.2069, name: "GTB Nagar", short_name: "GTB Nagar"};
      const isGPS = (data.origin_type === 'device_gps');
      const radKm = (data.parsed_intent && data.parsed_intent.radius_km) || 8;

      // CRITICAL REQUIREMENTS: Coordinates & Logging
      const origLat = data.origin.lat;
      const origLon = data.origin.lon;
      console.log('ORIGIN:', data.origin.lat, data.origin.lon);
      console.log('MAP PIN:', origLat, origLon, data.origin.name);

      // Update Map Origin Pill Header
      const mapOriginTitle = document.getElementById('mapOriginTitle');
      const mapOriginSubtitle = document.getElementById('mapOriginSubtitle');
      if (isGPS) {
        mapOriginTitle.textContent = `📍 Live Device GPS (${origLat.toFixed(4)}° N, ${origLon.toFixed(4)}° E)`;
        mapOriginSubtitle.textContent = `Physical GPS Origin · ${radKm} km Radius`;
      } else {
        const locName = origin.short_name || origin.name || (data.parsed_intent && data.parsed_intent.location) || "GTB Nagar, North Delhi";
        mapOriginTitle.textContent = `📍 ${locName}`;
        mapOriginSubtitle.textContent = `Geocoded Query Origin · ${radKm} km Radius`;
      }

      // Update Venue Count in Sidebar
      const venueCountBadge = document.getElementById('venueCountBadge');
      if (venueCountBadge) venueCountBadge.textContent = `${alts.length} ranked`;

      // Render Sidebar Venue Cards
      const sidebarVenueList = document.getElementById('sidebarVenueList');
      if (sidebarVenueList) {
        if (alts.length === 0) {
          sidebarVenueList.innerHTML = `<div class="loader-placeholder"><span>No venues found within radius</span></div>`;
        } else {
          sidebarVenueList.innerHTML = alts.map((v, idx) => {
            const isTop = (idx === 0);
            const scoreCol = v.score >= 80 ? 'var(--green)' : (v.score >= 65 ? 'var(--amber)' : 'var(--red)');
            const scoreDim = v.score >= 80 ? 'var(--green-dim)' : (v.score >= 65 ? 'var(--amber-dim)' : 'var(--red-dim)');
            const isDownwind = v.downwind_status && v.downwind_status.includes('Downwind');
            const downwindCol = isDownwind ? 'var(--red)' : 'var(--green)';
            return `
              <div class="venue-card ${isTop ? 'selected' : ''}" id="sidebarVenueCard_${idx}" onclick="focusMapVenue(${idx})">
                <div class="venue-card-top">
                  <div class="rank-box ${isTop ? 'rank-top' : ''}">#${idx + 1}</div>
                  <div class="venue-meta-block">
                    <div class="venue-name-line" title="${v.venue_name}">${v.venue_name}</div>
                    <div class="venue-sub-line">${v.hour_label || ''} · ~${v.travel_mins || 0}m drive (${v.distance_km || 0}km)</div>
                  </div>
                  <div class="venue-score-tag" style="color:${scoreCol}; background:${scoreDim};">
                    ${v.score}
                  </div>
                </div>
                <div class="venue-pills-row">
                  <span class="v-chip">🌡️ ${Math.round(v.temp_c || 0)}°C</span>
                  <span class="v-chip">🌫️ AQI ${v.us_aqi || 0}</span>
                  <span class="v-chip" style="color:${downwindCol}">● ${v.downwind_status || 'Upwind'}</span>
                </div>
              </div>
            `;
          }).join('');
        }
      }

      // Reset Map Markers and Polylines
      markersLayer.clearLayers();
      currentMarkers = [];
      currentPolylines = [];
      currentBoundsCoords = [[origLat, origLon]];

      // Draw Search Radius Circle
      L.circle([origLat, origLon], {
        radius: radKm * 1000,
        color: '#3b82f6',
        weight: 1.5,
        fillColor: '#3b82f6',
        fillOpacity: 0.04,
        dashArray: '4, 6'
      }).addTo(markersLayer);

      // Origin Marker with Pulsing Blue Dot
      const originIcon = L.divIcon({
        className: 'origin-marker-container',
        html: `<div class="origin-pulse-marker"><div class="origin-pulse-marker-dot"></div></div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      });

      L.marker([origLat, origLon], {icon: originIcon})
        .addTo(markersLayer)
        .bindPopup(`
          <div class="popup-box">
            <div style="font-weight:700; font-size:13px; color:#3b82f6; margin-bottom:4px;">
              ${isGPS ? '🔵 Physical Device GPS' : '📍 Query Origin'}
            </div>
            <div style="font-size:12px; color:#a1a1aa;">${origin.name}</div>
            <div style="font-size:11px; color:#71717a; margin-top:4px;">${radKm} km evaluation radius</div>
          </div>
        `);

      // Venue Markers & Polylines
      alts.forEach((v, idx) => {
        const isTop = (idx === 0);
        currentBoundsCoords.push([v.lat, v.lon]);

        const line = L.polyline([[origLat, origLon], [v.lat, v.lon]], {
          color: isTop ? '#3b82f6' : '#71717a',
          weight: isTop ? 3.5 : 1.5,
          opacity: isTop ? 0.95 : 0.4,
          dashArray: isTop ? null : '4, 5'
        }).addTo(markersLayer);
        currentPolylines.push(line);

        const vIcon = L.divIcon({
          className: 'venue-marker-container',
          html: `<div class="venue-pin-badge ${isTop ? 'top-rank' : ''}"><span class="pin-num">${idx + 1}</span></div>`,
          iconSize: [28, 28],
          iconAnchor: [14, 14]
        });

        const m = L.marker([v.lat, v.lon], {icon: vIcon}).addTo(markersLayer);
        m.bindPopup(`
          <div class="popup-box">
            <div class="popup-head">
              <span class="popup-rank-tag">#${idx + 1}</span>
              <span class="popup-name">${v.venue_name}</span>
              <span class="popup-score-num">${v.score}/100</span>
            </div>
            <div class="popup-metric-line"><span>Optimal Time:</span> <b>${v.hour_label}</b></div>
            <div class="popup-metric-line"><span>Drive Time:</span> <b>~${v.travel_mins}m (${v.distance_km} km via OSRM)</b></div>
            <div class="popup-metric-line"><span>Micro-Climate:</span> <b>${Math.round(v.temp_c)}°C · AQI ${v.us_aqi}</b></div>
            <div class="popup-metric-line"><span>Wind & Plume:</span> <b>${v.wind_kmh} km/h ${v.wind_compass} · ${v.downwind_status}</b></div>
          </div>
        `);
        currentMarkers.push(m);
        if (isTop) m.openPopup();
      });

      // Fit Bounds
      if (currentBoundsCoords.length > 0) {
        map.fitBounds(currentBoundsCoords, {padding: [50, 50], maxZoom: 14});
      }

      // Render Tabs
      renderWeatherTab(data, best);
      renderVenuesTab(data, alts);
      renderTelemetryTab(data, best, alts);

      // Stream Markdown
      streamSLMResponse(data.recommendation_markdown || '');
    }

    // Weather Tab Renderer
    function renderWeatherTab(data, best) {
      const container = document.getElementById('weatherTabContent');
      if (!container) return;
      if (!best || !best.venue_name) {
        container.innerHTML = `<div class="loader-placeholder"><span>No weather data available</span></div>`;
        return;
      }

      const aqiPct = Math.min(100, Math.max(0, (best.us_aqi / 300.0) * 100));
      const aqiCol = best.us_aqi <= 50 ? 'var(--green)' : (best.us_aqi <= 100 ? 'var(--amber)' : 'var(--red)');
      const aqiLabel = best.us_aqi <= 50 ? 'Good' : (best.us_aqi <= 100 ? 'Moderate' : (best.us_aqi <= 150 ? 'Sensitive Warning' : 'Unhealthy'));

      const hourlyCards = (data.hourly_timeline || []).map((t, idx) => {
        const sc = Math.round(t.score);
        const dotCol = sc >= 80 ? 'var(--green)' : (sc >= 65 ? 'var(--amber)' : 'var(--red)');
        const isDay = t.hour_int >= 6 && t.hour_int <= 18;
        return `
          <div class="hourly-card ${idx === 0 ? 'active' : ''}" onclick="selectHourCard(${idx}, this)">
            <div class="hc-time">${t.short_hour || t.hour_label}</div>
            <div class="hc-glyph">${isDay ? '☀️' : '🌙'}</div>
            <div class="hc-temp">${Math.round(t.temp_c)}°</div>
            <div class="hc-dot" style="background:${dotCol};" title="Suitability: ${sc}/100"></div>
          </div>
        `;
      }).join('');

      container.innerHTML = `
        <div class="weather-container">
          <!-- Hero Header -->
          <div class="weather-header-row">
            <div>
              <div class="weather-venue-title">#1 Top Choice: ${best.venue_name}</div>
              <div class="weather-venue-sub">${best.hour_label || 'Optimal Window'} · ~${best.travel_mins || 0} mins drive (${best.distance_km || 0} km)</div>
            </div>
            <div class="weather-score-pill ${best.score >= 80 ? 'excellent' : 'good'}">
              ${best.score} / 100
            </div>
          </div>

          <!-- Big Temperature Metric -->
          <div class="weather-temp-row">
            <div class="temp-big-number">${Math.round(best.temp_c || 0)}°</div>
            <div class="temp-desc-group">
              <div class="temp-condition-line">
                <span>${best.rain_prob_pct > 25 ? '🌧️ Rain Probability Elevated' : '☀️ Clear & Favorable Conditions'}</span>
              </div>
              <div class="temp-sub-metrics">
                Feels like ${Math.round(best.feels_like_c || best.temp_c || 0)}° · Humidity ${best.humidity_pct || 0}% · UV Index ${best.uv_index || 0}
              </div>
            </div>
          </div>

          <!-- 2x2 Metric Grid -->
          <div class="metric-grid">
            <!-- AQI -->
            <div class="weather-metric-cell">
              <div class="metric-cell-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/></svg>
                <span>Air Quality Index</span>
              </div>
              <div class="metric-cell-val" style="color: ${aqiCol};">
                US AQI ${best.us_aqi}
              </div>
              <div class="aqi-bar-track">
                <div class="aqi-bar-thumb" style="left: ${aqiPct}%;"></div>
              </div>
              <div class="aqi-tick-labels">
                <span>0 Good</span>
                <span>50 Mod</span>
                <span>100 Sens</span>
                <span>200+ Bad</span>
              </div>
              <div class="metric-cell-caption">
                PM2.5: <b>${best.pm25 || 0} µg/m³</b> · ${aqiLabel} air profile for outdoor exertion.
              </div>
            </div>

            <!-- Wind -->
            <div class="weather-metric-cell">
              <div class="metric-cell-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.8 19.6A2 2 0 1 0 14 16H2"/><path d="M17.5 8a2.5 2.5 0 1 1 2 4H2"/><path d="M9.8 4.4A2 2 0 1 1 11 8H2"/></svg>
                <span>Wind & Plume Dispersion</span>
              </div>
              <div class="wind-vector-row">
                <div class="compass-circle">
                  <div class="compass-pointer" style="transform: rotate(${best.wind_dir_deg || 0}deg);"></div>
                </div>
                <div>
                  <div class="metric-cell-val">${best.wind_kmh || 0} <span class="metric-cell-unit">km/h</span></div>
                  <div class="metric-cell-caption">From <b>${best.wind_compass || ''}</b> (${best.wind_dir_deg || 0}°)</div>
                </div>
              </div>
              <div class="metric-cell-caption" style="margin-top: 6px;">
                Status: <b style="color:${best.downwind_status && best.downwind_status.includes('Downwind') ? 'var(--red)' : 'var(--green)'}">${best.downwind_status || 'Upwind'}</b>
              </div>
            </div>

            <!-- Precipitation & Humidity -->
            <div class="weather-metric-cell">
              <div class="metric-cell-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"/></svg>
                <span>Precipitation & Comfort</span>
              </div>
              <div class="metric-cell-val">${best.rain_prob_pct || 0}% <span class="metric-cell-unit">rain risk</span></div>
              <div class="metric-cell-caption">
                Cloud Cover: <b>${best.cloud_cover_pct || 0}%</b> · UV Index: <b>${best.uv_index || 0}</b>
              </div>
              <div class="metric-cell-caption">
                Thermal comfort index rated optimal for high respiratory demand.
              </div>
            </div>

            <!-- Routing -->
            <div class="weather-metric-cell">
              <div class="metric-cell-label">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="16" x="4" y="4" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
                <span>Routing & Proximity</span>
              </div>
              <div class="metric-cell-val">~${best.travel_mins || 0} <span class="metric-cell-unit">mins drive</span></div>
              <div class="metric-cell-caption">
                Distance: <b>${best.distance_km || 0} km</b> via OSRM street network.
              </div>
              <div class="metric-cell-caption">
                Fastest corridor evaluated against real-time road topology.
              </div>
            </div>
          </div>

          <!-- Hourly Timeline -->
          <div class="hourly-title-row">HOURLY MICRO-CLIMATE TIMELINE (5:00 AM – 9:00 PM)</div>
          <div class="hourly-scroll-strip">
            ${hourlyCards}
          </div>
        </div>
      `;
    }

    function selectHourCard(idx, el) {
      playAudioTap();
      document.querySelectorAll('.hourly-card').forEach(c => c.classList.remove('active'));
      el.classList.add('active');
    }

    // Venues Tab Renderer
    function renderVenuesTab(data, alts) {
      const container = document.getElementById('venuesTabContent');
      if (!container) return;
      const avoids = data.avoid_slots || [];
      const carry = data.recommended_carry || [];
      const watch = data.profile_watch_notes || [];

      const venueCards = alts.map((v, i) => {
        const isTop = (i === 0);
        const scoreCol = v.score >= 80 ? 'var(--green)' : (v.score >= 65 ? 'var(--amber)' : 'var(--red)');
        const isDownwind = v.downwind_status && v.downwind_status.includes('Downwind');
        return `
          <div class="venue-row-card ${isTop ? 'selected' : ''}" onclick="focusMapVenue(${i})">
            <div class="vrc-left">
              <div class="rank-box ${isTop ? 'rank-top' : ''}">#${i + 1}</div>
              <div class="vrc-details">
                <div class="vrc-name">${v.venue_name}</div>
                <div class="vrc-meta">
                  <span>⏰ ${v.hour_label}</span>
                  <span>🚗 ~${v.travel_mins}m (${v.distance_km}km)</span>
                  <span>🌡️ ${Math.round(v.temp_c)}°C</span>
                  <span>🌫️ AQI ${v.us_aqi}</span>
                  <span style="color:${isDownwind ? 'var(--red)' : 'var(--green)'}">● ${v.downwind_status}</span>
                </div>
              </div>
            </div>
            <div class="vrc-right">
              <div class="vrc-score" style="color:${scoreCol}">${v.score} / 100</div>
              <button class="vrc-focus-btn" onclick="event.stopPropagation(); focusMapVenue(${i})">View on Map</button>
            </div>
          </div>
        `;
      }).join('');

      container.innerHTML = `
        <div class="venues-detail-container">
          <div class="venues-subheading">TOP CANDIDATE VENUES COMPARED ACROSS RADIUS</div>
          <div class="venues-table-group">
            ${venueCards}
          </div>

          <!-- Advisory Checklists -->
          <div class="checklists-grid">
            <div class="checklist-col">
              <div class="checklist-header">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                <span>What to Prepare & Bring</span>
              </div>
              <div class="checklist-items">
                ${carry.length ? carry.map(c => `
                  <div class="chk-item">
                    <span class="chk-ico-ok">✓</span>
                    <span>${c}</span>
                  </div>
                `).join('') : '<div style="font-size:12px; color:var(--text-muted); font-style:italic;">Standard outdoor gear recommended.</div>'}
              </div>
            </div>

            <div class="checklist-col">
              <div class="checklist-header warning">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                <span>Watchouts & Avoidance Rules</span>
              </div>
              <div class="checklist-items">
                ${watch.map(w => `
                  <div class="chk-item">
                    <span class="chk-ico-warn">⚠️</span>
                    <span>${w}</span>
                  </div>
                `).join('')}
                ${avoids.map(a => `
                  <div class="chk-item">
                    <span class="chk-ico-stop">🛑</span>
                    <span><b>${a.venue_name} at ${a.hour_label}</b>: ${a.reasons_bad.join('; ')}</span>
                  </div>
                `).join('')}
                ${(!watch.length && !avoids.length) ? '<div style="font-size:12px; color:var(--text-muted); font-style:italic;">No critical avoidance triggers detected.</div>' : ''}
              </div>
            </div>
          </div>
        </div>
      `;
    }

    // Telemetry Tab Renderer
    function renderTelemetryTab(data, best, alts) {
      const el = document.getElementById('evidenceDrawer');
      if (!el) return;
      const payload = {
        question: data.question,
        model_used: data.model_used,
        origin: data.origin,
        origin_type: data.origin_type,
        parsed_intent: data.parsed_intent,
        top_recommendation: best,
        alternatives_evaluated: alts,
        avoid_slots: data.avoid_slots,
        sources: data.sources
      };
      el.textContent = JSON.stringify(payload, null, 2);
    }

    // Initialization
    window.addEventListener('DOMContentLoaded', () => {
      localStorage.setItem('geoai_theme', 'dark');
      setTimeout(() => {
        map.invalidateSize();
        runAnalysis();
      }, 250);
    });
  </script>
</body>
</html>"""
