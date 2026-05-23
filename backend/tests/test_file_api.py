"""
Integration tests for file API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.file import File, FileCategory

TEST_PASSWORD = "TestPassword123"  # Test-only credential
TEST_HASHED_PASSWORD = "hashed"  # Test-only placeholder for hashed_password field


class TestFileMetadata:
    """Test get file metadata endpoint"""

    def test_get_file_metadata_owner(
        self,
        client: TestClient,
        test_db: Session,
        test_user: User
    ):
        """Owner should get file metadata"""
        # Create file
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

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD}
        )

        # Get metadata
        response = client.get(f"/api/v1/files/{file_record.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == file_record.id
        assert data["original_filename"] == "test.pdf"
        assert data["mime_type"] == "application/pdf"

    def test_get_file_metadata_not_owner(
        self,
        client: TestClient,
        test_db: Session,
        test_user: User
    ):
        """Non-owner should not get file metadata"""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=TEST_HASHED_PASSWORD,
            full_name="Other User",
            role=UserRole.READER
        )
        test_db.add(other_user)
        test_db.commit()

        # Create file owned by other user
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

        # Login as test_user
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD}
        )

        # Try to get metadata
        response = client.get(f"/api/v1/files/{file_record.id}")
        assert response.status_code == 403

    def test_get_file_metadata_not_found(
        self,
        client: TestClient,
        test_user: User
    ):
        """Non-existent file should return 404"""
        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD}
        )

        response = client.get("/api/v1/files/99999")
        assert response.status_code == 404


class TestFileDelete:
    """Test file delete endpoint"""

    def test_delete_file_success(
        self,
        client: TestClient,
        test_db: Session,
        test_user: User
    ):
        """Successful file deletion"""
        # Create file
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
        file_id = file_record.id

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD}
        )

        # Delete
        response = client.delete(f"/api/v1/files/{file_id}")
        assert response.status_code == 200
        assert response.json()["file_id"] == file_id

        # Verify file is deleted from database
        deleted_file = test_db.query(File).filter(File.id == file_id).first()
        assert deleted_file is None

    def test_delete_file_not_owner(
        self,
        client: TestClient,
        test_db: Session,
        test_user: User
    ):
        """Non-owner should not delete file"""
        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=TEST_HASHED_PASSWORD,
            full_name="Other User",
            role=UserRole.READER
        )
        test_db.add(other_user)
        test_db.commit()

        # Create file owned by other user
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

        # Login as test_user
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD}
        )

        # Try to delete
        response = client.delete(f"/api/v1/files/{file_record.id}")
        assert response.status_code == 403


class TestFileList:
    """Test list files endpoint"""

    def test_list_files(
        self,
        client: TestClient,
        test_db: Session,
        test_user: User
    ):
        """List user's files"""
        # Create files
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

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD}
        )

        # List files
        response = client.get("/api/v1/files")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 2
        assert len(data["files"]) == 2
        assert data["storage_used_bytes"] == 3000

    def test_list_files_by_category(
        self,
        client: TestClient,
        test_db: Session,
        test_user: User
    ):
        """List files filtered by category"""
        # Create files
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

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD}
        )

        # List tax files only
        response = client.get("/api/v1/files?category=tax")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert data["files"][0]["category"] == "tax"


class TestStorageQuota:
    """Test storage quota endpoint"""

    def test_get_storage_quota(
        self,
        client: TestClient,
        test_db: Session,
        test_user: User
    ):
        """Get user's storage quota"""
        # Create file
        file_record = File(
            uploaded_by=test_user.id,
            filename="uuid_test.pdf",
            original_filename="test.pdf",
            file_path="tax/uuid_test.pdf",
            mime_type="application/pdf",
            file_size=10 * 1024 * 1024,  # 10MB
            category=FileCategory.TAX
        )
        test_db.add(file_record)
        test_db.commit()

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD}
        )

        # Get quota
        response = client.get("/api/v1/files/storage/quota")
        assert response.status_code == 200

        data = response.json()
        assert data["storage_used_bytes"] == 10 * 1024 * 1024
        assert data["storage_limit_bytes"] == 200 * 1024 * 1024
        assert data["storage_used_mb"] == pytest.approx(10.0)
        assert data["storage_limit_mb"] == pytest.approx(200.0)
        assert data["storage_percentage"] == pytest.approx(5.0)
        assert data["files_count"] == 1
