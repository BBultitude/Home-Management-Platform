"""
Knowledge Article Schemas
Pydantic models for knowledge base API requests and responses
Includes schemas for all 8 article types
"""

from datetime import date
from decimal import Decimal
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from uuid import UUID

from app.models.knowledge_article import ArticleType


# Base schemas
class KnowledgeArticleCreate(BaseModel):
    """Base schema for creating a knowledge article"""
    article_type: ArticleType = Field(..., description="Type of article")
    title: str = Field(..., min_length=1, max_length=255, description="Article title")
    data: dict[str, Any] = Field(..., description="Article data (type-specific)")
    tags: Optional[list[str]] = Field(None, description="Tags for search")
    attachment_ids: Optional[list[UUID]] = Field(None, description="File IDs to attach")

    model_config = ConfigDict(from_attributes=True)


class KnowledgeArticleUpdate(BaseModel):
    """Schema for updating a knowledge article"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    data: Optional[dict[str, Any]] = None
    tags: Optional[list[str]] = None

    model_config = ConfigDict(from_attributes=True)


class KnowledgeArticleResponse(BaseModel):
    """Schema for knowledge article response"""
    id: str
    article_type: str
    title: str
    data: dict[str, Any]
    tags: list[str]
    created_by: Optional[str] = None
    created_at: str
    updated_at: str
    attachment_count: int

    model_config = ConfigDict(from_attributes=True)


class KnowledgeArticleListResponse(BaseModel):
    """Schema for list of knowledge articles"""
    articles: list[KnowledgeArticleResponse]
    total: int


# Article type-specific data schemas (for documentation and validation)

class MeasurementData(BaseModel):
    """Data schema for Measurement articles"""
    location: str = Field(..., description="Location measured (e.g., 'Master Bedroom')")
    measurement_type: str = Field(..., description="Type of measurement")
    value: Decimal = Field(..., description="Measurement value")
    unit: str = Field(..., description="Unit (cm, m, inches, feet)")
    notes: Optional[str] = None
    date_measured: Optional[date] = None
    photo_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class PaintData(BaseModel):
    """Data schema for Paint articles"""
    room_area: str = Field(..., description="Room or area painted")
    surface_type: str = Field(..., description="Surface type (Wall, Ceiling, Trim, Door)")
    brand: str = Field(..., description="Paint brand")
    product_line: str = Field(..., description="Product line/series")
    color_name: str = Field(..., description="Color name")
    color_code: Optional[str] = None
    finish: str = Field(..., description="Finish (Matte, Satin, SemiGloss, Gloss)")
    retailer: Optional[str] = None
    purchase_date: Optional[date] = None
    quantity_used: Optional[str] = None
    coverage_area: Optional[str] = None
    notes: Optional[str] = None
    photo_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class TechDeviceData(BaseModel):
    """Data schema for TechDevice articles (passwords encrypted by service)"""
    device_type: str = Field(..., description="Device type (Router, Modem, AccessPoint, SmartDevice)")
    brand_model: str = Field(..., description="Brand and model")
    location: str = Field(..., description="Physical location")
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    wifi_ssid: Optional[str] = None
    wifi_password: Optional[str] = Field(None, description="Will be encrypted")
    admin_url: Optional[str] = None
    admin_username: Optional[str] = None
    admin_password: Optional[str] = Field(None, description="Will be encrypted")
    purchase_date: Optional[date] = None
    warranty_expiry: Optional[date] = None
    notes: Optional[str] = None
    manual_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class StorageLocationData(BaseModel):
    """Data schema for StorageLocation articles"""
    storage_area: str = Field(..., description="Storage area (e.g., 'Garage - Top Shelf Left')")
    items_stored: list[str] = Field(..., description="List of items stored")
    category: str = Field(..., description="Category (Seasonal, Tools, Documents, Holiday)")
    notes: Optional[str] = None
    photo_id: Optional[UUID] = None
    last_updated: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class ServiceRecord(BaseModel):
    """Service record for vehicles and appliances"""
    date: date
    odometer: Optional[int] = Field(None, description="Odometer reading (vehicles only)")
    service_type: str
    cost: Optional[Decimal] = None
    provider: Optional[str] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VehicleData(BaseModel):
    """Data schema for Vehicle articles"""
    vehicle_type: str = Field(..., description="Vehicle type (Car, Motorcycle, Bicycle)")
    make: str
    model: str
    year: int
    vin: Optional[str] = None
    registration_number: Optional[str] = None
    registration_expiry: Optional[date] = None
    insurance_policy_id: Optional[UUID] = Field(None, description="Link to insurance policy")
    service_history: Optional[list[dict]] = Field(None, description="List of service records")
    next_service_due: Optional[date] = None
    next_service_km: Optional[int] = None
    notes: Optional[str] = None
    photos: Optional[list[UUID]] = None
    manual_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class EmergencyContactData(BaseModel):
    """Data schema for EmergencyContact articles"""
    name: str
    relationship_role: str = Field(..., description="Relationship or role (Family, Electrician, Plumber)")
    primary_phone: str
    secondary_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    when_to_call: Optional[str] = Field(None, description="When to call (Power outage, Medical emergency)")
    category: str = Field(..., description="Category (Medical, Utilities, Trades, Family)")
    notes: Optional[str] = None
    pinned: Optional[bool] = Field(False, description="Pin to dashboard for quick access")

    model_config = ConfigDict(from_attributes=True)


class ApplianceData(BaseModel):
    """Data schema for Appliance articles"""
    appliance_type: str = Field(..., description="Appliance type (Fridge, Washer, HVAC, Oven)")
    brand: str
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    location: str = Field(..., description="Location in house")
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    retailer: Optional[str] = None
    warranty_expiry: Optional[date] = None
    manual_id: Optional[UUID] = None
    service_history: Optional[list[dict]] = Field(None, description="List of service records")
    energy_rating: Optional[str] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VendorData(BaseModel):
    """Data schema for Vendor articles"""
    business_name: str
    contact_person: Optional[str] = None
    service_type: str = Field(..., description="Service type (Electrician, Plumber, Landscaper)")
    phone: str
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating (1-5 stars)")
    last_used_date: Optional[date] = None
    services_performed: Optional[list[str]] = Field(None, description="List of services performed")
    cost_range: Optional[str] = None
    notes_review: Optional[str] = None
    recommended_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Search and filter schemas
class KnowledgeSearchRequest(BaseModel):
    """Schema for knowledge article search"""
    query: str = Field(..., min_length=1, description="Search query")
    article_types: Optional[list[ArticleType]] = Field(None, description="Filter by article types")
    tags: Optional[list[str]] = Field(None, description="Filter by tags")
    limit: Optional[int] = Field(50, ge=1, le=100)

    model_config = ConfigDict(from_attributes=True)


# Attachment schemas
class AttachmentResponse(BaseModel):
    """Schema for attachment response"""
    id: str
    article_id: str
    file_id: str

    model_config = ConfigDict(from_attributes=True)
