"""
Document Service
Handles CRUD operations and expiry alerts for documents
"""

from datetime import date
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.document import Document, DocumentType


class DocumentService:
    """Service for document operations"""

    @staticmethod
    def create_document(
        db: Session,
        document_type: DocumentType,
        title: str,
        file_id: UUID,
        description: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        uploaded_date: Optional[date] = None,
        expiry_date: Optional[date] = None
    ) -> Document:
        """Create a new document"""
        # Verify file exists
        from app.models.file import File
        file = db.query(File).filter(File.id == file_id).first()
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        if expiry_date and expiry_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expiry date cannot be in the past"
            )

        document = Document(
            document_type=document_type.value,
            title=title,
            description=description,
            category=category,
            tags=tags or [],
            uploaded_date=uploaded_date or date.today(),
            expiry_date=expiry_date,
            file_id=file_id
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def get_document(db: Session, document_id: UUID) -> Document:
        """Get a document by ID"""
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        return document

    @staticmethod
    def list_documents(
        db: Session,
        document_type: Optional[DocumentType] = None,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Document]:
        """List documents with optional filters"""
        query = db.query(Document)

        if document_type:
            query = query.filter(Document.document_type == document_type.value)

        if category:
            query = query.filter(Document.category == category)

        if tag:
            query = query.filter(Document.tags.contains([tag]))

        query = query.order_by(Document.uploaded_date.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def update_document(
        db: Session,
        document_id: UUID,
        document_type: Optional[DocumentType] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        expiry_date: Optional[date] = None
    ) -> Document:
        """Update a document"""
        document = DocumentService.get_document(db, document_id)

        if document_type is not None:
            document.document_type = document_type.value

        if title is not None:
            document.title = title

        if description is not None:
            document.description = description

        if category is not None:
            document.category = category

        if tags is not None:
            document.tags = tags

        if expiry_date is not None:
            if expiry_date < date.today():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Expiry date cannot be in the past"
                )
            document.expiry_date = expiry_date

        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def delete_document(db: Session, document_id: UUID) -> None:
        """Delete a document (cascade deletes file)"""
        document = DocumentService.get_document(db, document_id)

        db.delete(document)
        db.commit()

    @staticmethod
    def get_expiry_alerts(db: Session, days_threshold: int = 30) -> list[Document]:
        """
        Get documents with upcoming expiry dates

        Args:
            db: Database session
            days_threshold: Number of days before expiry to alert (default 30)

        Returns:
            List of documents expiring within threshold
        """
        today = date.today()
        threshold_date = date.fromordinal(today.toordinal() + days_threshold)

        documents = db.query(Document).filter(
            Document.expiry_date.isnot(None),
            Document.expiry_date >= today,
            Document.expiry_date <= threshold_date
        ).order_by(Document.expiry_date).all()

        return documents

    @staticmethod
    def search_documents(db: Session, search_term: str, limit: int = 50) -> list[Document]:
        """
        Search documents by title, description, category, or tags

        Args:
            db: Database session
            search_term: Text to search for
            limit: Maximum results to return

        Returns:
            List of matching documents
        """
        search_pattern = f"%{search_term}%"

        documents = db.query(Document).filter(
            (Document.title.ilike(search_pattern)) |
            (Document.description.ilike(search_pattern)) |
            (Document.category.ilike(search_pattern))
        ).order_by(Document.uploaded_date.desc()).limit(limit).all()

        return documents
