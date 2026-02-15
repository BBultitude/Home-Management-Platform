"""
Quote Schemas
Pydantic models for quote API requests and responses
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from uuid import UUID


class QuoteCreate(BaseModel):
    """Schema for creating a quote"""
    project_id: UUID = Field(..., description="Project ID")
    contractor_name: str = Field(..., min_length=1, max_length=255, description="Contractor name")
    contact_phone: Optional[str] = Field(None, max_length=50)
    contact_email: Optional[EmailStr] = None
    quote_amount: Decimal = Field(..., gt=0, description="Quote amount")
    quote_date: date = Field(..., description="Date quote was provided")
    expiry_date: Optional[date] = Field(None, description="Quote expiry date")
    scope_of_work: Optional[str] = Field(None, description="Scope of work description")
    selected: Optional[bool] = Field(False, description="Whether quote is selected")
    document_id: Optional[int] = Field(None, description="ID of attached quote document")
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class QuoteUpdate(BaseModel):
    """Schema for updating a quote"""
    contractor_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=50)
    contact_email: Optional[EmailStr] = None
    quote_amount: Optional[Decimal] = Field(None, gt=0)
    quote_date: Optional[date] = None
    expiry_date: Optional[date] = None
    scope_of_work: Optional[str] = None
    selected: Optional[bool] = None
    document_id: Optional[int] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class QuoteResponse(BaseModel):
    """Schema for quote response"""
    id: str
    project_id: str
    contractor_name: str
    contact_phone: Optional[str]
    contact_email: Optional[str]
    quote_amount: float
    quote_date: str
    expiry_date: Optional[str]
    scope_of_work: Optional[str]
    selected: bool
    document_id: Optional[str]
    notes: Optional[str]
    created_at: str
    is_expired: Optional[bool] = None
    days_until_expiry: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class QuoteListResponse(BaseModel):
    """Schema for list of quotes"""
    quotes: list[QuoteResponse]
    total: int


class QuoteComparisonResponse(BaseModel):
    """Schema for quote comparison"""
    project_id: str
    project_name: str
    quotes: list[QuoteResponse]
    lowest_quote: Optional[QuoteResponse]
    selected_quote: Optional[QuoteResponse]
