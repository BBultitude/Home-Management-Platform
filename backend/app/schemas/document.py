"""
Document Schemas
Pydantic models for document API requests and responses
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

from app.models.document import DocumentType


class DocumentCreate(BaseModel):
    """Schema for creating a document"""
    document_type: DocumentType = Field(..., description="Type of document")
    title: str = Field(..., min_length=1, max_length=255, description="Document title")
    description: Optional[str] = Field(None, max_length=5000, description="Document description")
    category: Optional[str] = Field(None, max_length=100, description="Document category")
    tags: Optional[list[str]] = Field(None, description="Document tags for search")
    uploaded_date: Optional[date] = Field(None, description="Upload date (defaults to today)")
    expiry_date: Optional[date] = Field(None, description="Document expiry date")
    file_id: UUID = Field(..., description="ID of uploaded file")

    model_config = ConfigDict(from_attributes=True)


class DocumentUpdate(BaseModel):
    """Schema for updating a document"""
    document_type: Optional[DocumentType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[list[str]] = None
    expiry_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: str
    document_type: str
    title: str
    description: Optional[str]
    category: Optional[str]
    tags: list[str]
    uploaded_date: str
    expiry_date: Optional[str]
    file_id: str
    created_at: str
    is_expired: Optional[bool] = None
    days_until_expiry: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """Schema for list of documents"""
    documents: list[DocumentResponse]
    total: int


class ExpiryAlertResponse(BaseModel):
    """Schema for document expiry alerts"""
    document_id: str
    title: str
    document_type: str
    expiry_date: str
    days_until_expiry: int
