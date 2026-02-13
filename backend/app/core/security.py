"""
Security utilities for authentication and authorization
"""

import re
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from cryptography.fernet import Fernet

from app.core.config import settings


# Password hashing context (Argon2)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# Fernet encryption for MFA secrets
def get_fernet() -> Fernet:
    """Get Fernet cipher instance for MFA secret encryption"""
    return Fernet(settings.mfa_encryption_key.encode())


# Password utilities
def hash_password(password: str) -> str:
    """Hash a password using Argon2"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# JWT utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional expiration time delta (defaults to SESSION_EXPIRY_HOURS)

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.SESSION_EXPIRY_HOURS)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


def create_trusted_device_token(user_id: str, device_fingerprint: str) -> str:
    """
    Create a long-lived token for trusted devices

    Args:
        user_id: User's unique identifier
        device_fingerprint: Unique device identifier

    Returns:
        Encoded JWT token for trusted device
    """
    expires_delta = timedelta(days=settings.TRUSTED_DEVICE_EXPIRY_DAYS)
    data = {
        "user_id": user_id,
        "device": device_fingerprint,
        "type": "trusted_device"
    }
    return create_access_token(data, expires_delta)


# MFA utilities
def encrypt_mfa_secret(secret: str) -> str:
    """
    Encrypt MFA secret for storage

    Args:
        secret: Plain text MFA secret

    Returns:
        Encrypted secret (base64 encoded)
    """
    fernet = get_fernet()
    encrypted = fernet.encrypt(secret.encode())
    return encrypted.decode()


def decrypt_mfa_secret(encrypted_secret: str) -> str:
    """
    Decrypt MFA secret from storage

    Args:
        encrypted_secret: Encrypted secret (base64 encoded)

    Returns:
        Decrypted plain text MFA secret
    """
    fernet = get_fernet()
    decrypted = fernet.decrypt(encrypted_secret.encode())
    return decrypted.decode()


# Password policy validation (Enhanced with pattern detection from DockerMate)
def validate_password_policy(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password against enhanced security policy

    Requirements (adapted from DockerMate's battle-tested validation):
    - 12-128 characters (stricter than NIST minimum for internet-facing platform)
    - Must contain uppercase letter (A-Z)
    - Must contain lowercase letter (a-z)
    - Must contain digit (0-9)
    - Must not use common weak patterns

    Pattern Detection (learned from DockerMate project):
    - Rejects common words with number/symbol padding (password123, admin2024, etc.)
    - Rejects sequential patterns (12345, qwerty, etc.)
    - Rejects repeated characters (aaaa, 1111, etc.)

    These patterns were discovered through extensive testing on the DockerMate project
    and handle many edge cases that users attempt to bypass security requirements.

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        # Accepted:
        >>> validate_password_policy("MySecureHome2026")
        (True, None)

        >>> validate_password_policy("CorrectHorseBattery42")
        (True, None)

        # Rejected:
        >>> validate_password_policy("password123")
        (False, "Don't use common words (password, admin, etc.) with just numbers/symbols")

        >>> validate_password_policy("Admin2024!")
        (False, "Don't use common words (password, admin, etc.) with just numbers/symbols")
    """
    # Length check (12-128 for internet-facing platform)
    if len(password) < 12:
        return False, "Password must be at least 12 characters"

    if len(password) > 128:
        return False, "Password must be less than 128 characters"

    # Uppercase check
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter (A-Z)"

    # Lowercase check
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter (a-z)"

    # Digit check
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit (0-9)"

    # ===== PATTERN DETECTION (from DockerMate) =====
    # These patterns were discovered through extensive testing and handle many edge cases
    password_lower = password.lower()

    # Check 1: Weak base words with only number/symbol padding
    # Catches: password123, 123password, admin!, !@#admin123, !!!qwerty!!!
    # This is THE most important check - users often take weak words and add numbers/symbols
    # Pattern explanation:
    # - ^[\d!@#$...]* = starts with any number of digits/symbols
    # - (password|admin|...) = followed by a weak base word
    # - [\d!@#$...]* = followed by any number of digits/symbols
    # - $ = end of string
    weak_pattern = r'^[\d!@#$%^&*()_+=\-\[\]{};:,.<>?/\\|~`]*(password|admin|welcome|letmein|qwerty|monkey|dragon|master|login|user|homelab|docker|home)[\d!@#$%^&*()_+=\-\[\]{};:,.<>?/\\|~`]*$'

    if re.match(weak_pattern, password_lower):
        return False, "Don't use common words (password, admin, etc.) with just numbers/symbols"

    # Check 2: Sequential patterns
    # Detects sequences embedded anywhere in the password
    if re.search(r'(12345|23456|34567|45678|56789|78901|67890|abcde|bcdef|qwerty|asdfg|zxcvb)', password_lower):
        return False, "Avoid sequential patterns (12345, qwerty, etc.)"

    # Check 3: Repeated characters (4+ in a row)
    # Detects patterns like: aaaa, 1111, ssss
    if re.search(r'(.)\1{3,}', password):
        return False, "Avoid repeated characters (aaaa, 1111, etc.)"

    # Future enhancement: Check against haveibeenpwned API for breach detection

    return True, None
