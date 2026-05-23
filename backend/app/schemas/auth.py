"""
Authentication schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional

from app.models.user import UserRole
from app.core.security import validate_password_policy


class UserRegister(BaseModel):
    """Schema for user registration (admin-only)"""
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.READER

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password meets enhanced security requirements (adapted from DockerMate)"""
        is_valid, error_message = validate_password_policy(v)
        if not is_valid:
            raise ValueError(error_message)
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str
    remember_device: bool = False


class MFAVerify(BaseModel):
    """Schema for MFA code verification"""
    code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$")
    remember_device: bool = False


class UserResponse(BaseModel):
    """Schema for user response (public info)"""
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    mfa_enabled: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Schema for login response"""
    user: UserResponse
    requires_mfa: bool
    message: str
    mfa_token: Optional[str] = None  # Temporary token for MFA verification (5 min expiry)


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"


class PasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(..., min_length=12, max_length=128)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password meets enhanced security requirements (adapted from DockerMate)"""
        is_valid, error_message = validate_password_policy(v)
        if not is_valid:
            raise ValueError(error_message)
        return v
