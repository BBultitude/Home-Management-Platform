"""
Admin API endpoints
User management, system statistics, and administrative oversight
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, require_admin
from app.models.user import User, UserRole
from app.services.admin_service import AdminService
from app.services.audit_service import AuditService
from app.models.audit_log import AuditModule, AuditAction, AuditLog
from app.schemas.admin import (
    UserUpdateRequest,
    UserRoleUpdateRequest,
    UserActiveUpdateRequest,
    UserDetailResponse,
    UserListResponse,
    MFAResetResponse,
    SystemStatsResponse,
    UserStatisticsResponse
)
from app.schemas.audit import AuditLogResponse, AuditLogListResponse


router = APIRouter(prefix="/admin", tags=["admin"])


# ===== User Management Endpoints =====

@router.get("/users", response_model=UserListResponse)
async def list_users(
    search: Optional[str] = Query(None, description="Search by username, email, or name"),
    role: Optional[str] = Query(None, description="Filter by role: admin, editor, reader"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users with optional filtering (admin only)

    Supports search and filtering by role and active status.
    """
    role_filter = UserRole(role) if role else None

    users = AdminService.list_users(
        db=db,
        search=search,
        role=role_filter,
        is_active=is_active,
        limit=limit,
        offset=offset
    )

    total = AdminService.get_user_count(
        db=db,
        search=search,
        role=role_filter,
        is_active=is_active
    )

    return UserListResponse(
        users=[
            UserDetailResponse(
                id=str(u.id),
                username=u.username,
                email=u.email,
                full_name=u.full_name,
                role=u.role.value,
                is_active=u.is_active,
                mfa_enabled=u.mfa_enabled,
                created_at=u.created_at.isoformat(),
                updated_at=u.updated_at.isoformat(),
                last_login=u.last_login.isoformat() if u.last_login else None
            )
            for u in users
        ],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get user details by ID (admin only)"""
    user = AdminService.get_user_by_id(db, user_id)

    return UserDetailResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.put("/users/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user details (admin only)

    Can update username, email, and full name.
    Cannot update role (use dedicated endpoint).
    """
    user = AdminService.update_user(
        db=db,
        user_id=user_id,
        admin_user=current_user,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name
    )

    return UserDetailResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.put("/users/{user_id}/role", response_model=UserDetailResponse)
async def update_user_role(
    user_id: UUID,
    role_data: UserRoleUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user role (admin only)

    Prevents:
    - Changing own role
    - Removing last admin
    """
    user = AdminService.update_user_role(
        db=db,
        user_id=user_id,
        admin_user=current_user,
        new_role=UserRole(role_data.role)
    )

    return UserDetailResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.put("/users/{user_id}/active", response_model=UserDetailResponse)
async def toggle_user_active(
    user_id: UUID,
    active_data: UserActiveUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Activate or deactivate user (admin only)

    Prevents:
    - Deactivating self
    - Deactivating last admin
    """
    user = AdminService.toggle_user_active(
        db=db,
        user_id=user_id,
        admin_user=current_user,
        is_active=active_data.is_active
    )

    return UserDetailResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete user (admin only)

    Prevents:
    - Deleting self
    - Deleting last admin

    WARNING: This permanently deletes the user.
    """
    AdminService.delete_user(db, user_id, current_user)

    return {"message": "User deleted successfully", "user_id": str(user_id)}


@router.post("/users/{user_id}/reset-mfa", response_model=MFAResetResponse)
async def reset_user_mfa(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Reset user's MFA setup (admin only)

    Generates new MFA secret and QR code.
    User must re-scan and re-enable MFA.
    """
    result = AdminService.reset_user_mfa(db, user_id, current_user)

    return MFAResetResponse(**result)


# ===== System Statistics Endpoints =====

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get system-wide statistics (admin only)

    Returns user counts, security stats, and activity metrics.
    """
    stats = AdminService.get_system_stats(db)

    return SystemStatsResponse(**stats)


@router.get("/users/{user_id}/stats", response_model=UserStatisticsResponse)
async def get_user_statistics(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific user (admin only)

    Returns activity counts and account information.
    """
    stats = AdminService.get_user_statistics(db, user_id)

    return UserStatisticsResponse(**stats)


# ===== Enhanced Audit Log Endpoints =====

@router.get("/audit/users/{user_id}", response_model=AuditLogListResponse)
async def get_user_audit_logs(
    user_id: UUID,
    module: Optional[str] = Query(None, description="Filter by module"),
    action: Optional[str] = Query(None, description="Filter by action"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific user (admin only)

    Returns all audit log entries for the specified user.
    """
    query = db.query(AuditLog).filter(AuditLog.user_id == user_id)

    if module:
        query = query.filter(AuditLog.module == AuditModule(module))

    if action:
        query = query.filter(AuditLog.action == AuditAction(action))

    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/audit/modules/{module}", response_model=AuditLogListResponse)
async def get_module_audit_logs(
    module: str,
    action: Optional[str] = Query(None, description="Filter by action"),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific module (admin only)

    Returns all audit log entries for the specified module.
    """
    query = db.query(AuditLog).filter(AuditLog.module == AuditModule(module))

    if action:
        query = query.filter(AuditLog.action == AuditAction(action))

    if user_id:
        query = query.filter(AuditLog.user_id == UUID(user_id))

    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/audit/actions/{action}", response_model=AuditLogListResponse)
async def get_action_audit_logs(
    action: str,
    module: Optional[str] = Query(None, description="Filter by module"),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get audit logs for a specific action (admin only)

    Returns all audit log entries for the specified action type.
    """
    query = db.query(AuditLog).filter(AuditLog.action == AuditAction(action))

    if module:
        query = query.filter(AuditLog.module == AuditModule(module))

    if user_id:
        query = query.filter(AuditLog.user_id == UUID(user_id))

    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        limit=limit,
        offset=offset
    )
