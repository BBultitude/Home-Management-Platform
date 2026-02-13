"""
Unit tests for AuthService
"""

import pytest
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.auth_service import AuthService
from app.models.user import User, UserRole
from app.core.security import verify_password


class TestAuthService:
    """Test suite for AuthService"""

    def test_create_user_success(self, db_session: Session):
        """Test creating a new user"""
        user = AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User",
            role=UserRole.READER
        )

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.role == UserRole.READER
        assert user.is_active is True
        assert user.mfa_enabled is False
        assert verify_password("TestPassword123", user.hashed_password)

    def test_create_user_duplicate_username(self, db_session: Session):
        """Test creating user with duplicate username fails"""
        # Create first user
        AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test1@example.com",
            password="TestPassword123",
            full_name="Test User 1",
            role=UserRole.READER
        )

        # Try to create second user with same username
        with pytest.raises(HTTPException) as exc_info:
            AuthService.create_user(
                db=db_session,
                username="testuser",
                email="test2@example.com",
                password="TestPassword456",
                full_name="Test User 2",
                role=UserRole.READER
            )

        assert exc_info.value.status_code == 400
        assert "Username already exists" in exc_info.value.detail

    def test_create_user_duplicate_email(self, db_session: Session):
        """Test creating user with duplicate email fails"""
        # Create first user
        AuthService.create_user(
            db=db_session,
            username="testuser1",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User 1",
            role=UserRole.READER
        )

        # Try to create second user with same email
        with pytest.raises(HTTPException) as exc_info:
            AuthService.create_user(
                db=db_session,
                username="testuser2",
                email="test@example.com",
                password="TestPassword456",
                full_name="Test User 2",
                role=UserRole.READER
            )

        assert exc_info.value.status_code == 400
        assert "Email already exists" in exc_info.value.detail

    def test_authenticate_user_success(self, db_session: Session):
        """Test successful user authentication"""
        # Create user
        created_user = AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User",
            role=UserRole.READER
        )

        # Authenticate
        authenticated_user = AuthService.authenticate_user(
            db=db_session,
            username="testuser",
            password="TestPassword123"
        )

        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        assert authenticated_user.username == "testuser"

    def test_authenticate_user_wrong_password(self, db_session: Session):
        """Test authentication fails with wrong password"""
        # Create user
        AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User",
            role=UserRole.READER
        )

        # Try to authenticate with wrong password
        authenticated_user = AuthService.authenticate_user(
            db=db_session,
            username="testuser",
            password="WrongPassword"
        )

        assert authenticated_user is None

    def test_authenticate_user_nonexistent(self, db_session: Session):
        """Test authentication fails for nonexistent user"""
        authenticated_user = AuthService.authenticate_user(
            db=db_session,
            username="nonexistent",
            password="SomePassword123"
        )

        assert authenticated_user is None

    def test_authenticate_user_inactive(self, db_session: Session):
        """Test authentication fails for inactive user"""
        # Create user
        user = AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User",
            role=UserRole.READER
        )

        # Deactivate user
        user.is_active = False
        db_session.commit()

        # Try to authenticate
        authenticated_user = AuthService.authenticate_user(
            db=db_session,
            username="testuser",
            password="TestPassword123"
        )

        assert authenticated_user is None

    def test_authenticate_user_deleted(self, db_session: Session):
        """Test authentication fails for deleted user"""
        # Create user
        user = AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User",
            role=UserRole.READER
        )

        # Mark user as deleted
        user.is_deleted = True
        db_session.commit()

        # Try to authenticate
        authenticated_user = AuthService.authenticate_user(
            db=db_session,
            username="testuser",
            password="TestPassword123"
        )

        assert authenticated_user is None

    def test_create_session_token(self, db_session: Session):
        """Test creating session token"""
        # Create user
        user = AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User",
            role=UserRole.READER
        )

        # Create token
        token = AuthService.create_session_token(user)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_update_last_login(self, db_session: Session):
        """Test updating last login timestamp"""
        # Create user
        user = AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User",
            role=UserRole.READER
        )

        # Initially last_login should be None
        assert user.last_login is None

        # Update last login
        AuthService.update_last_login(db_session, user)

        # Refresh to get updated value
        db_session.refresh(user)
        assert user.last_login is not None

    def test_change_password_success(self, db_session: Session):
        """Test changing password"""
        # Create user
        user = AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="OldPassword123",
            full_name="Test User",
            role=UserRole.READER
        )

        old_hash = user.hashed_password

        # Change password
        result = AuthService.change_password(
            db=db_session,
            user=user,
            current_password="OldPassword123",
            new_password="NewPassword456"
        )

        assert result is True
        db_session.refresh(user)
        assert user.hashed_password != old_hash
        assert verify_password("NewPassword456", user.hashed_password)
        assert not verify_password("OldPassword123", user.hashed_password)

    def test_change_password_wrong_current(self, db_session: Session):
        """Test changing password fails with wrong current password"""
        # Create user
        user = AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="OldPassword123",
            full_name="Test User",
            role=UserRole.READER
        )

        # Try to change password with wrong current password
        with pytest.raises(HTTPException) as exc_info:
            AuthService.change_password(
                db=db_session,
                user=user,
                current_password="WrongPassword",
                new_password="NewPassword456"
            )

        assert exc_info.value.status_code == 400
        assert "Current password is incorrect" in exc_info.value.detail

    def test_get_user_by_id(self, db_session: Session):
        """Test getting user by ID"""
        # Create user
        user = AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User",
            role=UserRole.READER
        )

        # Get by ID
        retrieved_user = AuthService.get_user_by_id(db_session, user.id)

        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.username == "testuser"

    def test_get_user_by_id_inactive(self, db_session: Session):
        """Test getting inactive user by ID returns None"""
        # Create user
        user = AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User",
            role=UserRole.READER
        )

        # Deactivate
        user.is_active = False
        db_session.commit()

        # Try to get
        retrieved_user = AuthService.get_user_by_id(db_session, user.id)

        assert retrieved_user is None

    def test_get_user_by_username(self, db_session: Session):
        """Test getting user by username"""
        # Create user
        user = AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User",
            role=UserRole.READER
        )

        # Get by username
        retrieved_user = AuthService.get_user_by_username(db_session, "testuser")

        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.username == "testuser"

    def test_get_user_by_username_deleted(self, db_session: Session):
        """Test getting deleted user by username returns None"""
        # Create user
        user = AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
            full_name="Test User",
            role=UserRole.READER
        )

        # Mark as deleted
        user.is_deleted = True
        db_session.commit()

        # Try to get
        retrieved_user = AuthService.get_user_by_username(db_session, "testuser")

        assert retrieved_user is None
