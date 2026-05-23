"""
Admin Service
Administrative functions for user management, system maintenance, and oversight
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.models.audit_log import AuditLog, AuditAction, AuditModule
from app.services.audit_service import AuditService
from app.services.mfa_service import MFAService


class AdminService:
    """Service for administrative operations"""

    # ===== User Management =====

    @staticmethod
    def list_users(
        db: Session,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[User]:
        """
        List all users with optional filtering

        Args:
            db: Database session
            search: Search by username, email, or full_name
            role: Filter by role
            is_active: Filter by active status
            limit: Maximum entries to return
            offset: Pagination offset

        Returns:
            List of User objects
        """
        query = db.query(User)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.full_name.ilike(search_pattern)
                )
            )

        if role is not None:
            query = query.filter(User.role == role)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        query = query.order_by(User.created_at.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def get_user_count(
        db: Session,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Get total user count with optional filtering"""
        query = db.query(func.count(User.id))

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                    User.full_name.ilike(search_pattern)
                )
            )

        if role is not None:
            query = query.filter(User.role == role)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.scalar()

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> User:
        """Get user by ID"""
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    @staticmethod
    def update_user(
        db: Session,
        user_id: UUID,
        admin_user: User,
        username: Optional[str] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None
    ) -> User:
        """
        Update user details (admin only)

        Args:
            db: Database session
            user_id: User ID to update
            admin_user: Admin performing the update
            username: New username (optional)
            email: New email (optional)
            full_name: New full name (optional)

        Returns:
            Updated User

        Raises:
            404: User not found
            400: Username or email already exists
        """
        user = AdminService.get_user_by_id(db, user_id)

        # Check if username is taken
        if username and username != user.username:
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
            user.username = username

        # Check if email is taken
        if email and email != user.email:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
            user.email = email

        if full_name is not None:
            user.full_name = full_name

        user.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(user)

        # Audit log
        AuditService.log(
            db=db,
            user_id=admin_user.id,
            action=AuditAction.UPDATE,
            module=AuditModule.USERS,
            details=f"Admin updated user {user.username}",
            metadata={
                "target_user_id": str(user_id),
                "updated_fields": [k for k, v in {
                    "username": username,
                    "email": email,
                    "full_name": full_name
                }.items() if v is not None]
            }
        )

        return user

    @staticmethod
    def update_user_role(
        db: Session,
        user_id: UUID,
        admin_user: User,
        new_role: UserRole
    ) -> User:
        """
        Update user role (admin only)

        Args:
            db: Database session
            user_id: User ID to update
            admin_user: Admin performing the update
            new_role: New role to assign

        Returns:
            Updated User

        Raises:
            404: User not found
            400: Cannot change own role or last admin role
        """
        user = AdminService.get_user_by_id(db, user_id)

        # Prevent admin from changing their own role
        if user.id == admin_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role"
            )

        # Prevent removing last admin
        if user.role == UserRole.ADMIN and new_role != UserRole.ADMIN:
            admin_count = db.query(User).filter(
                User.role == UserRole.ADMIN,
                User.is_active == True
            ).count()

            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last admin user"
                )

        old_role = user.role
        user.role = new_role
        user.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(user)

        # Audit log
        AuditService.log(
            db=db,
            user_id=admin_user.id,
            action=AuditAction.UPDATE,
            module=AuditModule.USERS,
            details=f"Changed role for user {user.username} from {old_role.value} to {new_role.value}",
            metadata={
                "target_user_id": str(user_id),
                "old_role": old_role.value,
                "new_role": new_role.value
            }
        )

        return user

    @staticmethod
    def toggle_user_active(
        db: Session,
        user_id: UUID,
        admin_user: User,
        is_active: bool
    ) -> User:
        """
        Activate or deactivate user (admin only)

        Args:
            db: Database session
            user_id: User ID to update
            admin_user: Admin performing the update
            is_active: New active status

        Returns:
            Updated User

        Raises:
            404: User not found
            400: Cannot deactivate self or last admin
        """
        user = AdminService.get_user_by_id(db, user_id)

        # Prevent admin from deactivating themselves
        if user.id == admin_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )

        # Prevent deactivating last admin
        if not is_active and user.role == UserRole.ADMIN:
            admin_count = db.query(User).filter(
                User.role == UserRole.ADMIN,
                User.is_active == True
            ).count()

            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate the last admin user"
                )

        user.is_active = is_active
        user.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(user)

        # Audit log
        action_text = "activated" if is_active else "deactivated"
        AuditService.log(
            db=db,
            user_id=admin_user.id,
            action=AuditAction.UPDATE,
            module=AuditModule.USERS,
            details=f"Admin {action_text} user {user.username}",
            metadata={
                "target_user_id": str(user_id),
                "is_active": is_active
            }
        )

        return user

    @staticmethod
    def delete_user(
        db: Session,
        user_id: UUID,
        admin_user: User
    ) -> None:
        """
        Delete user (admin only)

        Args:
            db: Database session
            user_id: User ID to delete
            admin_user: Admin performing the deletion

        Raises:
            404: User not found
            400: Cannot delete self or last admin
        """
        user = AdminService.get_user_by_id(db, user_id)

        # Prevent admin from deleting themselves
        if user.id == admin_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        # Prevent deleting last admin
        if user.role == UserRole.ADMIN:
            admin_count = db.query(User).filter(
                User.role == UserRole.ADMIN,
                User.is_active == True
            ).count()

            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete the last admin user"
                )

        username = user.username

        # Audit log before deletion
        AuditService.log(
            db=db,
            user_id=admin_user.id,
            action=AuditAction.DELETE,
            module=AuditModule.USERS,
            details=f"Admin deleted user {username}",
            metadata={
                "target_user_id": str(user_id),
                "username": username,
                "role": user.role.value
            }
        )

        db.delete(user)
        db.commit()

    @staticmethod
    def reset_user_mfa(
        db: Session,
        user_id: UUID,
        admin_user: User
    ) -> dict:
        """
        Reset user's MFA setup (admin only)

        Args:
            db: Database session
            user_id: User ID to reset MFA for
            admin_user: Admin performing the reset

        Returns:
            Dictionary with new MFA secret and QR code

        Raises:
            404: User not found
        """
        user = AdminService.get_user_by_id(db, user_id)

        # Generate new MFA secret
        secret, qr_code = MFAService.generate_secret(user.username)

        # Save encrypted secret
        user.mfa_secret = MFAService.encrypt_secret(secret)
        user.mfa_enabled = False  # User must re-enable after scanning
        user.updated_at = datetime.now(timezone.utc)

        db.commit()

        # Audit log
        AuditService.log(
            db=db,
            user_id=admin_user.id,
            action=AuditAction.UPDATE,
            module=AuditModule.AUTH,
            details=f"Admin reset MFA for user {user.username}",
            metadata={
                "target_user_id": str(user_id),
                "mfa_reset": True
            }
        )

        return {
            "secret": secret,
            "qr_code": qr_code,
            "message": f"MFA reset for user {user.username}. User must scan QR code and re-enable MFA."
        }

    # ===== System Statistics =====

    @staticmethod
    def get_system_stats(db: Session) -> dict:
        """
        Get system statistics

        Returns:
            Dictionary with system-wide statistics
        """
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        admin_users = db.query(User).filter(
            User.role == UserRole.ADMIN,
            User.is_active == True
        ).count()
        editor_users = db.query(User).filter(
            User.role == UserRole.EDITOR,
            User.is_active == True
        ).count()
        reader_users = db.query(User).filter(
            User.role == UserRole.READER,
            User.is_active == True
        ).count()

        # MFA statistics
        mfa_enabled = db.query(User).filter(User.mfa_enabled == True).count()

        # Recent activity (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_logins = db.query(AuditLog).filter(
            AuditLog.action == AuditAction.LOGIN,
            AuditLog.created_at >= seven_days_ago
        ).count()

        total_audit_logs = db.query(AuditLog).count()

        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users,
                "by_role": {
                    "admin": admin_users,
                    "editor": editor_users,
                    "reader": reader_users
                }
            },
            "security": {
                "mfa_enabled_count": mfa_enabled,
                "mfa_enabled_percentage": round((mfa_enabled / total_users * 100) if total_users > 0 else 0, 1)
            },
            "activity": {
                "recent_logins_7d": recent_logins,
                "total_audit_logs": total_audit_logs
            }
        }

    @staticmethod
    def get_user_statistics(db: Session, user_id: UUID) -> dict:
        """
        Get statistics for a specific user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary with user-specific statistics
        """
        user = AdminService.get_user_by_id(db, user_id)

        # Count audit logs by action
        total_actions = db.query(AuditLog).filter(AuditLog.user_id == user_id).count()

        create_count = db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == AuditAction.CREATE
        ).count()

        update_count = db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == AuditAction.UPDATE
        ).count()

        delete_count = db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == AuditAction.DELETE
        ).count()

        login_count = db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == AuditAction.LOGIN
        ).count()

        # Last login
        last_login_log = db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.action == AuditAction.LOGIN
        ).order_by(AuditLog.created_at.desc()).first()

        last_login = last_login_log.created_at if last_login_log else None

        return {
            "user_id": str(user_id),
            "username": user.username,
            "activity": {
                "total_actions": total_actions,
                "creates": create_count,
                "updates": update_count,
                "deletes": delete_count,
                "logins": login_count,
                "last_login": last_login.isoformat() if last_login else None
            },
            "account": {
                "created_at": user.created_at.isoformat(),
                "is_active": user.is_active,
                "mfa_enabled": user.mfa_enabled,
                "role": user.role.value
            }
        }
