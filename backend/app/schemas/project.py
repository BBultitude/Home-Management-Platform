"""
Project Schemas
Pydantic models for project API requests and responses
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

from app.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    """Schema for creating a project"""
    project_name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    priority_item_id: Optional[UUID] = Field(None, description="Originating priority item ID")
    status: Optional[ProjectStatus] = Field(ProjectStatus.PLANNED, description="Project status")
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    budget: Optional[Decimal] = Field(None, ge=0)
    actual_cost: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    project_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    budget: Optional[Decimal] = Field(None, ge=0)
    actual_cost: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: str
    project_name: str
    description: Optional[str] = None
    priority_item_id: Optional[str] = None
    status: str
    start_date: Optional[str] = None
    completion_date: Optional[str] = None
    budget: Optional[float] = None
    actual_cost: Optional[float] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    """Schema for list of projects"""
    projects: list[ProjectResponse]
    total: int
