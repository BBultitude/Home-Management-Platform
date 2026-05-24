"""
Trusted Device model for MFA remember-me functionality
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class TrustedDevice(Base):
    """
    Trusted Device model for MFA remember-me tokens

    When a user enables "Remember this device" during MFA verification,
    a trusted device record is created with a 30-day expiry.
    """
    __tablename__ = "trusted_devices"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign key to user
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Device identification
    device_fingerprint: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )  # Hash of user agent + IP
    device_name: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., "Chrome on Windows"

    # Token (hashed)
    device_token: Mapped[str] = mapped_column(String(500), nullable=False, index=True)  # JWT token for device

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Metadata
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv4 or IPv6
    user_agent: Mapped[str] = mapped_column(String(500), nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True
    )
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="trusted_devices")

    def __repr__(self) -> str:
        return f"<TrustedDevice(id={self.id}, user_id={self.user_id}, device='{self.device_name}')>"

    def is_expired(self) -> bool:
        """Check if trusted device token has expired"""
        now = datetime.now(timezone.utc)
        exp = self.expires_at.replace(tzinfo=timezone.utc) if self.expires_at.tzinfo is None else self.expires_at
        return now > exp

    @property
    def days_until_expiry(self) -> int:
        """Calculate days until expiry"""
        if self.is_expired():
            return 0
        now = datetime.now(timezone.utc)
        exp = self.expires_at.replace(tzinfo=timezone.utc) if self.expires_at.tzinfo is None else self.expires_at
        delta = exp - now
        return delta.days

    @classmethod
    def calculate_expiry(cls, days: int = 30) -> datetime:
        """Calculate expiry datetime (default 30 days from now)"""
        return datetime.now(timezone.utc) + timedelta(days=days)
