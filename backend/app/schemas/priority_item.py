"""
Priority Item Schemas
Pydantic models for priority item API requests and responses
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID

from app.models.priority_item import PriorityStatus


class PriorityItemCreate(BaseModel):
    """Schema for creating a priority item"""
    description: str = Field(..., min_length=1, max_length=500, description="Description of repair/upgrade")
    cost: Decimal = Field(..., gt=0, description="Estimated cost")
    severity: int = Field(..., ge=1, le=5, description="Severity (1-5): 1=cosmetic, 5=serious/safety")
    frequency: int = Field(..., ge=1, le=5, description="Frequency (1-5): 1=rare, 5=constant")

    model_config = ConfigDict(from_attributes=True)


class PriorityItemUpdate(BaseModel):
    """Schema for updating a priority item"""
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    cost: Optional[Decimal] = Field(None, gt=0)
    severity: Optional[int] = Field(None, ge=1, le=5)
    frequency: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[PriorityStatus] = None

    model_config = ConfigDict(from_attributes=True)


class PriorityItemResponse(BaseModel):
    """Schema for priority item response"""
    id: str
    description: str
    cost: float
    severity: int
    frequency: int
    benefit_score: int
    cost_score: int
    net_score: int
    status: str
    project_id: Optional[str]
    created_at: str
    updated_at: str
    completed_at: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class PriorityItemListResponse(BaseModel):
    """Schema for list of priority items"""
    items: list[PriorityItemResponse]
    total: int


class ConvertToProjectRequest(BaseModel):
    """Schema for converting priority item to project"""
    project_name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    budget: Optional[Decimal] = Field(None, ge=0, description="Project budget")
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
