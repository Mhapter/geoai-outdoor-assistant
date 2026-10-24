"""
Location Provider Abstraction for Fieldwise Outdoor Intelligence.
Supports:
1. Direct coordinate parsing (lat, lon) with automated reverse geocoding.
2. Google Maps Platform Places API (New) Text Search & Nearby Search when API key is provided.
3. OpenStreetMap multi-engine fallback (Nominatim + Photon + Open-Meteo Geocoding).
4. Authoritative verified landmark gazetteer with exact token boundaries.
"""

import os
import re
import math
import httpx
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import diskcache

from app.schemas.location_models import (
    NormalizedLocation,
    VerificationStatus,
)

logger = logging.getLogger("fieldwise.geocoding")
from app.cache import cache
CACHE_TTL = 86400  # 24 hours for spatial lookups

USER_AGENT = "Fieldwise-Outdoor-Intelligence/2.0 (CSRE IIT Bombay GeoAI; contact: geoai@csre.iitb.ac.in)"

# Curated reference locations with authoritative ground-truth coordinates
AUTHORITATIVE_GAZETTEER: Dict[str, Dict[str, Any]] = {
    "bennett university": {
        "id": "ref_bennett_university",
        "name": "Bennett University",
        "formatted_address": "Bennett University, Plot Nos 8-11, TechZone 2, Greater Noida, Gautam Buddha Nagar, Uttar Pradesh 201310, India",
        "lat": 28.450628,
        "lon": 77.583925,
        "category": "university_campus",
        "locality": "Greater Noida",
        "region": "Uttar Pradesh",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=28.450628,77.583925"
    },
    "iit bombay": {
        "id": "ref_iit_bombay",
        "name": "Indian Institute of Technology Bombay",
        "formatted_address": "IIT Bombay Main Gate, Powai, Mumbai, Maharashtra 400076, India",
        "lat": 19.133444,
        "lon": 72.913333,
        "category": "university_campus",
        "locality": "Mumbai",
        "region": "Maharashtra",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=19.133444,72.913333"
    },
    "iitb": {
        "id": "ref_iit_bombay",
        "name": "Indian Institute of Technology Bombay",
        "formatted_address": "IIT Bombay Main Gate, Powai, Mumbai, Maharashtra 400076, India",
        "lat": 19.133444,
        "lon": 72.913333,
        "category": "university_campus",
        "locality": "Mumbai",
        "region": "Maharashtra",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=19.133444,72.913333"
    },
    "iit delhi": {
        "id": "ref_iit_delhi",
        "name": "Indian Institute of Technology Delhi",
        "formatted_address": "IIT Delhi, Hauz Khas, New Delhi, Delhi 110016, India",
        "lat": 28.544976,
        "lon": 77.192627,
        "category": "university_campus",
        "locality": "New Delhi",
        "region": "Delhi",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=28.544976,77.192627"
    },
    "iit madras": {
        "id": "ref_iit_madras",
        "name": "Indian Institute of Technology Madras",
        "formatted_address": "IIT Madras, Sardar Patel Road, Chennai, Tamil Nadu 600036, India",
        "lat": 12.991510,
        "lon": 80.233720,
        "category": "university_campus",
        "locality": "Chennai",
        "region": "Tamil Nadu",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=12.991510,80.233720"
    },
    "cubbon park": {
        "id": "ref_cubbon_park",
        "name": "Cubbon Park",
        "formatted_address": "Cubbon Park, Kasturba Road, Bengaluru, Karnataka 560001, India",
        "lat": 12.976353,
        "lon": 77.592918,
        "category": "park",
        "locality": "Bengaluru",
        "region": "Karnataka",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=12.976353,77.592918"
    },
    "lodhi garden": {
        "id": "ref_lodhi_garden",
        "name": "Lodhi Garden",
        "formatted_address": "Lodhi Garden, Lodhi Road, New Delhi, Delhi 110003, India",
        "lat": 28.593100,
        "lon": 77.219700,
        "category": "park",
        "locality": "New Delhi",
        "region": "Delhi",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=28.593100,77.219700"
    },
    "marine drive": {
        "id": "ref_marine_drive",
        "name": "Marine Drive",
        "formatted_address": "Marine Drive Promenade, Netaji Subhash Chandra Bose Road, Mumbai, Maharashtra 400020, India",
        "lat": 18.943200,
        "lon": 72.823000,
        "category": "promenade",
        "locality": "Mumbai",
        "region": "Maharashtra",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=18.943200,72.823000"
    },
    "koregaon park": {
        "id": "ref_koregaon_park",
        "name": "Koregaon Park",
        "formatted_address": "Koregaon Park, Pune, Maharashtra 411001, India",
        "lat": 18.536200,
        "lon": 73.894000,
        "category": "locality",
        "locality": "Pune",
        "region": "Maharashtra",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=18.536200,73.894000"
    },
    "whitefield": {
        "id": "ref_whitefield",
        "name": "Whitefield",
        "formatted_address": "Whitefield, Bengaluru, Karnataka 560066, India",
        "lat": 12.969800,
        "lon": 77.750000,
        "category": "locality",
        "locality": "Bengaluru",
        "region": "Karnataka",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=12.969800,77.750000"
    },
    "greater noida": {
        "id": "ref_greater_noida",
        "name": "Greater Noida",
        "formatted_address": "Greater Noida, Gautam Buddha Nagar, Uttar Pradesh, India",
        "lat": 28.474400,
        "lon": 77.504000,
        "category": "city",
        "locality": "Greater Noida",
        "region": "Uttar Pradesh",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=28.474400,77.504000"
    },
    "pari chowk": {
        "id": "ref_pari_chowk",
        "name": "Pari Chowk",
        "formatted_address": "Pari Chowk, Greater Noida, Uttar Pradesh 201310, India",
        "lat": 28.468200,
        "lon": 77.514200,
        "category": "junction",
        "locality": "Greater Noida",
        "region": "Uttar Pradesh",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=28.468200,77.514200"
    },
    "powai": {
        "id": "ref_powai",
        "name": "Powai",
        "formatted_address": "Powai, Mumbai, Maharashtra 400076, India",
        "lat": 19.119700,
        "lon": 72.905100,
        "category": "locality",
        "locality": "Mumbai",
        "region": "Maharashtra",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=19.119700,72.905100"
    },
    "powai lake": {
        "id": "ref_powai_lake",
        "name": "Powai Lake",
        "formatted_address": "Powai Lake, Powai, Mumbai, Maharashtra 400076, India",
        "lat": 19.125000,
        "lon": 72.905000,
        "category": "lake",
        "locality": "Mumbai",
        "region": "Maharashtra",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=19.125000,72.905000"
    },
    "lonavala": {
        "id": "ref_lonavala",
        "name": "Lonavala",
        "formatted_address": "Lonavala, Pune District, Maharashtra 410401, India",
        "lat": 18.754600,
        "lon": 73.406200,
        "category": "town",
        "locality": "Lonavala",
        "region": "Maharashtra",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=18.754600,73.406200"
    },
    "bandra": {
        "id": "ref_bandra",
        "name": "Bandra West",
        "formatted_address": "Bandra West, Mumbai, Maharashtra 400050, India",
        "lat": 19.059600,
        "lon": 72.829500,
        "category": "locality",
        "locality": "Mumbai",
        "region": "Maharashtra",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=19.059600,72.829500"
    },
    "noida": {
        "id": "ref_noida",
        "name": "Noida",
        "formatted_address": "Noida, Gautam Buddha Nagar, Uttar Pradesh, India",
        "lat": 28.535500,
        "lon": 77.391000,
        "category": "city",
        "locality": "Noida",
        "region": "Uttar Pradesh",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=28.535500,77.391000"
    },
    "noida stadium": {
        "id": "ref_noida_stadium",
        "name": "Noida Stadium",
        "formatted_address": "Noida Stadium, Sector 21A, Noida, Gautam Buddha Nagar, Uttar Pradesh 201301, India",
        "lat": 28.591000,
        "lon": 77.338000,
        "category": "sports_centre",
        "locality": "Noida",
        "region": "Uttar Pradesh",
        "country": "India",
        "google_maps_url": "https://www.google.com/maps/search/?api=1&query=28.591000,77.338000"
    }
}


def parse_explicit_coordinates(text: str) -> Optional[Tuple[float, float]]:
    """
    Detects if a user input string represents explicit geographical coordinates.
    Supports:
    - 28.4506, 77.5839
    - 28.4506,77.5839
    - 28.4506 N, 77.5839 E
    - lat: 28.4506, lon: 77.5839
    - 28.4506 77.5839
    Returns (lat, lon) or None if not coordinates.
    """
    clean = text.strip()
    # Pattern 1: lat, lon with optional N/S/E/W
    p1 = re.match(
        r"^(?:lat(?:itude)?[:\s]*)?([+-]?\d+(?:\.\d+)?)\s*(?:[°\s]*([NS]))?[,\s]+(?:lon(?:gitude)?[:\s]*)?([+-]?\d+(?:\.\d+)?)\s*(?:[°\s]*([EW]))?$",
        clean,
        re.IGNORECASE
    )
    if p1:
        lat = float(p1.group(1))
        lat_dir = (p1.group(2) or "").upper()
        lon = float(p1.group(3))
        lon_dir = (p1.group(4) or "").upper()

        if lat_dir == "S" and lat > 0:
            lat = -lat
        if lon_dir == "W" and lon > 0:
            lon = -lon

        if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
            return (lat, lon)

    return None


class BaseLocationProvider(ABC):
    """Abstract contract for location geocoding and search providers."""

    @abstractmethod
    async def geocode(
        self,
        query: str,
        near_lat: Optional[float] = None,
        near_lon: Optional[float] = None,
        radius_km: float = 10.0,
        limit: int = 5
    ) -> List[NormalizedLocation]:
        pass

    @abstractmethod
    async def reverse_geocode(self, lat: float, lon: float) -> Optional[NormalizedLocation]:
        pass

    @abstractmethod
    async def autocomplete(
        self,
        query: str,
        near_lat: Optional[float] = None,
        near_lon: Optional[float] = None,
        limit: int = 6
    ) -> List[Dict[str, Any]]:
        pass


class GooglePlacesProvider(BaseLocationProvider):
    """
    Location provider using Google Maps Platform Places API (New).
    Used when GOOGLE_MAPS_API_KEY or GOOGLE_PLACES_API_KEY is configured.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key.strip()
        self.text_search_url = "https://places.googleapis.com/v1/places:searchText"
        self.nearby_search_url = "https://places.googleapis.com/v1/places:searchNearby"
        self.reverse_geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"

    async def geocode(
        self,
        query: str,
        near_lat: Optional[float] = None,
        near_lon: Optional[float] = None,
        radius_km: float = 10.0,
        limit: int = 5
    ) -> List[NormalizedLocation]:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.types,places.googleMapsUri,places.addressComponents"
        }
        body: Dict[str, Any] = {
            "textQuery": query,
            "pageSize": min(limit, 10),
            "languageCode": "en"
        }
        if near_lat is not None and near_lon is not None:
            body["locationBias"] = {
                "circle": {
                    "center": {"latitude": near_lat, "longitude": near_lon},
                    "radius": radius_km * 1000.0
                }
            }

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.post(self.text_search_url, json=body, headers=headers)
                if resp.status_code == 200:
                    places = resp.json().get("places", [])
                    results: List[NormalizedLocation] = []
                    for p in places:
                        loc = p.get("location", {})
                        p_lat = loc.get("latitude")
                        p_lon = loc.get("longitude")
                        if p_lat is None or p_lon is None:
                            continue

                        name = p.get("displayName", {}).get("text", query)
                        addr = p.get("formattedAddress", name)
                        g_url = p.get("googleMapsUri") or f"https://www.google.com/maps/search/?api=1&query={p_lat},{p_lon}"
                        types = p.get("types", [])
                        category = types[0] if types else "point_of_interest"

                        # Extract locality / region from address components
                        locality, region, country = None, None, None
                        for comp in p.get("addressComponents", []):
                            c_types = comp.get("types", [])
                            if "locality" in c_types:
                                locality = comp.get("longText")
                            elif "administrative_area_level_1" in c_types:
                                region = comp.get("longText")
                            elif "country" in c_types:
                                country = comp.get("longText")

                        results.append(NormalizedLocation(
                            id=p.get("id", f"google_{p_lat}_{p_lon}"),
                            name=name,
                            formatted_address=addr,
                            lat=float(p_lat),
                            lon=float(p_lon),
                            category=category,
                            provider="google_places",
                            verification_status=VerificationStatus.VERIFIED,
                            google_maps_url=g_url,
                            locality=locality,
                            region=region,
                            country=country,
                            metadata={"types": types, "place_id": p.get("id")}
                        ))
                    return results
        except Exception as e:
            logger.warning("Google Places API error: %s", e)

        return []

    async def reverse_geocode(self, lat: float, lon: float) -> Optional[NormalizedLocation]:
        params = {
            "latlng": f"{lat},{lon}",
            "key": self.api_key,
            "language": "en"
        }
        try:
            async with httpx.AsyncClient(timeout=3.5) as client:
                resp = await client.get(self.reverse_geocode_url, params=params)
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    if results:
                        top = results[0]
                        p_id = top.get("place_id", f"google_{lat}_{lon}")
                        addr = top.get("formatted_address", f"{lat:.5f}, {lon:.5f}")
                        locality, region, country = None, None, None
                        for comp in top.get("address_components", []):
                            c_types = comp.get("types", [])
                            if "locality" in c_types:
                                locality = comp.get("long_name")
                            elif "administrative_area_level_1" in c_types:
                                region = comp.get("long_name")
                            elif "country" in c_types:
                                country = comp.get("long_name")

                        return NormalizedLocation(
                            id=p_id,
                            name=locality or addr.split(",")[0],
                            formatted_address=addr,
                            lat=lat,
                            lon=lon,
                            category="locality",
                            provider="google_places",
                            verification_status=VerificationStatus.VERIFIED,
                            google_maps_url=f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
                            locality=locality,
                            region=region,
                            country=country,
                            metadata={"place_id": p_id}
                        )
        except Exception as e:
            logger.warning("Google Reverse Geocode error: %s", e)
        return None

    async def autocomplete(
        self,
        query: str,
        near_lat: Optional[float] = None,
        near_lon: Optional[float] = None,
        limit: int = 6
    ) -> List[Dict[str, Any]]:
        # Places Autocomplete (New)
        url = "https://places.googleapis.com/v1/places:autocomplete"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key
        }
        body: Dict[str, Any] = {
            "input": query,
            "languageCode": "en"
        }
        if near_lat is not None and near_lon is not None:
            body["locationBias"] = {
                "circle": {
                    "center": {"latitude": near_lat, "longitude": near_lon},
                    "radius": 25000.0
                }
            }

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.post(url, json=body, headers=headers)
                if resp.status_code == 200:
                    suggestions = resp.json().get("suggestions", [])
                    out = []
                    for s in suggestions[:limit]:
                        pred = s.get("placePrediction", {})
                        text = pred.get("text", {}).get("text", "")
                        main = pred.get("structuredFormat", {}).get("mainText", {}).get("text", text)
                        sec = pred.get("structuredFormat", {}).get("secondaryText", {}).get("text", "")
                        p_id = pred.get("placeId", "")
                        out.append({
                            "name": main,
                            "description": sec,
                            "full_name": text,
                            "place_id": p_id,
                            "provider": "google_places",
                            "type": "google_place"
                        })
                    return out
        except Exception as e:
            logger.warning("Google Autocomplete error: %s", e)
        return []


class OpenStreetMapProvider(BaseLocationProvider):
    """
    Robust OpenStreetMap provider using Nominatim, Photon, and Open-Meteo Geocoding.
    Configured with proper User-Agent, timeouts, error recovery, and structured addresses.
    """

    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.nominatim_reverse_url = "https://nominatim.openstreetmap.org/reverse"
        self.photon_url = "https://photon.komoot.io/api/"
        self.openmeteo_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.headers = {"User-Agent": USER_AGENT, "Accept-Language": "en"}

    async def geocode(
        self,
        query: str,
        near_lat: Optional[float] = None,
        near_lon: Optional[float] = None,
        radius_km: float = 10.0,
        limit: int = 5
    ) -> List[NormalizedLocation]:
        results: List[NormalizedLocation] = []
        seen_keys = set()

        def add_res(nl: NormalizedLocation):
            k = (round(nl.lat, 4), round(nl.lon, 4))
            if k not in seen_keys:
                seen_keys.add(k)
                results.append(nl)

        clean_q = query.strip()

        # Step 1: Query Nominatim with structured address details
        try:
            params = {
                "q": clean_q,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": limit
            }
            if near_lat is not None and near_lon is not None:
                # Add bounded viewbox if near coords exist
                deg_offset = radius_km / 111.0
                params["viewbox"] = f"{near_lon - deg_offset},{near_lat + deg_offset},{near_lon + deg_offset},{near_lat - deg_offset}"
                params["bounded"] = 0

            async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
                resp = await client.get(self.nominatim_url, params=params, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data:
                        lat = float(item["lat"])
                        lon = float(item["lon"])
                        addr = item.get("address", {})
                        loc = (
                            addr.get("city") or
                            addr.get("town") or
                            addr.get("suburb") or
                            addr.get("village") or
                            addr.get("county")
                        )
                        reg = addr.get("state")
                        cntry = addr.get("country")
                        cat = item.get("category") or item.get("type") or "poi"
                        name = item.get("name") or addr.get(cat) or clean_q.title()

                        add_res(NormalizedLocation(
                            id=f"osm_nom_{item.get('osm_type', 'node')}_{item.get('osm_id', '')}",
                            name=name,
                            formatted_address=item.get("display_name", clean_q),
                            lat=lat,
                            lon=lon,
                            category=cat,
                            provider="osm_nominatim",
                            verification_status=VerificationStatus.UNVERIFIED,
                            google_maps_url=f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
                            locality=loc,
                            region=reg,
                            country=cntry,
                            postal_code=addr.get("postcode"),
                            metadata={"osm_id": item.get("osm_id"), "place_rank": item.get("place_rank")}
                        ))
        except Exception as e:
            logger.warning("Nominatim geocode failed: %s", e)

        # Step 2: Query Photon (Komoot OSM POI Engine) if Nominatim results are sparse
        if len(results) < limit:
            try:
                p_params: Dict[str, Any] = {"q": clean_q, "limit": limit}
                if near_lat is not None and near_lon is not None:
                    p_params["lat"] = near_lat
                    p_params["lon"] = near_lon

                async with httpx.AsyncClient(timeout=3.5, follow_redirects=True) as client:
                    resp = await client.get(self.photon_url, params=p_params, headers=self.headers)
                    if resp.status_code == 200:
                        feats = resp.json().get("features", [])
                        for f in feats:
                            props = f.get("properties", {})
                            geom = f.get("geometry", {}).get("coordinates", [])
                            if len(geom) >= 2:
                                p_lon, p_lat = float(geom[0]), float(geom[1])
                                p_name = props.get("name") or clean_q.title()
                                disp_parts = [
                                    p_name,
                                    props.get("street"),
                                    props.get("city") or props.get("district"),
                                    props.get("state"),
                                    props.get("country")
                                ]
                                full_addr = ", ".join(p for p in disp_parts if p)

                                add_res(NormalizedLocation(
                                    id=f"osm_photon_{props.get('osm_id', f'{p_lat}_{p_lon}')}",
                                    name=p_name,
                                    formatted_address=full_addr,
                                    lat=p_lat,
                                    lon=p_lon,
                                    category=props.get("osm_value") or props.get("osm_key") or "point_of_interest",
                                    provider="osm_photon",
                                    verification_status=VerificationStatus.UNVERIFIED,
                                    google_maps_url=f"https://www.google.com/maps/search/?api=1&query={p_lat},{p_lon}",
                                    locality=props.get("city") or props.get("district"),
                                    region=props.get("state"),
                                    country=props.get("country"),
                                    postal_code=props.get("postcode"),
                                    metadata=props
                                ))
            except Exception as e:
                logger.warning("Photon geocode failed: %s", e)

        # Step 3: Open-Meteo Geocoding for major cities & districts
        if len(results) < limit:
            try:
                async with httpx.AsyncClient(timeout=3.0, follow_redirects=True) as client:
                    resp = await client.get(
                        self.openmeteo_url,
                        params={"name": clean_q, "count": limit, "language": "en", "format": "json"},
                        headers=self.headers
                    )
                    if resp.status_code == 200:
                        om_res = resp.json().get("results", [])
                        for item in om_res:
                            lat = float(item["latitude"])
                            lon = float(item["longitude"])
                            p_name = item.get("name", clean_q.title())
                            parts = [p_name, item.get("admin2"), item.get("admin1"), item.get("country")]
                            full_addr = ", ".join(p for p in parts if p)

                            add_res(NormalizedLocation(
                                id=f"openmeteo_{item.get('id', f'{lat}_{lon}')}",
                                name=p_name,
                                formatted_address=full_addr,
                                lat=lat,
                                lon=lon,
                                category="city",
                                provider="open_meteo",
                                verification_status=VerificationStatus.UNVERIFIED,
                                google_maps_url=f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
                                locality=item.get("name"),
                                region=item.get("admin1"),
                                country=item.get("country"),
                                metadata=item
                            ))
            except Exception as e:
                logger.warning("Open-Meteo geocode failed: %s", e)

        return results[:limit]

    async def reverse_geocode(self, lat: float, lon: float) -> Optional[NormalizedLocation]:
        cache_key = f"osm_rev_v2:{round(lat, 5)}:{round(lon, 5)}"
        if cache_key in cache:
            return NormalizedLocation(**cache[cache_key])

        params = {
            "lat": lat,
            "lon": lon,
            "format": "jsonv2",
            "addressdetails": 1,
            "zoom": 18
        }
        try:
            async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
                resp = await client.get(self.nominatim_reverse_url, params=params, headers=self.headers)
                if resp.status_code == 200:
                    data = resp.json()
                    addr = data.get("address", {})
                    loc = (
                        addr.get("city") or
                        addr.get("town") or
                        addr.get("suburb") or
                        addr.get("village") or
                        addr.get("neighbourhood") or
                        addr.get("county")
                    )
                    name = data.get("name") or loc or data.get("display_name", f"{lat:.4f}, {lon:.4f}").split(",")[0]
                    reg = addr.get("state")
                    cntry = addr.get("country")

                    res = NormalizedLocation(
                        id=f"osm_rev_{data.get('osm_id', f'{lat}_{lon}')}",
                        name=name,
                        formatted_address=data.get("display_name", f"{lat:.5f}, {lon:.5f}"),
                        lat=lat,
                        lon=lon,
                        category=data.get("category") or data.get("type") or "place",
                        provider="osm_nominatim_reverse",
                        verification_status=VerificationStatus.VERIFIED,
                        google_maps_url=f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
                        locality=loc,
                        region=reg,
                        country=cntry,
                        postal_code=addr.get("postcode"),
                        metadata={"osm_id": data.get("osm_id")}
                    )
                    cache.set(cache_key, res.model_dump(), expire=CACHE_TTL)
                    return res
        except Exception as e:
            logger.warning("OSM reverse geocode failed: %s", e)
        return None

    async def autocomplete(
        self,
        query: str,
        near_lat: Optional[float] = None,
        near_lon: Optional[float] = None,
        limit: int = 6
    ) -> List[Dict[str, Any]]:
        clean_q = query.strip()
        if len(clean_q) < 2:
            return []

        suggestions: List[Dict[str, Any]] = []
        seen = set()

        try:
            params: Dict[str, Any] = {"q": clean_q, "limit": limit * 2}
            if near_lat is not None and near_lon is not None:
                params["lat"] = near_lat
                params["lon"] = near_lon

            async with httpx.AsyncClient(timeout=2.5, follow_redirects=True) as client:
                resp = await client.get(self.photon_url, params=params, headers=self.headers)
                if resp.status_code == 200:
                    for f in resp.json().get("features", []):
                        props = f.get("properties", {})
                        geom = f.get("geometry", {}).get("coordinates", [])
                        if len(geom) >= 2:
                            lon_val, lat_val = float(geom[0]), float(geom[1])
                            k = (round(lat_val, 2), round(lon_val, 2))
                            if k not in seen:
                                seen.add(k)
                                p_name = props.get("name") or clean_q.title()
                                desc_parts = [
                                    props.get("city") or props.get("district"),
                                    props.get("state"),
                                    props.get("country")
                                ]
                                desc = ", ".join(p for p in desc_parts if p)
                                suggestions.append({
                                    "name": p_name,
                                    "description": desc,
                                    "lat": lat_val,
                                    "lon": lon_val,
                                    "full_name": f"{p_name}, {desc}" if desc else p_name,
                                    "provider": "osm_photon",
                                    "type": props.get("osm_value") or "place"
                                })
                                if len(suggestions) >= limit:
                                    break
        except Exception:
            pass

        return suggestions


class CompositeLocationService:
    """
    Primary Location Service orchestrating Google Places API (New) when key is configured,
    authoritative reference gazetteers, and OpenStreetMap fallbacks.
    Also handles coordinate detection, reverse geocoding, and deduplication.
    """

    def __init__(self):
        google_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("GOOGLE_PLACES_API_KEY") or ""
        self.google_provider = GooglePlacesProvider(google_key) if google_key.strip() else None
        self.osm_provider = OpenStreetMapProvider()

    @property
    def has_google_places(self) -> bool:
        return self.google_provider is not None

    async def search_location(
        self,
        query: str,
        near_lat: Optional[float] = None,
        near_lon: Optional[float] = None,
        radius_km: float = 10.0,
        limit: int = 5
    ) -> List[NormalizedLocation]:
        """
        Unified search pipeline:
        1. Check if query is explicit GPS coordinates.
        2. Check exact authoritative gazetteer matches.
        3. If Google Places API is configured, query Google Places (New).
        4. Query OpenStreetMap providers (Nominatim & Photon).
        5. Return validated NormalizedLocation records.
        """
        if not query or not query.strip():
            return []

        clean_q = query.strip()
        lower_q = clean_q.lower()

        # Step 1: Detect explicit coordinate input
        coords = parse_explicit_coordinates(clean_q)
        if coords:
            c_lat, c_lon = coords
            # Reverse-geocode to discover real address
            rev = await self.reverse_geocode(c_lat, c_lon)
            if rev:
                rev.name = f"Coordinates: {c_lat:.4f}° N, {c_lon:.4f}° E"
                return [rev]
            return [NormalizedLocation(
                id=f"coord_{c_lat}_{c_lon}",
                name=f"GPS Coordinates ({c_lat:.4f}° N, {c_lon:.4f}° E)",
                formatted_address=f"Latitude: {c_lat:.6f}, Longitude: {c_lon:.6f}",
                lat=c_lat,
                lon=c_lon,
                category="coordinates",
                provider="explicit_coordinates",
                verification_status=VerificationStatus.VERIFIED,
                google_maps_url=f"https://www.google.com/maps/search/?api=1&query={c_lat},{c_lon}",
                metadata={"type": "direct_gps_input"}
            )]

        # Step 2: Authoritative gazetteer match
        # Check exact key, or prefix with comma/delimiter (e.g. "bennett university, greater noida" -> "bennett university")
        matched_ref = None
        if lower_q in AUTHORITATIVE_GAZETTEER:
            matched_ref = AUTHORITATIVE_GAZETTEER[lower_q]
        else:
            # Check if query starts with a known landmark followed by locality
            for k, ref in AUTHORITATIVE_GAZETTEER.items():
                if lower_q.startswith(k + ",") or lower_q.startswith(k + " "):
                    loc_name = (ref.get("locality") or "").lower()
                    reg_name = (ref.get("region") or "").lower()
                    rest_of_query = lower_q[len(k):].strip(" ,")
                    if not rest_of_query or (loc_name and loc_name in rest_of_query) or (reg_name and reg_name in rest_of_query):
                        matched_ref = ref
                        break

        if matched_ref:
            return [NormalizedLocation(
                id=matched_ref["id"],
                name=matched_ref["name"],
                formatted_address=matched_ref["formatted_address"],
                lat=matched_ref["lat"],
                lon=matched_ref["lon"],
                category=matched_ref["category"],
                provider="authoritative_gazetteer",
                verification_status=VerificationStatus.VERIFIED,
                google_maps_url=matched_ref["google_maps_url"],
                locality=matched_ref.get("locality"),
                region=matched_ref.get("region"),
                country=matched_ref.get("country"),
                metadata={"gazetteer_match": "exact"}
            )]

        # Step 3: Google Places API if configured
        if self.google_provider:
            g_results = await self.google_provider.geocode(
                clean_q,
                near_lat=near_lat,
                near_lon=near_lon,
                radius_km=radius_km,
                limit=limit
            )
            if g_results:
                return g_results

        # Step 4: OpenStreetMap Provider
        osm_results = await self.osm_provider.geocode(
            clean_q,
            near_lat=near_lat,
            near_lon=near_lon,
            radius_km=radius_km,
            limit=limit
        )
        return osm_results

    async def reverse_geocode(self, lat: float, lon: float) -> Optional[NormalizedLocation]:
        """Reverse geocode with Google provider fallback to OpenStreetMap."""
        if self.google_provider:
            res = await self.google_provider.reverse_geocode(lat, lon)
            if res:
                return res
        return await self.osm_provider.reverse_geocode(lat, lon)

    async def autocomplete(
        self,
        query: str,
        near_lat: Optional[float] = None,
        near_lon: Optional[float] = None,
        limit: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Autocomplete combining authoritative gazetteer matches,
        Google Places Autocomplete (if key available), and OSM Photon.
        """
        clean_q = query.strip()
        lower_q = clean_q.lower()
        if len(clean_q) < 2:
            return []

        suggestions: List[Dict[str, Any]] = []
        seen_names = set()

        # Check gazetteer prefixes
        for k, v in AUTHORITATIVE_GAZETTEER.items():
            if lower_q in k:
                if v["name"] not in seen_names:
                    seen_names.add(v["name"])
                    suggestions.append({
                        "name": v["name"],
                        "description": f"{v.get('locality', '')}, {v.get('region', '')}".strip(" ,"),
                        "lat": v["lat"],
                        "lon": v["lon"],
                        "full_name": v["formatted_address"],
                        "provider": "authoritative_gazetteer",
                        "type": "verified_landmark"
                    })
                    if len(suggestions) >= limit:
                        return suggestions

        # Google autocomplete if available
        if self.google_provider:
            g_suggs = await self.google_provider.autocomplete(clean_q, near_lat, near_lon, limit)
            if g_suggs:
                return g_suggs

        # OpenStreetMap fallback
        osm_suggs = await self.osm_provider.autocomplete(clean_q, near_lat, near_lon, limit - len(suggestions))
        for s in osm_suggs:
            if s["name"] not in seen_names:
                seen_names.add(s["name"])
                suggestions.append(s)

        return suggestions[:limit]


# Global singleton instance
location_service = CompositeLocationService()
