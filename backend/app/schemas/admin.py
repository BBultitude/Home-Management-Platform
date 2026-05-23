"""
Admin Schemas
Pydantic models for admin user management and system oversight
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from uuid import UUID


# ===== User Management Schemas =====

class UserUpdateRequest(BaseModel):
    """Schema for updating user details"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=255)

    model_config = ConfigDict(from_attributes=True)


class UserRoleUpdateRequest(BaseModel):
    """Schema for updating user role"""
    role: str = Field(..., description="New role: admin, editor, or reader")

    model_config = ConfigDict(from_attributes=True)


class UserActiveUpdateRequest(BaseModel):
    """Schema for activating/deactivating user"""
    is_active: bool = Field(..., description="Active status")

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(BaseModel):
    """Schema for detailed user response (admin view)"""
    id: str
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    mfa_enabled: bool
    created_at: str
    updated_at: str
    last_login: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema for list of users"""
    users: list[UserDetailResponse]
    total: int
    limit: int
    offset: int


class MFAResetResponse(BaseModel):
    """Schema for MFA reset response"""
    secret: str
    qr_code: str
    message: str


# ===== System Statistics Schemas =====

class UserStats(BaseModel):
    """User count statistics"""
    total: int
    active: int
    inactive: int
    by_role: dict


class SecurityStats(BaseModel):
    """Security statistics"""
    mfa_enabled_count: int
    mfa_enabled_percentage: float


class ActivityStats(BaseModel):
    """Activity statistics"""
    recent_logins_7d: int
    total_audit_logs: int


class SystemStatsResponse(BaseModel):
    """Schema for system statistics"""
    users: UserStats
    security: SecurityStats
    activity: ActivityStats


class UserActivityStats(BaseModel):
    """User activity statistics"""
    total_actions: int
    creates: int
    updates: int
    deletes: int
    logins: int
    last_login: Optional[str] = None


class UserAccountInfo(BaseModel):
    """User account information"""
    created_at: str
    is_active: bool
    mfa_enabled: bool
    role: str


class UserStatisticsResponse(BaseModel):
    """Schema for user-specific statistics"""
    user_id: str
    username: str
    activity: UserActivityStats
    account: UserAccountInfo


# ===== Audit Log Query Schemas =====

class AuditLogQueryRequest(BaseModel):
    """Schema for audit log queries"""
    user_id: Optional[str] = None
    module: Optional[str] = None
    action: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)

    model_config = ConfigDict(from_attributes=True)
