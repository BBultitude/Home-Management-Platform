"""
Income Source Schemas
Pydantic models for income source API requests and responses
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.income_source import IncomeFrequency


class IncomeSourceCreate(BaseModel):
    """Schema for creating an income source"""
    source_name: str = Field(..., min_length=1, max_length=255, description="Name of income source")
    amount: Decimal = Field(..., gt=0, description="Income amount")
    frequency: IncomeFrequency = Field(..., description="Payment frequency")

    model_config = ConfigDict(from_attributes=True)


class IncomeSourceUpdate(BaseModel):
    """Schema for updating an income source"""
    source_name: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0)
    frequency: Optional[IncomeFrequency] = None

    model_config = ConfigDict(from_attributes=True)


class IncomeSourceResponse(BaseModel):
    """Schema for income source response"""
    id: int
    source_name: str
    amount: float
    frequency: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IncomeSourceListResponse(BaseModel):
    """Schema for list of income sources"""
    income_sources: list[IncomeSourceResponse]
    total: int
