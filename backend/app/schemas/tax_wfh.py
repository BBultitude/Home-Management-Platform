"""
Tax WFH Entry schemas for API requests and responses
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class TaxWFHEntryCreate(BaseModel):
    """Request schema for creating a WFH entry"""
    date: date
    hours: Decimal = Field(..., gt=0, le=24)
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('hours')
    @classmethod
    def validate_hours(cls, v: Decimal) -> Decimal:
        """Validate hours is positive and reasonable"""
        if v <= 0:
            raise ValueError("Hours must be greater than 0")
        if v > 24:
            raise ValueError("Hours cannot exceed 24 per day")
        return v


class TaxWFHEntryUpdate(BaseModel):
    """Request schema for updating a WFH entry"""
    hours: Optional[Decimal] = Field(None, gt=0, le=24)
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('hours')
    @classmethod
    def validate_hours(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate hours if provided"""
        if v is not None:
            if v <= 0:
                raise ValueError("Hours must be greater than 0")
            if v > 24:
                raise ValueError("Hours cannot exceed 24 per day")
        return v


class TaxWFHEntryResponse(BaseModel):
    """Response schema for a WFH entry"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date: date
    hours: float
    notes: Optional[str] = None
    deduction_amount: float
    created_at: datetime
    updated_at: datetime


class TaxWFHEntryListResponse(BaseModel):
    """Response schema for listing WFH entries"""
    entries: list[TaxWFHEntryResponse]
    total: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class TaxWFHDeleteResponse(BaseModel):
    """Response after deleting a WFH entry"""
    message: str = "WFH entry deleted successfully"
    entry_id: int


class TaxWFHFYSummaryResponse(BaseModel):
    """Response schema for financial year summary"""
    financial_year: int
    fy_start_date: date
    fy_end_date: date
    total_days: int
    total_hours: float
    ato_rate_per_hour: float
    total_deduction: float
    entries: list[dict]  # Simplified entry dict
