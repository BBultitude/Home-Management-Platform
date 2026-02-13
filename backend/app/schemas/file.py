"""
File schemas for API requests and responses
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.file import FileCategory


class FileUploadResponse(BaseModel):
    """Response after successful file upload"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    original_filename: str
    mime_type: str
    file_size: int
    category: FileCategory
    description: Optional[str] = None
    uploaded_at: datetime
    message: str = "File uploaded successfully"


class FileResponse(BaseModel):
    """File metadata response"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    original_filename: str
    file_path: str
    mime_type: str
    file_size: int
    category: FileCategory
    description: Optional[str] = None
    uploaded_at: datetime


class FileListResponse(BaseModel):
    """Response for listing files"""
    files: list[FileResponse]
    total: int
    storage_used_bytes: int
    storage_limit_bytes: int = Field(default=200 * 1024 * 1024)


class FileDeleteResponse(BaseModel):
    """Response after file deletion"""
    message: str = "File deleted successfully"
    file_id: int


class UserStorageResponse(BaseModel):
    """User storage quota information"""
    storage_used_bytes: int
    storage_limit_bytes: int
    storage_used_mb: float
    storage_limit_mb: float
    storage_percentage: float
    files_count: int
