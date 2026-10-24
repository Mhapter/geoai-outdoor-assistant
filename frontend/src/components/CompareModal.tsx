"use client";

import React from "react";
import { X, Check, ArrowRight, ShieldCheck, Gauge, Thermometer, Navigation, Trees } from "lucide-react";
import { SlotScore } from "@/types";

interface CompareModalProps {
  isOpen: boolean;
  onClose: () => void;
  bestSlot: SlotScore;
  alternatives: SlotScore[];
  selectedVenueName: string;
  onSelectVenue: (venueName: string) => void;
}

export const CompareModal: React.FC<CompareModalProps> = ({
  isOpen,
  onClose,
  bestSlot,
  alternatives,
  selectedVenueName,
  onSelectVenue
}) => {
  if (!isOpen) return null;

  const allVenues = [bestSlot, ...(alternatives || [])].slice(0, 4);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl max-w-4xl w-full border border-[#e5e0d8] shadow-2xl p-6 relative">
        {/* Modal Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#f2f6f3]">
          <div>
            <h2 className="text-lg font-bold text-[#15221b] flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-[#264331]" />
              <span>Compare Evaluated Places</span>
            </h2>
            <p className="text-xs text-[#57685e] mt-0.5">
              Side-by-side meteorological and geospatial comparison
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#829288] hover:text-[#15221b] hover:bg-[#f2f6f3] transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Comparison Grid */}
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="border-b border-[#e5e0d8] text-[#57685e]">
                <th className="py-2.5 px-3 font-semibold">Place</th>
                <th className="py-2.5 px-3 font-semibold">Suitability</th>
                <th className="py-2.5 px-3 font-semibold">Distance & Drive</th>
                <th className="py-2.5 px-3 font-semibold">Weather</th>
                <th className="py-2.5 px-3 font-semibold">Air Quality</th>
                <th className="py-2.5 px-3 font-semibold">Environment</th>
                <th className="py-2.5 px-3 font-semibold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#f2f6f3]">
              {allVenues.map((v, idx) => {
                const isSelected = v.venue_name === selectedVenueName;
                return (
                  <tr
                    key={idx}
                    className={`transition-colors ${
                      isSelected ? "bg-[#f2f6f3]/80 font-medium" : "hover:bg-[#faf8f5]"
                    }`}
                  >
                    {/* Name */}
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-[#1b2f22] text-[#faf8f5] text-[10px] font-bold flex items-center justify-center shrink-0">
                          {idx === 0 ? "★" : idx + 1}
                        </span>
                        <div>
                          <div className="font-bold text-[#15221b]">{v.venue_name}</div>
                          <div className="text-[11px] text-[#829288]">{v.hour_label}</div>
                        </div>
                      </div>
                    </td>

                    {/* Score */}
                    <td className="py-3 px-3">
                      <span className={`inline-block px-2 py-0.5 rounded text-[11px] font-bold ${
                        v.score >= 80
                          ? "bg-emerald-100 text-emerald-800"
                          : v.score >= 60
                          ? "bg-slate-100 text-[#1b2f22]"
                          : "bg-amber-100 text-amber-800"
                      }`}>
                        {v.score}/100 ({v.suitability_label})
                      </span>
                    </td>

                    {/* Distance */}
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-1 text-[#15221b]">
                        <Navigation className="w-3.5 h-3.5 text-[#335942]" />
                        <span>{v.distance_km} km (~{v.travel_mins} min)</span>
                      </div>
                    </td>

                    {/* Weather */}
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-1 text-[#15221b]">
                        <Thermometer className="w-3.5 h-3.5 text-rose-500" />
                        <span>{v.temp_c}°C</span>
                        <span className="text-[#829288] text-[10px]">({v.wind_kmh} km/h {v.wind_compass})</span>
                      </div>
                    </td>

                    {/* Air Quality */}
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-1">
                        <Gauge className="w-3.5 h-3.5 text-emerald-600" />
                        <span className="font-semibold text-[#15221b]">AQI {v.us_aqi}</span>
                      </div>
                    </td>

                    {/* Environment */}
                    <td className="py-3 px-3 text-[#57685e]">
                      <div className="flex items-center gap-1">
                        <Trees className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span className="truncate max-w-[120px]">{v.downwind_status || "Open Space"}</span>
                      </div>
                    </td>

                    {/* Action */}
                    <td className="py-3 px-3 text-right">
                      {isSelected ? (
                        <span className="inline-flex items-center gap-1 text-emerald-700 font-bold text-xs">
                          <Check className="w-3.5 h-3.5" />
                          <span>Active</span>
                        </span>
                      ) : (
                        <button
                          onClick={() => {
                            onSelectVenue(v.venue_name);
                            onClose();
                          }}
                          className="px-2.5 py-1 rounded-lg bg-[#1b2f22] text-[#faf8f5] hover:bg-[#264331] font-semibold text-xs cursor-pointer inline-flex items-center gap-1 transition-colors"
                        >
                          <span>Select</span>
                          <ArrowRight className="w-3 h-3" />
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="mt-4 pt-3 border-t border-[#f2f6f3] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-[#faf8f5] hover:bg-[#f2f6f3] border border-[#e5e0d8] text-xs font-semibold text-[#15221b] cursor-pointer"
          >
            Close Comparison
          </button>
        </div>
      </div>
    </div>
  );
};
