"""
Data contracts and Pydantic schemas for Fieldwise Outdoor Intelligence Assistant.
"""

from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: Optional[str] = Field(None, description="Natural-language query, e.g., 'Jogging tomorrow morning in Greater Noida'")
    query: Optional[str] = Field(None, description="Alias for natural-language question")
    activity: Optional[str] = Field(None, description="Explicit activity key if selected directly")
    location: Optional[str] = Field(None, description="Explicit location name if entered directly")
    radius_km: Optional[float] = Field(10.0, ge=1.0, le=100.0, description="Search radius in kilometers")
    user_lat: Optional[float] = Field(None, description="User device latitude for GPS-based queries")
    user_lon: Optional[float] = Field(None, description="User device longitude for GPS-based queries")
    date_window: Optional[str] = Field(None, description="'today', 'tomorrow', 'weekend', 'saturday', 'sunday', or specific ISO date")
    time_window: Optional[str] = Field(None, description="'morning', 'afternoon', 'evening', 'night', 'golden_hour', or 'all_day'")
    personal_profiles: Optional[List[str]] = Field(default_factory=list, description="Personal constraints e.g. ['asthma', 'senior', 'child', 'pregnancy']")


class HealthResponse(BaseModel):
    status: str
    version: str
    app_name: str
    model_id: str
    model_loaded: bool
    parameters: str
    data_sources: Dict[str, str]
    attribution: str


class ActivityInfo(BaseModel):
    id: str
    label: str
    icon: str
    category: str
    description: str
    ideal_temp_c: Tuple[float, float]
    max_temp_c: float
    max_aqi: int
    max_wind_kmh: float
    max_rain_prob: float
    needs_daylight: bool
    carry_items: List[str]
    watch_notes: str


class CandidateVenue(BaseModel):
    name: str
    lat: float
    lon: float
    venue_type: str
    distance_km: float
    travel_mins: int
    tags: Optional[Dict[str, Any]] = None
    osm_id: Optional[str] = None


class HourlyCondition(BaseModel):
    hour_iso: str
    hour_label: str
    day_name: str
    day_date: str
    temp_c: float
    feels_like_c: float
    humidity_pct: int
    precip_prob_pct: int
    rain_mm: float
    wind_kmh: float
    wind_dir_deg: int
    wind_compass: str
    us_aqi: int
    pm25: float
    pm10: float
    uv_index: float
    cloud_cover_pct: int
    is_daylight: bool
    golden_hour: bool


class SlotScore(BaseModel):
    venue_name: str
    lat: float
    lon: float
    hour_iso: str
    hour_label: str
    day_name: str
    day_date: str
    score: int
    suitability_label: str
    temp_c: float
    feels_like_c: float
    rain_prob_pct: int
    rain_mm: float
    wind_kmh: float
    wind_compass: str
    us_aqi: int
    pm25: float
    pm10: float
    uv_index: float
    distance_km: float
    travel_mins: int
    straight_line_dist_km: float = 0.0
    route_dist_km: float = 0.0
    routing_provider: str = "OSRM"
    downwind_status: str
    reasons_good: List[str]
    reasons_bad: List[str]
    reasons_missing: List[str]
    images: List[Dict[str, Any]] = Field(default_factory=list)
    has_verified_photos: bool = False
    google_maps_url: Optional[str] = None
    verification_status: Optional[str] = "verified"
    verification_notes: List[str] = Field(default_factory=list)
    provider: Optional[str] = "osm"


class SourceProvenance(BaseModel):
    name: str
    type: str
    url: Optional[str] = None
    fetched_at: str
    attribution: str
    freshness: str
    details: str


class RecommendationResponse(BaseModel):
    status: str
    question: Optional[str] = None
    message: Optional[str] = None
    parsed_intent: Dict[str, Any]
    origin: Dict[str, Any]
    origin_type: str
    best_recommendation: Optional[SlotScore] = None
    alternative_venues: List[SlotScore] = []
    avoid_slots: List[SlotScore] = []
    hourly_timeline: List[HourlyCondition] = []
    recommended_carry: List[str] = []
    profile_watch_notes: List[str] = []
    recommendation_markdown: str
    model_used: str
    is_fallback: bool
    sources: List[SourceProvenance] = []
    warnings: List[str] = []
