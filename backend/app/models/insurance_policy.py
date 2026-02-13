"""
Insurance Policy Model
Tracks household insurance policies with renewal dates
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import Column, String, Numeric, Date, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class PolicyType(str, Enum):
    """Insurance policy types"""
    HOME = "Home"
    CAR = "Car"
    HEALTH = "Health"
    LIFE = "Life"
    PET = "Pet"
    TRAVEL = "Travel"
    CONTENTS = "Contents"
    LANDLORD = "Landlord"
    INCOME_PROTECTION = "Income Protection"
    OTHER = "Other"


class PremiumFrequency(str, Enum):
    """Premium payment frequency"""
    MONTHLY = "Monthly"
    ANNUALLY = "Annually"


class InsurancePolicy(Base):
    """Insurance policy model"""
    __tablename__ = "insurance_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_type = Column(String(50), nullable=False)
    provider = Column(String(255), nullable=False)
    policy_number = Column(String(255), nullable=True)
    coverage_amount = Column(Numeric(12, 2), nullable=True)
    premium = Column(Numeric(10, 2), nullable=False)
    premium_frequency = Column(String(50), nullable=False)
    excess = Column(Numeric(10, 2), nullable=True)
    renewal_date = Column(Date, nullable=False)
    coverage_notes = Column(Text, nullable=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="SET NULL"), nullable=True)
    vehicle_id = Column(UUID(as_uuid=True), nullable=True)  # FK to knowledge_articles when implemented
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    document = relationship("File", foreign_keys=[document_id])

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "policy_type": self.policy_type,
            "provider": self.provider,
            "policy_number": self.policy_number,
            "coverage_amount": float(self.coverage_amount) if self.coverage_amount else None,
            "premium": float(self.premium),
            "premium_frequency": self.premium_frequency,
            "excess": float(self.excess) if self.excess else None,
            "renewal_date": self.renewal_date.isoformat(),
            "coverage_notes": self.coverage_notes,
            "document_id": str(self.document_id) if self.document_id else None,
            "vehicle_id": str(self.vehicle_id) if self.vehicle_id else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def days_until_renewal(self) -> int:
        """Calculate days until renewal"""
        from datetime import date
        today = date.today()
        delta = self.renewal_date - today
        return delta.days

    def is_renewal_due(self, days_threshold: int = 30) -> bool:
        """Check if renewal is due within threshold days"""
        return 0 <= self.days_until_renewal() <= days_threshold
