"use client";

import React from "react";
import { X, Star, Trash2, MapPin, ArrowRight } from "lucide-react";

export interface FavoriteSpot {
  id: string;
  name: string;
  lat: number;
  lon: number;
  activity?: string;
  score?: number;
  savedAt: string;
}

interface FavoritesModalProps {
  isOpen: boolean;
  onClose: () => void;
  favorites: FavoriteSpot[];
  onRemoveFavorite: (id: string) => void;
  onSelectFavorite: (spot: FavoriteSpot) => void;
}

export const FavoritesModal: React.FC<FavoritesModalProps> = ({
  isOpen,
  onClose,
  favorites,
  onRemoveFavorite,
  onSelectFavorite
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl max-w-lg w-full border border-[#e5e0d8] shadow-2xl p-6 relative">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#f2f6f3]">
          <div className="flex items-center gap-2">
            <Star className="w-5 h-5 text-amber-500 fill-amber-500" />
            <h2 className="text-base font-bold text-[#15221b]">
              Saved Favorite Places ({favorites.length})
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#829288] hover:text-[#15221b] hover:bg-[#f2f6f3] cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="mt-4 space-y-2.5 max-h-80 overflow-y-auto pr-1">
          {favorites.length === 0 ? (
            <div className="text-center py-8 text-xs text-[#57685e]">
              <Star className="w-8 h-8 text-[#dce5df] mx-auto mb-2" />
              <p className="font-semibold text-[#15221b]">No saved spots yet</p>
              <p className="mt-0.5">Click &ldquo;Save to Favorites&rdquo; on any recommendation to bookmark it here.</p>
            </div>
          ) : (
            favorites.map((fav) => (
              <div
                key={fav.id}
                className="p-3 rounded-xl border border-[#e5e0d8] bg-[#faf8f5] hover:bg-white flex items-center justify-between gap-3 transition-colors"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-1.5 font-bold text-xs sm:text-sm text-[#15221b] truncate">
                    <MapPin className="w-3.5 h-3.5 text-[#335942] shrink-0" />
                    <span className="truncate">{fav.name}</span>
                  </div>
                  <div className="text-[11px] text-[#57685e] mt-0.5">
                    Saved on {new Date(fav.savedAt).toLocaleDateString()}
                    {fav.score ? ` • Last Score: ${fav.score}/100` : ""}
                  </div>
                </div>

                <div className="flex items-center gap-1.5 shrink-0">
                  <button
                    onClick={() => {
                      onSelectFavorite(fav);
                      onClose();
                    }}
                    className="px-2.5 py-1 rounded-lg bg-[#1b2f22] text-[#faf8f5] text-xs font-semibold hover:bg-[#264331] inline-flex items-center gap-1 cursor-pointer transition-colors"
                  >
                    <span>Check</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>

                  <button
                    onClick={() => onRemoveFavorite(fav.id)}
                    title="Remove from favorites"
                    className="p-1 rounded-lg text-[#829288] hover:text-rose-600 hover:bg-rose-50 cursor-pointer transition-colors"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="mt-4 pt-3 border-t border-[#f2f6f3] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-[#faf8f5] hover:bg-[#f2f6f3] border border-[#e5e0d8] text-xs font-semibold text-[#15221b] cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
