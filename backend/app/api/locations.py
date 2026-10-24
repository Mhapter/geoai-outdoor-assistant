"""
Locations, Geocoding, and Verification REST API Endpoints for Fieldwise.
Provides:
- GET /api/locations/search — Multi-provider location search (Google Places API New + OSM)
- GET /api/locations/autocomplete — Fast predictive search
- POST /api/locations/verify — Spatial accuracy and verification pipeline audit
- POST /api/locations/report — User reporting for incorrect coordinates / places
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, status

from app.schemas.location_models import (
    LocationSearchResponse,
    NormalizedLocation,
    LocationVerificationReport,
    ReportLocationIssueRequest,
    ReportLocationIssueResponse,
    VerificationStatus
)
from app.services.location_provider import location_service
from app.services.location_verification import verification_pipeline

router = APIRouter(prefix="/locations", tags=["Locations & Verification"])
logger = logging.getLogger("fieldwise.locations_api")

# Persistent report storage in diskcache or memory
from app.services.location_provider import cache


@router.get("/search", response_model=LocationSearchResponse)
async def search_locations(
    q: str = Query(..., min_length=1, description="Query string: place name, address, coordinates, or landmark"),
    near_lat: Optional[float] = Query(None, description="Latitude for nearby bias"),
    near_lon: Optional[float] = Query(None, description="Longitude for nearby bias"),
    radius_km: float = Query(10.0, ge=0.5, le=100.0, description="Search radius in kilometers"),
    limit: int = Query(5, ge=1, le=20, description="Max results to return")
):
    """
    Searches for locations across Google Places API (New) (if configured),
    curated authoritative gazetteer, and OpenStreetMap (Nominatim & Photon).
    Validates all coordinates and runs automatic spatial verification.
    """
    clean_q = q.strip()
    results = await location_service.search_location(
        query=clean_q,
        near_lat=near_lat,
        near_lon=near_lon,
        radius_km=radius_km,
        limit=limit
    )

    if not results:
        return LocationSearchResponse(
            status="no_results",
            query=clean_q,
            count=0,
            primary_result=None,
            results=[],
            provider_used="none",
            warnings=[f"No matching locations discovered for query: '{clean_q}'"]
        )

    # Deduplicate results within 50m
    deduped = verification_pipeline.deduplicate_locations(results)

    # Run verification pipeline for each candidate
    for loc in deduped:
        verification_pipeline.verify_location(
            location=loc,
            expected_locality=clean_q,
            origin_lat=near_lat,
            origin_lon=near_lon,
            max_radius_km=radius_km
        )

    primary = deduped[0] if deduped else None
    provider_used = primary.provider if primary else "unknown"

    return LocationSearchResponse(
        status="ok",
        query=clean_q,
        count=len(deduped),
        primary_result=primary,
        results=deduped,
        provider_used=provider_used,
        verification_summary={
            "verified_count": sum(1 for r in deduped if r.verification_status == VerificationStatus.VERIFIED),
            "unverified_count": sum(1 for r in deduped if r.verification_status == VerificationStatus.UNVERIFIED),
            "discrepancies_detected": sum(1 for r in deduped if r.verification_status == VerificationStatus.DISCREPANCY_DETECTED),
            "has_google_places": location_service.has_google_places
        }
    )


@router.get("/autocomplete")
async def autocomplete_locations(
    q: str = Query(..., min_length=1, description="Prefix to autocomplete"),
    near_lat: Optional[float] = Query(None, description="Nearby bias latitude"),
    near_lon: Optional[float] = Query(None, description="Nearby bias longitude"),
    limit: int = Query(6, ge=1, le=15)
):
    """
    Instant autocomplete endpoint returning suggestions with exact GPS coordinates.
    """
    suggestions = await location_service.autocomplete(
        query=q,
        near_lat=near_lat,
        near_lon=near_lon,
        limit=limit
    )
    return {"status": "ok", "query": q, "suggestions": suggestions}


@router.post("/verify", response_model=LocationVerificationReport)
async def verify_location_candidate(
    loc: NormalizedLocation,
    expected_locality: Optional[str] = Query(None, description="Expected city or administrative area"),
    origin_lat: Optional[float] = Query(None, description="Query center latitude for distance validation"),
    origin_lon: Optional[float] = Query(None, description="Query center longitude for distance validation"),
    max_radius_km: float = Query(10.0, ge=1.0, le=100.0)
):
    """
    Audits an individual location: verifies WGS84 bounds, distance from search origin,
    locality concordance, and cross-checks with reverse geocoding.
    """
    # Try reverse-geocoding to compare independent source
    rev_loc = None
    try:
        rev_loc = await location_service.reverse_geocode(loc.lat, loc.lon)
    except Exception:
        pass

    report = verification_pipeline.verify_location(
        location=loc,
        expected_locality=expected_locality,
        origin_lat=origin_lat,
        origin_lon=origin_lon,
        max_radius_km=max_radius_km,
        reverse_geocode_loc=rev_loc
    )
    return report


@router.post("/report", response_model=ReportLocationIssueResponse)
async def report_location_issue(req: ReportLocationIssueRequest):
    """
    Crowdsourced data quality auditing: allows users to flag an inaccurate coordinate,
    closed venue, or wrong category. Reports are logged and stored in the cache database.
    """
    report_id = f"loc_issue_{uuid.uuid4().hex[:10]}"
    now_iso = datetime.now(timezone.utc).isoformat()

    report_record = {
        "report_id": report_id,
        "location_id": req.location_id,
        "location_name": req.location_name,
        "reported_lat": req.reported_lat,
        "reported_lon": req.reported_lon,
        "issue_type": req.issue_type,
        "suggested_correction": req.suggested_correction,
        "notes": req.notes,
        "user_contact": req.user_contact,
        "reported_at": now_iso,
        "status": "pending_review"
    }

    # Store in cache
    existing_reports = cache.get("location_reports_list", [])
    existing_reports.append(report_record)
    cache.set("location_reports_list", existing_reports, expire=86400 * 30)

    logger.info("New location discrepancy reported: %s for %s (%f, %f)", req.issue_type, req.location_name, req.reported_lat, req.reported_lon)

    return ReportLocationIssueResponse(
        status="ok",
        report_id=report_id,
        message=f"Thank you. Discrepancy report {report_id} has been logged for administrative verification.",
        received_at=now_iso
    )


@router.get("/reports")
async def get_reported_issues():
    """Returns list of reported location issues for data quality dashboard."""
    reports = cache.get("location_reports_list", [])
    return {
        "status": "ok",
        "total_reports": len(reports),
        "reports": reports
    }
