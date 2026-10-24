"use client";

import React, { useState } from "react";
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Bot,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import { SlotScore } from "@/types";

interface EvidenceBreakdownProps {
  slot: SlotScore;
  markdownExplanation?: string;
  modelUsed?: string;
  isFallback?: boolean;
}

export const EvidenceBreakdown: React.FC<EvidenceBreakdownProps> = ({
  slot,
  markdownExplanation,
  modelUsed = "Qwen2.5-1.5B-Instruct",
  isFallback = false
}) => {
  const [showAiNotes, setShowAiNotes] = useState(false);

  return (
    <div className="bg-white rounded-2xl border border-[#e5e0d8] p-4 lg:p-5 shadow-xs space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-[#f2f6f3]">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-[#264331]" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-[#15221b]">
            Why This Spot?
          </h3>
        </div>

        <button
          type="button"
          onClick={() => setShowAiNotes(!showAiNotes)}
          className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-[#faf8f5] hover:bg-[#f2f6f3] border border-[#e5e0d8] text-[#335942] flex items-center gap-1.5 transition-colors cursor-pointer"
        >
          <Bot className="w-3.5 h-3.5" />
          <span>{showAiNotes ? "Hide AI Reasoning" : "View AI Reasoning"}</span>
          {showAiNotes ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      {/* 2 Simple Columns */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Good factors */}
        <div className="p-3.5 rounded-xl bg-emerald-50/70 border border-emerald-100">
          <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-900 mb-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Favorable Factors</span>
          </div>
          {slot.reasons_good && slot.reasons_good.length > 0 ? (
            <ul className="space-y-1.5 text-xs text-[#15221b]">
              {slot.reasons_good.map((r, i) => (
                <li key={i} className="flex items-start gap-1.5">
                  <span className="text-emerald-600 font-bold">•</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-[#57685e]">Standard pleasant conditions.</p>
          )}
        </div>

        {/* Cautions */}
        <div className="p-3.5 rounded-xl bg-amber-50/70 border border-amber-100">
          <div className="flex items-center gap-1.5 text-xs font-bold text-amber-900 mb-2">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span>Things to Keep in Mind</span>
          </div>
          {slot.reasons_bad && slot.reasons_bad.length > 0 ? (
            <ul className="space-y-1.5 text-xs text-[#15221b]">
              {slot.reasons_bad.map((r, i) => (
                <li key={i} className="flex items-start gap-1.5">
                  <span className="text-amber-600 font-bold">•</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-emerald-800">No major negative risks identified.</p>
          )}
        </div>
      </div>

      {/* Collapsible AI Explanation */}
      {showAiNotes && (
        <div className="pt-3 border-t border-[#f2f6f3] text-xs">
          <div className="p-3.5 rounded-xl bg-[#faf8f5] border border-[#e5e0d8] space-y-2">
            <div className="flex items-center justify-between text-[11px] text-[#57685e]">
              <span className="font-semibold text-[#1b2f22]">Model: {modelUsed}</span>
              <span>{isFallback ? "Deterministic Evidence Engine" : "Local Transformers Inference"}</span>
            </div>
            <div className="text-xs text-[#15221b] whitespace-pre-line leading-relaxed">
              {markdownExplanation || "AI reasoning synthesized from live meteorological and geospatial telemetry."}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
