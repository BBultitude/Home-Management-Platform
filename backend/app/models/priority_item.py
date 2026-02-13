"""
Priority Item Model
Tracks home repairs/upgrades with cost-benefit scoring
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
import math
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class PriorityStatus(str, Enum):
    """Priority item status"""
    PENDING = "Pending"
    CONVERTED_TO_PROJECT = "ConvertedToProject"
    DONE = "Done"
    DISMISSED = "Dismissed"


class PriorityItem(Base):
    """Priority item model for repair/upgrade prioritization"""
    __tablename__ = "priority_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String(500), nullable=False)
    cost = Column(Numeric(12, 2), nullable=False)
    severity = Column(Integer, nullable=False)  # 1-5 scale
    frequency = Column(Integer, nullable=False)  # 1-5 scale
    benefit_score = Column(Integer, nullable=False)  # Auto-calculated: severity + frequency
    cost_score = Column(Integer, nullable=False)  # Auto-calculated: log10(cost) + 1
    net_score = Column(Integer, nullable=False)  # Auto-calculated: benefit - cost_score
    status = Column(String(50), nullable=False, default=PriorityStatus.PENDING.value)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Constraints
    __table_args__ = (
        CheckConstraint('severity >= 1 AND severity <= 5', name='check_severity_range'),
        CheckConstraint('frequency >= 1 AND frequency <= 5', name='check_frequency_range'),
    )

    # Relationships
    project = relationship("Project", foreign_keys=[project_id], back_populates="priority_item")

    @staticmethod
    def calculate_scores(cost: Decimal, severity: int, frequency: int) -> dict:
        """
        Calculate benefit, cost, and net scores

        Scoring Algorithm:
        - Benefit Score (2-10): severity + frequency
        - Cost Score (1-5): log10(cost) + 1
        - Net Score (-3 to 9): benefit_score - cost_score

        Returns:
            Dictionary with benefit_score, cost_score, net_score
        """
        benefit_score = severity + frequency

        if cost <= 0:
            cost_score = 1
        else:
            cost_score = max(1, int(round(math.log10(float(cost)))) + 1)

        net_score = benefit_score - cost_score

        return {
            "benefit_score": benefit_score,
            "cost_score": cost_score,
            "net_score": net_score
        }

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "description": self.description,
            "cost": float(self.cost),
            "severity": self.severity,
            "frequency": self.frequency,
            "benefit_score": self.benefit_score,
            "cost_score": self.cost_score,
            "net_score": self.net_score,
            "status": self.status,
            "project_id": str(self.project_id) if self.project_id else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
