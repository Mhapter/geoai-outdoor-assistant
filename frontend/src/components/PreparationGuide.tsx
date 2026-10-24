"use client";

import React from "react";
import {
  Luggage,
  Eye,
  Ban,
  CheckCircle2,
  AlertTriangle
} from "lucide-react";
import { SlotScore } from "@/types";

interface PreparationGuideProps {
  carryItems: string[];
  watchNotes: string[];
  avoidSlots: SlotScore[];
}

export const PreparationGuide: React.FC<PreparationGuideProps> = ({
  carryItems,
  watchNotes,
  avoidSlots
}) => {
  return (
    <div className="bg-white rounded-2xl border border-[#e5e0d8] p-4 lg:p-5 shadow-xs">
      <div className="pb-2.5 mb-3 border-b border-[#f2f6f3] flex items-center gap-2">
        <Luggage className="w-4 h-4 text-[#264331]" />
        <h3 className="text-xs font-bold uppercase tracking-wider text-[#15221b]">
          Tips for Your Outing
        </h3>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* 1. What to Bring */}
        <div className="p-3.5 rounded-xl bg-[#faf8f5] border border-[#e5e0d8]">
          <div className="flex items-center gap-1.5 text-xs font-bold text-[#1b2f22] mb-2">
            <Luggage className="w-3.5 h-3.5 text-[#335942]" />
            <span>What to Bring</span>
          </div>
          {carryItems && carryItems.length > 0 ? (
            <ul className="space-y-1.5 text-xs text-[#15221b]">
              {carryItems.map((item, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-[#57685e]">Comfortable gear and water bottle.</p>
          )}
        </div>

        {/* 2. What to Watch */}
        <div className="p-3.5 rounded-xl bg-[#faf8f5] border border-[#e5e0d8]">
          <div className="flex items-center gap-1.5 text-xs font-bold text-[#1b2f22] mb-2">
            <Eye className="w-3.5 h-3.5 text-amber-600" />
            <span>What to Watch</span>
          </div>
          {watchNotes && watchNotes.length > 0 ? (
            <ul className="space-y-1.5 text-xs text-[#15221b]">
              {watchNotes.map((note, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                  <span>{note}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-[#57685e]">
              Check local air quality and stay hydrated.
            </p>
          )}
        </div>

        {/* 3. When to Avoid */}
        <div className="p-3.5 rounded-xl bg-rose-50/50 border border-rose-100">
          <div className="flex items-center gap-1.5 text-xs font-bold text-rose-900 mb-2">
            <Ban className="w-3.5 h-3.5 text-rose-600" />
            <span>When to Avoid</span>
          </div>
          {avoidSlots && avoidSlots.length > 0 ? (
            <div className="space-y-1.5 text-xs text-[#15221b]">
              {avoidSlots.slice(0, 2).map((av, idx) => (
                <div key={idx} className="p-2 rounded-lg bg-white border border-rose-200">
                  <div className="font-semibold text-rose-950 text-xs">
                    {av.venue_name}
                  </div>
                  <div className="text-[11px] text-[#57685e]">
                    Avoid around {av.hour_label} (Score: {av.score}/100)
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-[#57685e]">
              Avoid peak midday sun (12 PM - 3 PM) and heavy traffic rush hours.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
