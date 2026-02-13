"""
File Upload/Download API endpoints
"""

from fastapi import APIRouter, Depends, File, UploadFile, Form, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.api.dependencies import get_current_active_user, get_db, require_permission
from app.models.user import User
from app.models.file import FileCategory
from app.services.file_service import FileService
from app.services.audit_service import AuditService
from app.schemas.file import (
    FileUploadResponse,
    FileResponse,
    FileListResponse,
    FileDeleteResponse,
    UserStorageResponse
)


router = APIRouter(prefix="/files", tags=["files"])


def get_client_info(request: Request) -> tuple[str, str]:
    """Extract IP address and user agent from request"""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    return ip_address, user_agent


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    category: FileCategory = Form(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(require_permission("files:upload")),
    db: Session = Depends(get_db)
):
    """
    Upload a file

    Requires permission: files:upload

    Limits:
    - Max file size: 20MB
    - Max user storage: 200MB
    - Allowed types: PDF, JPG, PNG, GIF, WEBP, DOCX, XLSX, TXT, CSV
    """
    # Upload file
    file_record = FileService.upload_file(
        db=db,
        user=current_user,
        file=file,
        category=category,
        description=description
    )

    # Log audit event
    ip_address, user_agent = get_client_info(request)
    AuditService.log_file_upload(
        db=db,
        user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
        file_id=file_record.id,
        filename=file_record.original_filename,
        file_size=file_record.file_size,
        mime_type=file_record.mime_type
    )

    return FileUploadResponse(
        id=file_record.id,
        filename=file_record.filename,
        original_filename=file_record.original_filename,
        mime_type=file_record.mime_type,
        file_size=file_record.file_size,
        category=file_record.category,
        description=file_record.description,
        uploaded_at=file_record.uploaded_at,
        message="File uploaded successfully"
    )


@router.get("/{file_id}", response_model=FileResponse)
async def get_file_metadata(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get file metadata

    Users can access their own files. Admins can access all files.
    """
    file_record = FileService.get_file(db, file_id, current_user)

    return FileResponse(
        id=file_record.id,
        filename=file_record.filename,
        original_filename=file_record.original_filename,
        file_path=file_record.file_path,
        mime_type=file_record.mime_type,
        file_size=file_record.file_size,
        category=file_record.category,
        description=file_record.description,
        uploaded_at=file_record.uploaded_at
    )


@router.get("/{file_id}/download")
async def download_file(
    request: Request,
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Download a file

    Users can download their own files. Admins can download all files.
    """
    # Get file and check permissions
    file_record = FileService.get_file(db, file_id, current_user)

    # Get file path
    file_path = FileService.get_file_path(file_record)

    # Log audit event
    ip_address, user_agent = get_client_info(request)
    AuditService.log_file_download(
        db=db,
        user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
        file_id=file_record.id,
        filename=file_record.original_filename
    )

    # Return file
    return FileResponse(
        path=str(file_path),
        filename=file_record.original_filename,
        media_type=file_record.mime_type
    )


@router.delete("/{file_id}", response_model=FileDeleteResponse)
async def delete_file(
    request: Request,
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a file (permanent delete)

    Users can delete their own files. Admins can delete all files.
    """
    # Get file for audit logging (before deletion)
    file_record = FileService.get_file(db, file_id, current_user)
    filename = file_record.original_filename

    # Delete file
    FileService.delete_file(db, file_id, current_user)

    # Log audit event
    ip_address, user_agent = get_client_info(request)
    AuditService.log_file_deleted(
        db=db,
        user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
        file_id=file_id,
        filename=filename
    )

    return FileDeleteResponse(
        message="File deleted successfully",
        file_id=file_id
    )


@router.get("", response_model=FileListResponse)
async def list_files(
    category: Optional[FileCategory] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List user's files

    Users can list their own files. Admins can list all files (use user_id filter).
    """
    files = FileService.list_user_files(
        db=db,
        user_id=current_user.id,
        category=category,
        limit=limit,
        offset=offset
    )

    # Get storage info
    storage_used = FileService.get_user_storage_used(db, current_user.id)

    file_responses = [
        FileResponse(
            id=f.id,
            filename=f.filename,
            original_filename=f.original_filename,
            file_path=f.file_path,
            mime_type=f.mime_type,
            file_size=f.file_size,
            category=f.category,
            description=f.description,
            uploaded_at=f.uploaded_at
        )
        for f in files
    ]

    return FileListResponse(
        files=file_responses,
        total=len(files),
        storage_used_bytes=storage_used,
        storage_limit_bytes=FileService.MAX_USER_STORAGE
    )


@router.get("/storage/quota", response_model=UserStorageResponse)
async def get_storage_quota(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's storage quota information
    """
    storage_used = FileService.get_user_storage_used(db, current_user.id)
    storage_limit = FileService.MAX_USER_STORAGE

    # Count files
    files_count = len(FileService.list_user_files(db, current_user.id, limit=10000))

    # Convert to MB
    storage_used_mb = storage_used / (1024 * 1024)
    storage_limit_mb = storage_limit / (1024 * 1024)
    storage_percentage = (storage_used / storage_limit * 100) if storage_limit > 0 else 0

    return UserStorageResponse(
        storage_used_bytes=storage_used,
        storage_limit_bytes=storage_limit,
        storage_used_mb=round(storage_used_mb, 2),
        storage_limit_mb=round(storage_limit_mb, 2),
        storage_percentage=round(storage_percentage, 2),
        files_count=files_count
    )
