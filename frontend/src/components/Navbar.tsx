"use client";

import React from "react";
import { Compass, Database, FileText, Star, ShieldCheck } from "lucide-react";
import { HealthInfo } from "@/types";

interface NavbarProps {
  health: HealthInfo | null;
  onOpenSources: () => void;
  favoritesCount?: number;
  onOpenFavorites?: () => void;
  onOpenDataQuality?: () => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const Navbar: React.FC<NavbarProps> = ({
  health,
  onOpenSources,
  favoritesCount = 0,
  onOpenFavorites,
  onOpenDataQuality
}) => {
  return (
    <header className="sticky top-0 z-40 bg-[#faf8f5]/95 backdrop-blur-md border-b border-[#e5e0d8] px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
        {/* Brand identity */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#1b2f22] flex items-center justify-center text-[#faf8f5] shadow-xs">
            <Compass className="w-4 h-4 text-[#81c784]" />
          </div>
          <div>
            <span className="font-bold text-base sm:text-lg text-[#15221b] tracking-tight">
              Fieldwise
            </span>
            <span className="hidden sm:inline text-xs text-[#57685e] ml-2">
              Outdoor Intelligence
            </span>
          </div>
        </div>

        {/* Quick status & links */}
        <div className="flex items-center gap-2">
          {/* Saved spots */}
          {onOpenFavorites && (
            <button
              onClick={onOpenFavorites}
              className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-lg bg-white border border-[#e5e0d8] text-[#15221b] hover:bg-[#f2f6f3] transition-colors cursor-pointer"
            >
              <Star className={`w-3.5 h-3.5 ${favoritesCount > 0 ? "text-amber-500 fill-amber-500" : "text-[#829288]"}`} />
              <span>Saved</span>
              {favoritesCount > 0 && (
                <span className="px-1.5 py-0.2 rounded-full bg-amber-100 text-amber-900 text-[10px] font-bold">
                  {favoritesCount}
                </span>
              )}
            </button>
          )}

          {/* Model Status */}
          <div className="hidden sm:flex items-center gap-1.5 text-[11px] font-medium px-2.5 py-1 rounded-full bg-[#f2f6f3] text-[#335942] border border-[#dce5df]">
            <span className={`w-2 h-2 rounded-full ${health?.status === "ok" ? "bg-emerald-500 animate-pulse" : "bg-amber-500"}`} />
            <span>Qwen2.5 (≤3B)</span>
          </div>

          {/* Data Quality & Export */}
          {onOpenDataQuality && (
            <button
              onClick={onOpenDataQuality}
              title="Verification & Export Dashboard"
              className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 hover:bg-emerald-100 transition-colors cursor-pointer"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
              <span className="hidden sm:inline">Data Quality & Export</span>
            </button>
          )}

          {/* Sources */}
          <button
            onClick={onOpenSources}
            className="flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-lg bg-white border border-[#e5e0d8] text-[#15221b] hover:bg-[#f2f6f3] transition-colors cursor-pointer"
          >
            <Database className="w-3.5 h-3.5 text-[#335942]" />
            <span className="hidden sm:inline">Sources</span>
          </button>

          {/* API Docs */}
          <a
            href={`${API_BASE}/docs`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-lg bg-white border border-[#e5e0d8] text-[#15221b] hover:bg-[#f2f6f3] transition-colors"
          >
            <FileText className="w-3.5 h-3.5 text-[#335942]" />
            <span className="hidden sm:inline">API</span>
          </a>
        </div>
      </div>
    </header>
  );
};
