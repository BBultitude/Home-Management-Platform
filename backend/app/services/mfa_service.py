"""
MFA (Multi-Factor Authentication) Service
Handles TOTP-based two-factor authentication
"""

import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.trusted_device import TrustedDevice
from app.core.security import encrypt_mfa_secret, decrypt_mfa_secret, create_trusted_device_token
from app.core.config import settings


class MFAService:
    """Service for MFA operations"""

    @staticmethod
    def generate_mfa_secret() -> str:
        """
        Generate a new TOTP secret (base32 encoded)

        Returns:
            Base32-encoded secret string (compatible with authenticator apps)
        """
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(user: User, secret: str) -> str:
        """
        Generate QR code for TOTP setup

        Args:
            user: User object (for username/email in QR)
            secret: TOTP secret (base32)

        Returns:
            Base64-encoded PNG image data (data URI compatible)
        """
        # Create provisioning URI (compatible with Google Authenticator, Bitwarden, etc.)
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.username,
            issuer_name="Home Management Platform"
        )

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()

        return f"data:image/png;base64,{img_base64}"

    @staticmethod
    def verify_totp_code(secret: str, code: str) -> bool:
        """
        Verify TOTP code against secret

        Args:
            secret: TOTP secret (base32)
            code: 6-digit code from authenticator app

        Returns:
            True if code is valid, False otherwise
        """
        if not code or len(code) != 6 or not code.isdigit():
            return False

        totp = pyotp.TOTP(secret)
        # Verify with window=1 to account for time drift (±30 seconds)
        return totp.verify(code, valid_window=1)

    @staticmethod
    def setup_mfa(user: User) -> tuple[str, str]:
        """
        Start MFA setup process

        Generates a new secret but does NOT enable MFA yet.
        User must verify the code before MFA is enabled.

        Args:
            user: User object

        Returns:
            Tuple of (secret, qr_code_data_uri)
        """
        secret = MFAService.generate_mfa_secret()
        qr_code = MFAService.generate_qr_code(user, secret)
        return secret, qr_code

    @staticmethod
    def enable_mfa(db: Session, user: User, secret: str, code: str) -> bool:
        """
        Enable MFA for user after verifying TOTP code

        Args:
            db: Database session
            user: User object
            secret: TOTP secret (from setup)
            code: 6-digit verification code

        Returns:
            True if MFA enabled successfully

        Raises:
            ValueError: If code verification fails
        """
        # Verify code before enabling
        if not MFAService.verify_totp_code(secret, code):
            raise ValueError("Invalid verification code")

        # Encrypt secret before storing
        encrypted_secret = encrypt_mfa_secret(secret)

        # Enable MFA
        user.mfa_enabled = True
        user.mfa_secret = encrypted_secret
        db.commit()

        return True

    @staticmethod
    def disable_mfa(db: Session, user: User) -> None:
        """
        Disable MFA for user

        Args:
            db: Database session
            user: User object
        """
        user.mfa_enabled = False
        user.mfa_secret = None
        db.commit()

        # Revoke all trusted devices when MFA is disabled
        db.query(TrustedDevice).filter(TrustedDevice.user_id == user.id).delete()
        db.commit()

    @staticmethod
    def verify_user_totp(user: User, code: str) -> bool:
        """
        Verify TOTP code for user during login

        Args:
            user: User object (must have MFA enabled)
            code: 6-digit code from authenticator app

        Returns:
            True if code is valid

        Raises:
            ValueError: If user doesn't have MFA enabled
        """
        if not user.mfa_enabled or not user.mfa_secret:
            raise ValueError("MFA is not enabled for this user")

        # Decrypt secret
        secret = decrypt_mfa_secret(user.mfa_secret)

        # Verify code
        return MFAService.verify_totp_code(secret, code)

    @staticmethod
    def create_trusted_device(
        db: Session,
        user_id: int,
        device_name: str,
        device_fingerprint: str,
        ip_address: str,
        user_agent: str
    ) -> TrustedDevice:
        """
        Create a trusted device entry

        Args:
            db: Database session
            user_id: User ID
            device_name: Human-readable device name
            device_fingerprint: Unique device identifier
            ip_address: IP address
            user_agent: User agent string

        Returns:
            Created TrustedDevice object
        """
        # Generate token for this device
        token = create_trusted_device_token(str(user_id), device_fingerprint)

        # Calculate expiry (30 days)
        expires_at = TrustedDevice.calculate_expiry()

        # Create device
        device = TrustedDevice(
            user_id=user_id,
            device_name=device_name,
            device_fingerprint=device_fingerprint,
            device_token=token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )

        db.add(device)
        db.commit()
        db.refresh(device)

        return device

    @staticmethod
    def verify_trusted_device(db: Session, user_id: int, device_fingerprint: str) -> Optional[TrustedDevice]:
        """
        Check if device is trusted and not expired

        Args:
            db: Database session
            user_id: User ID
            device_fingerprint: Device fingerprint to check

        Returns:
            TrustedDevice if valid and not expired, None otherwise
        """
        device = db.query(TrustedDevice).filter(
            TrustedDevice.user_id == user_id,
            TrustedDevice.device_fingerprint == device_fingerprint,
            TrustedDevice.is_active == True
        ).first()

        if not device:
            return None

        # Check if expired
        if device.is_expired():
            return None

        # Update last used timestamp
        device.last_used_at = datetime.utcnow()
        db.commit()

        return device

    @staticmethod
    def revoke_trusted_device(db: Session, user_id: int, device_id: int) -> bool:
        """
        Revoke a trusted device

        Args:
            db: Database session
            user_id: User ID (for authorization check)
            device_id: Device ID to revoke

        Returns:
            True if device was revoked
        """
        device = db.query(TrustedDevice).filter(
            TrustedDevice.id == device_id,
            TrustedDevice.user_id == user_id
        ).first()

        if not device:
            return False

        device.is_active = False
        db.commit()
        return True

    @staticmethod
    def revoke_all_trusted_devices(db: Session, user_id: int) -> int:
        """
        Revoke all trusted devices for a user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Number of devices revoked
        """
        result = db.query(TrustedDevice).filter(
            TrustedDevice.user_id == user_id,
            TrustedDevice.is_active == True
        ).update({"is_active": False})

        db.commit()
        return result

    @staticmethod
    def get_trusted_devices(db: Session, user_id: int) -> list[TrustedDevice]:
        """
        Get all trusted devices for a user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            List of TrustedDevice objects
        """
        return db.query(TrustedDevice).filter(
            TrustedDevice.user_id == user_id,
            TrustedDevice.is_active == True
        ).order_by(TrustedDevice.created_at.desc()).all()
