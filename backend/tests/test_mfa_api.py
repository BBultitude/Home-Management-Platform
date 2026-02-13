"""
Integration tests for MFA API endpoints
Tests the complete MFA flow end-to-end
"""

import pytest
import pyotp
from fastapi.testclient import TestClient

from app.models.user import User
from app.services.auth_service import AuthService
from app.services.mfa_service import MFAService


class TestMFASetup:
    """Test MFA setup endpoint"""

    def test_setup_mfa_success(self, client: TestClient, test_user: User):
        """Test successful MFA setup"""
        # Login first
        token = AuthService.create_session_token(test_user)
        client.cookies.set("access_token", token)

        # Setup MFA
        response = client.post("/api/v1/mfa/setup")

        assert response.status_code == 200
        data = response.json()
        assert "secret" in data
        assert "qr_code" in data
        assert data["qr_code"].startswith("data:image/png;base64,")
        assert len(data["secret"]) == 32
        assert "Scan QR code" in data["message"]

    def test_setup_mfa_already_enabled(self, client: TestClient, test_user_with_mfa: User):
        """Test that setup fails if MFA already enabled"""
        token = AuthService.create_session_token(test_user_with_mfa)
        client.cookies.set("access_token", token)

        response = client.post("/api/v1/mfa/setup")

        assert response.status_code == 400
        assert "already enabled" in response.json()["detail"]

    def test_setup_mfa_unauthenticated(self, client: TestClient):
        """Test that setup requires authentication"""
        response = client.post("/api/v1/mfa/setup")
        assert response.status_code == 401


class TestMFAEnable:
    """Test MFA enable endpoint"""

    def test_enable_mfa_success(self, client: TestClient, test_user: User):
        """Test successful MFA enablement"""
        # Login first
        token = AuthService.create_session_token(test_user)
        client.cookies.set("access_token", token)

        # Setup MFA to get secret
        setup_response = client.post("/api/v1/mfa/setup")
        secret = setup_response.json()["secret"]

        # Generate valid TOTP code
        totp = pyotp.TOTP(secret)
        code = totp.now()

        # Enable MFA
        response = client.post(
            "/api/v1/mfa/enable",
            json={"secret": secret, "code": code}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mfa_enabled"] is True
        assert "enabled successfully" in data["message"]

    def test_enable_mfa_invalid_code(self, client: TestClient, test_user: User):
        """Test MFA enable fails with invalid code"""
        token = AuthService.create_session_token(test_user)
        client.cookies.set("access_token", token)

        # Setup MFA to get secret
        setup_response = client.post("/api/v1/mfa/setup")
        secret = setup_response.json()["secret"]

        # Try to enable with invalid code
        response = client.post(
            "/api/v1/mfa/enable",
            json={"secret": secret, "code": "000000"}
        )

        assert response.status_code == 400
        assert "Invalid verification code" in response.json()["detail"]

    def test_enable_mfa_already_enabled(self, client: TestClient, test_user_with_mfa: User):
        """Test that enable fails if MFA already enabled"""
        token = AuthService.create_session_token(test_user_with_mfa)
        client.cookies.set("access_token", token)

        response = client.post(
            "/api/v1/mfa/enable",
            json={"secret": "JBSWY3DPEHPK3PXP", "code": "123456"}
        )

        assert response.status_code == 400
        assert "already enabled" in response.json()["detail"]


class TestMFADisable:
    """Test MFA disable endpoint"""

    def test_disable_mfa_success(self, client: TestClient, test_user_with_mfa: User):
        """Test successful MFA disable"""
        token = AuthService.create_session_token(test_user_with_mfa)
        client.cookies.set("access_token", token)

        # Disable MFA with correct password
        response = client.post(
            "/api/v1/mfa/disable",
            json={"password": "MfaPassword123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["mfa_enabled"] is False
        assert "disabled successfully" in data["message"]
        assert data["devices_revoked"] >= 0

    def test_disable_mfa_wrong_password(self, client: TestClient, test_user_with_mfa: User):
        """Test MFA disable fails with wrong password"""
        token = AuthService.create_session_token(test_user_with_mfa)
        client.cookies.set("access_token", token)

        response = client.post(
            "/api/v1/mfa/disable",
            json={"password": "WrongPassword123"}
        )

        assert response.status_code == 401
        assert "Invalid password" in response.json()["detail"]

    def test_disable_mfa_not_enabled(self, client: TestClient, test_user: User):
        """Test that disable fails if MFA not enabled"""
        token = AuthService.create_session_token(test_user)
        client.cookies.set("access_token", token)

        response = client.post(
            "/api/v1/mfa/disable",
            json={"password": "TestPassword123"}
        )

        assert response.status_code == 400
        assert "not enabled" in response.json()["detail"]


class TestMFALoginFlow:
    """Test complete MFA login flow"""

    def test_login_with_mfa_enabled(self, client: TestClient, test_user_with_mfa: User):
        """Test login flow when MFA is enabled"""
        # Step 1: Login with username/password
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "mfauser", "password": "MfaPassword123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["requires_mfa"] is True
        assert "mfa_token" in data
        assert "verification required" in data["message"]

        # Should NOT set session cookie yet
        assert "access_token" not in client.cookies

        mfa_token = data["mfa_token"]

        # Step 2: Verify TOTP code
        from app.core.security import decrypt_mfa_secret
        secret = decrypt_mfa_secret(test_user_with_mfa.mfa_secret)
        totp = pyotp.TOTP(secret)
        code = totp.now()

        response = client.post(
            "/api/v1/auth/mfa/verify",
            json={"code": code, "remember_device": False},
            headers={"Authorization": f"Bearer {mfa_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["requires_mfa"] is False
        assert "successful" in data["message"]

        # Should set session cookie now
        assert "access_token" in client.cookies

    def test_login_with_invalid_mfa_code(self, client: TestClient, test_user_with_mfa: User):
        """Test login fails with invalid MFA code"""
        # Step 1: Login with username/password
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "mfauser", "password": "MfaPassword123"}
        )

        mfa_token = response.json()["mfa_token"]

        # Step 2: Try to verify with invalid code
        response = client.post(
            "/api/v1/auth/mfa/verify",
            json={"code": "000000", "remember_device": False},
            headers={"Authorization": f"Bearer {mfa_token}"}
        )

        assert response.status_code == 401
        assert "Invalid MFA code" in response.json()["detail"]

        # Should NOT set session cookie
        assert "access_token" not in client.cookies

    def test_login_without_mfa(self, client: TestClient, test_user: User):
        """Test login flow when MFA is not enabled"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["requires_mfa"] is False
        assert "successful" in data["message"]

        # Should set session cookie immediately
        assert "access_token" in client.cookies

    def test_mfa_verify_without_token(self, client: TestClient):
        """Test MFA verify fails without token"""
        response = client.post(
            "/api/v1/auth/mfa/verify",
            json={"code": "123456", "remember_device": False}
        )

        assert response.status_code == 401
        assert "MFA token required" in response.json()["detail"]

    def test_mfa_verify_with_expired_token(self, client: TestClient, test_user_with_mfa: User):
        """Test MFA verify fails with invalid token type"""
        # Create a regular access token instead of MFA pending token
        token = AuthService.create_session_token(test_user_with_mfa)

        response = client.post(
            "/api/v1/auth/mfa/verify",
            json={"code": "123456", "remember_device": False},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401
        assert "Invalid or expired MFA token" in response.json()["detail"]


class TestTrustedDevicesAPI:
    """Test trusted device management endpoints"""

    def test_list_trusted_devices_empty(self, client: TestClient, test_user: User):
        """Test listing trusted devices when none exist"""
        token = AuthService.create_session_token(test_user)
        client.cookies.set("access_token", token)

        response = client.get("/api/v1/mfa/trusted-devices")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["devices"]) == 0

    def test_list_trusted_devices(self, client: TestClient, test_user: User, test_db):
        """Test listing trusted devices"""
        # Create some trusted devices
        MFAService.create_trusted_device(
            db=test_db,
            user_id=test_user.id,
            device_name="Device 1",
            device_fingerprint="fingerprint-1",
            ip_address="127.0.0.1",
            user_agent="Browser 1"
        )
        MFAService.create_trusted_device(
            db=test_db,
            user_id=test_user.id,
            device_name="Device 2",
            device_fingerprint="fingerprint-2",
            ip_address="127.0.0.2",
            user_agent="Browser 2"
        )

        token = AuthService.create_session_token(test_user)
        client.cookies.set("access_token", token)

        response = client.get("/api/v1/mfa/trusted-devices")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["devices"]) == 2
        assert data["devices"][0]["device_name"] == "Device 2"  # Newest first

    def test_revoke_trusted_device(self, client: TestClient, test_user: User, test_db):
        """Test revoking a trusted device"""
        # Create a device
        device = MFAService.create_trusted_device(
            db=test_db,
            user_id=test_user.id,
            device_name="Test Device",
            device_fingerprint="test-fingerprint",
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )

        token = AuthService.create_session_token(test_user)
        client.cookies.set("access_token", token)

        # Revoke the device
        response = client.post(f"/api/v1/mfa/trusted-devices/{device.id}/revoke")

        assert response.status_code == 200
        data = response.json()
        assert data["devices_revoked"] == 1
        assert "revoked successfully" in data["message"]

    def test_revoke_nonexistent_device(self, client: TestClient, test_user: User):
        """Test revoking non-existent device"""
        token = AuthService.create_session_token(test_user)
        client.cookies.set("access_token", token)

        response = client.post("/api/v1/mfa/trusted-devices/99999/revoke")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_revoke_all_trusted_devices(self, client: TestClient, test_user: User, test_db):
        """Test revoking all trusted devices"""
        # Create multiple devices
        for i in range(3):
            MFAService.create_trusted_device(
                db=test_db,
                user_id=test_user.id,
                device_name=f"Device {i}",
                device_fingerprint=f"fingerprint-{i}",
                ip_address="127.0.0.1",
                user_agent="Browser"
            )

        token = AuthService.create_session_token(test_user)
        client.cookies.set("access_token", token)

        # Revoke all devices
        response = client.post("/api/v1/mfa/trusted-devices/revoke-all")

        assert response.status_code == 200
        data = response.json()
        assert data["devices_revoked"] == 3
        assert "3 devices" in data["message"]

        # Verify all devices are revoked
        list_response = client.get("/api/v1/mfa/trusted-devices")
        assert list_response.json()["total"] == 0


class TestMFAEndToEnd:
    """Test complete MFA lifecycle end-to-end"""

    def test_complete_mfa_lifecycle(self, client: TestClient, test_user: User, test_db):
        """Test full MFA lifecycle: setup → enable → login → disable"""
        # Step 1: Login as regular user
        token = AuthService.create_session_token(test_user)
        client.cookies.set("access_token", token)

        # Step 2: Setup MFA
        setup_response = client.post("/api/v1/mfa/setup")
        assert setup_response.status_code == 200
        secret = setup_response.json()["secret"]

        # Step 3: Enable MFA with valid code
        totp = pyotp.TOTP(secret)
        code = totp.now()
        enable_response = client.post(
            "/api/v1/mfa/enable",
            json={"secret": secret, "code": code}
        )
        assert enable_response.status_code == 200
        assert enable_response.json()["mfa_enabled"] is True

        # Step 4: Logout
        client.cookies.clear()

        # Step 5: Login with MFA
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )
        assert login_response.status_code == 200
        assert login_response.json()["requires_mfa"] is True
        mfa_token = login_response.json()["mfa_token"]

        # Step 6: Verify MFA code
        new_code = totp.now()
        verify_response = client.post(
            "/api/v1/auth/mfa/verify",
            json={"code": new_code, "remember_device": False},
            headers={"Authorization": f"Bearer {mfa_token}"}
        )
        assert verify_response.status_code == 200
        assert "access_token" in client.cookies

        # Step 7: Disable MFA
        disable_response = client.post(
            "/api/v1/mfa/disable",
            json={"password": "TestPassword123"}
        )
        assert disable_response.status_code == 200
        assert disable_response.json()["mfa_enabled"] is False

        # Step 8: Verify can now login without MFA
        client.cookies.clear()
        final_login = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )
        assert final_login.status_code == 200
        assert final_login.json()["requires_mfa"] is False
        assert "access_token" in client.cookies
