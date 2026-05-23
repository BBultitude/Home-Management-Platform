"""
Pytest configuration and shared fixtures
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.services.mfa_service import MFAService
import pyotp

# Test database URL (SQLite for testing)
import os
import tempfile
# Use a temporary directory for test database to avoid permission issues
test_db_path = os.path.join(tempfile.gettempdir(), "home_platform_test.db")
SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///{test_db_path}"

# Create test engine
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db):
    """Alias for db fixture to match test naming"""
    return db


@pytest.fixture(scope="function")
def test_db(db):
    """Alias for db fixture to match test naming in MFA tests"""
    return db


@pytest.fixture(scope="function")
def admin_user(db_session):
    """Create an admin user for testing"""
    user = AuthService.create_user(
        db=db_session,
        username="admin",
        email="admin@test.com",
        password="AdminPassword123",
        full_name="Admin User",
        role=UserRole.ADMIN
    )
    return user


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a regular user without MFA for testing"""
    user = AuthService.create_user(
        db=db_session,
        username="testuser",
        email="testuser@test.com",
        password="TestPassword123",
        full_name="Test User",
        role=UserRole.READER
    )
    return user


@pytest.fixture(scope="function")
def test_user_with_mfa(db_session):
    """Create a user with MFA enabled for testing"""
    user = AuthService.create_user(
        db=db_session,
        username="mfauser",
        email="mfauser@test.com",
        password="MfaPassword123",
        full_name="MFA User",
        role=UserRole.READER
    )

    # Enable MFA
    secret = MFAService.generate_mfa_secret()
    totp = pyotp.TOTP(secret)
    code = totp.now()
    MFAService.enable_mfa(db_session, user, secret, code)

    return user


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass  # intentional - db lifecycle is managed by the db fixture

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
