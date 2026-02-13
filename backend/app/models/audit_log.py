"""
Audit Log model for tracking critical actions
"""

from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean, Enum, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.database import Base


class EventType(str, enum.Enum):
    """Audit event types"""
    # Authentication
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    MFA_SETUP = "MFA_SETUP"
    MFA_ENABLED = "MFA_ENABLED"
    MFA_DISABLED = "MFA_DISABLED"
    MFA_VERIFIED = "MFA_VERIFIED"
    MFA_FAILED = "MFA_FAILED"
    TRUSTED_DEVICE_ADDED = "TRUSTED_DEVICE_ADDED"
    TRUSTED_DEVICE_REVOKED = "TRUSTED_DEVICE_REVOKED"

    # User Management (Admin)
    USER_CREATE = "USER_CREATE"
    USER_UPDATE = "USER_UPDATE"
    USER_DELETE = "USER_DELETE"
    USER_MFA_RESET = "USER_MFA_RESET"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"

    # Tax Records
    TAX_WFH_CREATE = "TAX_WFH_CREATE"
    TAX_WFH_UPDATE = "TAX_WFH_UPDATE"
    TAX_WFH_DELETE = "TAX_WFH_DELETE"
    TAX_WFH_EXPORT = "TAX_WFH_EXPORT"
    TAX_TRAVEL_CREATE = "TAX_TRAVEL_CREATE"
    TAX_TRAVEL_UPDATE = "TAX_TRAVEL_UPDATE"
    TAX_TRAVEL_DELETE = "TAX_TRAVEL_DELETE"
    TAX_TRAVEL_EXPORT = "TAX_TRAVEL_EXPORT"
    TAX_READ_OTHER = "TAX_READ_OTHER"  # Admin reading other user's tax data

    # Files
    FILE_UPLOAD = "FILE_UPLOAD"
    FILE_DOWNLOAD = "FILE_DOWNLOAD"
    FILE_DELETE = "FILE_DELETE"

    # Financial
    FINANCIAL_CREATE = "FINANCIAL_CREATE"
    FINANCIAL_UPDATE = "FINANCIAL_UPDATE"
    FINANCIAL_DELETE = "FINANCIAL_DELETE"

    # Assets
    ASSET_CREATE = "ASSET_CREATE"
    ASSET_UPDATE = "ASSET_UPDATE"
    ASSET_DELETE = "ASSET_DELETE"

    # Projects
    PROJECT_CREATE = "PROJECT_CREATE"
    PROJECT_UPDATE = "PROJECT_UPDATE"
    PROJECT_DELETE = "PROJECT_DELETE"

    # Knowledge Base
    KNOWLEDGE_CREATE = "KNOWLEDGE_CREATE"
    KNOWLEDGE_UPDATE = "KNOWLEDGE_UPDATE"
    KNOWLEDGE_DELETE = "KNOWLEDGE_DELETE"


# Alias for backwards compatibility
AuditAction = EventType


class Severity(str, enum.Enum):
    """Audit event severity levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditModule(str, enum.Enum):
    """System modules for audit logging"""
    AUTH = "auth"
    USER_MANAGEMENT = "user_management"
    TAX = "tax"
    FINANCIAL = "financial"
    ASSETS = "assets"
    PROJECTS = "projects"
    KNOWLEDGE = "knowledge"
    FILES = "files"
    SYSTEM = "system"


class AuditLog(Base):
    """
    Audit Log model for tracking all critical actions

    Retention:
    - Tax-related logs: 5 years (ATO compliance)
    - Authentication logs: 5 years
    - Other logs: 2 years
    """
    __tablename__ = "audit_logs"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign key to user (nullable for system actions or failed logins)
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Event details
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="event_type", native_enum=False),
        nullable=False,
        index=True
    )
    username: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[Severity] = mapped_column(
        Enum(Severity, name="severity", native_enum=False),
        default=Severity.INFO,
        nullable=False,
        index=True
    )

    # Resource affected (e.g., user ID, tax record ID, file ID)
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # Request metadata
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True, index=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Additional context (JSON for flexible storage - works with PostgreSQL and SQLite)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, event_type='{self.event_type.value}', user_id={self.user_id}, severity={self.severity.value})>"

    @property
    def is_tax_related(self) -> bool:
        """Check if log is tax-related (5-year retention)"""
        return self.event_type.name.startswith("TAX_")

    @property
    def is_auth_related(self) -> bool:
        """Check if log is authentication-related (5-year retention)"""
        return self.event_type in [
            EventType.LOGIN_SUCCESS,
            EventType.LOGIN_FAILED,
            EventType.LOGOUT,
            EventType.MFA_SETUP,
            EventType.MFA_ENABLED,
            EventType.MFA_DISABLED,
            EventType.MFA_VERIFIED,
            EventType.MFA_FAILED
        ]

    @property
    def retention_years(self) -> int:
        """Calculate retention period in years"""
        if self.is_tax_related or self.is_auth_related:
            return 5  # ATO compliance
        return 2  # Default retention
