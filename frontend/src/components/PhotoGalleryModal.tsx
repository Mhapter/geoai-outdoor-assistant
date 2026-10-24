"use client";

import React, { useState } from "react";
import { X, ChevronLeft, ChevronRight, ExternalLink, Camera, ShieldCheck, AlertCircle } from "lucide-react";

export interface PhotoItem {
  url: string;
  title?: string;
  source?: string;
  source_url?: string;
  attribution?: string;
  license?: string;
  geotagged?: boolean;
}

interface PhotoGalleryModalProps {
  isOpen: boolean;
  onClose: () => void;
  venueName: string;
  photos: PhotoItem[];
  initialIndex?: number;
}

export const PhotoGalleryModal: React.FC<PhotoGalleryModalProps> = ({
  isOpen,
  onClose,
  venueName,
  photos = [],
  initialIndex = 0
}) => {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);

  if (!isOpen) return null;

  const hasPhotos = photos && photos.length > 0;
  const currentPhoto = hasPhotos ? photos[currentIndex] || photos[0] : null;

  const handlePrev = () => {
    if (!hasPhotos) return;
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : photos.length - 1));
  };

  const handleNext = () => {
    if (!hasPhotos) return;
    setCurrentIndex((prev) => (prev < photos.length - 1 ? prev + 1 : 0));
  };

  const googleMapsSearchUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(venueName)}`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md p-4 sm:p-6 overflow-hidden">
      <div className="bg-[#15221b] text-[#f4f7f5] rounded-2xl max-w-4xl w-full border border-[#24382c] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-[#24382c] bg-[#0d1410]">
          <div className="flex items-center gap-2 min-w-0">
            <Camera className="w-4 h-4 text-[#81c784] shrink-0" />
            <div className="min-w-0">
              <h3 className="font-bold text-sm sm:text-base text-white truncate">
                {venueName}
              </h3>
              <p className="text-[11px] text-[#9ab3a3] truncate">
                {hasPhotos
                  ? `Verified Photo ${currentIndex + 1} of ${photos.length}${currentPhoto?.title ? ` • ${currentPhoto.title}` : ""}`
                  : "No verified venue photography"}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <a
              href={googleMapsSearchUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-[#24382c] hover:bg-[#335942] text-[#81c784] transition-colors"
            >
              <span>View on Google Maps</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-[#9ab3a3] hover:text-white hover:bg-[#24382c] transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Main Photo Showcase or Verified Empty State */}
        {hasPhotos && currentPhoto ? (
          <div className="relative flex-1 bg-black flex items-center justify-center min-h-[300px] sm:min-h-[420px] overflow-hidden select-none">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={currentPhoto.url}
              alt={currentPhoto.title || venueName}
              className="max-h-[60vh] w-auto max-w-full object-contain transition-all duration-300"
            />

            {/* Left Arrow */}
            {photos.length > 1 && (
              <button
                onClick={handlePrev}
                className="absolute left-3 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/60 hover:bg-black/90 text-white backdrop-blur-xs transition-colors cursor-pointer"
                title="Previous Photo"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
            )}

            {/* Right Arrow */}
            {photos.length > 1 && (
              <button
                onClick={handleNext}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/60 hover:bg-black/90 text-white backdrop-blur-xs transition-colors cursor-pointer"
                title="Next Photo"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            )}

            {/* Source & Attribution Badge */}
            <div className="absolute bottom-3 left-3 right-3 flex flex-wrap items-center justify-between gap-2 text-[11px] bg-black/80 backdrop-blur-xs px-3 py-2 rounded-xl border border-white/10 text-[#d1e0d7]">
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                <span className="font-semibold text-white truncate">{currentPhoto.title}</span>
                {currentPhoto.license && (
                  <span className="text-[10px] text-emerald-400 font-mono">({currentPhoto.license})</span>
                )}
              </div>
              <div className="flex items-center gap-2 text-[10px] text-[#9ab3a3]">
                <span>{currentPhoto.attribution || currentPhoto.source || "Wikimedia Commons"}</span>
                {currentPhoto.source_url && (
                  <a
                    href={currentPhoto.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-emerald-400 hover:underline flex items-center gap-0.5"
                  >
                    <span>License & Details</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 p-10 flex flex-col items-center justify-center text-center space-y-3 min-h-[320px]">
            <div className="w-14 h-14 rounded-2xl bg-[#24382c] border border-[#335942] flex items-center justify-center text-[#81c784]">
              <Camera className="w-7 h-7" />
            </div>
            <h4 className="font-bold text-base text-white">No Verified Venue Photo Available</h4>
            <p className="text-xs text-[#9ab3a3] max-w-md leading-relaxed">
              Fieldwise strictly verifies every photograph against exact geographic coordinates and entity records. We do not display random stock photos, generic cityscapes, or unrelated venue images.
            </p>
            <a
              href={googleMapsSearchUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-2 inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-700 hover:bg-emerald-600 text-white font-semibold text-xs transition"
            >
              <span>Search Photos on Google Maps</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        )}

        {/* Bottom Thumbnail Strip */}
        {hasPhotos && photos.length > 1 && (
          <div className="p-3 bg-[#0d1410] border-t border-[#24382c] flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 overflow-x-auto scrollbar-none py-1">
              {photos.map((photo, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentIndex(idx)}
                  className={`w-14 h-11 rounded-lg overflow-hidden border-2 shrink-0 transition-all cursor-pointer ${
                    currentIndex === idx
                      ? "border-[#81c784] scale-105 shadow-md"
                      : "border-transparent opacity-60 hover:opacity-100"
                  }`}
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={photo.url} alt={photo.title || "Venue thumbnail"} className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
