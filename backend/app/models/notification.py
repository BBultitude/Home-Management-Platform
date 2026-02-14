"""
Notification Model
User notifications for alerts, reminders, and system messages
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.database import Base


class NotificationType(str, enum.Enum):
    """Notification type enumeration"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    REMINDER = "reminder"


class NotificationCategory(str, enum.Enum):
    """Notification category for grouping"""
    SYSTEM = "system"
    TAX = "tax"
    FINANCIAL = "financial"
    ASSETS = "assets"
    PROJECTS = "projects"
    KNOWLEDGE = "knowledge"
    MEALS = "meals"


class Notification(Base):
    """Notification model for user alerts"""
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # No FK - notifications can exist without user

    type = Column(SQLEnum(NotificationType), nullable=False, default=NotificationType.INFO)
    category = Column(SQLEnum(NotificationCategory), nullable=False, default=NotificationCategory.SYSTEM)

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Optional action link (e.g., "/assets/insurance/123")
    action_url = Column(String(500), nullable=True)
    action_label = Column(String(100), nullable=True)  # e.g., "View Policy", "Update"

    # Metadata for filtering
    is_read = Column(Boolean, default=False, nullable=False)
    is_dismissed = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = Column(DateTime, nullable=True)

    def to_dict(self) -> dict:
        """Convert notification to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "type": self.type.value,
            "category": self.category.value,
            "title": self.title,
            "message": self.message,
            "action_url": self.action_url,
            "action_label": self.action_label,
            "is_read": self.is_read,
            "is_dismissed": self.is_dismissed,
            "created_at": self.created_at.isoformat(),
            "read_at": self.read_at.isoformat() if self.read_at else None,
        }
