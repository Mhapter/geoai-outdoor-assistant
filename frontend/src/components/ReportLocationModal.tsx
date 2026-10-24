"use client";

import React, { useState } from "react";
import { X, Flag, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";

interface ReportLocationModalProps {
  isOpen: boolean;
  onClose: () => void;
  venueName: string;
  lat: number;
  lon: number;
  locationId?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const ReportLocationModal: React.FC<ReportLocationModalProps> = ({
  isOpen,
  onClose,
  venueName,
  lat,
  lon,
  locationId
}) => {
  const [issueType, setIssueType] = useState<string>("wrong_coordinates");
  const [correction, setCorrection] = useState<string>("");
  const [notes, setNotes] = useState<string>("");
  const [contact, setContact] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedId, setSubmittedId] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      const res = await fetch(`${API_BASE}/api/locations/report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          location_id: locationId || venueName,
          location_name: venueName,
          reported_lat: lat,
          reported_lon: lon,
          issue_type: issueType,
          suggested_correction: correction.trim() || undefined,
          notes: notes.trim() || undefined,
          user_contact: contact.trim() || undefined
        })
      });

      if (!res.ok) {
        throw new Error("Failed to submit location report.");
      }

      const data = await res.json();
      setSubmittedId(data.report_id);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Submission failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
      <div className="bg-white rounded-2xl max-w-md w-full shadow-xl border border-stone-200 overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-stone-100 bg-stone-50">
          <div className="flex items-center gap-2 text-rose-800">
            <Flag className="w-4 h-4" />
            <h3 className="font-semibold text-sm text-stone-900">Report Location Issue</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-stone-400 hover:text-stone-700 rounded-lg hover:bg-stone-200/50 transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        {submittedId ? (
          <div className="p-6 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto border border-emerald-200">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h4 className="font-bold text-stone-900 text-base">Report Submitted</h4>
            <p className="text-xs text-stone-600 leading-relaxed">
              Ticket <strong className="font-mono text-emerald-700">{submittedId}</strong> has been logged into our data verification queue. Thank you for keeping geospatial data accurate.
            </p>
            <button
              onClick={() => {
                setSubmittedId(null);
                onClose();
              }}
              className="mt-4 px-4 py-2 bg-emerald-800 hover:bg-emerald-900 text-white rounded-xl text-xs font-semibold transition cursor-pointer"
            >
              Done
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs">
            {errorMsg && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <div>
              <label className="block font-semibold text-stone-700 mb-1">Target Venue</label>
              <div className="p-2.5 bg-stone-50 border border-stone-200 rounded-lg font-medium text-stone-900">
                {venueName}
                <div className="font-mono text-[10px] text-stone-500 mt-0.5">
                  Coordinates: {lat.toFixed(5)}°, {lon.toFixed(5)}°
                </div>
              </div>
            </div>

            <div>
              <label className="block font-semibold text-stone-700 mb-1">Issue Category</label>
              <select
                value={issueType}
                onChange={(e) => setIssueType(e.target.value)}
                className="w-full p-2 border border-stone-200 rounded-lg bg-white text-stone-800 focus:outline-hidden focus:ring-1 focus:ring-emerald-700"
              >
                <option value="wrong_coordinates">Marker shows incorrect coordinates</option>
                <option value="place_closed">Place is permanently closed or demolished</option>
                <option value="wrong_name">Incorrect or misspelled name</option>
                <option value="wrong_category">Wrong activity / venue category</option>
                <option value="other">Other geospatial discrepancy</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-stone-700 mb-1">
                Suggested Correction (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Correct coordinates or updated address"
                value={correction}
                onChange={(e) => setCorrection(e.target.value)}
                className="w-full p-2 border border-stone-200 rounded-lg text-stone-800 focus:outline-hidden focus:ring-1 focus:ring-emerald-700"
              />
            </div>

            <div>
              <label className="block font-semibold text-stone-700 mb-1">Details & Evidence</label>
              <textarea
                rows={3}
                placeholder="Explain why this place or coordinate is incorrect..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full p-2 border border-stone-200 rounded-lg text-stone-800 focus:outline-hidden focus:ring-1 focus:ring-emerald-700 resize-none"
              />
            </div>

            <div className="pt-2 flex items-center justify-end gap-2 border-t border-stone-100">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-1.5 rounded-lg border border-stone-200 text-stone-600 hover:bg-stone-50 font-medium transition cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-rose-700 hover:bg-rose-800 text-white font-semibold transition disabled:opacity-50 cursor-pointer"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Sending...</span>
                  </>
                ) : (
                  <span>Submit Discrepancy</span>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
