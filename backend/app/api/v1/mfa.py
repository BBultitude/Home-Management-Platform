"""
MFA API Endpoints
Handles multi-factor authentication operations
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth_service import AuthService
from app.services.mfa_service import MFAService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.mfa import (
    MFASetupResponse,
    MFAEnableRequest,
    MFAEnableResponse,
    MFADisableRequest,
    MFADisableResponse,
    MFAVerifyRequest,
    MFAVerifyResponse,
    TrustedDeviceResponse,
    TrustedDeviceListResponse,
    RevokeDeviceResponse,
)

router = APIRouter(prefix="/mfa", tags=["mfa"])


@router.post("/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Initiate MFA setup for current user

    Generates a new TOTP secret and QR code.
    User must scan QR code with authenticator app and verify before MFA is enabled.

    **Note**: MFA is NOT enabled until verification via /mfa/enable endpoint.
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled for this account"
        )

    secret, qr_code = MFAService.setup_mfa(current_user)

    return MFASetupResponse(
        secret=secret,
        qr_code=qr_code,
        message="Scan QR code with authenticator app (Google Authenticator, Bitwarden, etc.) and verify with code"
    )


@router.post("/enable", response_model=MFAEnableResponse)
async def enable_mfa(
    request: MFAEnableRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Enable MFA after verifying TOTP code

    Verifies the code from authenticator app and enables MFA if valid.
    The secret is encrypted and stored securely.
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled for this account"
        )

    try:
        MFAService.enable_mfa(db, current_user, request.secret, request.code)
        return MFAEnableResponse(
            message="MFA enabled successfully. Use authenticator app for future logins.",
            mfa_enabled=True
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/disable", response_model=MFADisableResponse)
async def disable_mfa(
    request: MFADisableRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Disable MFA for current user

    Requires password verification for security.
    All trusted devices will be revoked when MFA is disabled.
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled for this account"
        )

    # Verify password before disabling MFA
    if not AuthService.verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    # Get count of trusted devices before revoking
    devices_count = len(MFAService.get_trusted_devices(db, current_user.id))

    # Disable MFA (this also revokes all trusted devices)
    MFAService.disable_mfa(db, current_user)

    return MFADisableResponse(
        message="MFA disabled successfully. All trusted devices have been revoked.",
        mfa_enabled=False,
        devices_revoked=devices_count
    )


@router.get("/trusted-devices", response_model=TrustedDeviceListResponse)
async def list_trusted_devices(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    List all trusted devices for current user

    Shows devices that can skip MFA verification for 30 days.
    """
    devices = MFAService.get_trusted_devices(db, current_user.id)

    return TrustedDeviceListResponse(
        devices=devices,
        total=len(devices)
    )


@router.post("/trusted-devices/{device_id}/revoke", response_model=RevokeDeviceResponse)
async def revoke_trusted_device(
    device_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Revoke a specific trusted device

    The device will need to complete MFA verification on next login.
    """
    success = MFAService.revoke_trusted_device(db, current_user.id, device_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trusted device not found"
        )

    return RevokeDeviceResponse(
        message="Trusted device revoked successfully",
        devices_revoked=1
    )


@router.post("/trusted-devices/revoke-all", response_model=RevokeDeviceResponse)
async def revoke_all_trusted_devices(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Revoke all trusted devices for current user

    Useful if user suspects their account may be compromised.
    All devices will need to complete MFA verification on next login.
    """
    devices_revoked = MFAService.revoke_all_trusted_devices(db, current_user.id)

    return RevokeDeviceResponse(
        message=f"All trusted devices revoked successfully ({devices_revoked} devices)",
        devices_revoked=devices_revoked
    )
