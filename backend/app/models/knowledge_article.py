"""
Knowledge Article Model
Stores structured household reference information using JSONB
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, ForeignKey, DateTime, Text, ARRAY, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class ArticleType(str, Enum):
    """Knowledge article types"""
    MEASUREMENT = "Measurement"
    PAINT = "Paint"
    TECH_DEVICE = "TechDevice"
    STORAGE_LOCATION = "StorageLocation"
    VEHICLE = "Vehicle"
    EMERGENCY_CONTACT = "EmergencyContact"
    APPLIANCE = "Appliance"
    VENDOR = "Vendor"


class KnowledgeArticle(Base):
    """Knowledge article model with JSONB data storage"""
    __tablename__ = "knowledge_articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    data = Column(JSONB, nullable=False)
    tags = Column(ARRAY(String), nullable=True, default=None)
    search_vector = Column(TSVECTOR, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    attachments = relationship("KnowledgeAttachment", back_populates="article", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "article_type": self.article_type,
            "title": self.title,
            "data": self.data,
            "tags": self.tags or [],
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "attachment_count": len(self.attachments) if self.attachments else 0
        }


class KnowledgeAttachment(Base):
    """Knowledge article attachment linking"""
    __tablename__ = "knowledge_attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_articles.id", ondelete="CASCADE"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    article = relationship("KnowledgeArticle", back_populates="attachments")
    file = relationship("File")

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "article_id": str(self.article_id),
            "file_id": str(self.file_id)
        }
