"""
Integration tests for authentication API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.services.auth_service import AuthService

TEST_PASSWORD = "TestPassword123"  # Test-only credential
TEST_PASSWORD_OLD = "OldPassword123"  # Test-only credential (change-password tests)
TEST_PASSWORD_NEW = "NewPassword456"  # Test-only credential (change-password tests)
TEST_PASSWORD_WRONG = "WrongPassword"  # Test-only: intentionally incorrect password
TEST_PASSWORD_NONEXISTENT = "SomePassword123"  # Test-only: password for non-existent user
TEST_PASSWORD_REGISTER = "NewPassword123"  # Test-only credential (registration tests)
TEST_PASSWORD_TOO_SHORT = "Short1"  # Test-only: intentionally invalid (too short) password
TEST_PASSWORD_WEAK = "Password123"  # Test-only: intentionally weak password


class TestAuthAPI:
    """Test suite for authentication API endpoints"""

    def test_login_success(self, client: TestClient, db_session: Session):
        """Test successful login"""
        # Create user
        AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password=TEST_PASSWORD,
            full_name="Test User",
            role=UserRole.READER
        )

        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Login successful"
        assert data["requires_mfa"] is False
        assert data["user"]["username"] == "testuser"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["role"] == "Reader"

        # Check cookie was set
        assert "access_token" in response.cookies

    def test_login_invalid_credentials(self, client: TestClient, db_session: Session):
        """Test login with invalid credentials"""
        # Create user
        AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password=TEST_PASSWORD,
            full_name="Test User",
            role=UserRole.READER
        )

        # Try to login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD_WRONG}
        )

        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": TEST_PASSWORD_NONEXISTENT}
        )

        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    def test_get_current_user(self, client: TestClient, db_session: Session):
        """Test getting current user info"""
        # Create and login user
        AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password=TEST_PASSWORD,
            full_name="Test User",
            role=UserRole.READER
        )

        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD}
        )

        # Get current user
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["role"] == "Reader"

    def test_get_current_user_unauthenticated(self, client: TestClient):
        """Test getting current user without authentication"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_register_user_as_admin(self, client: TestClient, db_session: Session, admin_user: User):
        """Test registering new user as admin"""
        # Login as admin
        token = AuthService.create_session_token(admin_user)
        client.cookies.set("access_token", token)

        # Register new user
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": TEST_PASSWORD_REGISTER,
                "full_name": "New User",
                "role": "Editor"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert data["role"] == "Editor"
        assert data["is_active"] is True

    def test_register_user_as_non_admin(self, client: TestClient, db_session: Session):
        """Test that non-admin cannot register users"""
        # Create and login as reader
        user = AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password=TEST_PASSWORD,
            full_name="Test User",
            role=UserRole.READER
        )

        token = AuthService.create_session_token(user)
        client.cookies.set("access_token", token)

        # Try to register new user
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": TEST_PASSWORD_REGISTER,
                "full_name": "New User",
                "role": "Reader"
            }
        )

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_register_duplicate_username(self, client: TestClient, db_session: Session, admin_user: User):
        """Test registering user with duplicate username"""
        # Create existing user
        AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password=TEST_PASSWORD,
            full_name="Test User",
            role=UserRole.READER
        )

        # Login as admin
        token = AuthService.create_session_token(admin_user)
        client.cookies.set("access_token", token)

        # Try to register with same username
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "different@example.com",
                "password": TEST_PASSWORD_REGISTER,
                "full_name": "Different User",
                "role": "Reader"
            }
        )

        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]

    def test_logout(self, client: TestClient, db_session: Session):
        """Test logout"""
        # Create and login user
        AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password=TEST_PASSWORD,
            full_name="Test User",
            role=UserRole.READER
        )

        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD}
        )

        # Logout
        response = client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logout successful"
        assert data["username"] == "testuser"

    def test_change_password_success(self, client: TestClient, db_session: Session):
        """Test changing password"""
        # Create and login user
        AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password=TEST_PASSWORD_OLD,
            full_name="Test User",
            role=UserRole.READER
        )

        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD_OLD}
        )

        # Change password
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": TEST_PASSWORD_OLD,
                "new_password": TEST_PASSWORD_NEW
            }
        )

        assert response.status_code == 200
        assert "Password changed successfully" in response.json()["message"]

        # Verify can login with new password
        client.post("/api/v1/auth/logout")
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD_NEW}
        )

        assert login_response.status_code == 200

    def test_change_password_wrong_current(self, client: TestClient, db_session: Session):
        """Test changing password with wrong current password"""
        # Create and login user
        AuthService.create_user(
            db=db_session,
            username="testuser",
            email="test@example.com",
            password=TEST_PASSWORD_OLD,
            full_name="Test User",
            role=UserRole.READER
        )

        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": TEST_PASSWORD_OLD}
        )

        # Try to change password with wrong current password
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": TEST_PASSWORD_WRONG,
                "new_password": TEST_PASSWORD_NEW
            }
        )

        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]

    def test_password_validation_too_short(self, client: TestClient, admin_user: User):
        """Test password validation - too short"""
        # Login as admin
        token = AuthService.create_session_token(admin_user)
        client.cookies.set("access_token", token)

        # Try to register with short password
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": TEST_PASSWORD_TOO_SHORT,  # Only 6 characters
                "full_name": "New User",
                "role": "Reader"
            }
        )

        assert response.status_code == 422  # Validation error
        assert "at least 12 characters" in str(response.json())

    def test_username_validation(self, client: TestClient, admin_user: User):
        """Test username validation"""
        # Login as admin
        token = AuthService.create_session_token(admin_user)
        client.cookies.set("access_token", token)

        # Try to register with invalid username (too short)
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "ab",  # Only 2 characters
                "email": "new@example.com",
                "password": TEST_PASSWORD_WEAK,
                "full_name": "New User",
                "role": "Reader"
            }
        )

        assert response.status_code == 422  # Validation error
