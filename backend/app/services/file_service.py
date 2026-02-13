"""
File Service
Handles file uploads, downloads, and deletion with validation and quota management
"""

import os
import uuid
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status, UploadFile

from app.models.file import File, FileCategory
from app.models.user import User
from app.core.config import settings


class FileService:
    """Service for file operations"""

    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # XLSX
        "text/plain",
        "text/csv",
    }

    # File extensions mapping
    MIME_TO_EXT = {
        "application/pdf": ".pdf",
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "text/plain": ".txt",
        "text/csv": ".csv",
    }

    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
    MAX_USER_STORAGE = 200 * 1024 * 1024  # 200MB per user

    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """
        Validate uploaded file

        Args:
            file: Uploaded file

        Raises:
            HTTPException: If file is invalid
        """
        # Check MIME type
        if file.content_type not in FileService.ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: PDF, JPG, PNG, GIF, WEBP, DOCX, XLSX, TXT, CSV"
            )

        # Check file size (read file to get actual size)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > FileService.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {FileService.MAX_FILE_SIZE / (1024 * 1024)}MB"
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove directory components
        filename = os.path.basename(filename)

        # Remove null bytes
        filename = filename.replace('\x00', '')

        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext

        return filename

    @staticmethod
    def get_user_storage_used(db: Session, user_id: int) -> int:
        """
        Calculate total storage used by user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Total bytes used
        """
        result = db.query(func.sum(File.file_size)).filter(
            File.uploaded_by == user_id
        ).scalar()

        return result or 0

    @staticmethod
    def check_user_quota(db: Session, user_id: int, file_size: int) -> None:
        """
        Check if user has enough storage quota

        Args:
            db: Database session
            user_id: User ID
            file_size: Size of file to upload

        Raises:
            HTTPException: If quota exceeded
        """
        current_usage = FileService.get_user_storage_used(db, user_id)

        if current_usage + file_size > FileService.MAX_USER_STORAGE:
            raise HTTPException(
                status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                detail=f"Storage quota exceeded. Used: {current_usage / (1024 * 1024):.2f}MB, "
                       f"Limit: {FileService.MAX_USER_STORAGE / (1024 * 1024)}MB"
            )

    @staticmethod
    def generate_storage_path(category: FileCategory, original_filename: str, mime_type: str) -> tuple[str, str]:
        """
        Generate unique storage path for file

        Args:
            category: File category
            original_filename: Original filename
            mime_type: MIME type

        Returns:
            Tuple of (file_path, filename)
        """
        # Generate UUID
        file_uuid = str(uuid.uuid4())

        # Get file extension from MIME type or filename
        ext = FileService.MIME_TO_EXT.get(mime_type)
        if not ext:
            _, ext = os.path.splitext(original_filename)

        # Create stored filename: uuid_sanitized-name.ext
        sanitized_name = FileService.sanitize_filename(original_filename)
        name_without_ext = os.path.splitext(sanitized_name)[0]
        filename = f"{file_uuid}_{name_without_ext}{ext}"

        # Create path: uploads/{category}/{filename}
        file_path = f"{category.value}/{filename}"

        return file_path, filename

    @staticmethod
    def save_file_to_disk(file: UploadFile, file_path: str) -> None:
        """
        Save file to disk

        Args:
            file: Uploaded file
            file_path: Relative file path

        Raises:
            HTTPException: If file save fails
        """
        # Get upload directory from settings
        upload_dir = Path(settings.UPLOAD_DIR)
        full_path = upload_dir / file_path

        # Create directory if it doesn't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        try:
            with open(full_path, "wb") as f:
                file.file.seek(0)
                f.write(file.file.read())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )

    @staticmethod
    def upload_file(
        db: Session,
        user: User,
        file: UploadFile,
        category: FileCategory,
        description: Optional[str] = None
    ) -> File:
        """
        Upload a file

        Args:
            db: Database session
            user: User uploading the file
            file: Uploaded file
            category: File category
            description: Optional file description

        Returns:
            Created File object

        Raises:
            HTTPException: If validation fails or quota exceeded
        """
        # Validate file
        FileService.validate_file(file)

        # Get file size
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        # Check quota
        FileService.check_user_quota(db, user.id, file_size)

        # Generate storage path
        file_path, filename = FileService.generate_storage_path(
            category, file.filename, file.content_type
        )

        # Save to disk
        FileService.save_file_to_disk(file, file_path)

        # Create database record
        file_record = File(
            uploaded_by=user.id,
            filename=filename,
            original_filename=FileService.sanitize_filename(file.filename),
            file_path=file_path,
            mime_type=file.content_type,
            file_size=file_size,
            category=category,
            description=description
        )

        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        return file_record

    @staticmethod
    def get_file(db: Session, file_id: int, user: User) -> File:
        """
        Get file metadata

        Args:
            db: Database session
            file_id: File ID
            user: Current user

        Returns:
            File object

        Raises:
            HTTPException: If file not found or access denied
        """
        file = db.query(File).filter(File.id == file_id).first()

        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        # Check access (user owns file or is admin)
        from app.models.user import UserRole
        if file.uploaded_by != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return file

    @staticmethod
    def get_file_path(file: File) -> Path:
        """
        Get full file path on disk

        Args:
            file: File object

        Returns:
            Full path to file
        """
        upload_dir = Path(settings.UPLOAD_DIR)
        return upload_dir / file.file_path

    @staticmethod
    def delete_file(db: Session, file_id: int, user: User) -> None:
        """
        Delete a file (permanent delete)

        Args:
            db: Database session
            file_id: File ID
            user: Current user

        Raises:
            HTTPException: If file not found or access denied
        """
        file = FileService.get_file(db, file_id, user)

        # Delete from disk
        file_path = FileService.get_file_path(file)
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception:
            pass  # Ignore disk errors

        # Delete from database
        db.delete(file)
        db.commit()

    @staticmethod
    def list_user_files(
        db: Session,
        user_id: int,
        category: Optional[FileCategory] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[File]:
        """
        List files for a user

        Args:
            db: Database session
            user_id: User ID
            category: Optional category filter
            limit: Maximum files to return
            offset: Pagination offset

        Returns:
            List of File objects
        """
        query = db.query(File).filter(
            File.uploaded_by == user_id
        )

        if category:
            query = query.filter(File.category == category)

        query = query.order_by(File.uploaded_at.desc())
        query = query.limit(limit).offset(offset)

        return query.all()
