"""
Document Model
Tracks important household documents
"""

from datetime import date, datetime
from enum import Enum
from sqlalchemy import Column, String, Date, Text, ForeignKey, DateTime, ARRAY, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class DocumentType(str, Enum):
    """Document types"""
    CONTRACT = "Contract"
    RECEIPT = "Receipt"
    WARRANTY = "Warranty"
    MANUAL = "Manual"
    CERTIFICATE = "Certificate"
    LEGAL = "Legal"
    MEDICAL = "Medical"
    FINANCIAL = "Financial"
    OTHER = "Other"


class Document(Base):
    """Important document model"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    tags = Column(ARRAY(String), nullable=True, default=[])
    uploaded_date = Column(Date, default=date.today, nullable=False)
    expiry_date = Column(Date, nullable=True)
    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    file = relationship("File", foreign_keys=[file_id])

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "document_type": self.document_type,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "tags": self.tags or [],
            "uploaded_date": self.uploaded_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "file_id": str(self.file_id),
            "created_at": self.created_at.isoformat()
        }

    def is_expired(self) -> bool:
        """Check if document is expired"""
        if not self.expiry_date:
            return False
        return date.today() > self.expiry_date

    def days_until_expiry(self) -> int | None:
        """Calculate days until expiry, None if no expiry date"""
        if not self.expiry_date:
            return None
        delta = self.expiry_date - date.today()
        return delta.days
