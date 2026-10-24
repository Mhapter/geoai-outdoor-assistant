"use client";

import React from "react";
import { X, Database, ExternalLink, ShieldCheck, Clock } from "lucide-react";
import { SourceProvenance } from "@/types";

interface SourcesModalProps {
  isOpen: boolean;
  onClose: () => void;
  sources: SourceProvenance[];
}

export const SourcesModal: React.FC<SourcesModalProps> = ({
  isOpen,
  onClose,
  sources
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
      <div className="bg-white rounded-2xl border border-[#e5e0d8] shadow-xl max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#e5e0d8] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-[#f2f6f3] flex items-center justify-center text-[#264331]">
              <Database className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-base text-[#15221b]">
                Live Data Sources & Methodology
              </h3>
              <p className="text-xs text-[#57685e]">
                Every claim is grounded in live retrieved data — zero hallucinated weather or venues
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-[#829288] hover:text-[#15221b] hover:bg-[#faf8f5] transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Sources Content */}
        <div className="p-6 overflow-y-auto space-y-4">
          <div className="p-3.5 rounded-xl bg-[#f2f6f3] border border-[#dce5df] text-xs text-[#264331] flex items-start gap-2.5">
            <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Zero-Hallucination Integrity Mandate:</span> Fieldwise
              queries authoritative open REST endpoints in real-time. The small language model (≤3B)
              is strictly context-conditioned on retrieved facts and does not guess coordinates or forecast variables.
            </div>
          </div>

          <div className="space-y-3">
            {sources.map((src, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl border border-[#e5e0d8] bg-[#faf8f5] hover:bg-white transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="font-bold text-sm text-[#15221b] flex items-center gap-1.5">
                      <span>{src.name}</span>
                      {src.url && (
                        <a
                          href={src.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[#335942] hover:underline"
                        >
                          <ExternalLink className="w-3.5 h-3.5 inline" />
                        </a>
                      )}
                    </h4>
                    <span className="text-xs font-semibold text-[#57685e]">
                      {src.type}
                    </span>
                  </div>
                  <span className="text-[11px] px-2 py-0.5 rounded-md bg-[#e2ebe4] text-[#264331] font-medium">
                    {src.freshness}
                  </span>
                </div>

                <p className="text-xs text-[#57685e] mt-2 leading-relaxed">
                  {src.details}
                </p>

                <div className="mt-2.5 pt-2 border-t border-[#e5e0d8] flex flex-wrap items-center justify-between text-[11px] text-[#829288] gap-1">
                  <span>Attribution: <strong>{src.attribution}</strong></span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Fetched: {new Date(src.fetched_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="p-4 rounded-xl border border-[#e5e0d8] text-xs text-[#57685e] space-y-1">
            <div className="font-bold text-[#15221b]">Attribution Notice:</div>
            <p>
              Map data © OpenStreetMap contributors under ODbL 1.0. Meteorological data courtesy of
              Open-Meteo.com under Creative Commons Attribution 4.0 International (CC-BY 4.0).
              Routing engine powered by OSRM.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-[#e5e0d8] bg-[#faf8f5] flex justify-end">
          <button
            onClick={onClose}
            className="text-xs font-semibold px-4 py-2 rounded-lg bg-[#1b2f22] text-[#faf8f5] hover:bg-[#264331] transition-colors cursor-pointer"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
