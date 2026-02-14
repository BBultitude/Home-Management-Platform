"""
Project Model
Tracks home improvement projects
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import Column, String, Text, Date, Numeric, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class ProjectStatus(str, Enum):
    """Project status"""
    PLANNED = "Planned"
    APPROVED = "Approved"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Project(Base):
    """Project model for home improvement tracking"""
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default=ProjectStatus.PLANNED.value)
    start_date = Column(Date, nullable=True)
    completion_date = Column(Date, nullable=True)
    budget = Column(Numeric(12, 2), nullable=True)
    actual_cost = Column(Numeric(12, 2), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    priority_item = relationship("PriorityItem", back_populates="project", uselist=False)
    quotes = relationship("Quote", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "project_name": self.project_name,
            "description": self.description,
            "priority_item_id": str(self.priority_item.id) if self.priority_item else None,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "budget": float(self.budget) if self.budget else None,
            "actual_cost": float(self.actual_cost) if self.actual_cost else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
