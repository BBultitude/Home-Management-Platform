"""
Tests for file service core functions
"""

import pytest
from sqlalchemy.orm import Session

from app.services.file_service import FileService
from app.models.file import File, FileCategory
from app.models.user import User, UserRole

TEST_HASHED_PASSWORD = "hashed"  # Test-only placeholder for hashed_password field


class TestFilenameSanitization:
    """Test filename sanitization"""

    def test_sanitize_normal_filename(self):
        """Normal filename should pass through"""
        result = FileService.sanitize_filename("document.pdf")
        assert result == "document.pdf"

    def test_sanitize_path_traversal(self):
        """Path traversal attempt should be sanitized"""
        result = FileService.sanitize_filename("../../etc/passwd")
        assert result == "passwd"

    def test_sanitize_null_bytes(self):
        """Null bytes should be removed"""
        result = FileService.sanitize_filename("test\x00.pdf")
        assert result == "test.pdf"

    def test_sanitize_long_filename(self):
        """Very long filename should be truncated"""
        long_name = "a" * 300 + ".pdf"
        result = FileService.sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".pdf")


class TestStorageQuota:
    """Test storage quota management"""

    def test_get_user_storage_empty(self, test_db: Session, test_user: User):
        """User with no files should have 0 storage"""
        storage = FileService.get_user_storage_used(test_db, test_user.id)
        assert storage == 0

    def test_get_user_storage_with_files(self, test_db: Session, test_user: User):
        """User storage should sum all files"""
        file1 = File(
            uploaded_by=test_user.id,
            filename="uuid1_file1.pdf",
            original_filename="file1.pdf",
            file_path="tax/uuid1_file1.pdf",
            mime_type="application/pdf",
            file_size=1000,
            category=FileCategory.TAX
        )
        file2 = File(
            uploaded_by=test_user.id,
            filename="uuid2_file2.pdf",
            original_filename="file2.pdf",
            file_path="tax/uuid2_file2.pdf",
            mime_type="application/pdf",
            file_size=2000,
            category=FileCategory.TAX
        )
        test_db.add_all([file1, file2])
        test_db.commit()

        storage = FileService.get_user_storage_used(test_db, test_user.id)
        assert storage == 3000


class TestStoragePath:
    """Test storage path generation"""

    def test_generate_storage_path_pdf(self):
        """PDF should generate correct path"""
        file_path, filename = FileService.generate_storage_path(
            FileCategory.TAX,
            "test.pdf",
            "application/pdf"
        )
        assert file_path.startswith("tax/")
        assert file_path.endswith("_test.pdf")
        assert filename.endswith("_test.pdf")

    def test_generate_storage_path_uuid_unique(self):
        """Each generated path should have unique UUID"""
        path1, _ = FileService.generate_storage_path(
            FileCategory.TAX,
            "test.pdf",
            "application/pdf"
        )
        path2, _ = FileService.generate_storage_path(
            FileCategory.TAX,
            "test.pdf",
            "application/pdf"
        )
        assert path1 != path2


class TestFileAccess:
    """Test file access and permissions"""

    def test_get_file_owner(self, test_db: Session, test_user: User):
        """Owner should be able to access their file"""
        file_record = File(
            uploaded_by=test_user.id,
            filename="uuid_test.pdf",
            original_filename="test.pdf",
            file_path="tax/uuid_test.pdf",
            mime_type="application/pdf",
            file_size=1000,
            category=FileCategory.TAX
        )
        test_db.add(file_record)
        test_db.commit()

        result = FileService.get_file(test_db, file_record.id, test_user)
        assert result.id == file_record.id

    def test_get_file_other_user(self, test_db: Session, test_user: User):
        """Non-owner should not access file"""
        # Create file owned by another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=TEST_HASHED_PASSWORD,
            full_name="Other User",
            role=UserRole.READER
        )
        test_db.add(other_user)
        test_db.commit()

        file_record = File(
            uploaded_by=other_user.id,
            filename="uuid_test.pdf",
            original_filename="test.pdf",
            file_path="tax/uuid_test.pdf",
            mime_type="application/pdf",
            file_size=1000,
            category=FileCategory.TAX
        )
        test_db.add(file_record)
        test_db.commit()

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            FileService.get_file(test_db, file_record.id, test_user)
        assert exc_info.value.status_code == 403

    def test_get_file_admin(self, test_db: Session):
        """Admin should access any file"""
        # Create regular user and their file
        regular_user = User(
            username="regular",
            email="regular@example.com",
            hashed_password=TEST_HASHED_PASSWORD,
            full_name="Regular User",
            role=UserRole.READER
        )
        test_db.add(regular_user)
        test_db.commit()

        file_record = File(
            uploaded_by=regular_user.id,
            filename="uuid_test.pdf",
            original_filename="test.pdf",
            file_path="tax/uuid_test.pdf",
            mime_type="application/pdf",
            file_size=1000,
            category=FileCategory.TAX
        )
        test_db.add(file_record)
        test_db.commit()

        # Create admin
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=TEST_HASHED_PASSWORD,
            full_name="Admin User",
            role=UserRole.ADMIN
        )
        test_db.add(admin_user)
        test_db.commit()

        # Admin should access
        result = FileService.get_file(test_db, file_record.id, admin_user)
        assert result.id == file_record.id


class TestFileList:
    """Test file listing"""

    def test_list_user_files(self, test_db: Session, test_user: User):
        """List should return user's files"""
        file1 = File(
            uploaded_by=test_user.id,
            filename="uuid1_file1.pdf",
            original_filename="file1.pdf",
            file_path="tax/uuid1_file1.pdf",
            mime_type="application/pdf",
            file_size=1000,
            category=FileCategory.TAX
        )
        file2 = File(
            uploaded_by=test_user.id,
            filename="uuid2_file2.pdf",
            original_filename="file2.pdf",
            file_path="insurance/uuid2_file2.pdf",
            mime_type="application/pdf",
            file_size=2000,
            category=FileCategory.INSURANCE
        )
        test_db.add_all([file1, file2])
        test_db.commit()

        files = FileService.list_user_files(test_db, test_user.id)
        assert len(files) == 2

    def test_list_user_files_by_category(self, test_db: Session, test_user: User):
        """List should filter by category"""
        file1 = File(
            uploaded_by=test_user.id,
            filename="uuid1_file1.pdf",
            original_filename="file1.pdf",
            file_path="tax/uuid1_file1.pdf",
            mime_type="application/pdf",
            file_size=1000,
            category=FileCategory.TAX
        )
        file2 = File(
            uploaded_by=test_user.id,
            filename="uuid2_file2.pdf",
            original_filename="file2.pdf",
            file_path="insurance/uuid2_file2.pdf",
            mime_type="application/pdf",
            file_size=2000,
            category=FileCategory.INSURANCE
        )
        test_db.add_all([file1, file2])
        test_db.commit()

        files = FileService.list_user_files(
            test_db,
            test_user.id,
            category=FileCategory.TAX
        )
        assert len(files) == 1
        assert files[0].category == FileCategory.TAX
