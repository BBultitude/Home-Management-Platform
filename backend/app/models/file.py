"""
File model for uploaded documents and attachments
"""

from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, BigInteger, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.database import Base


class FileCategory(str, enum.Enum):
    """File categories for organizing uploads"""
    INSURANCE = "insurance"
    QUOTE = "quote"
    UTILITY = "utility"
    KNOWLEDGE = "knowledge"
    TAX = "tax"
    PROJECT = "project"
    ASSET = "asset"
    OTHER = "other"


class File(Base):
    """
    File model for all uploaded documents and attachments

    Storage structure: /uploads/{category}/{uuid}_{filename}
    Max file size: 20MB per file
    Max storage per user: 200MB (tax files only)
    """
    __tablename__ = "files"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign key to user (uploader)
    uploaded_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # File metadata
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)  # Bytes

    # Categorization
    category: Mapped[FileCategory] = mapped_column(
        Enum(FileCategory, name="file_category", native_enum=False),
        nullable=False,
        index=True
    )

    # Optional associations (nullable - not all files are linked to records)
    linked_resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    linked_resource_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    # Description/notes
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Timestamps
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationship
    uploaded_by_user: Mapped["User"] = relationship("User", back_populates="files")

    def __repr__(self) -> str:
        return f"<File(id={self.id}, filename='{self.filename}', category='{self.category.value}')>"

    @property
    def file_size_mb(self) -> float:
        """Convert file size to MB"""
        return self.file_size / (1024 * 1024)

    @property
    def is_image(self) -> bool:
        """Check if file is an image"""
        return self.mime_type.startswith("image/")

    @property
    def is_pdf(self) -> bool:
        """Check if file is a PDF"""
        return self.mime_type == "application/pdf"

    @property
    def is_document(self) -> bool:
        """Check if file is a document"""
        doc_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ]
        return self.mime_type in doc_types
