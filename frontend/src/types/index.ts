export interface CandidateVenue {
  osm_id?: string;
  name: string;
  lat: float;
  lon: float;
  venue_type: string;
  distance_km: number;
  travel_mins?: number;
  tags?: Record<string, string | number | boolean | null | undefined>;
  env_context?: {
    green_cover_nearby: boolean;
    water_body_nearby: boolean;
    water_name?: string | null;
    major_road?: {
      name: string;
      dist_km: number;
      wind_from_hazard_deg: number;
      direction_from_venue: string;
    } | null;
    industry?: {
      name: string;
      dist_km: number;
      wind_from_hazard_deg: number;
      direction_from_venue: string;
    } | null;
  };
}

export type float = number;

export interface SlotScore {
  venue_name: string;
  lat: number;
  lon: number;
  hour_iso: string;
  hour_label: string;
  day_name: string;
  day_date: string;
  score: number;
  suitability_label: "Optimal" | "Good" | "Marginal" | "Avoid";
  temp_c: number;
  feels_like_c: number;
  rain_prob_pct: number;
  rain_mm: number;
  wind_kmh: number;
  wind_compass: string;
  us_aqi: number;
  pm25: number;
  pm10: number;
  uv_index: number;
  distance_km: number;
  travel_mins: number;
  straight_line_dist_km?: number;
  route_dist_km?: number;
  routing_provider?: string;
  has_verified_photos?: boolean;
  downwind_status: string;
  reasons_good: string[];
  reasons_bad: string[];
  reasons_missing: string[];
  images?: Array<{
    url: string;
    title?: string;
    source?: string;
    source_url?: string;
    attribution?: string;
    license?: string;
    geotagged?: boolean;
    distance_from_venue_m?: number;
    verified?: boolean;
  }>;
  google_maps_url?: string;
  verification_status?: "verified" | "unverified" | "discrepancy_detected" | "inconclusive";
  verification_notes?: string[];
  provider?: string;
}

export interface HourlyCondition {
  hour_iso: string;
  hour_label: string;
  day_name: string;
  day_date: string;
  temp_c: number;
  feels_like_c: number;
  humidity_pct: number;
  precip_prob_pct: number;
  rain_mm: number;
  wind_kmh: number;
  wind_dir_deg: number;
  wind_compass: string;
  us_aqi: number;
  pm25: number;
  pm10: number;
  uv_index: number;
  cloud_cover_pct: number;
  is_daylight: boolean;
  golden_hour: boolean;
}

export interface SourceProvenance {
  name: string;
  type: string;
  url?: string;
  fetched_at: string;
  attribution: string;
  freshness: string;
  details: string;
}

export interface RecommendationResponse {
  status: "ok" | "missing_location" | "location_not_found" | "no_venues" | "error";
  question?: string;
  message?: string;
  parsed_intent: {
    activity?: string;
    location?: string;
    radius_km?: number;
    target_hours?: number[] | null;
    time_window_label?: string;
    day_offset?: number;
    day_label?: string;
    personal_profiles?: string[];
    compare_mode?: string | null;
  };
  origin: {
    name: string;
    short_name: string;
    lat: number;
    lon: number;
    geocoder?: string;
  };
  origin_type: string;
  best_recommendation?: SlotScore | null;
  alternative_venues: SlotScore[];
  avoid_slots: SlotScore[];
  hourly_timeline: HourlyCondition[];
  recommended_carry: string[];
  profile_watch_notes: string[];
  recommendation_markdown: string;
  model_used: string;
  is_fallback: boolean;
  sources: SourceProvenance[];
  warnings: string[];
}

export interface ActivityInfo {
  id: string;
  label: string;
  icon: string;
  category: string;
  description: string;
  ideal_temp_c: [number, number];
  max_temp_c: number;
  max_aqi: number;
  max_wind_kmh: number;
  max_rain_prob: number;
  needs_daylight: boolean;
  carry_items: string[];
  watch_notes: string;
}

export interface HealthInfo {
  status: string;
  version: string;
  app_name: string;
  model_id: string;
  model_loaded: boolean;
  parameters: string;
  data_sources: Record<string, string>;
  attribution: string;
}
