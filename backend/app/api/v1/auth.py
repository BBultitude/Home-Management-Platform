"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from datetime import timedelta

from app.db.database import get_db
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    LoginResponse,
    TokenResponse,
    PasswordChange,
    MFAVerify,
)
from app.services.auth_service import AuthService
from app.services.mfa_service import MFAService
from app.api.dependencies import (
    get_current_active_user,
    require_admin,
)
from app.models.user import User
from app.core.config import settings, is_development
from app.core.security import decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user (Admin only)"
)
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Register a new user (Admin only)

    Admins can create accounts for new users with specified roles.
    Passwords must be 12-128 characters with uppercase, lowercase, digit,
    and no common weak patterns (enhanced security for internet-facing platform).

    Args:
        user_data: User registration data
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        Created user object

    Raises:
        400: Username or email already exists
        403: Insufficient permissions (not admin)
    """
    user = AuthService.create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role
    )

    return user


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with username and password"
)
async def login(
    user_data: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with username and password

    On successful authentication:
    - Sets HTTP-only cookie with JWT token (secure, SameSite=Strict)
    - Updates last_login timestamp
    - Returns user info and MFA requirement status

    Args:
        user_data: Login credentials
        response: FastAPI response object (for setting cookies)
        db: Database session

    Returns:
        Login response with user info and MFA status

    Raises:
        401: Invalid credentials or inactive account
    """
    # Authenticate user
    user = AuthService.authenticate_user(
        db=db,
        username=user_data.username,
        password=user_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if MFA is enabled
    if user.mfa_enabled:
        # Check for trusted device
        # TODO: Implement device fingerprinting from request headers
        # For now, always require MFA

        # Create temporary MFA pending token (5 min expiry)
        mfa_token = AuthService.create_mfa_pending_token(user)

        return LoginResponse(
            user=UserResponse.model_validate(user),
            requires_mfa=True,
            mfa_token=mfa_token,
            message="MFA verification required. Please enter your 6-digit code."
        )

    # Generate session token
    access_token = AuthService.create_session_token(user)

    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not is_development(),  # HTTPS only in production
        samesite="strict",
        max_age=int(timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS).total_seconds())
    )

    # Update last login
    AuthService.update_last_login(db, user)

    return LoginResponse(
        user=UserResponse.model_validate(user),
        requires_mfa=False,
        message="Login successful"
    )


@router.post(
    "/mfa/verify",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify MFA code and complete login"
)
async def verify_mfa(
    mfa_data: MFAVerify,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Verify MFA code and complete login

    After successful password authentication, users with MFA enabled must
    verify their TOTP code. This endpoint:
    - Verifies the temporary MFA token (from /login)
    - Verifies the 6-digit TOTP code
    - Creates full session token and sets HTTP-only cookie
    - Optionally creates trusted device entry (30 day expiry)

    Args:
        mfa_data: MFA verification data (code, remember_device flag)
        request: FastAPI request object (for device info)
        response: FastAPI response object (for setting cookies)
        db: Database session

    Returns:
        Login response with user info

    Raises:
        401: Invalid or expired MFA token, or invalid TOTP code
    """
    # Get MFA token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MFA token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    mfa_token = auth_header.split(" ")[1]

    # Decode MFA pending token
    payload = decode_access_token(mfa_token)
    if not payload or payload.get("type") != "mfa_pending":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from token
    user_id = int(payload.get("sub"))
    user = AuthService.get_user_by_id(db, user_id)
    if not user or not user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA token"
        )

    # Verify TOTP code
    try:
        if not MFAService.verify_user_totp(user, mfa_data.code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # Create full session token
    access_token = AuthService.create_session_token(user)

    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=not is_development(),
        samesite="strict",
        max_age=int(timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS).total_seconds())
    )

    # Update last login
    AuthService.update_last_login(db, user)

    # TODO: Handle remember_device flag
    # if mfa_data.remember_device:
    #     # Extract device fingerprint from headers
    #     # Create trusted device entry
    #     pass

    return LoginResponse(
        user=UserResponse.model_validate(user),
        requires_mfa=False,
        message="MFA verification successful. Login complete."
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout and clear session"
)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout current user

    Clears the HTTP-only cookie containing the JWT token.

    Args:
        response: FastAPI response object (for clearing cookies)
        current_user: Current authenticated user

    Returns:
        Success message
    """
    # Clear the access token cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=not is_development(),
        samesite="strict"
    )

    return {
        "message": "Logout successful",
        "username": current_user.username
    }


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user info"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information

    Returns the currently authenticated user's profile information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user object

    Raises:
        401: Not authenticated
        403: Inactive or deleted account
    """
    return UserResponse.model_validate(current_user)


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change current user password"
)
async def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Change current user's password

    Requires current password for verification.
    New password must be 12-128 characters with uppercase, lowercase, digit,
    and no common weak patterns (enhanced security for internet-facing platform).

    Args:
        password_data: Current and new password
        db: Database session
        current_user: Current authenticated user

    Returns:
        Success message

    Raises:
        400: Current password is incorrect
        401: Not authenticated
    """
    AuthService.change_password(
        db=db,
        user=current_user,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )

    return {
        "message": "Password changed successfully",
        "username": current_user.username
    }
