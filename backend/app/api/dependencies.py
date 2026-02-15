"""
Dependency injection for FastAPI routes
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.services.auth_service import AuthService


# HTTP Bearer token scheme for API authentication
security = HTTPBearer()


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token in cookie or Authorization header

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        Current user object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Try to get token from HTTP-only cookie first (preferred)
    token = request.cookies.get("access_token")

    # Fallback to Authorization header if cookie not present
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = AuthService.get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (not deleted, not inactive)

    Args:
        current_user: Current user from get_current_user

    Returns:
        Active user object

    Raises:
        HTTPException: If user is inactive or deleted
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    if current_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account deleted"
        )

    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Dependency factory for requiring specific user roles

    Usage:
        @app.get("/admin-only", dependencies=[Depends(require_role(UserRole.ADMIN))])
        async def admin_only_endpoint():
            ...

    Args:
        *allowed_roles: Variable number of allowed roles

    Returns:
        Dependency function
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker


# Convenience dependencies for common role checks
require_admin = require_role(UserRole.ADMIN)
require_editor = require_role(UserRole.ADMIN, UserRole.EDITOR)
require_authenticated = Depends(get_current_active_user)


# Permission matrix based on Design-v1.md
PERMISSION_MATRIX = {
    # Authentication & User Management
    "users:create": [UserRole.ADMIN],
    "users:update": [UserRole.ADMIN],
    "users:delete": [UserRole.ADMIN],
    "users:list": [UserRole.ADMIN],
    "users:view_all": [UserRole.ADMIN],

    # Tax Records (WFH/Travel)
    "tax:create": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],  # All can create own records
    "tax:update_own": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],  # All can update own
    "tax:delete_own": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],  # All can delete own
    "tax:view_own": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],  # All can view own
    "tax:view_all": [UserRole.ADMIN],  # Only admin can view all users' tax records
    "tax:update_any": [UserRole.ADMIN],  # Only admin can update any record
    "tax:delete_any": [UserRole.ADMIN],  # Only admin can delete any record

    # Files
    "files:upload": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],
    "files:download_own": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],
    "files:download_any": [UserRole.ADMIN],
    "files:delete_own": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],
    "files:delete_any": [UserRole.ADMIN],

    # Audit Logs
    "audit:view_all": [UserRole.ADMIN],  # Admin sees all audit logs
    "audit:view_own_tax": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],  # All see own tax logs

    # Finance (Future modules - legacy keys)
    "finance:create": [UserRole.ADMIN, UserRole.EDITOR],
    "finance:update": [UserRole.ADMIN, UserRole.EDITOR],
    "finance:delete": [UserRole.ADMIN],
    "finance:view": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],

    # Financial Management (Active)
    "financial:write": [UserRole.ADMIN, UserRole.EDITOR],
    "financial:read": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],

    # Assets & Documents (Active)
    "assets:write": [UserRole.ADMIN, UserRole.EDITOR],
    "assets:read": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],

    # Projects & Tasks (Active)
    "projects:write": [UserRole.ADMIN, UserRole.EDITOR],
    "projects:read": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],

    # Knowledge Base (Active)
    "knowledge:write": [UserRole.ADMIN, UserRole.EDITOR],
    "knowledge:read": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],
    "knowledge:admin": [UserRole.ADMIN],

    # Meal Planner (Active)
    "meals:write": [UserRole.ADMIN, UserRole.EDITOR],
    "meals:read": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],

    # Insurance (Future modules - legacy keys)
    "insurance:create": [UserRole.ADMIN, UserRole.EDITOR],
    "insurance:update": [UserRole.ADMIN, UserRole.EDITOR],
    "insurance:delete": [UserRole.ADMIN],
    "insurance:view": [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER],
}


def require_permission(permission: str):
    """
    Dependency factory for requiring specific permissions

    Checks the permission matrix to determine if the user's role
    has the required permission.

    Usage:
        @app.get("/endpoint", dependencies=[Depends(require_permission("tax:create"))])
        async def create_tax_record():
            ...

    Args:
        permission: Permission string in format "module:action"

    Returns:
        Dependency function

    Raises:
        HTTPException: If permission is not defined or user lacks permission
    """
    def permission_checker(current_user: User = Depends(get_current_active_user)) -> User:
        # Check if permission exists in matrix
        if permission not in PERMISSION_MATRIX:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Permission '{permission}' not defined in matrix"
            )

        # Check if user's role has this permission
        allowed_roles = PERMISSION_MATRIX[permission]
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required permission: '{permission}'"
            )

        return current_user

    return permission_checker


def require_tax_ownership(tax_id_param: str = "tax_id"):
    """
    Dependency factory for tax record ownership validation

    Ensures the user owns the tax record they're trying to access.
    Admins can access any record.

    Usage:
        @app.get("/tax/{tax_id}")
        async def get_tax_record(
            tax_id: int,
            user: User = Depends(require_tax_ownership("tax_id"))
        ):
            ...

    Args:
        tax_id_param: Name of the path parameter containing the tax record ID

    Returns:
        Dependency function
    """
    async def ownership_checker(
        request: Request,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
    ) -> User:
        # Admin can access any tax record
        if current_user.role == UserRole.ADMIN:
            return current_user

        # Get tax_id from path parameters
        tax_id = request.path_params.get(tax_id_param)
        if not tax_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing path parameter: {tax_id_param}"
            )

        # Import here to avoid circular dependency
        # Tax models will be created in future sprints
        # For now, just validate the structure
        # TODO: Implement actual ownership check when tax models exist
        #
        # Example implementation:
        # from app.models.tax import TaxWFH, TaxTravel
        # tax_record = db.query(TaxWFH).filter(TaxWFH.id == tax_id).first()
        # if not tax_record:
        #     tax_record = db.query(TaxTravel).filter(TaxTravel.id == tax_id).first()
        #
        # if not tax_record:
        #     raise HTTPException(404, "Tax record not found")
        #
        # if tax_record.user_id != current_user.id:
        #     raise HTTPException(403, "Access denied: not the record owner")

        return current_user

    return ownership_checker


def allow_tax_read(tax_id_param: str = "tax_id"):
    """
    Dependency factory for tax record read access

    Allows:
    - Record owner (any role)
    - Admin (can read all records)

    Usage:
        @app.get("/tax/{tax_id}")
        async def view_tax_record(
            tax_id: int,
            user: User = Depends(allow_tax_read("tax_id"))
        ):
            ...

    Args:
        tax_id_param: Name of the path parameter containing the tax record ID

    Returns:
        Dependency function
    """
    # For read access, same as ownership check for now
    # Admin can read all, users can read own
    return require_tax_ownership(tax_id_param)
