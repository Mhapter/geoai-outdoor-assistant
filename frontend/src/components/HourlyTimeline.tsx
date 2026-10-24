"use client";

import React, { useState } from "react";
import {
  Clock,
  Sun,
  Moon,
  Sparkles
} from "lucide-react";
import { HourlyCondition } from "@/types";

interface HourlyTimelineProps {
  timeline: HourlyCondition[];
  venueName?: string;
}

export const HourlyTimeline: React.FC<HourlyTimelineProps> = ({
  timeline,
  venueName = "Venue"
}) => {
  const [selectedHourIso, setSelectedHourIso] = useState<string | null>(null);

  if (!timeline || timeline.length === 0) {
    return null;
  }

  const activeCondition =
    timeline.find((t) => t.hour_iso === selectedHourIso) || timeline[0];

  const getConditionColor = (c: HourlyCondition) => {
    if (c.us_aqi <= 70 && c.precip_prob_pct <= 20 && c.temp_c <= 32) return "bg-emerald-500";
    if (c.us_aqi <= 120 && c.precip_prob_pct <= 40) return "bg-amber-400";
    return "bg-rose-500";
  };

  return (
    <div className="bg-white rounded-2xl border border-[#e5e0d8] p-4 lg:p-5 shadow-xs">
      <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#f2f6f3]">
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-[#264331]" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-[#15221b]">
            Hourly Forecast
          </h3>
          <span className="text-xs text-[#57685e]">
            for {venueName}
          </span>
        </div>

        <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-[#f2f6f3] text-[#335942]">
          {activeCondition.day_name} {activeCondition.hour_label}
        </span>
      </div>

      {/* Visual Condition Heat Strip */}
      <div className="mb-2">
        <div className="flex h-1.5 w-full rounded-full overflow-hidden bg-[#e5e0d8]">
          {timeline.map((item, idx) => (
            <div
              key={idx}
              className={`flex-1 ${getConditionColor(item)} transition-opacity ${
                item.hour_iso === (selectedHourIso || timeline[0].hour_iso) ? "opacity-100 ring-2 ring-[#1b2f22]" : "opacity-75"
              }`}
              title={`${item.hour_label}: ${item.temp_c}°C, AQI ${item.us_aqi}`}
            />
          ))}
        </div>
      </div>

      {/* Horizontal Scrollable Timeline Chips */}
      <div className="flex gap-2 overflow-x-auto pb-2 pt-1 scrollbar-thin">
        {timeline.map((item, idx) => {
          const isSelected = item.hour_iso === (selectedHourIso || timeline[0].hour_iso);
          return (
            <button
              key={idx}
              type="button"
              onClick={() => setSelectedHourIso(item.hour_iso)}
              className={`flex-shrink-0 w-20 p-2.5 rounded-xl border text-center transition-all cursor-pointer ${
                isSelected
                  ? "bg-[#1b2f22] text-[#faf8f5] border-[#1b2f22] shadow-xs"
                  : "bg-[#faf8f5] border-[#e5e0d8] hover:bg-white text-[#15221b]"
              }`}
            >
              <div className="text-[11px] font-bold opacity-85 mb-1">
                {item.hour_label}
              </div>

              <div className="flex justify-center mb-1">
                {item.golden_hour ? (
                  <Sparkles className="w-4 h-4 text-amber-400" />
                ) : item.is_daylight ? (
                  <Sun className="w-4 h-4 text-amber-500" />
                ) : (
                  <Moon className="w-4 h-4 text-slate-400" />
                )}
              </div>

              <div className="text-xs font-bold mb-1">
                {item.temp_c}°C
              </div>

              <div className={`text-[10px] font-semibold px-1 py-0.5 rounded ${
                isSelected
                  ? "bg-white/20 text-[#faf8f5]"
                  : item.us_aqi <= 60
                  ? "bg-emerald-100 text-emerald-800"
                  : item.us_aqi <= 100
                  ? "bg-amber-100 text-amber-800"
                  : "bg-rose-100 text-rose-800"
              }`}>
                AQI {item.us_aqi}
              </div>
            </button>
          );
        })}
      </div>

      {/* Compact 1-Line Stat Strip */}
      <div className="mt-2.5 py-2 px-3 bg-[#faf8f5] rounded-xl border border-[#e5e0d8] flex flex-wrap items-center justify-between gap-2 text-xs text-[#57685e]">
        <div className="flex items-center gap-1.5 font-semibold text-[#15221b]">
          <span>🌡️ {activeCondition.temp_c}°C</span>
          <span className="text-[#829288] font-normal">(feels {activeCondition.feels_like_c}°C)</span>
        </div>
        <span>•</span>
        <div className="flex items-center gap-1 font-semibold text-[#15221b]">
          <span>🍃 US AQI {activeCondition.us_aqi}</span>
          <span className="text-[#829288] font-normal">({activeCondition.pm25} µg PM2.5)</span>
        </div>
        <span>•</span>
        <div className="flex items-center gap-1 text-[#15221b]">
          <span>💨 {activeCondition.wind_kmh} km/h {activeCondition.wind_compass}</span>
        </div>
        <span>•</span>
        <div className="flex items-center gap-1 text-[#15221b]">
          <span>☀️ UV Index {activeCondition.uv_index}</span>
        </div>
      </div>
    </div>
  );
};
