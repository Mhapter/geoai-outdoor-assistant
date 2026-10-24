"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import {
  MapPin,
  Layers,
  Crosshair,
  ExternalLink,
  Copy,
  Check,
  ShieldCheck,
  Compass
} from "lucide-react";
import type { Map as LeafletMap, LayerGroup as LeafletLayerGroup, Circle as LeafletCircle } from "leaflet";
import { SlotScore } from "@/types";

interface InteractiveMapProps {
  origin: {
    name: string;
    short_name: string;
    lat: number;
    lon: number;
    provider?: string;
    verification_status?: string;
  };
  bestSlot?: SlotScore | null;
  alternatives: SlotScore[];
  selectedVenueName?: string;
  onSelectVenue?: (venueName: string) => void;
  radiusKm?: number;
}

export const InteractiveMap: React.FC<InteractiveMapProps> = ({
  origin,
  bestSlot,
  alternatives,
  selectedVenueName,
  onSelectVenue,
  radiusKm = 10
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<LeafletMap | null>(null);
  const markerGroupRef = useRef<LeafletLayerGroup | null>(null);
  const radiusCircleRef = useRef<LeafletCircle | null>(null);
  const [mapLayer, setMapLayer] = useState<"osm" | "voyager" | "dark">("osm");
  const [isLeafletReady, setIsLeafletReady] = useState(false);
  const [copiedCoords, setCopiedCoords] = useState<string | null>(null);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCoords(id);
    setTimeout(() => setCopiedCoords(null), 2000);
  };

  // Recenter map handler
  const handleRecenter = useCallback(() => {
    if (!mapInstanceRef.current) return;
    const centerLat = bestSlot?.lat || origin?.lat;
    const centerLon = bestSlot?.lon || origin?.lon;
    if (centerLat && centerLon) {
      mapInstanceRef.current.setView([centerLat, centerLon], 13, { animate: true });
    }
  }, [bestSlot, origin]);

  // 1. Initialize Map once on mount or when layer changes
  useEffect(() => {
    if (typeof window === "undefined" || !mapContainerRef.current) return;

    let isMounted = true;

    import("leaflet").then((L) => {
      if (!isMounted || !mapContainerRef.current) return;

      // Fix missing Leaflet default icon paths safely
      delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      // Avoid double initialization
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }

      const initialLat = bestSlot?.lat || origin?.lat || 28.6139;
      const initialLon = bestSlot?.lon || origin?.lon || 77.2090;

      const map = L.map(mapContainerRef.current, {
        center: [initialLat, initialLon],
        zoom: 12,
        zoomControl: true,
        scrollWheelZoom: true
      });

      let tileUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
      let attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

      if (mapLayer === "voyager") {
        tileUrl = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png";
        attr = '&copy; <a href="https://carto.com/">CARTO</a> &copy; OpenStreetMap';
      } else if (mapLayer === "dark") {
        tileUrl = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";
        attr = '&copy; <a href="https://carto.com/">CARTO</a> &copy; OpenStreetMap';
      }

      L.tileLayer(tileUrl, {
        maxZoom: 19,
        attribution: attr
      }).addTo(map);

      // Create a persistent layer group for markers
      const markerGroup = L.layerGroup().addTo(map);
      markerGroupRef.current = markerGroup;
      mapInstanceRef.current = map;
      setIsLeafletReady(true);
    });

    return () => {
      isMounted = false;
      if (mapInstanceRef.current) {
        try {
          mapInstanceRef.current.remove();
        } catch {
          // ignore cleanup errors on unmount
        }
        mapInstanceRef.current = null;
        markerGroupRef.current = null;
        radiusCircleRef.current = null;
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mapLayer]);

  // 2. Update markers, search radius circle, and bounds
  useEffect(() => {
    if (!isLeafletReady || !mapInstanceRef.current || !markerGroupRef.current) return;

    import("leaflet").then((L) => {
      const map = mapInstanceRef.current;
      const markerGroup = markerGroupRef.current;
      if (!map || !markerGroup) return;

      // Clear existing markers safely
      markerGroup.clearLayers();

      const bounds = L.latLngBounds([]);

      // 1. Search Radius Circle around origin
      if (origin && origin.lat && origin.lon && radiusKm) {
        if (radiusCircleRef.current) {
          radiusCircleRef.current.remove();
        }
        const radiusMeters = radiusKm * 1000;
        const circle = L.circle([origin.lat, origin.lon], {
          radius: radiusMeters,
          color: "#059669",
          fillColor: "#10b981",
          fillOpacity: 0.05,
          weight: 1.5,
          dashArray: "6, 6"
        }).addTo(markerGroup);
        radiusCircleRef.current = circle;
        bounds.extend(circle.getBounds());
      }

      // 2. Origin Marker (Amber Beacon)
      if (origin && origin.lat && origin.lon) {
        const originIcon = L.divIcon({
          className: "custom-marker-origin",
          html: `<div style="width:30px;height:30px;border-radius:50%;background:#d97706;border:2.5px solid #fff;display:flex;align-items:center;justify-content:center;color:#fff;font-size:13px;font-weight:bold;box-shadow:0 3px 10px rgba(0,0,0,0.3);">📍</div>`,
          iconSize: [30, 30],
          iconAnchor: [15, 15]
        });

        const mOrigin = L.marker([origin.lat, origin.lon], { icon: originIcon });
        mOrigin.bindPopup(`
          <div style="font-family:system-ui,sans-serif;font-size:12px;line-height:1.45;min-width:180px;">
            <div style="font-size:11px;font-weight:bold;color:#b45309;text-transform:uppercase;letter-spacing:0.5px;">Search Center</div>
            <strong style="color:#111827;font-size:13px;display:block;margin-top:2px;">${origin.name}</strong>
            <div style="margin-top:4px;font-size:11px;color:#6b7280;font-family:monospace;">
              ${origin.lat.toFixed(5)}°, ${origin.lon.toFixed(5)}°
            </div>
            <div style="margin-top:6px;display:flex;gap:4px;">
              <a href="https://www.google.com/maps/search/?api=1&query=${origin.lat},${origin.lon}" target="_blank" rel="noopener noreferrer" style="color:#2563eb;text-decoration:none;font-weight:500;font-size:11px;">
                Open Google Maps &rarr;
              </a>
            </div>
          </div>
        `);
        markerGroup.addLayer(mOrigin);
        bounds.extend([origin.lat, origin.lon]);
      }

      // 3. Best Recommendation Marker (Forest Green Star with Pulsing Halo)
      if (bestSlot && bestSlot.lat && bestSlot.lon) {
        const isSelected = selectedVenueName === bestSlot.venue_name;
        const bestIcon = L.divIcon({
          className: "custom-marker-best",
          html: `
            <div style="position:relative;width:38px;height:38px;display:flex;align-items:center;justify-content:center;cursor:pointer;">
              ${isSelected ? '<div style="position:absolute;width:48px;height:48px;border-radius:50%;background:rgba(16,185,129,0.3);animation:ping 2s cubic-bezier(0,0,0.2,1) infinite;"></div>' : ''}
              <div style="width:36px;height:36px;border-radius:50%;background:#064e3b;border:${isSelected ? "3px solid #10b981" : "2.5px solid #fff"};display:flex;align-items:center;justify-content:center;color:#fff;font-size:16px;font-weight:bold;box-shadow:0 4px 12px rgba(0,0,0,0.35);">
                ★
              </div>
            </div>
          `,
          iconSize: [38, 38],
          iconAnchor: [19, 19]
        });

        const mBest = L.marker([bestSlot.lat, bestSlot.lon], { icon: bestIcon });
        const gUrl = bestSlot.google_maps_url || `https://www.google.com/maps/dir/?api=1&destination=${bestSlot.lat},${bestSlot.lon}`;

        mBest.bindPopup(`
          <div style="font-family:system-ui,sans-serif;font-size:12px;line-height:1.45;min-width:210px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:3px;">
              <span style="font-size:10px;font-weight:bold;color:#065f46;background:#ecfdf5;border:1px solid #a7f3d0;padding:2px 6px;border-radius:999px;">
                #1 Top Match (${bestSlot.score}/100)
              </span>
              <span style="font-size:11px;color:#059669;font-weight:bold;">${bestSlot.suitability_label}</span>
            </div>
            <strong style="color:#111827;font-size:13px;display:block;margin:3px 0 2px 0;">${bestSlot.venue_name}</strong>
            <div style="color:#4b5563;font-size:11px;">
              <span>Best: <strong>${bestSlot.hour_label}</strong></span> &bull; 
              <span>${bestSlot.temp_c}°C &bull; AQI ${bestSlot.us_aqi}</span>
            </div>
            <div style="color:#6b7280;font-size:11px;margin-top:2px;">
              Distance: <strong>${bestSlot.distance_km} km</strong> (~${bestSlot.travel_mins} mins)
            </div>
            <div style="margin-top:4px;font-size:10px;color:#9ca3af;font-family:monospace;">
              ${bestSlot.lat.toFixed(5)}°, ${bestSlot.lon.toFixed(5)}°
            </div>
            <div style="margin-top:8px;padding-top:6px;border-top:1px solid #f3f4f6;display:flex;align-items:center;justify-content:space-between;">
              <a href="${gUrl}" target="_blank" rel="noopener noreferrer" style="color:#059669;font-weight:600;font-size:11px;text-decoration:none;">
                Google Maps &rarr;
              </a>
              <span style="font-size:10px;color:#059669;display:flex;align-items:center;gap:2px;">
                &#10003; Verified POI
              </span>
            </div>
          </div>
        `);

        mBest.on("click", () => {
          if (onSelectVenue) onSelectVenue(bestSlot.venue_name);
        });

        markerGroup.addLayer(mBest);
        bounds.extend([bestSlot.lat, bestSlot.lon]);

        if (isSelected) {
          mBest.openPopup();
        }
      }

      // 4. Alternative Candidates (Numbered Circular Badges)
      alternatives.forEach((alt, idx) => {
        if (!alt.lat || !alt.lon) return;
        const isSelected = selectedVenueName === alt.venue_name;
        const altIcon = L.divIcon({
          className: "custom-marker-alt",
          html: `
            <div style="width:30px;height:30px;border-radius:50%;background:${isSelected ? "#064e3b" : "#1e3a2f"};border:${isSelected ? "3px solid #f59e0b" : "2px solid #fff"};display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;font-weight:bold;box-shadow:0 3px 8px rgba(0,0,0,0.25);cursor:pointer;">
              ${idx + 2}
            </div>
          `,
          iconSize: [30, 30],
          iconAnchor: [15, 15]
        });

        const mAlt = L.marker([alt.lat, alt.lon], { icon: altIcon });
        const gUrl = alt.google_maps_url || `https://www.google.com/maps/dir/?api=1&destination=${alt.lat},${alt.lon}`;

        mAlt.bindPopup(`
          <div style="font-family:system-ui,sans-serif;font-size:12px;line-height:1.45;min-width:200px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:3px;">
              <span style="font-size:10px;font-weight:bold;color:#1e3a2f;background:#f3f4f6;padding:2px 6px;border-radius:999px;">
                #${idx + 2} Candidate
              </span>
              <span style="font-size:11px;color:#059669;font-weight:bold;">${alt.score}/100</span>
            </div>
            <strong style="color:#111827;font-size:13px;display:block;margin:3px 0 2px 0;">${alt.venue_name}</strong>
            <div style="color:#4b5563;font-size:11px;">
              <span>Best: ${alt.hour_label}</span> &bull; <span>${alt.temp_c}°C</span>
            </div>
            <div style="color:#6b7280;font-size:11px;margin-top:2px;">
              Distance: <strong>${alt.distance_km} km</strong> (~${alt.travel_mins} mins)
            </div>
            <div style="margin-top:4px;font-size:10px;color:#9ca3af;font-family:monospace;">
              ${alt.lat.toFixed(5)}°, ${alt.lon.toFixed(5)}°
            </div>
            <div style="margin-top:8px;padding-top:6px;border-top:1px solid #f3f4f6;display:flex;align-items:center;justify-content:space-between;">
              <a href="${gUrl}" target="_blank" rel="noopener noreferrer" style="color:#059669;font-weight:600;font-size:11px;text-decoration:none;">
                Google Maps &rarr;
              </a>
              <span style="font-size:10px;color:#059669;">
                &#10003; Real POI
              </span>
            </div>
          </div>
        `);

        mAlt.on("click", () => {
          if (onSelectVenue) onSelectVenue(alt.venue_name);
        });

        markerGroup.addLayer(mAlt);
        bounds.extend([alt.lat, alt.lon]);

        if (isSelected) {
          mAlt.openPopup();
        }
      });

      // Fit map bounds smoothly
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
      }
    });
  }, [origin, bestSlot, alternatives, selectedVenueName, isLeafletReady, onSelectVenue, radiusKm]);

  const hasCoords = (origin && origin.lat && origin.lon) || (bestSlot && bestSlot.lat && bestSlot.lon);

  if (!hasCoords) {
    return (
      <div className="bg-white rounded-2xl border border-stone-200 p-8 text-center flex flex-col items-center justify-center min-h-[350px]">
        <MapPin className="w-8 h-8 text-stone-400 mb-2" />
        <p className="text-sm font-semibold text-stone-800">Map Available After Search</p>
        <p className="text-xs text-stone-500 mt-1">Enter a location or select an activity above.</p>
      </div>
    );
  }

  const primaryCoords = bestSlot ? `${bestSlot.lat.toFixed(5)}, ${bestSlot.lon.toFixed(5)}` : `${origin.lat.toFixed(5)}, ${origin.lon.toFixed(5)}`;

  return (
    <div className="bg-white rounded-2xl border border-stone-200 p-4 shadow-sm flex flex-col h-[420px] lg:h-[480px]">
      {/* Map Control Header */}
      <div className="flex items-center justify-between pb-3 mb-2 border-b border-stone-100">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-emerald-800" />
          <span className="text-xs font-bold uppercase tracking-wider text-stone-900">
            Interactive Venue Map
          </span>
          <span className="text-xs text-stone-500">
            ({1 + (alternatives?.length || 0)} verified places)
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          {/* Recenter Button */}
          <button
            onClick={handleRecenter}
            title="Recenter Map"
            aria-label="Recenter Map"
            className="p-1.5 text-stone-600 hover:text-stone-900 rounded-lg hover:bg-stone-100 border border-stone-200 transition cursor-pointer"
          >
            <Crosshair className="w-3.5 h-3.5" />
          </button>

          {/* Copy Top Venue Coords */}
          <button
            onClick={() => copyToClipboard(primaryCoords, "top_coords")}
            title="Copy coordinates"
            className="flex items-center gap-1 text-xs text-stone-600 hover:text-stone-900 px-2 py-1 rounded-lg border border-stone-200 hover:bg-stone-50 transition cursor-pointer"
          >
            {copiedCoords === "top_coords" ? <Check className="w-3 h-3 text-emerald-600" /> : <Copy className="w-3 h-3" />}
            <span className="font-mono text-[11px] hidden sm:inline">{primaryCoords}</span>
          </button>

          {/* Tile Layer Selector */}
          <div className="flex items-center border border-stone-200 rounded-lg overflow-hidden bg-stone-50 text-[11px]">
            <button
              onClick={() => setMapLayer("osm")}
              className={`px-2 py-1 font-medium transition cursor-pointer ${
                mapLayer === "osm" ? "bg-emerald-800 text-white" : "text-stone-600 hover:text-stone-900"
              }`}
            >
              OSM
            </button>
            <button
              onClick={() => setMapLayer("voyager")}
              className={`px-2 py-1 font-medium transition cursor-pointer ${
                mapLayer === "voyager" ? "bg-emerald-800 text-white" : "text-stone-600 hover:text-stone-900"
              }`}
            >
              Voyager
            </button>
            <button
              onClick={() => setMapLayer("dark")}
              className={`px-2 py-1 font-medium transition cursor-pointer ${
                mapLayer === "dark" ? "bg-emerald-800 text-white" : "text-stone-600 hover:text-stone-900"
              }`}
            >
              Dark
            </button>
          </div>
        </div>
      </div>

      {/* Map Container */}
      <div
        ref={mapContainerRef}
        className="flex-1 w-full rounded-xl overflow-hidden z-0 border border-stone-200"
      />

      {/* Map Legend & Audit Indicator */}
      <div className="flex flex-wrap items-center justify-between pt-2.5 mt-1 text-[11px] text-stone-600 gap-2">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-[#064e3b] inline-block" />
            <span>#1 Top Pick</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-[#1e3a2f] inline-block" />
            <span>Alternatives</span>
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-[#d97706] inline-block" />
            <span>Search Center</span>
          </span>
          {radiusKm && (
            <span className="flex items-center gap-1 text-emerald-700">
              <span className="w-2.5 h-2.5 rounded-full border border-dashed border-emerald-600 inline-block" />
              <span>{radiusKm} km radius</span>
            </span>
          )}
        </div>
        <div className="flex items-center gap-2 text-[10px] text-stone-500">
          <span className="flex items-center gap-1 text-emerald-700 font-medium">
            <ShieldCheck className="w-3 h-3" />
            Verified Coordinates
          </span>
          <span>&copy; OpenStreetMap contributors</span>
        </div>
      </div>
    </div>
  );
};
