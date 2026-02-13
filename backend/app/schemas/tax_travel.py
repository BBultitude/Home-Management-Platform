"""
Tax Travel Entry schemas for API requests and responses
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class TaxTravelEntryCreate(BaseModel):
    """Request schema for creating a travel entry"""
    date: date
    purpose: str = Field(..., min_length=1, max_length=255)
    start_location: str = Field(..., min_length=1, max_length=255)
    end_location: str = Field(..., min_length=1, max_length=255)
    distance_km: Decimal = Field(..., gt=0, le=10000)
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('distance_km')
    @classmethod
    def validate_distance(cls, v: Decimal) -> Decimal:
        """Validate distance is positive and reasonable"""
        if v <= 0:
            raise ValueError("Distance must be greater than 0")
        if v > 10000:
            raise ValueError("Distance cannot exceed 10,000 km per trip")
        return v


class TaxTravelEntryUpdate(BaseModel):
    """Request schema for updating a travel entry"""
    purpose: Optional[str] = Field(None, min_length=1, max_length=255)
    start_location: Optional[str] = Field(None, min_length=1, max_length=255)
    end_location: Optional[str] = Field(None, min_length=1, max_length=255)
    distance_km: Optional[Decimal] = Field(None, gt=0, le=10000)
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('distance_km')
    @classmethod
    def validate_distance(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate distance if provided"""
        if v is not None:
            if v <= 0:
                raise ValueError("Distance must be greater than 0")
            if v > 10000:
                raise ValueError("Distance cannot exceed 10,000 km per trip")
        return v


class TaxTravelEntryResponse(BaseModel):
    """Response schema for a travel entry"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date: date
    purpose: str
    start_location: str
    end_location: str
    distance_km: float
    notes: Optional[str] = None
    deduction_amount: Optional[float] = None  # Calculated with rate
    created_at: datetime
    updated_at: datetime


class TaxTravelEntryListResponse(BaseModel):
    """Response schema for listing travel entries"""
    entries: list[TaxTravelEntryResponse]
    total: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class TaxTravelDeleteResponse(BaseModel):
    """Response after deleting a travel entry"""
    message: str = "Travel entry deleted successfully"
    entry_id: int


class TaxTravelFYSummaryResponse(BaseModel):
    """Response schema for financial year summary"""
    financial_year: int
    fy_start_date: date
    fy_end_date: date
    total_trips: int
    total_km: float
    rate_per_km: float
    total_deduction: float
    entries: list[dict]  # Simplified entry dict
