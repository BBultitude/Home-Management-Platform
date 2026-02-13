"""
MFA (Multi-Factor Authentication) Schemas
Request and response models for MFA operations
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MFASetupResponse(BaseModel):
    """Response for MFA setup initiation"""
    secret: str = Field(..., description="TOTP secret (temporary, for verification)")
    qr_code: str = Field(..., description="Base64-encoded QR code data URI")
    message: str = Field(default="Scan QR code with authenticator app and verify")

    model_config = {"from_attributes": True}


class MFAEnableRequest(BaseModel):
    """Request to enable MFA after setup"""
    secret: str = Field(..., description="TOTP secret from setup")
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")


class MFAEnableResponse(BaseModel):
    """Response after enabling MFA"""
    message: str = Field(default="MFA enabled successfully")
    mfa_enabled: bool = Field(default=True)


class MFADisableRequest(BaseModel):
    """Request to disable MFA"""
    password: str = Field(..., description="Current password for verification")


class MFADisableResponse(BaseModel):
    """Response after disabling MFA"""
    message: str = Field(default="MFA disabled successfully")
    mfa_enabled: bool = Field(default=False)
    devices_revoked: int = Field(..., description="Number of trusted devices revoked")


class MFAVerifyRequest(BaseModel):
    """Request to verify TOTP code during login"""
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")
    trust_device: bool = Field(default=False, description="Trust this device for 30 days")
    device_name: Optional[str] = Field(None, description="Human-readable device name")


class MFAVerifyResponse(BaseModel):
    """Response after successful MFA verification"""
    message: str = Field(default="MFA verification successful")
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer")
    trusted_device_token: Optional[str] = Field(None, description="Trusted device token (if trust_device=true)")


class TrustedDeviceResponse(BaseModel):
    """Response model for trusted device"""
    id: int
    device_name: str
    device_fingerprint: str
    ip_address: str
    user_agent: str
    created_at: datetime
    last_used_at: datetime
    expires_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}


class TrustedDeviceListResponse(BaseModel):
    """Response for listing trusted devices"""
    devices: list[TrustedDeviceResponse]
    total: int


class RevokeDeviceResponse(BaseModel):
    """Response after revoking device(s)"""
    message: str
    devices_revoked: int
