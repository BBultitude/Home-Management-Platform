"""
User model for authentication and authorization
"""

from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from typing import List

from app.db.database import Base

_CASCADE_ALL_DELETE_ORPHAN = "all, delete-orphan"
_PERM_TAX_READ_ALL = "tax:read_all"
_PERM_ALL_READ = "*:read"


class UserRole(str, enum.Enum):
    """User roles for RBAC"""
    ADMIN = "Admin"
    EDITOR = "Editor"
    READER = "Reader"


class User(Base):
    """
    User model for authentication and authorization

    RBAC Roles:
    - Admin: Full access, user management, cannot modify others' tax records
    - Editor: Create/edit/delete in all modules, modify only own tax records
    - Reader: Read-only access to all modules
    """
    __tablename__ = "users"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Authentication
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Authorization
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False),
        default=UserRole.READER,
        nullable=False,
        index=True
    )

    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # MFA settings
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Encrypted

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    trusted_devices: Mapped[List["TrustedDevice"]] = relationship(
        "TrustedDevice",
        back_populates="user",
        cascade=_CASCADE_ALL_DELETE_ORPHAN
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="user",
        cascade=_CASCADE_ALL_DELETE_ORPHAN
    )
    files: Mapped[List["File"]] = relationship(
        "File",
        back_populates="uploaded_by_user",
        cascade=_CASCADE_ALL_DELETE_ORPHAN
    )
    tax_wfh_entries: Mapped[List["TaxWFHEntry"]] = relationship(
        "TaxWFHEntry",
        back_populates="user",
        cascade=_CASCADE_ALL_DELETE_ORPHAN
    )
    tax_travel_entries: Mapped[List["TaxTravelEntry"]] = relationship(
        "TaxTravelEntry",
        back_populates="user",
        cascade=_CASCADE_ALL_DELETE_ORPHAN
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == UserRole.ADMIN

    @property
    def is_editor(self) -> bool:
        """Check if user has editor role"""
        return self.role == UserRole.EDITOR

    @property
    def is_reader(self) -> bool:
        """Check if user has reader role"""
        return self.role == UserRole.READER

    def has_permission(self, permission: str) -> bool:
        """
        Check if user has a specific permission

        Args:
            permission: Permission string (e.g., "user:manage", "tax:write_own")

        Returns:
            Boolean indicating if user has permission
        """
        # Admin permissions
        if self.is_admin:
            admin_permissions = [
                "user:manage",
                "audit:read",
                "tax:read_own",
                _PERM_TAX_READ_ALL,
                _PERM_ALL_READ,
                "*:write"
            ]
            # Special case: Admins CANNOT write to others' tax records
            if permission == "tax:write_other":
                return False
            return permission in admin_permissions or permission.endswith(":read")

        # Editor permissions
        if self.is_editor:
            editor_permissions = [
                "tax:write_own",
                _PERM_TAX_READ_ALL,
                _PERM_ALL_READ,
                "*:write"
            ]
            return permission in editor_permissions

        # Reader permissions (read-only)
        if self.is_reader:
            reader_permissions = [_PERM_TAX_READ_ALL, _PERM_ALL_READ]
            return permission in reader_permissions

        return False
