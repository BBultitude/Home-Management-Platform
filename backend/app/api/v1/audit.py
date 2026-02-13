"""
Audit Log API Endpoints
Provides access to audit trail for admins and users
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.services.audit_service import AuditService
from app.api.dependencies import require_admin, get_current_active_user
from app.models.user import User
from app.models.audit_log import EventType, Severity, AuditLog
from app.schemas.audit import AuditLogResponse, AuditLogListResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get(
    "",
    response_model=AuditLogListResponse,
    summary="Get all audit logs (Admin only)"
)
async def get_all_audit_logs(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs to return"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    severity: Optional[Severity] = Query(None, description="Filter by severity"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all audit logs (Admin-only)

    Returns audit logs with optional filtering. Only admins can access
    all logs across all users.

    **Query Parameters:**
    - **limit**: Number of logs to return (1-1000, default 100)
    - **offset**: Pagination offset
    - **event_type**: Filter by specific event type (LOGIN_SUCCESS, USER_CREATE, etc.)
    - **user_id**: Filter by specific user
    - **severity**: Filter by severity (INFO, WARNING, ERROR, CRITICAL)

    **Returns:**
    - List of audit log entries
    - Total count
    - Pagination info
    """
    logs = AuditService.get_all_logs(
        db=db,
        limit=limit,
        offset=offset,
        event_type=event_type,
        user_id=user_id,
        severity=severity
    )

    # Get total count for pagination
    total = db.query(AuditLog).count()

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get(
    "/tax",
    response_model=AuditLogListResponse,
    summary="Get user's own tax audit logs"
)
async def get_user_tax_audit_logs(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs to return"),
    offset: int = Query(0, ge=0, description="Number of logs to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's tax-related audit logs

    Returns audit logs for TAX_WFH_* and TAX_TRAVEL_* events created by
    the current user. This allows users to see their own tax record history.

    **Query Parameters:**
    - **limit**: Number of logs to return (1-1000, default 100)
    - **offset**: Pagination offset

    **Returns:**
    - List of tax-related audit log entries for current user
    - Total count
    - Pagination info
    """
    logs = AuditService.get_user_tax_logs(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )

    # Count user's tax logs
    total = db.query(AuditLog).filter(
        AuditLog.user_id == current_user.id
    ).filter(
        AuditLog.event_type.in_([
            EventType.TAX_WFH_CREATE,
            EventType.TAX_WFH_UPDATE,
            EventType.TAX_WFH_DELETE,
            EventType.TAX_TRAVEL_CREATE,
            EventType.TAX_TRAVEL_UPDATE,
            EventType.TAX_TRAVEL_DELETE,
        ])
    ).count()

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        limit=limit,
        offset=offset
    )
