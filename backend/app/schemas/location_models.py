"""
Normalized Location Data Contracts and Models for Fieldwise.
Standardizes place, coordinate, verification, and audit schemas across providers.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    DISCREPANCY_DETECTED = "discrepancy_detected"
    INCONCLUSIVE = "inconclusive"


class NormalizedLocation(BaseModel):
    """
    Unified canonical location representation across Google Maps Platform Places API,
    OpenStreetMap (Nominatim, Photon, Overpass), and curated authoritative gazetteers.
    """
    id: str = Field(..., description="Stable provider or spatial identifier")
    name: str = Field(..., description="Primary name of the place, venue or landmark")
    formatted_address: str = Field(..., description="Full canonical formatted address")
    lat: float = Field(..., description="WGS84 latitude between -90.0 and +90.0")
    lon: float = Field(..., description="WGS84 longitude between -180.0 and +180.0")
    category: str = Field("point_of_interest", description="Geospatial or activity category")
    provider: str = Field(..., description="Source provider: google_places, osm_photon, osm_nominatim, osm_overpass, gazetteer")
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.UNVERIFIED,
        description="Independent verification status"
    )
    google_maps_url: Optional[str] = Field(None, description="Direct Google Maps reference or directions link")
    locality: Optional[str] = Field(None, description="City, town, or locality")
    region: Optional[str] = Field(None, description="State, province, or region")
    country: Optional[str] = Field(None, description="Country name or ISO country code")
    postal_code: Optional[str] = Field(None, description="Postal or ZIP code if available")
    distance_km: Optional[float] = Field(None, description="Calculated distance in km from query center")
    confidence_level: Optional[str] = Field(None, description="High, Medium, or Low evidence confidence")
    verification_notes: List[str] = Field(default_factory=list, description="Audit trail notes from verification engine")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Raw provider metadata, osm tags, place types")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @field_validator("lat")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError(f"Latitude {v} out of valid WGS84 range [-90.0, 90.0]")
        return round(v, 6)

    @field_validator("lon")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError(f"Longitude {v} out of valid WGS84 range [-180.0, 180.0]")
        return round(v, 6)


class LocationVerificationReport(BaseModel):
    """
    Detailed audit and quality evaluation for a candidate location.
    """
    target_id: str
    target_name: str
    lat: float
    lon: float
    is_valid_coordinate: bool
    is_within_locality: bool
    distance_from_origin_km: Optional[float] = None
    distance_within_tolerance: bool = True
    reverse_geocoded_address: Optional[str] = None
    reverse_geocoded_locality: Optional[str] = None
    provider_agreement: Optional[str] = None  # "matched", "discrepant", "single_source"
    verification_status: VerificationStatus
    audit_notes: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LocationSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Place name, address, coordinates, or landmark")
    near_lat: Optional[float] = Field(None, description="Optional center latitude for nearby search")
    near_lon: Optional[float] = Field(None, description="Optional center longitude for nearby search")
    radius_km: Optional[float] = Field(10.0, ge=0.5, le=100.0, description="Search radius in kilometers")
    category: Optional[str] = Field(None, description="Optional activity or category filter")
    limit: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results to return")


class LocationSearchResponse(BaseModel):
    status: str
    query: str
    count: int
    primary_result: Optional[NormalizedLocation] = None
    results: List[NormalizedLocation] = Field(default_factory=list)
    provider_used: str
    verification_summary: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class ReportLocationIssueRequest(BaseModel):
    location_id: Optional[str] = None
    location_name: str
    reported_lat: float
    reported_lon: float
    issue_type: str = Field(..., description="'wrong_coordinates', 'place_closed', 'wrong_name', 'wrong_category', 'other'")
    suggested_correction: Optional[str] = None
    notes: Optional[str] = None
    user_contact: Optional[str] = None


class ReportLocationIssueResponse(BaseModel):
    status: str
    report_id: str
    message: str
    received_at: str
