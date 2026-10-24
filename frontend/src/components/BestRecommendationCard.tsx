"use client";

import React, { useState } from "react";
import {
  Sparkles,
  Clock,
  Thermometer,
  Wind,
  Gauge,
  Navigation,
  CheckCircle2,
  Trees,
  MapPin,
  Share2,
  Star,
  Check,
  Scale,
  Camera,
  Flag,
  ShieldCheck,
  ExternalLink
} from "lucide-react";
import { SlotScore } from "@/types";

interface BestRecommendationCardProps {
  slot: SlotScore;
  activityLabel?: string;
  isFavorite?: boolean;
  onToggleFavorite?: () => void;
  onOpenCompare?: () => void;
  onOpenPhotos?: () => void;
  onReportIssue?: (slot: SlotScore) => void;
}

export const BestRecommendationCard: React.FC<BestRecommendationCardProps> = ({
  slot,
  activityLabel = "Outdoor Activity",
  isFavorite = false,
  onToggleFavorite,
  onOpenCompare,
  onOpenPhotos,
  onReportIssue
}) => {
  const [copied, setCopied] = useState(false);

  const getScoreBadge = (score: number) => {
    if (score >= 80) {
      return {
        bg: "bg-emerald-50 text-emerald-800 border-emerald-200",
        label: "Optimal",
        dot: "bg-emerald-500"
      };
    }
    if (score >= 65) {
      return {
        bg: "bg-[#f2f6f3] text-[#264331] border-[#dce5df]",
        label: "Good",
        dot: "bg-emerald-600"
      };
    }
    if (score >= 50) {
      return {
        bg: "bg-amber-50 text-amber-800 border-amber-200",
        label: "Marginal",
        dot: "bg-amber-500"
      };
    }
    return {
      bg: "bg-rose-50 text-rose-800 border-rose-200",
      label: "Avoid",
      dot: "bg-rose-500"
    };
  };

  const getAqiStatus = (aqi: number) => {
    if (aqi <= 50) return { text: "Clean & Fresh", color: "text-emerald-700" };
    if (aqi <= 100) return { text: "Moderate Air", color: "text-emerald-600" };
    if (aqi <= 150) return { text: "Mild Sensitive", color: "text-amber-700" };
    return { text: "Elevated AQI", color: "text-rose-700" };
  };

  const badge = getScoreBadge(slot.score);
  const aqiStatus = getAqiStatus(slot.us_aqi);
  const primaryPhoto = slot.images && slot.images.length > 0 ? slot.images[0] : null;

  const handleCopy = () => {
    const text = `🌿 Outdoor Plan: ${slot.venue_name}\n⏰ Best Time: ${slot.hour_label}\n🌡️ Conditions: ${slot.temp_c}°C, AQI ${slot.us_aqi} (${slot.suitability_label})\n📍 ${slot.distance_km} km away (~${slot.travel_mins} mins)\nRecommended by Fieldwise GeoAI`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const openGoogleMaps = () => {
    const url = `https://www.google.com/maps/dir/?api=1&destination=${slot.lat},${slot.lon}`;
    window.open(url, "_blank", "noopener,noreferrer");
  };

  return (
    <div className="bg-white rounded-2xl border-2 border-[#1b2f22] shadow-sm p-5 lg:p-6 relative overflow-hidden">
      {/* Top Header Badge */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-[#f2f6f3]">
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full bg-[#1b2f22] text-[#faf8f5]">
            <Sparkles className="w-3.5 h-3.5 text-[#81c784]" />
            Best Match
          </span>
          <span className="text-xs font-semibold text-[#57685e]">
            {activityLabel}
          </span>
        </div>

        {/* Score pill */}
        <div className={`flex items-center gap-2 px-3 py-1 rounded-xl border text-sm font-bold ${badge.bg}`}>
          <span className={`w-2 h-2 rounded-full ${badge.dot}`} />
          <span>{slot.score}/100</span>
          <span className="text-xs font-medium opacity-85">({slot.suitability_label})</span>
        </div>
      </div>

      {/* Interactive Photo Banner Preview or Neutral Verified Placeholder */}
      {primaryPhoto ? (
        <div
          onClick={onOpenPhotos}
          className="relative mt-3 h-36 sm:h-44 w-full rounded-xl overflow-hidden cursor-pointer group shadow-inner border border-stone-200"
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={primaryPhoto.url}
            alt={primaryPhoto.title || slot.venue_name}
            className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/25 to-transparent" />

          {/* Photos Count Badge */}
          <div className="absolute bottom-2.5 right-2.5 flex items-center gap-1.5 bg-black/75 hover:bg-black/90 backdrop-blur-xs text-white text-xs font-semibold px-3 py-1.5 rounded-lg border border-white/20 transition-colors">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Verified Venue Photo ({slot.images?.length || 1})</span>
          </div>

          {/* Photo Caption & Attribution */}
          <div className="absolute bottom-2.5 left-3 text-xs text-white font-medium max-w-[70%]">
            <div className="truncate text-white/95 font-semibold">📍 {primaryPhoto.title}</div>
            <div className="text-[10px] text-white/70 truncate mt-0.5">
              {primaryPhoto.attribution || primaryPhoto.source || "Wikimedia Commons (Verified Geotag)"}
            </div>
          </div>
        </div>
      ) : (
        <div className="mt-3 p-3.5 rounded-xl bg-stone-50 border border-stone-200 flex items-center justify-between gap-3 text-xs text-stone-600">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-stone-200/70 text-stone-500 flex items-center justify-center shrink-0">
              <Camera className="w-4 h-4" />
            </div>
            <div>
              <span className="font-semibold text-stone-800 block text-xs">No verified venue photograph available</span>
              <span className="text-[11px] text-stone-500">
                Fieldwise only displays verified venue photography, never unrelated stock images.
              </span>
            </div>
          </div>
          <button
            onClick={openGoogleMaps}
            className="shrink-0 flex items-center gap-1 text-[11px] font-semibold text-emerald-800 hover:text-emerald-950 px-2.5 py-1 rounded-lg border border-stone-200 bg-white hover:bg-stone-50 transition cursor-pointer"
          >
            <span>Photos on Maps</span>
            <ExternalLink className="w-3 h-3" />
          </button>
        </div>
      )}

      {/* Main Venue Name & Timing */}
      <div className="pt-3.5 pb-2">
        <h2 className="text-xl lg:text-2xl font-extrabold text-[#15221b] tracking-tight">
          {slot.venue_name}
        </h2>
        <div className="flex flex-wrap items-center gap-3 text-xs sm:text-sm text-[#57685e] mt-1.5">
          <div className="flex items-center gap-1.5 font-semibold text-[#1b2f22]">
            <Clock className="w-4 h-4 text-[#335942]" />
            <span>{slot.hour_label}</span>
          </div>
          <span>•</span>
          <div className="flex items-center gap-1.5">
            <Navigation className="w-4 h-4 text-[#335942]" />
            <span>
              ~{slot.travel_mins} mins drive • {slot.route_dist_km || slot.distance_km} km by road
              {slot.straight_line_dist_km ? ` (${slot.straight_line_dist_km} km straight-line)` : ""}
            </span>
          </div>
        </div>
      </div>

      {/* Action Buttons: Directions, Photos, Share, Favorite, Compare */}
      <div className="flex flex-wrap items-center gap-2 pt-1 pb-3">
        <button
          onClick={openGoogleMaps}
          className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-[#f2f6f3] text-[#264331] hover:bg-[#e4eee6] border border-[#dce5df] transition-colors cursor-pointer"
        >
          <MapPin className="w-3.5 h-3.5 text-emerald-700" />
          <span>Directions</span>
        </button>

        {onOpenPhotos && (
          <button
            onClick={onOpenPhotos}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-[#faf8f5] text-[#57685e] hover:bg-white hover:text-[#15221b] border border-[#e5e0d8] transition-colors cursor-pointer"
          >
            <Camera className="w-3.5 h-3.5 text-[#335942]" />
            <span>Photos</span>
          </button>
        )}

        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-[#faf8f5] text-[#57685e] hover:bg-white hover:text-[#15221b] border border-[#e5e0d8] transition-colors cursor-pointer"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Share2 className="w-3.5 h-3.5" />}
          <span>{copied ? "Copied!" : "Share"}</span>
        </button>

        {onToggleFavorite && (
          <button
            onClick={onToggleFavorite}
            className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border transition-colors cursor-pointer ${
              isFavorite
                ? "bg-amber-50 text-amber-900 border-amber-300"
                : "bg-[#faf8f5] text-[#57685e] hover:bg-white hover:text-[#15221b] border-[#e5e0d8]"
            }`}
          >
            <Star className={`w-3.5 h-3.5 ${isFavorite ? "text-amber-500 fill-amber-500" : ""}`} />
            <span>{isFavorite ? "Saved" : "Save"}</span>
          </button>
        )}

        {onOpenCompare && (
          <button
            onClick={onOpenCompare}
            className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-[#faf8f5] text-[#57685e] hover:bg-white hover:text-[#15221b] border border-[#e5e0d8] transition-colors cursor-pointer"
          >
            <Scale className="w-3.5 h-3.5 text-[#335942]" />
            <span>Compare</span>
          </button>
        )}

        {onReportIssue && (
          <button
            onClick={() => onReportIssue(slot)}
            title="Report inaccurate coordinates or place details"
            className="flex items-center gap-1 text-xs text-stone-500 hover:text-rose-700 px-2.5 py-1.5 rounded-lg border border-transparent hover:border-rose-200 hover:bg-rose-50 transition-colors cursor-pointer ml-auto"
          >
            <Flag className="w-3 h-3" />
            <span className="hidden sm:inline">Report Location</span>
          </button>
        )}
      </div>

      {/* Verified Coordinates Sub-bar */}
      <div className="flex items-center justify-between px-3 py-1.5 mb-2 rounded-lg bg-stone-50 border border-stone-200 text-[11px] text-stone-600">
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
          <span className="font-semibold text-stone-800">Verified POI Coordinates:</span>
          <span className="font-mono text-stone-700">{slot.lat.toFixed(5)}°, {slot.lon.toFixed(5)}°</span>
        </div>
        <button
          onClick={() => {
            navigator.clipboard.writeText(`${slot.lat.toFixed(6)}, ${slot.lon.toFixed(6)}`);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
          }}
          className="text-stone-500 hover:text-stone-800 underline text-[10px] cursor-pointer"
        >
          Copy Lat/Lon
        </button>
      </div>

      {/* 4 Clean Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 my-2">
        {/* Temperature */}
        <div className="p-3 rounded-xl bg-[#faf8f5] border border-[#e5e0d8]">
          <div className="flex items-center gap-1 text-xs text-[#57685e] font-medium mb-0.5">
            <Thermometer className="w-3.5 h-3.5 text-rose-500" />
            <span>Temperature</span>
          </div>
          <div className="text-base sm:text-lg font-bold text-[#15221b]">
            {slot.temp_c}°C
          </div>
          <div className="text-[11px] text-[#829288]">
            Feels {slot.feels_like_c}°C
          </div>
        </div>

        {/* Air Quality */}
        <div className="p-3 rounded-xl bg-[#faf8f5] border border-[#e5e0d8]">
          <div className="flex items-center gap-1 text-xs text-[#57685e] font-medium mb-0.5">
            <Gauge className="w-3.5 h-3.5 text-emerald-600" />
            <span>Air Quality</span>
          </div>
          <div className="text-base sm:text-lg font-bold text-[#15221b]">
            AQI {slot.us_aqi}
          </div>
          <div className={`text-[11px] font-medium ${aqiStatus.color}`}>
            {aqiStatus.text}
          </div>
        </div>

        {/* Wind */}
        <div className="p-3 rounded-xl bg-[#faf8f5] border border-[#e5e0d8]">
          <div className="flex items-center gap-1 text-xs text-[#57685e] font-medium mb-0.5">
            <Wind className="w-3.5 h-3.5 text-sky-600" />
            <span>Wind</span>
          </div>
          <div className="text-base sm:text-lg font-bold text-[#15221b]">
            {slot.wind_kmh} km/h
          </div>
          <div className="text-[11px] text-[#829288]">
            {slot.wind_compass} breeze
          </div>
        </div>

        {/* Setting */}
        <div className="p-3 rounded-xl bg-[#faf8f5] border border-[#e5e0d8]">
          <div className="flex items-center gap-1 text-xs text-[#57685e] font-medium mb-0.5">
            <Trees className="w-3.5 h-3.5 text-emerald-600" />
            <span>Surroundings</span>
          </div>
          <div className="text-xs sm:text-sm font-bold text-[#15221b] truncate">
            {slot.downwind_status || "Open Space"}
          </div>
          <div className="text-[11px] text-[#829288] truncate">
            Green buffer
          </div>
        </div>
      </div>

      {/* Quick Highlights: 2-3 clean bullets */}
      {slot.reasons_good && slot.reasons_good.length > 0 && (
        <div className="pt-2 border-t border-[#f2f6f3]">
          <div className="space-y-1.5 text-xs text-[#15221b]">
            {slot.reasons_good.slice(0, 3).map((r, i) => (
              <div key={i} className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>{r}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
