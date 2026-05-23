"""
Insurance Policy Schemas
Pydantic models for insurance policy API requests and responses
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

from app.models.insurance_policy import PolicyType, PremiumFrequency


class InsurancePolicyCreate(BaseModel):
    """Schema for creating an insurance policy"""
    policy_type: PolicyType = Field(..., description="Type of insurance policy")
    provider: str = Field(..., min_length=1, max_length=255, description="Insurance provider name")
    policy_number: Optional[str] = Field(None, max_length=255, description="Policy number")
    coverage_amount: Optional[Decimal] = Field(None, ge=0, description="Coverage amount")
    premium: Decimal = Field(..., gt=0, description="Premium amount")
    premium_frequency: PremiumFrequency = Field(..., description="Premium payment frequency")
    excess: Optional[Decimal] = Field(None, ge=0, description="Excess/deductible amount")
    renewal_date: date = Field(..., description="Policy renewal date")
    coverage_notes: Optional[str] = Field(None, max_length=5000, description="Coverage details and notes")
    document_id: Optional[int] = Field(None, description="ID of attached policy document")
    vehicle_id: Optional[UUID] = Field(None, description="ID of associated vehicle (if applicable)")

    model_config = ConfigDict(from_attributes=True)


class InsurancePolicyUpdate(BaseModel):
    """Schema for updating an insurance policy"""
    policy_type: Optional[PolicyType] = None
    provider: Optional[str] = Field(None, min_length=1, max_length=255)
    policy_number: Optional[str] = Field(None, max_length=255)
    coverage_amount: Optional[Decimal] = Field(None, ge=0)
    premium: Optional[Decimal] = Field(None, gt=0)
    premium_frequency: Optional[PremiumFrequency] = None
    excess: Optional[Decimal] = Field(None, ge=0)
    renewal_date: Optional[date] = None
    coverage_notes: Optional[str] = Field(None, max_length=5000)
    document_id: Optional[int] = None
    vehicle_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class InsurancePolicyResponse(BaseModel):
    """Schema for insurance policy response"""
    id: str
    policy_type: str
    provider: str
    policy_number: Optional[str] = None
    coverage_amount: Optional[float] = None
    premium: float
    premium_frequency: str
    excess: Optional[float] = None
    renewal_date: str
    coverage_notes: Optional[str] = None
    document_id: Optional[str] = None
    vehicle_id: Optional[str] = None
    created_at: str
    updated_at: str
    days_until_renewal: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class InsurancePolicyListResponse(BaseModel):
    """Schema for list of insurance policies"""
    policies: list[InsurancePolicyResponse]
    total: int


class RenewalAlertResponse(BaseModel):
    """Schema for renewal alerts"""
    policy_id: str
    policy_type: str
    provider: str
    renewal_date: str
    days_until_renewal: int
    premium: float
    premium_frequency: str
