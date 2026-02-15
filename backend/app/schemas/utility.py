"""
Utility Schemas
Pydantic models for utility cost tracking API requests and responses
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.utility import UtilityType


class UtilityCreate(BaseModel):
    """Schema for creating a utility entry"""
    utility_type: UtilityType = Field(..., description="Type of utility")
    provider: str = Field(..., min_length=1, max_length=255, description="Provider name")
    billing_period_start: date = Field(..., description="Billing period start date")
    billing_period_end: date = Field(..., description="Billing period end date")
    usage: Decimal = Field(..., gt=0, description="Usage amount")
    unit: str = Field(..., min_length=1, max_length=50, description="Unit of measurement")
    cost: Decimal = Field(..., gt=0, description="Total cost")
    attachment_id: Optional[int] = Field(None, description="Optional bill PDF file ID")
    notes: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(from_attributes=True)


class UtilityUpdate(BaseModel):
    """Schema for updating a utility entry"""
    utility_type: Optional[UtilityType] = None
    provider: Optional[str] = Field(None, min_length=1, max_length=255)
    billing_period_start: Optional[date] = None
    billing_period_end: Optional[date] = None
    usage: Optional[Decimal] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    cost: Optional[Decimal] = Field(None, gt=0)
    attachment_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(from_attributes=True)


class UtilityResponse(BaseModel):
    """Schema for utility response"""
    id: int
    utility_type: str
    provider: str
    billing_period_start: date
    billing_period_end: date
    usage: float
    unit: str
    cost: float
    cost_per_unit: float
    attachment_id: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UtilityListResponse(BaseModel):
    """Schema for list of utilities"""
    utilities: list[UtilityResponse]
    total: int


class UtilityStatsResponse(BaseModel):
    """Schema for utility statistics"""
    utility_type: str
    average_cost: float
    total_usage: float
    total_cost: float
    entry_count: int
    period_start: Optional[date] = None
    period_end: Optional[date] = None


class MonthlyDataPoint(BaseModel):
    """Schema for monthly aggregated data point"""
    month: str = Field(..., description="Month in YYYY-MM format")
    cost: float = Field(..., description="Total cost for the month")
    usage: float = Field(..., description="Total usage for the month")
    cost_per_unit: float = Field(..., description="Average cost per unit for the month")
    entry_count: int = Field(..., description="Number of entries in this month")


class ProviderDataPoint(BaseModel):
    """Schema for provider comparison data point"""
    provider: str
    total_cost: float
    total_usage: float
    average_cost_per_unit: float
    entry_count: int
    period_start: Optional[date] = None
    period_end: Optional[date] = None


class UtilityGraphsResponse(BaseModel):
    """Schema for utility graphs data"""
    utility_type: str
    monthly_data: list[MonthlyDataPoint] = Field(..., description="Monthly time-series data")
    provider_comparison: list[ProviderDataPoint] = Field(..., description="Comparison by provider")
    rolling_12_month_avg_cost: float = Field(..., description="12-month rolling average cost")
    rolling_12_month_avg_usage: float = Field(..., description="12-month rolling average usage")
    total_entries: int = Field(..., description="Total number of entries analyzed")
