"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Navbar } from "@/components/Navbar";
import { QueryForm } from "@/components/QueryForm";
import { BestRecommendationCard } from "@/components/BestRecommendationCard";
import { InteractiveMap } from "@/components/InteractiveMap";
import { AlternativesList } from "@/components/AlternativesList";
import { HourlyTimeline } from "@/components/HourlyTimeline";
import { EvidenceBreakdown } from "@/components/EvidenceBreakdown";
import { PreparationGuide } from "@/components/PreparationGuide";
import { SourcesModal } from "@/components/SourcesModal";
import { CompareModal } from "@/components/CompareModal";
import { FavoritesModal, FavoriteSpot } from "@/components/FavoritesModal";
import { LoadingSkeleton } from "@/components/LoadingSkeleton";
import { PhotoGalleryModal, PhotoItem } from "@/components/PhotoGalleryModal";
import { DataQualityModal } from "@/components/DataQualityModal";
import { ReportLocationModal } from "@/components/ReportLocationModal";
import {
  RecommendationResponse,
  ActivityInfo,
  HealthInfo,
  SlotScore
} from "@/types";
import { AlertCircle, MapPin } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [health, setHealth] = useState<HealthInfo | null>(null);
  const [activities, setActivities] = useState<ActivityInfo[]>([]);
  const [recommendation, setRecommendation] = useState<RecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedVenueName, setSelectedVenueName] = useState<string>("");
  const [isSourcesOpen, setIsSourcesOpen] = useState<boolean>(false);
  const [isCompareOpen, setIsCompareOpen] = useState<boolean>(false);
  const [isFavoritesOpen, setIsFavoritesOpen] = useState<boolean>(false);
  const [isDataQualityOpen, setIsDataQualityOpen] = useState<boolean>(false);
  const [reportingVenue, setReportingVenue] = useState<SlotScore | null>(null);
  const [galleryState, setGalleryState] = useState<{
    isOpen: boolean;
    venueName: string;
    photos: PhotoItem[];
  }>({
    isOpen: false,
    venueName: "",
    photos: []
  });

  const openGallery = (venueName: string, photos: PhotoItem[]) => {
    setGalleryState({
      isOpen: true,
      venueName,
      photos
    });
  };

  const [favorites, setFavorites] = useState<FavoriteSpot[]>(() => {
    if (typeof window !== "undefined") {
      try {
        const stored = localStorage.getItem("fieldwise_favs");
        if (stored) return JSON.parse(stored);
      } catch {
        // ignore
      }
    }
    return [];
  });

  const handleToggleFavorite = (slot: SlotScore) => {
    setFavorites((prev) => {
      const exists = prev.some((f) => f.name === slot.venue_name);
      let updated: FavoriteSpot[];
      if (exists) {
        updated = prev.filter((f) => f.name !== slot.venue_name);
      } else {
        updated = [
          ...prev,
          {
            id: slot.venue_name,
            name: slot.venue_name,
            lat: slot.lat,
            lon: slot.lon,
            score: slot.score,
            savedAt: new Date().toISOString()
          }
        ];
      }
      try {
        localStorage.setItem("fieldwise_favs", JSON.stringify(updated));
      } catch {
        // ignore storage errors
      }
      return updated;
    });
  };

  const handleRemoveFavorite = (id: string) => {
    setFavorites((prev) => {
      const updated = prev.filter((f) => f.id !== id);
      try {
        localStorage.setItem("fieldwise_favs", JSON.stringify(updated));
      } catch {
        // ignore
      }
      return updated;
    });
  };

  const handleQuerySubmit = useCallback(async (params: {
    question?: string;
    activity?: string;
    location?: string;
    radius_km?: number;
    user_lat?: number;
    user_lon?: number;
    date_window?: string;
    time_window?: string;
    personal_profiles?: string[];
  }) => {
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params)
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `Server returned status ${res.status}`);
      }

      const data: RecommendationResponse = await res.json();
      setRecommendation(data);

      if (data.best_recommendation) {
        setSelectedVenueName(data.best_recommendation.venue_name);
      }
    } catch (err: unknown) {
      console.error("Evaluation failed:", err);
      const errMsg = err instanceof Error ? err.message : "Failed to connect to recommendation engine.";
      setError(errMsg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch initial health and activity definitions
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const [hRes, aRes] = await Promise.all([
          fetch(`${API_BASE}/api/health`).then((r) => r.json()),
          fetch(`${API_BASE}/api/activities`).then((r) => r.json())
        ]);
        setHealth(hRes);
        setActivities(aRes);
      } catch (err) {
        console.warn("Could not fetch metadata from backend API:", err);
      }
    };
    fetchMetadata();
  }, []);

  // Run initial query on mount so user immediately sees live interactive results
  useEffect(() => {
    const timer = setTimeout(() => {
      void handleQuerySubmit({
        question: "Find a good place for jogging tomorrow morning within 10 km of Greater Noida"
      });
    }, 0);
    return () => clearTimeout(timer);
  }, [handleQuerySubmit]);

  // Determine currently active slot to inspect
  const activeSlot: SlotScore | undefined =
    recommendation?.best_recommendation?.venue_name === selectedVenueName
      ? recommendation?.best_recommendation
      : recommendation?.alternative_venues.find((a) => a.venue_name === selectedVenueName) ||
        recommendation?.best_recommendation ||
        undefined;

  const isCurrentFavorite = Boolean(
    activeSlot && favorites.some((f) => f.name === activeSlot.venue_name)
  );

  return (
    <div className="min-h-screen bg-[#faf8f5] text-[#15221b] flex flex-col font-sans">
      {/* Sleek Navigation Bar */}
      <Navbar
        health={health}
        onOpenSources={() => setIsSourcesOpen(true)}
        favoritesCount={favorites.length}
        onOpenFavorites={() => setIsFavoritesOpen(true)}
        onOpenDataQuality={() => setIsDataQualityOpen(true)}
      />

      {/* Main Content Workspace */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-5 space-y-5">
        {/* Simple & Clean Search Form */}
        <QueryForm
          activities={activities}
          onSubmit={handleQuerySubmit}
          isLoading={isLoading}
        />

        {/* Error Notification */}
        {error && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Connection Note: </span>
              <span>{error}</span>
              <p className="mt-1 text-xs text-rose-700">
                Please make sure the backend is running at http://localhost:8000.
              </p>
            </div>
          </div>
        )}

        {/* Missing Location Guidance (User-Friendly) */}
        {recommendation?.status === "missing_location" && !isLoading && (
          <div className="p-5 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 space-y-2">
            <div className="flex items-center gap-2 font-bold text-sm sm:text-base">
              <MapPin className="w-5 h-5 text-amber-700 shrink-0" />
              <span>Where would you like to go?</span>
            </div>
            <p className="text-xs sm:text-sm text-amber-800 leading-relaxed">
              Please enter a city, area, or tap &ldquo;GPS&rdquo; above so we can check real weather, air quality, and places for you.
            </p>
          </div>
        )}

        {/* Loading Skeleton */}
        {isLoading && <LoadingSkeleton />}

        {/* Results Workspace: Clean Two-Column Layout */}
        {!isLoading && recommendation?.status === "ok" && recommendation.best_recommendation && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
            {/* Left Column: Recommendations & Advice (7 Cols) */}
            <div className="lg:col-span-7 space-y-5">
              {/* 1. Best Recommendation Card */}
              <BestRecommendationCard
                slot={activeSlot || recommendation.best_recommendation}
                activityLabel={
                  recommendation.parsed_intent?.activity?.replace("_", " ").toUpperCase() ||
                  "OUTDOOR"
                }
                isFavorite={isCurrentFavorite}
                onToggleFavorite={() => activeSlot && handleToggleFavorite(activeSlot)}
                onOpenCompare={() => setIsCompareOpen(true)}
                onOpenPhotos={() => activeSlot && openGallery(activeSlot.venue_name, activeSlot.images || [])}
                onReportIssue={(slot) => setReportingVenue(slot)}
              />

              {/* 2. Hourly Forecast */}
              <HourlyTimeline
                timeline={recommendation.hourly_timeline}
                venueName={activeSlot?.venue_name || recommendation.best_recommendation.venue_name}
              />

              {/* 3. Condition Insights */}
              <EvidenceBreakdown
                slot={activeSlot || recommendation.best_recommendation}
                markdownExplanation={recommendation.recommendation_markdown}
                modelUsed={recommendation.model_used}
                isFallback={recommendation.is_fallback}
              />

              {/* 4. Tips & Safety */}
              <PreparationGuide
                carryItems={recommendation.recommended_carry}
                watchNotes={recommendation.profile_watch_notes}
                avoidSlots={recommendation.avoid_slots}
              />
            </div>

            {/* Right Column: Map & Other Venues (5 Cols) */}
            <div className="lg:col-span-5 space-y-5 lg:sticky lg:top-16">
              {/* Interactive Venue Map */}
              <InteractiveMap
                origin={recommendation.origin}
                bestSlot={recommendation.best_recommendation}
                alternatives={recommendation.alternative_venues}
                selectedVenueName={selectedVenueName}
                onSelectVenue={(name) => setSelectedVenueName(name)}
                radiusKm={recommendation.parsed_intent?.radius_km || 10}
              />

              {/* Alternatives List */}
              <AlternativesList
                alternatives={recommendation.alternative_venues}
                selectedVenueName={selectedVenueName}
                onSelectVenue={(name) => setSelectedVenueName(name)}
                onOpenPhotos={(name: string, photos: PhotoItem[]) => openGallery(name, photos)}
              />
            </div>
          </div>
        )}
      </main>

      {/* Clean & Professional Footer */}
      <footer className="mt-auto border-t border-[#e5e0d8] bg-white py-4 px-4 lg:px-8 text-xs text-[#57685e]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2.5">
          <div>
            <strong>Fieldwise</strong> • Outdoor Intelligence
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsSourcesOpen(true)}
              className="text-[#335942] hover:underline cursor-pointer"
            >
              Data Sources
            </button>
            <span>•</span>
            <a
              href="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[#335942] hover:underline"
            >
              Model Card (Qwen 1.5B)
            </a>
            <span>•</span>
            <span>&copy; OpenStreetMap contributors</span>
          </div>
        </div>
      </footer>

      {/* Sources Modal */}
      <SourcesModal
        isOpen={isSourcesOpen}
        onClose={() => setIsSourcesOpen(false)}
        sources={recommendation?.sources || []}
      />

      {/* Compare Spots Modal */}
      {recommendation?.best_recommendation && (
        <CompareModal
          isOpen={isCompareOpen}
          onClose={() => setIsCompareOpen(false)}
          bestSlot={recommendation.best_recommendation}
          alternatives={recommendation.alternative_venues || []}
          selectedVenueName={selectedVenueName}
          onSelectVenue={(name) => setSelectedVenueName(name)}
        />
      )}

      {/* Favorites Modal */}
      <FavoritesModal
        isOpen={isFavoritesOpen}
        onClose={() => setIsFavoritesOpen(false)}
        favorites={favorites}
        onRemoveFavorite={handleRemoveFavorite}
        onSelectFavorite={(spot) => {
          handleQuerySubmit({
            location: spot.name,
            user_lat: spot.lat,
            user_lon: spot.lon
          });
        }}
      />

      {/* Photo Preview Gallery Modal (Google Images Style) */}
      <PhotoGalleryModal
        isOpen={galleryState.isOpen}
        onClose={() => setGalleryState((prev) => ({ ...prev, isOpen: false }))}
        venueName={galleryState.venueName}
        photos={galleryState.photos}
      />

      {/* Verification & Data Quality Dashboard */}
      <DataQualityModal
        isOpen={isDataQualityOpen}
        onClose={() => setIsDataQualityOpen(false)}
        recommendation={recommendation}
      />

      {/* Report Location Discrepancy Modal */}
      {reportingVenue && (
        <ReportLocationModal
          isOpen={Boolean(reportingVenue)}
          onClose={() => setReportingVenue(null)}
          venueName={reportingVenue.venue_name}
          lat={reportingVenue.lat}
          lon={reportingVenue.lon}
          locationId={reportingVenue.venue_name}
        />
      )}
    </div>
  );
}
