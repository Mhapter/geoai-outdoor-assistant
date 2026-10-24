"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Search,
  MapPin,
  SlidersHorizontal,
  Loader2,
  ChevronDown,
  ChevronUp,
  X,
  CheckCircle2,
  Navigation
} from "lucide-react";
import { ActivityInfo } from "@/types";

interface PlaceSuggestion {
  name: string;
  description: string;
  lat: number;
  lon: number;
  full_name?: string;
  type?: string;
}

interface QueryFormProps {
  activities: ActivityInfo[];
  onSubmit: (params: {
    question?: string;
    activity?: string;
    location?: string;
    radius_km?: number;
    user_lat?: number;
    user_lon?: number;
    date_window?: string;
    time_window?: string;
    personal_profiles?: string[];
  }) => void;
  isLoading: boolean;
}

const POPULAR_QUERIES = [
  "Running near Koregaon Park",
  "Cricket match within 15 km of Whitefield",
  "Swimming tomorrow near Noida Stadium",
  "Morning walk near Powai (mild asthma)",
  "Cycling to work at 8 AM near Bennett University",
  "Sunset photos around Bandra",
  "Weekend hike near Lonavala"
];

const QUICK_ACTIVITIES = [
  { id: "running", label: "Running", icon: "🏃" },
  { id: "cycling", label: "Cycling", icon: "🚴" },
  { id: "tennis", label: "Tennis", icon: "🎾" },
  { id: "cricket", label: "Cricket", icon: "🏏" },
  { id: "football", label: "Football", icon: "⚽" },
  { id: "swimming", label: "Swimming", icon: "🏊" },
  { id: "golf", label: "Golf", icon: "⛳" },
  { id: "hiking", label: "Hiking", icon: "🥾" },
  { id: "picnic", label: "Picnic", icon: "🧺" },
  { id: "photography", label: "Photography", icon: "📸" },
];

export const detectActivityFromText = (text: string): string | null => {
  const t = text.toLowerCase();
  if (t.includes("swim") || t.includes("pool") || t.includes("aquatic")) return "swimming";
  if (t.includes("cricket")) return "cricket";
  if (t.includes("football") || t.includes("soccer") || t.includes("turf")) return "football";
  if (t.includes("tennis")) return "tennis";
  if (t.includes("golf")) return "golf";
  if (t.includes("cycl") || t.includes("bike") || t.includes("bicycle")) return "cycling";
  if (t.includes("hike") || t.includes("trek") || t.includes("nature walk")) return "hiking";
  if (t.includes("picnic") || t.includes("outing")) return "picnic";
  if (t.includes("photo") || t.includes("sunset") || t.includes("golden hour")) return "photography";
  if (t.includes("jog") || t.includes("run") || t.includes("marathon")) return "running";
  if (t.includes("event") || t.includes("gathering") || t.includes("meetup")) return "event";
  return null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const QueryForm: React.FC<QueryFormProps> = ({
  onSubmit,
  isLoading
}) => {
  const [question, setQuestion] = useState("");
  const [selectedActivity, setSelectedActivity] = useState<string>("running");
  const [showFilters, setShowFilters] = useState<boolean>(false);
  const [location, setLocation] = useState<string>("");
  const [radiusKm, setRadiusKm] = useState<number>(10);
  const [timeWindow, setTimeWindow] = useState<string>("morning");
  const [selectedProfiles, setSelectedProfiles] = useState<string[]>([]);
  const [gpsLoading, setGpsLoading] = useState<boolean>(false);
  const [gpsCoords, setGpsCoords] = useState<{ lat: number; lon: number } | null>(null);

  // Google Suggest-style location autocomplete states
  const [locationInput, setLocationInput] = useState<string>("");
  const [suggestions, setSuggestions] = useState<PlaceSuggestion[]>([]);
  const [isSuggesting, setIsSuggesting] = useState<boolean>(false);
  const [showSuggestDropdown, setShowSuggestDropdown] = useState<boolean>(false);
  const [verifiedPlace, setVerifiedPlace] = useState<PlaceSuggestion | null>(null);
  const suggestTimerRef = useRef<NodeJS.Timeout | null>(null);
  const dropdownRef = useRef<HTMLDivElement | null>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowSuggestDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  const fetchPlaceSuggestions = async (term: string) => {
    const clean = term.trim();
    if (!clean || clean.length < 2) {
      setSuggestions([]);
      setShowSuggestDropdown(false);
      return;
    }
    setIsSuggesting(true);
    try {
      const res = await fetch(`${API_BASE}/api/locations/autocomplete?q=${encodeURIComponent(clean)}`);
      if (res.ok) {
        const data = await res.json();
        const list: PlaceSuggestion[] = data.suggestions || [];
        setSuggestions(list);
        setShowSuggestDropdown(list.length > 0);
      } else {
        // Fallback to legacy places autocomplete
        const fallbackRes = await fetch(`${API_BASE}/api/places/autocomplete?q=${encodeURIComponent(clean)}`);
        if (fallbackRes.ok) {
          const fbData = await fallbackRes.json();
          setSuggestions(fbData.suggestions || []);
          setShowSuggestDropdown((fbData.suggestions || []).length > 0);
        }
      }
    } catch {
      // ignore network errors
    } finally {
      setIsSuggesting(false);
    }
  };

  const handleLocationChange = (val: string) => {
    setLocationInput(val);
    setLocation(val);

    // Check if input is GPS coordinates: "lat, lon"
    const coordMatch = val.match(/^([+-]?\d{1,2}(?:\.\d+)?)\s*,\s*([+-]?\d{1,3}(?:\.\d+)?)$/);
    if (coordMatch) {
      const lat = parseFloat(coordMatch[1]);
      const lon = parseFloat(coordMatch[2]);
      if (lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
        setGpsCoords({ lat, lon });
        setVerifiedPlace({
          name: `GPS: ${lat.toFixed(4)}°, ${lon.toFixed(4)}°`,
          description: "Geographic coordinates input",
          lat,
          lon,
          type: "coordinates"
        });
        setShowSuggestDropdown(false);
        return;
      }
    }

    if (suggestTimerRef.current) clearTimeout(suggestTimerRef.current);
    suggestTimerRef.current = setTimeout(() => {
      fetchPlaceSuggestions(val);
    }, 200);
  };

  const handleSelectSuggestion = (place: PlaceSuggestion) => {
    setVerifiedPlace(place);
    setLocation(place.name);
    setLocationInput(place.name);
    setGpsCoords({ lat: place.lat, lon: place.lon });
    setShowSuggestDropdown(false);

    // If a question or activity is chosen, trigger search with verified coords
    onSubmit({
      question: question.trim() ? question : undefined,
      activity: selectedActivity,
      location: place.name,
      user_lat: place.lat,
      user_lon: place.lon,
      radius_km: radiusKm,
      date_window: "today",
      time_window: timeWindow,
      personal_profiles: selectedProfiles
    });
  };

  const handleClearLocation = () => {
    setVerifiedPlace(null);
    setGpsCoords(null);
    setLocation("");
    setLocationInput("");
  };

  const handleQuestionChange = (val: string) => {
    setQuestion(val);
    const detected = detectActivityFromText(val);
    if (detected) {
      setSelectedActivity(detected);
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const detected = question.trim() ? detectActivityFromText(question) : null;
    const finalActivity = detected || selectedActivity;
    if (detected && detected !== selectedActivity) {
      setSelectedActivity(detected);
    }
    onSubmit({
      question: question.trim() ? question : undefined,
      activity: finalActivity,
      location: location.trim() ? location : undefined,
      radius_km: radiusKm,
      user_lat: gpsCoords?.lat,
      user_lon: gpsCoords?.lon,
      date_window: "today",
      time_window: timeWindow,
      personal_profiles: selectedProfiles
    });
  };

  const handleSelectPopular = (q: string) => {
    setQuestion(q);
    const detected = detectActivityFromText(q);
    const act = detected || selectedActivity;
    if (detected) {
      setSelectedActivity(detected);
    }
    onSubmit({ question: q, activity: act });
  };

  const handleSelectActivity = (actId: string) => {
    setSelectedActivity(actId);
    if (question.trim()) {
      onSubmit({ question, activity: actId });
    }
  };

  const handleUseGps = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      return;
    }
    setGpsLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setGpsLoading(false);
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        setGpsCoords({ lat, lon });
        setVerifiedPlace({
          name: "My GPS Device Location",
          description: `${lat.toFixed(4)}° N, ${lon.toFixed(4)}° E (Browser Device Telemetry)`,
          lat,
          lon,
          type: "device_gps"
        });
        setLocation(`My Device GPS (${lat.toFixed(4)}, ${lon.toFixed(4)})`);
        setLocationInput(`My Device GPS (${lat.toFixed(4)}, ${lon.toFixed(4)})`);
        onSubmit({
          question: question.trim() || undefined,
          activity: selectedActivity,
          user_lat: lat,
          user_lon: lon,
          radius_km: radiusKm
        });
      },
      (err) => {
        setGpsLoading(false);
        alert(`Could not acquire GPS: ${err.message}. Please type an area name.`);
      },
      { timeout: 10000, enableHighAccuracy: true }
    );
  };

  const toggleProfile = (p: string) => {
    setSelectedProfiles((prev) =>
      prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]
    );
  };

  return (
    <div className="bg-white rounded-2xl border border-[#e5e0d8] p-4 lg:p-6 shadow-xs space-y-4">
      {/* 1. Main Search Bar */}
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row items-center gap-2">
        <div className="relative flex-1 w-full">
          <Search className="w-5 h-5 text-[#829288] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={question}
            onChange={(e) => handleQuestionChange(e.target.value)}
            placeholder="Ask where & when to go (e.g. 'Morning jog near Powai', 'Cricket in Whitefield')..."
            className="w-full pl-11 pr-24 py-3 bg-[#faf8f5] hover:bg-white focus:bg-white border border-[#e5e0d8] focus:border-[#264331] rounded-xl text-sm text-[#15221b] placeholder-[#829288] focus:outline-none transition-all shadow-inner"
          />
          <button
            type="button"
            onClick={handleUseGps}
            title="Use current GPS"
            className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-semibold px-2.5 py-1.5 rounded-lg bg-white border border-[#e5e0d8] text-[#335942] hover:bg-[#f2f6f3] flex items-center gap-1 transition-colors"
          >
            {gpsLoading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <MapPin className="w-3.5 h-3.5 text-amber-600" />
            )}
            <span className="hidden sm:inline">GPS</span>
          </button>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className={`px-3.5 py-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors cursor-pointer w-1/3 sm:w-auto ${
              showFilters
                ? "bg-[#1b2f22] text-[#faf8f5] border-[#1b2f22]"
                : "bg-[#faf8f5] text-[#57685e] border-[#e5e0d8] hover:bg-white"
            }`}
          >
            <SlidersHorizontal className="w-4 h-4" />
            <span>Filters</span>
            {showFilters ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          <button
            type="submit"
            disabled={isLoading}
            className="flex-1 sm:flex-initial px-6 py-3 rounded-xl bg-[#1b2f22] hover:bg-[#264331] text-[#faf8f5] font-semibold text-sm transition-all shadow-sm flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-[#81c784]" />
                <span>Checking...</span>
              </>
            ) : (
              <span>Find Best Place</span>
            )}
          </button>
        </div>
      </form>

      {/* Verified Location Banner (Google Suggest Target) */}
      {verifiedPlace && (
        <div className="flex items-center justify-between px-3.5 py-2 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-950 text-xs">
          <div className="flex items-center gap-2 min-w-0">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span className="font-bold">Verified Target:</span>
            <span className="font-semibold truncate">{verifiedPlace.name}</span>
            <span className="text-emerald-700 opacity-80 hidden sm:inline">
              ({verifiedPlace.description || `${verifiedPlace.lat.toFixed(4)}° N, ${verifiedPlace.lon.toFixed(4)}° E`})
            </span>
          </div>
          <button
            type="button"
            onClick={handleClearLocation}
            className="text-emerald-700 hover:text-emerald-900 p-1 rounded-md hover:bg-emerald-100 transition-colors cursor-pointer"
            title="Clear selected target"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* 2. Quick Activity Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
        <span className="text-xs font-semibold text-[#829288] shrink-0 mr-1">Activity:</span>
        {QUICK_ACTIVITIES.map((act) => {
          const isSelected = selectedActivity === act.id;
          return (
            <button
              key={act.id}
              type="button"
              onClick={() => handleSelectActivity(act.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold shrink-0 transition-all cursor-pointer ${
                isSelected
                  ? "bg-[#1b2f22] text-white shadow-2xs"
                  : "bg-[#faf8f5] text-[#57685e] hover:bg-white hover:text-[#15221b] border border-[#e5e0d8]"
              }`}
            >
              <span>{act.icon}</span>
              <span>{act.label}</span>
            </button>
          );
        })}
      </div>

      {/* 3. Quick Suggestions */}
      <div className="flex flex-wrap items-center gap-2 pt-1 text-xs text-[#57685e]">
        <span className="text-[#829288] font-medium">Try asking:</span>
        {POPULAR_QUERIES.slice(0, 4).map((q, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => handleSelectPopular(q)}
            className="px-2.5 py-1 rounded-lg bg-[#f2f6f3] text-[#264331] hover:bg-[#e4eee6] transition-colors cursor-pointer border border-[#dce5df]"
          >
            &ldquo;{q}&rdquo;
          </button>
        ))}
      </div>

      {/* 4. Collapsible Filters Drawer with Google Suggest Dropdown */}
      {showFilters && (
        <div className="pt-4 mt-2 border-t border-[#f2f6f3] space-y-4 text-xs">
          {/* Location Autocomplete Input */}
          <div className="relative" ref={dropdownRef}>
            <label className="font-semibold text-[#15221b] block mb-1 flex items-center justify-between">
              <span>📍 Location & Destination (Google Suggest):</span>
              {isSuggesting && (
                <span className="flex items-center gap-1 text-[11px] text-[#335942]">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  <span>Searching...</span>
                </span>
              )}
            </label>
            <div className="relative">
              <MapPin className="w-4 h-4 text-[#829288] absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                value={locationInput}
                onChange={(e) => handleLocationChange(e.target.value)}
                onFocus={() => { if (suggestions.length > 0) setShowSuggestDropdown(true); }}
                placeholder="Type city, area, or landmark (e.g. Noida, Whitefield, Powai)..."
                className="w-full pl-9 pr-8 py-2.5 rounded-xl bg-[#faf8f5] border border-[#e5e0d8] focus:border-[#264331] focus:bg-white text-[#15221b] text-xs outline-none transition-all shadow-2xs"
              />
              {locationInput && (
                <button
                  type="button"
                  onClick={handleClearLocation}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[#829288] hover:text-[#15221b] cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Google Suggest Autocomplete Dropdown */}
            {showSuggestDropdown && suggestions.length > 0 && (
              <div className="absolute left-0 right-0 top-full mt-1.5 bg-white rounded-xl border border-[#dce5df] shadow-2xl z-50 overflow-hidden divide-y divide-[#f2f6f3] max-h-64 overflow-y-auto">
                <div className="px-3.5 py-1.5 bg-[#f2f6f3] text-[10px] font-bold uppercase tracking-wider text-[#335942] flex items-center justify-between">
                  <span>Suggested Verified Places</span>
                  <span className="text-[9px] text-[#829288] font-normal">Click to lock GPS</span>
                </div>
                {suggestions.map((s, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectSuggestion(s)}
                    className="w-full px-3.5 py-2.5 text-left hover:bg-[#faf8f5] flex items-start gap-2.5 transition-colors cursor-pointer group"
                  >
                    <Navigation className="w-4 h-4 text-[#335942] shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
                    <div className="min-w-0 flex-1">
                      <div className="font-bold text-xs text-[#15221b] truncate group-hover:text-[#264331]">
                        {s.name}
                      </div>
                      <div className="text-[11px] text-[#829288] truncate">
                        {s.description}
                      </div>
                    </div>
                    <span className="text-[9px] font-semibold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 shrink-0">
                      Verified
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Radius */}
            <div>
              <label className="font-semibold text-[#15221b] block mb-1">
                Search Radius: <span className="text-[#335942]">{radiusKm} km</span>
              </label>
              <input
                type="range"
                min="2"
                max="35"
                step="1"
                value={radiusKm}
                onChange={(e) => setRadiusKm(Number(e.target.value))}
                className="w-full accent-[#1b2f22] cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-[#829288] mt-1">
                <span>2 km</span>
                <span>15 km</span>
                <span>35 km</span>
              </div>
            </div>

            {/* Time Window */}
            <div>
              <label className="font-semibold text-[#15221b] block mb-1">Preferred Time:</label>
              <select
                value={timeWindow}
                onChange={(e) => setTimeWindow(e.target.value)}
                className="w-full p-2.5 rounded-xl bg-[#faf8f5] border border-[#e5e0d8] text-[#15221b] focus:outline-none"
              >
                <option value="any">Any Time Today</option>
                <option value="morning">Morning (6 AM - 10 AM)</option>
                <option value="afternoon">Afternoon (12 PM - 4 PM)</option>
                <option value="evening">Evening (5 PM - 8 PM)</option>
                <option value="golden_hour">Golden Hour / Sunset</option>
              </select>
            </div>

            {/* Personal Considerations */}
            <div>
              <label className="font-semibold text-[#15221b] block mb-1">Personal Profiles:</label>
              <div className="flex flex-wrap gap-1.5">
                {[
                  { id: "asthma", label: "Mild Asthma" },
                  { id: "senior", label: "Senior Citizen" },
                  { id: "child", label: "Children / Family" },
                  { id: "pregnancy", label: "Pregnancy" }
                ].map((p) => {
                  const active = selectedProfiles.includes(p.id);
                  return (
                    <button
                      key={p.id}
                      type="button"
                      onClick={() => toggleProfile(p.id)}
                      className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-colors cursor-pointer border ${
                        active
                          ? "bg-amber-100 text-amber-900 border-amber-300"
                          : "bg-[#faf8f5] text-[#57685e] border-[#e5e0d8] hover:bg-white"
                      }`}
                    >
                      {active ? "✓ " : "+ "}{p.label}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
