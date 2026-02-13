"""
Unit tests for MFA Service
Tests TOTP generation, QR codes, verification, and trusted devices
"""

import pytest
import pyotp
import re
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from app.services.mfa_service import MFAService
from app.models.user import User, UserRole
from app.models.trusted_device import TrustedDevice


class TestMFASecretGeneration:
    """Test MFA secret generation"""

    def test_generate_mfa_secret(self):
        """Test that MFA secret is generated correctly"""
        secret = MFAService.generate_mfa_secret()

        # Should be base32 encoded string
        assert isinstance(secret, str)
        assert len(secret) == 32  # PyOTP default length
        # Should only contain valid base32 characters (A-Z, 2-7)
        assert re.match(r'^[A-Z2-7]+$', secret)

    def test_generate_multiple_unique_secrets(self):
        """Test that multiple secrets are unique"""
        secrets = [MFAService.generate_mfa_secret() for _ in range(10)]
        # All secrets should be unique
        assert len(secrets) == len(set(secrets))


class TestQRCodeGeneration:
    """Test QR code generation"""

    def test_generate_qr_code(self):
        """Test QR code generation for TOTP setup"""
        user = Mock(spec=User)
        user.username = "testuser"

        secret = MFAService.generate_mfa_secret()
        qr_code = MFAService.generate_qr_code(user, secret)

        # Should be a data URI
        assert qr_code.startswith("data:image/png;base64,")
        # Should have base64 encoded data
        assert len(qr_code) > 100  # QR codes are reasonably large

    def test_qr_code_contains_correct_provisioning_uri(self):
        """Test that QR code encodes correct provisioning URI"""
        user = Mock(spec=User)
        user.username = "testuser"
        secret = "JBSWY3DPEHPK3PXP"  # Fixed secret for testing

        # Generate QR code
        qr_code = MFAService.generate_qr_code(user, secret)

        # Verify it's a valid data URI
        assert qr_code.startswith("data:image/png;base64,")

        # The provisioning URI should follow this format:
        # otpauth://totp/Home%20Management%20Platform:testuser?secret=JBSWY3DPEHPK3PXP&issuer=Home%20Management%20Platform


class TestTOTPVerification:
    """Test TOTP code verification"""

    def test_verify_valid_totp_code(self):
        """Test verification of valid TOTP code"""
        secret = MFAService.generate_mfa_secret()
        totp = pyotp.TOTP(secret)
        code = totp.now()

        # Should verify successfully
        assert MFAService.verify_totp_code(secret, code) is True

    def test_verify_invalid_totp_code(self):
        """Test rejection of invalid TOTP code"""
        secret = MFAService.generate_mfa_secret()

        # Should reject invalid code
        assert MFAService.verify_totp_code(secret, "000000") is False

    def test_verify_code_with_time_window(self):
        """Test that verification allows small time drift"""
        secret = MFAService.generate_mfa_secret()
        totp = pyotp.TOTP(secret)

        # Get code from 30 seconds ago
        past_code = totp.at(datetime.now() - timedelta(seconds=30))

        # Should still verify (window=1 allows ±30 seconds)
        assert MFAService.verify_totp_code(secret, past_code) is True

    def test_verify_empty_code(self):
        """Test rejection of empty code"""
        secret = MFAService.generate_mfa_secret()
        assert MFAService.verify_totp_code(secret, "") is False

    def test_verify_non_digit_code(self):
        """Test rejection of non-digit code"""
        secret = MFAService.generate_mfa_secret()
        assert MFAService.verify_totp_code(secret, "abcdef") is False

    def test_verify_wrong_length_code(self):
        """Test rejection of wrong length code"""
        secret = MFAService.generate_mfa_secret()
        assert MFAService.verify_totp_code(secret, "12345") is False  # 5 digits
        assert MFAService.verify_totp_code(secret, "1234567") is False  # 7 digits


class TestMFASetup:
    """Test MFA setup process"""

    def test_setup_mfa(self):
        """Test MFA setup returns secret and QR code"""
        user = Mock(spec=User)
        user.username = "testuser"

        secret, qr_code = MFAService.setup_mfa(user)

        # Should return valid secret
        assert isinstance(secret, str)
        assert len(secret) == 32
        assert re.match(r'^[A-Z2-7]+$', secret)

        # Should return valid QR code
        assert qr_code.startswith("data:image/png;base64,")


class TestMFAEnableDisable:
    """Test enabling and disabling MFA"""

    def test_enable_mfa_with_valid_code(self, test_db, test_user):
        """Test enabling MFA with valid verification code"""
        secret = MFAService.generate_mfa_secret()
        totp = pyotp.TOTP(secret)
        code = totp.now()

        # Enable MFA
        result = MFAService.enable_mfa(test_db, test_user, secret, code)

        assert result is True
        assert test_user.mfa_enabled is True
        assert test_user.mfa_secret is not None
        assert test_user.mfa_secret != secret  # Should be encrypted

    def test_enable_mfa_with_invalid_code(self, test_db, test_user):
        """Test that enabling MFA fails with invalid code"""
        secret = MFAService.generate_mfa_secret()

        with pytest.raises(ValueError, match="Invalid verification code"):
            MFAService.enable_mfa(test_db, test_user, secret, "000000")

        # MFA should not be enabled
        assert test_user.mfa_enabled is False
        assert test_user.mfa_secret is None

    def test_disable_mfa(self, test_db, test_user_with_mfa):
        """Test disabling MFA"""
        # Disable MFA
        MFAService.disable_mfa(test_db, test_user_with_mfa)

        assert test_user_with_mfa.mfa_enabled is False
        assert test_user_with_mfa.mfa_secret is None

    def test_disable_mfa_revokes_trusted_devices(self, test_db, test_user_with_mfa):
        """Test that disabling MFA revokes all trusted devices"""
        # Create a trusted device
        device = MFAService.create_trusted_device(
            db=test_db,
            user_id=test_user_with_mfa.id,
            device_name="Test Device",
            device_fingerprint="test-fingerprint",
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )

        device_id = device.id
        assert device.is_active is True

        # Disable MFA
        MFAService.disable_mfa(test_db, test_user_with_mfa)

        # Device should be deleted (not just inactive)
        devices = test_db.query(TrustedDevice).filter(
            TrustedDevice.user_id == test_user_with_mfa.id
        ).all()
        assert len(devices) == 0

        # Verify device is actually deleted, not just inactive
        deleted_device = test_db.query(TrustedDevice).filter(
            TrustedDevice.id == device_id
        ).first()
        assert deleted_device is None


class TestVerifyUserTOTP:
    """Test TOTP verification for user"""

    def test_verify_user_totp_success(self, test_db, test_user_with_mfa):
        """Test successful TOTP verification for user"""
        # Generate code from user's secret (we need to decrypt it first)
        from app.core.security import decrypt_mfa_secret
        secret = decrypt_mfa_secret(test_user_with_mfa.mfa_secret)
        totp = pyotp.TOTP(secret)
        code = totp.now()

        # Verify code
        result = MFAService.verify_user_totp(test_user_with_mfa, code)
        assert result is True

    def test_verify_user_totp_invalid_code(self, test_db, test_user_with_mfa):
        """Test TOTP verification fails with invalid code"""
        result = MFAService.verify_user_totp(test_user_with_mfa, "000000")
        assert result is False

    def test_verify_user_totp_mfa_not_enabled(self, test_db, test_user):
        """Test that verification fails if MFA not enabled"""
        with pytest.raises(ValueError, match="MFA is not enabled"):
            MFAService.verify_user_totp(test_user, "123456")


class TestTrustedDevices:
    """Test trusted device management"""

    def test_create_trusted_device(self, test_db, test_user):
        """Test creating a trusted device"""
        device = MFAService.create_trusted_device(
            db=test_db,
            user_id=test_user.id,
            device_name="My Phone",
            device_fingerprint="unique-fingerprint-123",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0"
        )

        assert device.id is not None
        assert device.user_id == test_user.id
        assert device.device_name == "My Phone"
        assert device.device_fingerprint == "unique-fingerprint-123"
        assert device.is_active is True
        assert device.device_token is not None
        assert device.expires_at > datetime.utcnow()

    def test_verify_trusted_device_success(self, test_db, test_user):
        """Test verifying a valid trusted device"""
        # Create device
        device = MFAService.create_trusted_device(
            db=test_db,
            user_id=test_user.id,
            device_name="Test Device",
            device_fingerprint="test-fingerprint",
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )

        # Verify device
        verified = MFAService.verify_trusted_device(
            db=test_db,
            user_id=test_user.id,
            device_fingerprint="test-fingerprint"
        )

        assert verified is not None
        assert verified.id == device.id
        assert verified.last_used_at is not None

    def test_verify_trusted_device_not_found(self, test_db, test_user):
        """Test verifying non-existent device"""
        verified = MFAService.verify_trusted_device(
            db=test_db,
            user_id=test_user.id,
            device_fingerprint="nonexistent"
        )
        assert verified is None

    def test_verify_expired_trusted_device(self, test_db, test_user):
        """Test that expired devices are not verified"""
        # Create device
        device = MFAService.create_trusted_device(
            db=test_db,
            user_id=test_user.id,
            device_name="Test Device",
            device_fingerprint="test-fingerprint",
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )

        # Manually expire the device
        device.expires_at = datetime.utcnow() - timedelta(days=1)
        test_db.commit()

        # Verify should fail
        verified = MFAService.verify_trusted_device(
            db=test_db,
            user_id=test_user.id,
            device_fingerprint="test-fingerprint"
        )
        assert verified is None

    def test_revoke_trusted_device(self, test_db, test_user):
        """Test revoking a trusted device"""
        # Create device
        device = MFAService.create_trusted_device(
            db=test_db,
            user_id=test_user.id,
            device_name="Test Device",
            device_fingerprint="test-fingerprint",
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )

        # Revoke device
        result = MFAService.revoke_trusted_device(test_db, test_user.id, device.id)
        assert result is True

        # Refresh device
        test_db.refresh(device)
        assert device.is_active is False

    def test_revoke_nonexistent_device(self, test_db, test_user):
        """Test revoking non-existent device"""
        result = MFAService.revoke_trusted_device(test_db, test_user.id, 99999)
        assert result is False

    def test_revoke_all_trusted_devices(self, test_db, test_user):
        """Test revoking all trusted devices"""
        # Create multiple devices
        for i in range(3):
            MFAService.create_trusted_device(
                db=test_db,
                user_id=test_user.id,
                device_name=f"Device {i}",
                device_fingerprint=f"fingerprint-{i}",
                ip_address="127.0.0.1",
                user_agent="Test Browser"
            )

        # Revoke all
        count = MFAService.revoke_all_trusted_devices(test_db, test_user.id)
        assert count == 3

        # Verify all are inactive
        devices = MFAService.get_trusted_devices(test_db, test_user.id)
        assert len(devices) == 0

    def test_get_trusted_devices(self, test_db, test_user):
        """Test listing trusted devices"""
        # Create multiple devices
        for i in range(3):
            MFAService.create_trusted_device(
                db=test_db,
                user_id=test_user.id,
                device_name=f"Device {i}",
                device_fingerprint=f"fingerprint-{i}",
                ip_address="127.0.0.1",
                user_agent="Test Browser"
            )

        devices = MFAService.get_trusted_devices(test_db, test_user.id)
        assert len(devices) == 3
        # Should be ordered by created_at desc (newest first)
        assert devices[0].device_name == "Device 2"
        assert devices[1].device_name == "Device 1"
        assert devices[2].device_name == "Device 0"

    def test_get_trusted_devices_excludes_inactive(self, test_db, test_user):
        """Test that inactive devices are not returned"""
        # Create devices
        device1 = MFAService.create_trusted_device(
            db=test_db,
            user_id=test_user.id,
            device_name="Device 1",
            device_fingerprint="fingerprint-1",
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )

        device2 = MFAService.create_trusted_device(
            db=test_db,
            user_id=test_user.id,
            device_name="Device 2",
            device_fingerprint="fingerprint-2",
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )

        # Revoke device 1
        MFAService.revoke_trusted_device(test_db, test_user.id, device1.id)

        # Should only return device 2
        devices = MFAService.get_trusted_devices(test_db, test_user.id)
        assert len(devices) == 1
        assert devices[0].id == device2.id
