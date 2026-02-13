"""
Knowledge Base API endpoints
Handles household knowledge articles with full-text search and attachments
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db, require_permission
from app.models.user import User
from app.models.knowledge_article import ArticleType
from app.services.knowledge_service import KnowledgeService
from app.schemas.knowledge import (
    KnowledgeArticleCreate,
    KnowledgeArticleUpdate,
    KnowledgeArticleResponse,
    KnowledgeArticleListResponse,
    KnowledgeSearchRequest,
    AttachmentResponse
)


router = APIRouter(prefix="/knowledge", tags=["knowledge"])


# Knowledge Articles
@router.post("", response_model=KnowledgeArticleResponse)
async def create_knowledge_article(
    article_data: KnowledgeArticleCreate,
    current_user: User = Depends(require_permission("knowledge:write")),
    db: Session = Depends(get_db)
):
    """
    Create a new knowledge article

    Supports 8 article types:
    - Measurement: Room dimensions, window sizes, etc.
    - Paint: Paint colors and finishes by room
    - TechDevice: Network devices with encrypted passwords
    - StorageLocation: Storage organization
    - Vehicle: Vehicle details and service history
    - EmergencyContact: Important contacts
    - Appliance: Appliance details and warranties
    - Vendor: Contractor and vendor information

    Requires permission: knowledge:write
    """
    article = KnowledgeService.create_article(
        db=db,
        article_type=article_data.article_type,
        title=article_data.title,
        data=article_data.data,
        tags=article_data.tags,
        created_by=current_user.id,
        attachment_ids=article_data.attachment_ids
    )

    return KnowledgeArticleResponse(**article.to_dict())


@router.get("", response_model=KnowledgeArticleListResponse)
async def list_knowledge_articles(
    article_type: Optional[ArticleType] = Query(None, description="Filter by article type"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List knowledge articles with optional filters

    Articles are ordered by most recently updated
    """
    articles = KnowledgeService.list_articles(
        db=db,
        article_type=article_type,
        tag=tag,
        limit=limit,
        offset=offset
    )

    article_responses = [KnowledgeArticleResponse(**a.to_dict()) for a in articles]

    return KnowledgeArticleListResponse(
        articles=article_responses,
        total=len(articles)
    )


@router.post("/search", response_model=KnowledgeArticleListResponse)
async def search_knowledge_articles(
    search_request: KnowledgeSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Full-text search across knowledge articles

    Uses PostgreSQL full-text search for fast, relevant results.
    Searches across title, data fields, and tags.
    """
    articles = KnowledgeService.search_articles(
        db=db,
        query_text=search_request.query,
        article_types=search_request.article_types,
        tags=search_request.tags,
        limit=search_request.limit or 50
    )

    article_responses = [KnowledgeArticleResponse(**a.to_dict()) for a in articles]

    return KnowledgeArticleListResponse(
        articles=article_responses,
        total=len(articles)
    )


@router.get("/{article_id}", response_model=KnowledgeArticleResponse)
async def get_knowledge_article(
    article_id: UUID,
    decrypt_passwords: bool = Query(False, description="Decrypt passwords (requires knowledge:admin)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific knowledge article

    For TechDevice articles, passwords are encrypted by default.
    Set decrypt_passwords=true to decrypt (requires knowledge:admin permission).
    """
    # Check permission for password decryption
    if decrypt_passwords:
        # This will raise 403 if user doesn't have permission
        _admin_user = require_permission("knowledge:admin")(current_user)

    article = KnowledgeService.get_article(db, article_id, decrypt_passwords=decrypt_passwords)

    return KnowledgeArticleResponse(**article.to_dict())


@router.put("/{article_id}", response_model=KnowledgeArticleResponse)
async def update_knowledge_article(
    article_id: UUID,
    article_data: KnowledgeArticleUpdate,
    current_user: User = Depends(require_permission("knowledge:write")),
    db: Session = Depends(get_db)
):
    """
    Update a knowledge article

    Updates search index automatically
    """
    article = KnowledgeService.update_article(
        db=db,
        article_id=article_id,
        title=article_data.title,
        data=article_data.data,
        tags=article_data.tags
    )

    return KnowledgeArticleResponse(**article.to_dict())


@router.delete("/{article_id}")
async def delete_knowledge_article(
    article_id: UUID,
    current_user: User = Depends(require_permission("knowledge:write")),
    db: Session = Depends(get_db)
):
    """Delete a knowledge article (cascade deletes attachments)"""
    KnowledgeService.delete_article(db, article_id)

    return {"message": "Knowledge article deleted successfully", "id": str(article_id)}


# Attachments
@router.post("/{article_id}/attachments", response_model=AttachmentResponse)
async def add_attachment(
    article_id: UUID,
    file_id: UUID,
    current_user: User = Depends(require_permission("knowledge:write")),
    db: Session = Depends(get_db)
):
    """
    Add a file attachment to a knowledge article

    Links an existing uploaded file to the article
    """
    attachment = KnowledgeService.add_attachment(db, article_id, file_id)

    return AttachmentResponse(**attachment.to_dict())


@router.get("/{article_id}/attachments", response_model=list[AttachmentResponse])
async def list_attachments(
    article_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all attachments for a knowledge article"""
    attachments = KnowledgeService.list_attachments(db, article_id)

    return [AttachmentResponse(**a.to_dict()) for a in attachments]


@router.delete("/attachments/{attachment_id}")
async def remove_attachment(
    attachment_id: UUID,
    current_user: User = Depends(require_permission("knowledge:write")),
    db: Session = Depends(get_db)
):
    """Remove an attachment from a knowledge article"""
    KnowledgeService.remove_attachment(db, attachment_id)

    return {"message": "Attachment removed successfully", "id": str(attachment_id)}
