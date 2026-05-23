"""
Audit Logging Service
Handles logging of all critical system events for compliance and security
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.audit_log import AuditLog, EventType, Severity
from app.models.user import User


class AuditService:
    """Service for creating and querying audit logs"""

    @staticmethod
    def log_event(
        db: Session,
        event_type: EventType,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int | str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: Severity = Severity.INFO
    ) -> AuditLog:
        """
        Log an audit event

        Args:
            db: Database session
            event_type: Type of event (LOGIN, USER_CREATE, etc.)
            user_id: ID of user performing the action
            username: Username of user performing the action
            ip_address: IP address of the request
            user_agent: User agent string from the request
            resource_type: Type of resource affected (user, tax_wfh, file, etc.)
            resource_id: ID of the resource affected
            details: Additional event details as JSON
            severity: Event severity (INFO, WARNING, ERROR, CRITICAL)

        Returns:
            Created AuditLog object
        """
        log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            username=username or "system",
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            details=details or {},
            severity=severity
        )

        db.add(log)
        db.commit()
        db.refresh(log)

        return log

    # Authentication Events

    @staticmethod
    def log_login_success(
        db: Session,
        user: User,
        ip_address: str,
        user_agent: str,
        mfa_used: bool = False
    ) -> AuditLog:
        """Log successful login"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.LOGIN_SUCCESS,
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"mfa_used": mfa_used, "role": user.role.value},
            severity=Severity.INFO
        )

    @staticmethod
    def log_login_failed(
        db: Session,
        username: str,
        ip_address: str,
        user_agent: str,
        reason: str
    ) -> AuditLog:
        """Log failed login attempt"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.LOGIN_FAILED,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"reason": reason},
            severity=Severity.WARNING
        )

    @staticmethod
    def log_logout(
        db: Session,
        user: User,
        ip_address: str,
        user_agent: str
    ) -> AuditLog:
        """Log user logout"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.LOGOUT,
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=Severity.INFO
        )

    @staticmethod
    def log_mfa_setup(
        db: Session,
        user: User,
        ip_address: str,
        user_agent: str
    ) -> AuditLog:
        """Log MFA setup initiation"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.MFA_SETUP,
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=Severity.INFO
        )

    @staticmethod
    def log_mfa_enabled(
        db: Session,
        user: User,
        ip_address: str,
        user_agent: str
    ) -> AuditLog:
        """Log MFA enabled"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.MFA_ENABLED,
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"security_enhanced": True},
            severity=Severity.INFO
        )

    @staticmethod
    def log_mfa_disabled(
        db: Session,
        user: User,
        ip_address: str,
        user_agent: str,
        devices_revoked: int
    ) -> AuditLog:
        """Log MFA disabled"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.MFA_DISABLED,
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"devices_revoked": devices_revoked, "security_reduced": True},
            severity=Severity.WARNING
        )

    @staticmethod
    def log_mfa_verified(
        db: Session,
        user: User,
        ip_address: str,
        user_agent: str,
        trusted_device: bool = False
    ) -> AuditLog:
        """Log successful MFA verification"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.MFA_VERIFIED,
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"trusted_device": trusted_device},
            severity=Severity.INFO
        )

    # User Management Events

    @staticmethod
    def log_user_created(
        db: Session,
        admin_user: User,
        new_user: User,
        ip_address: str,
        user_agent: str
    ) -> AuditLog:
        """Log user creation"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.USER_CREATE,
            user_id=admin_user.id,
            username=admin_user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="user",
            resource_id=new_user.id,
            details={
                "created_username": new_user.username,
                "created_role": new_user.role.value,
                "created_email": new_user.email
            },
            severity=Severity.INFO
        )

    @staticmethod
    def log_user_updated(
        db: Session,
        admin_user: User,
        updated_user: User,
        ip_address: str,
        user_agent: str,
        changes: Dict[str, Any]
    ) -> AuditLog:
        """Log user update"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.USER_UPDATE,
            user_id=admin_user.id,
            username=admin_user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="user",
            resource_id=updated_user.id,
            details={"updated_username": updated_user.username, "changes": changes},
            severity=Severity.INFO
        )

    @staticmethod
    def log_user_deleted(
        db: Session,
        admin_user: User,
        deleted_user: User,
        ip_address: str,
        user_agent: str
    ) -> AuditLog:
        """Log user deletion"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.USER_DELETE,
            user_id=admin_user.id,
            username=admin_user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="user",
            resource_id=deleted_user.id,
            details={"deleted_username": deleted_user.username},
            severity=Severity.WARNING
        )

    @staticmethod
    def log_password_changed(
        db: Session,
        user: User,
        ip_address: str,
        user_agent: str,
        changed_by_admin: bool = False
    ) -> AuditLog:
        """Log password change"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.PASSWORD_CHANGE,
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"changed_by_admin": changed_by_admin},
            severity=Severity.INFO
        )

    # File Upload Events

    @staticmethod
    def log_file_upload(
        db: Session,
        user: User,
        ip_address: str,
        user_agent: str,
        file_id: int,
        filename: str,
        file_size: int,
        mime_type: str
    ) -> AuditLog:
        """Log file upload"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.FILE_UPLOAD,
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="file",
            resource_id=file_id,
            details={
                "filename": filename,
                "size_bytes": file_size,
                "mime_type": mime_type
            },
            severity=Severity.INFO
        )

    @staticmethod
    def log_file_download(
        db: Session,
        user: User,
        ip_address: str,
        user_agent: str,
        file_id: int,
        filename: str
    ) -> AuditLog:
        """Log file download"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.FILE_DOWNLOAD,
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="file",
            resource_id=file_id,
            details={"filename": filename},
            severity=Severity.INFO
        )

    @staticmethod
    def log_file_deleted(
        db: Session,
        user: User,
        ip_address: str,
        user_agent: str,
        file_id: int,
        filename: str
    ) -> AuditLog:
        """Log file deletion"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.FILE_DELETE,
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="file",
            resource_id=file_id,
            details={"filename": filename},
            severity=Severity.WARNING
        )

    # Tax Record Events (placeholders for future implementation)

    @staticmethod
    def log_tax_wfh_create(
        db: Session,
        user: User,
        ip_address: str,
        user_agent: str,
        tax_id: int,
        details: Dict[str, Any]
    ) -> AuditLog:
        """Log WFH tax record creation"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.TAX_WFH_CREATE,
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="tax_wfh",
            resource_id=tax_id,
            details=details,
            severity=Severity.INFO
        )

    @staticmethod
    def log_tax_travel_create(
        db: Session,
        user: User,
        ip_address: str,
        user_agent: str,
        tax_id: int,
        details: Dict[str, Any]
    ) -> AuditLog:
        """Log travel tax record creation"""
        return AuditService.log_event(
            db=db,
            event_type=EventType.TAX_TRAVEL_CREATE,
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type="tax_travel",
            resource_id=tax_id,
            details=details,
            severity=Severity.INFO
        )

    # Query Methods

    @staticmethod
    def get_all_logs(
        db: Session,
        limit: int = 100,
        offset: int = 0,
        event_type: Optional[EventType] = None,
        user_id: Optional[int] = None,
        severity: Optional[Severity] = None
    ) -> list[AuditLog]:
        """
        Get all audit logs (admin-only)

        Args:
            db: Database session
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            event_type: Filter by event type
            user_id: Filter by user ID
            severity: Filter by severity

        Returns:
            List of AuditLog objects
        """
        query = db.query(AuditLog)

        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if severity:
            query = query.filter(AuditLog.severity == severity)

        query = query.order_by(AuditLog.timestamp.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def get_user_tax_logs(
        db: Session,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        """
        Get tax-related audit logs for a specific user

        Returns logs for TAX_WFH_* and TAX_TRAVEL_* events that the user owns.

        Args:
            db: Database session
            user_id: User ID
            limit: Maximum number of logs to return
            offset: Number of logs to skip

        Returns:
            List of AuditLog objects
        """
        tax_event_types = [
            EventType.TAX_WFH_CREATE,
            EventType.TAX_WFH_UPDATE,
            EventType.TAX_WFH_DELETE,
            EventType.TAX_TRAVEL_CREATE,
            EventType.TAX_TRAVEL_UPDATE,
            EventType.TAX_TRAVEL_DELETE,
        ]

        query = db.query(AuditLog).filter(
            and_(
                AuditLog.user_id == user_id,
                AuditLog.event_type.in_(tax_event_types)
            )
        )

        query = query.order_by(AuditLog.timestamp.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def cleanup_old_logs(db: Session, retention_days: int = 730) -> int:
        """
        Delete audit logs older than retention period

        Default: 730 days (2 years) for general logs
        Tax logs should use 1825 days (5 years) per ATO requirements

        Args:
            db: Database session
            retention_days: Number of days to retain logs

        Returns:
            Number of logs deleted
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

        # For tax records, enforce 5-year retention
        tax_event_types = [
            EventType.TAX_WFH_CREATE,
            EventType.TAX_WFH_UPDATE,
            EventType.TAX_WFH_DELETE,
            EventType.TAX_TRAVEL_CREATE,
            EventType.TAX_TRAVEL_UPDATE,
            EventType.TAX_TRAVEL_DELETE,
        ]

        # Delete non-tax logs older than retention_days
        result = db.query(AuditLog).filter(
            and_(
                AuditLog.timestamp < cutoff_date,
                ~AuditLog.event_type.in_(tax_event_types)
            )
        ).delete()

        db.commit()
        return result

    @staticmethod
    def cleanup_old_tax_logs(db: Session, retention_days: int = 1825) -> int:
        """
        Delete tax audit logs older than 5 years (ATO requirement)

        Args:
            db: Database session
            retention_days: Number of days to retain (default 1825 = 5 years)

        Returns:
            Number of logs deleted
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

        tax_event_types = [
            EventType.TAX_WFH_CREATE,
            EventType.TAX_WFH_UPDATE,
            EventType.TAX_WFH_DELETE,
            EventType.TAX_TRAVEL_CREATE,
            EventType.TAX_TRAVEL_UPDATE,
            EventType.TAX_TRAVEL_DELETE,
        ]

        result = db.query(AuditLog).filter(
            and_(
                AuditLog.timestamp < cutoff_date,
                AuditLog.event_type.in_(tax_event_types)
            )
        ).delete()

        db.commit()
        return result
