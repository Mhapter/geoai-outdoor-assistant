"use client";

import React from "react";
import { ChevronRight, Camera } from "lucide-react";
import { SlotScore } from "@/types";

interface AlternativesListProps {
  alternatives: SlotScore[];
  selectedVenueName?: string;
  onSelectVenue: (venueName: string) => void;
  onOpenPhotos?: (venueName: string, photos: Array<{ url: string; title?: string; source?: string }>) => void;
}

export const AlternativesList: React.FC<AlternativesListProps> = ({
  alternatives,
  selectedVenueName,
  onSelectVenue,
  onOpenPhotos
}) => {
  if (!alternatives || alternatives.length === 0) {
    return null;
  }

  const getScoreBadge = (score: number) => {
    if (score >= 80) return "bg-emerald-100 text-emerald-900 border-emerald-300";
    if (score >= 60) return "bg-slate-100 text-[#1b2f22] border-slate-300";
    return "bg-amber-100 text-amber-900 border-amber-300";
  };

  return (
    <div className="bg-white rounded-2xl border border-[#e5e0d8] p-4 lg:p-5 shadow-xs">
      <div className="flex items-center justify-between pb-2.5 mb-2.5 border-b border-[#f2f6f3]">
        <h3 className="text-xs font-bold uppercase tracking-wider text-[#15221b]">
          Other Nearby Places ({alternatives.length})
        </h3>
        <span className="text-[11px] text-[#829288]">
          Click to view on map
        </span>
      </div>

      <div className="space-y-2.5">
        {alternatives.map((alt, idx) => {
          const isSelected = selectedVenueName === alt.venue_name;
          const photo = alt.images && alt.images.length > 0 ? alt.images[0] : null;

          return (
            <div
              key={idx}
              className={`w-full p-2.5 rounded-xl border transition-all flex items-center justify-between gap-3 ${
                isSelected
                  ? "bg-[#f2f6f3] border-[#264331] shadow-2xs ring-1 ring-[#264331]"
                  : "bg-[#faf8f5] border-[#e5e0d8] hover:bg-white text-[#15221b]"
              }`}
            >
              {/* Left Side: Thumbnail + Info */}
              <div
                onClick={() => onSelectVenue(alt.venue_name)}
                className="flex items-center gap-2.5 min-w-0 flex-1 cursor-pointer"
              >
                {/* Photo Thumbnail */}
                {photo ? (
                  <div
                    onClick={(e) => {
                      e.stopPropagation();
                      if (onOpenPhotos) onOpenPhotos(alt.venue_name, alt.images || [photo]);
                    }}
                    title="Click to preview photos"
                    className="relative w-12 h-12 rounded-lg overflow-hidden shrink-0 group border border-[#e5e0d8]"
                  >
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={photo.url}
                      alt={alt.venue_name}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                    />
                    <div className="absolute inset-0 bg-black/30 group-hover:bg-black/10 flex items-center justify-center transition-colors">
                      <Camera className="w-3.5 h-3.5 text-white drop-shadow-md" />
                    </div>
                  </div>
                ) : (
                  <span className="w-7 h-7 rounded-full bg-[#1b2f22] text-[#faf8f5] text-[11px] font-bold flex items-center justify-center shrink-0">
                    {idx + 2}
                  </span>
                )}

                <div className="min-w-0 flex-1">
                  <h4 className="font-bold text-xs sm:text-sm text-[#15221b] truncate">
                    {alt.venue_name}
                  </h4>
                  <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-[#57685e] mt-0.5">
                    <span>{alt.route_dist_km || alt.distance_km} km by road (~{alt.travel_mins} mins)</span>
                    {alt.straight_line_dist_km ? (
                      <span className="text-[10px] text-stone-500">({alt.straight_line_dist_km} km crow-flies)</span>
                    ) : null}
                    <span>•</span>
                    <span>{alt.temp_c}°C</span>
                    <span>•</span>
                    <span className={alt.us_aqi <= 100 ? "text-emerald-700 font-medium" : "text-amber-700 font-medium"}>
                      AQI {alt.us_aqi}
                    </span>
                  </div>
                </div>
              </div>

              {/* Right Side: Score Pill + Select */}
              <div
                onClick={() => onSelectVenue(alt.venue_name)}
                className="flex items-center gap-2 shrink-0 cursor-pointer"
              >
                <span className={`text-[11px] font-bold px-2 py-0.5 rounded-md border ${getScoreBadge(alt.score)}`}>
                  {alt.score}/100
                </span>
                <ChevronRight className="w-4 h-4 text-[#829288]" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
