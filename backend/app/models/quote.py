"""
Quote Model
Tracks contractor quotes for projects
"""

from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Column, String, Text, Date, Numeric, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class Quote(Base):
    """Quote model for contractor quotes"""
    __tablename__ = "quotes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    contractor_name = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(255), nullable=True)
    quote_amount = Column(Numeric(12, 2), nullable=False)
    quote_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    scope_of_work = Column(Text, nullable=True)
    selected = Column(Boolean, default=False, nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="quotes")
    document = relationship("File", foreign_keys=[document_id])

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "contractor_name": self.contractor_name,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "quote_amount": float(self.quote_amount),
            "quote_date": self.quote_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "scope_of_work": self.scope_of_work,
            "selected": self.selected,
            "document_id": str(self.document_id) if self.document_id else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat()
        }

    def is_expired(self) -> bool:
        """Check if quote is expired"""
        if not self.expiry_date:
            return False
        return date.today() > self.expiry_date

    def days_until_expiry(self) -> int | None:
        """Calculate days until expiry, None if no expiry date"""
        if not self.expiry_date:
            return None
        delta = self.expiry_date - date.today()
        return delta.days
