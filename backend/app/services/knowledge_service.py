"""
Knowledge Service
Handles CRUD operations for knowledge base articles with password encryption
"""

from datetime import datetime, timezone
from typing import Optional, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, text
from fastapi import HTTPException, status
from cryptography.fernet import Fernet

from app.models.knowledge_article import KnowledgeArticle, KnowledgeAttachment, ArticleType
from app.models.file import File
from app.core.config import settings


class KnowledgeService:
    """Service for knowledge article operations"""

    # Password fields that need encryption for TechDevice articles
    ENCRYPTED_FIELDS = ["wifi_password", "admin_password"]

    @staticmethod
    def _get_cipher() -> Fernet:
        """Get Fernet cipher for password encryption"""
        return Fernet(settings.mfa_encryption_key.encode())

    @staticmethod
    def _encrypt_passwords(article_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Encrypt password fields for TechDevice articles

        Args:
            article_type: Article type
            data: Article data

        Returns:
            Data with encrypted passwords
        """
        if article_type != ArticleType.TECH_DEVICE.value:
            return data

        cipher = KnowledgeService._get_cipher()
        encrypted_data = data.copy()

        for field in KnowledgeService.ENCRYPTED_FIELDS:
            if field in encrypted_data and encrypted_data[field]:
                # Encrypt the password
                encrypted_data[field] = cipher.encrypt(
                    encrypted_data[field].encode()
                ).decode()

        return encrypted_data

    @staticmethod
    def _decrypt_passwords(article_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Decrypt password fields for TechDevice articles

        Args:
            article_type: Article type
            data: Article data with encrypted passwords

        Returns:
            Data with decrypted passwords
        """
        if article_type != ArticleType.TECH_DEVICE.value:
            return data

        cipher = KnowledgeService._get_cipher()
        decrypted_data = data.copy()

        for field in KnowledgeService.ENCRYPTED_FIELDS:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    # Decrypt the password
                    decrypted_data[field] = cipher.decrypt(
                        decrypted_data[field].encode()
                    ).decode()
                except Exception:
                    # If decryption fails, leave as is (might be unencrypted legacy data)
                    pass

        return decrypted_data

    @staticmethod
    def _generate_search_vector(title: str, data: dict[str, Any], tags: list[str]) -> str:
        """
        Generate search vector text from article content

        Args:
            title: Article title
            data: Article data
            tags: Article tags

        Returns:
            Concatenated searchable text
        """
        search_parts = [title]

        # Add data values (skip encrypted passwords)
        for key, value in data.items():
            if key not in KnowledgeService.ENCRYPTED_FIELDS and value:
                if isinstance(value, (str, int, float)):
                    search_parts.append(str(value))
                elif isinstance(value, list):
                    search_parts.extend([str(item) for item in value if isinstance(item, (str, int, float))])

        # Add tags
        if tags:
            search_parts.extend(tags)

        return " ".join(search_parts)

    @staticmethod
    def create_article(
        db: Session,
        article_type: ArticleType,
        title: str,
        data: dict[str, Any],
        tags: Optional[list[str]] = None,
        created_by: Optional[UUID] = None,
        attachment_ids: Optional[list[UUID]] = None
    ) -> KnowledgeArticle:
        """Create a new knowledge article"""
        # Encrypt passwords if TechDevice
        encrypted_data = KnowledgeService._encrypt_passwords(article_type.value, data)

        # Generate search vector text
        search_text = KnowledgeService._generate_search_vector(title, data, tags or [])

        article = KnowledgeArticle(
            article_type=article_type.value,
            title=title,
            data=encrypted_data,
            tags=tags or [],
            created_by=created_by
        )

        db.add(article)
        db.flush()  # Get article ID

        # Update search vector using PostgreSQL to_tsvector
        db.execute(
            text("UPDATE knowledge_articles SET search_vector = to_tsvector('english', :search_text) WHERE id = :article_id"),
            {"search_text": search_text, "article_id": article.id}
        )

        # Add attachments
        if attachment_ids:
            for file_id in attachment_ids:
                # Verify file exists
                file = db.query(File).filter(File.id == file_id).first()
                if not file:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"File {file_id} not found"
                    )

                attachment = KnowledgeAttachment(
                    article_id=article.id,
                    file_id=file_id
                )
                db.add(attachment)

        db.commit()
        db.refresh(article)

        return article

    @staticmethod
    def get_article(db: Session, article_id: UUID, decrypt_passwords: bool = False) -> KnowledgeArticle:
        """
        Get a knowledge article by ID

        Args:
            db: Database session
            article_id: Article ID
            decrypt_passwords: Whether to decrypt passwords (requires extra permission check)

        Returns:
            KnowledgeArticle
        """
        article = db.query(KnowledgeArticle).filter(KnowledgeArticle.id == article_id).first()

        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge article not found"
            )

        # Decrypt passwords if requested
        if decrypt_passwords:
            article.data = KnowledgeService._decrypt_passwords(article.article_type, article.data)

        return article

    @staticmethod
    def list_articles(
        db: Session,
        article_type: Optional[ArticleType] = None,
        tag: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[KnowledgeArticle]:
        """List knowledge articles with optional filters"""
        query = db.query(KnowledgeArticle)

        if article_type:
            query = query.filter(KnowledgeArticle.article_type == article_type.value)

        if tag:
            query = query.filter(KnowledgeArticle.tags.contains([tag]))

        query = query.order_by(KnowledgeArticle.updated_at.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def update_article(
        db: Session,
        article_id: UUID,
        title: Optional[str] = None,
        data: Optional[dict[str, Any]] = None,
        tags: Optional[list[str]] = None
    ) -> KnowledgeArticle:
        """Update a knowledge article"""
        article = KnowledgeService.get_article(db, article_id)

        if title is not None:
            article.title = title

        if data is not None:
            # Encrypt passwords if TechDevice
            encrypted_data = KnowledgeService._encrypt_passwords(article.article_type, data)
            article.data = encrypted_data

        if tags is not None:
            article.tags = tags

        # Update search vector
        search_text = KnowledgeService._generate_search_vector(
            article.title,
            data or article.data,
            tags if tags is not None else article.tags
        )
        db.execute(
            text("UPDATE knowledge_articles SET search_vector = to_tsvector('english', :search_text) WHERE id = :article_id"),
            {"search_text": search_text, "article_id": article.id}
        )

        article.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(article)

        return article

    @staticmethod
    def delete_article(db: Session, article_id: UUID) -> None:
        """Delete a knowledge article (cascade deletes attachments)"""
        article = KnowledgeService.get_article(db, article_id)

        db.delete(article)
        db.commit()

    @staticmethod
    def search_articles(
        db: Session,
        query_text: str,
        article_types: Optional[list[ArticleType]] = None,
        tags: Optional[list[str]] = None,
        limit: int = 50
    ) -> list[KnowledgeArticle]:
        """
        Full-text search across knowledge articles

        Args:
            db: Database session
            query_text: Search query
            article_types: Optional filter by article types
            tags: Optional filter by tags
            limit: Maximum results

        Returns:
            List of matching articles
        """
        query = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.search_vector.op('@@')(func.to_tsquery('english', query_text))
        )

        if article_types:
            type_values = [at.value for at in article_types]
            query = query.filter(KnowledgeArticle.article_type.in_(type_values))

        if tags:
            # Match any of the provided tags
            tag_filters = [KnowledgeArticle.tags.contains([tag]) for tag in tags]
            query = query.filter(or_(*tag_filters))

        # Order by search rank
        query = query.order_by(
            func.ts_rank(
                KnowledgeArticle.search_vector,
                func.to_tsquery('english', query_text)
            ).desc()
        )

        query = query.limit(limit)

        return query.all()

    @staticmethod
    def add_attachment(db: Session, article_id: UUID, file_id: UUID) -> KnowledgeAttachment:
        """Add an attachment to a knowledge article"""
        # Verify article exists
        KnowledgeService.get_article(db, article_id)

        # Verify file exists
        file = db.query(File).filter(File.id == file_id).first()
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        # Check if already attached
        existing = db.query(KnowledgeAttachment).filter(
            KnowledgeAttachment.article_id == article_id,
            KnowledgeAttachment.file_id == file_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File already attached to this article"
            )

        attachment = KnowledgeAttachment(
            article_id=article_id,
            file_id=file_id
        )

        db.add(attachment)
        db.commit()
        db.refresh(attachment)

        return attachment

    @staticmethod
    def remove_attachment(db: Session, attachment_id: UUID) -> None:
        """Remove an attachment from a knowledge article"""
        attachment = db.query(KnowledgeAttachment).filter(
            KnowledgeAttachment.id == attachment_id
        ).first()

        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment not found"
            )

        db.delete(attachment)
        db.commit()

    @staticmethod
    def list_attachments(db: Session, article_id: UUID) -> list[KnowledgeAttachment]:
        """List all attachments for an article"""
        return db.query(KnowledgeAttachment).filter(
            KnowledgeAttachment.article_id == article_id
        ).all()
