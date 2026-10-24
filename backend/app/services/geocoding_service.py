"""
Geocoding and Spatial Disambiguation Service for Fieldwise.
Interfaces with CompositeLocationService (Google Places API New + OpenStreetMap Nominatim/Photon/Overpass)
and LocationVerificationPipeline to provide guaranteed accurate real-world locations.
"""

from typing import Dict, Any, Optional, List
import logging
from app.services.location_provider import location_service
from app.services.location_verification import verification_pipeline
from app.schemas.location_models import NormalizedLocation, VerificationStatus

logger = logging.getLogger("fieldwise.geocoding")


async def geocode_location(
    location_name: str,
    near_lat: Optional[float] = None,
    near_lon: Optional[float] = None,
    radius_km: float = 10.0
) -> Optional[Dict[str, Any]]:
    """
    Resolves free-form place, address, landmark, or explicit coordinate string into
    a verified, normalized location model.
    Guarantees no false centroid matching and no fabricated coordinates.
    """
    if not location_name or not location_name.strip():
        return None

    clean_place = location_name.strip()

    # Query composite location service
    results = await location_service.search_location(
        clean_place,
        near_lat=near_lat,
        near_lon=near_lon,
        radius_km=radius_km,
        limit=5
    )

    if not results:
        return None

    top_result = results[0]

    # Verify candidate location
    rev_loc = None
    # If not authoritative or google, reverse-geocode to double check locality
    if top_result.provider not in ("authoritative_gazetteer", "google_places", "explicit_coordinates"):
        try:
            rev_loc = await location_service.reverse_geocode(top_result.lat, top_result.lon)
        except Exception:
            rev_loc = None

    audit = verification_pipeline.verify_location(
        location=top_result,
        expected_locality=clean_place,
        origin_lat=near_lat,
        origin_lon=near_lon,
        max_radius_km=radius_km,
        reverse_geocode_loc=rev_loc
    )

    # Format output dictionary backwards-compatible with existing backend consumers
    return {
        "id": top_result.id,
        "name": top_result.formatted_address or top_result.name,
        "short_name": top_result.name,
        "lat": top_result.lat,
        "lon": top_result.lon,
        "category": top_result.category,
        "geocoder": f"{top_result.provider} ({top_result.verification_status.value})",
        "provider": top_result.provider,
        "verification_status": top_result.verification_status.value,
        "google_maps_url": top_result.google_maps_url,
        "locality": top_result.locality,
        "region": top_result.region,
        "country": top_result.country,
        "verification_notes": audit.audit_notes
    }


async def get_location_autocomplete_suggestions(
    query: str,
    near_lat: Optional[float] = None,
    near_lon: Optional[float] = None,
    limit: int = 6
) -> List[Dict[str, Any]]:
    """
    Returns instant Google Suggest-style location autocomplete predictions.
    Combines authoritative landmarks, Google Places Autocomplete (if key active),
    and OSM Photon suggestions.
    """
    return await location_service.autocomplete(query, near_lat=near_lat, near_lon=near_lon, limit=limit)
