"""
Assets & Documents API endpoints
Handles insurance policies and important documents
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db, require_permission
from app.models.user import User
from app.models.insurance_policy import PolicyType
from app.models.document import DocumentType
from app.services.insurance_policy_service import InsurancePolicyService
from app.services.document_service import DocumentService
from app.schemas.insurance_policy import (
    InsurancePolicyCreate,
    InsurancePolicyUpdate,
    InsurancePolicyResponse,
    InsurancePolicyListResponse,
    RenewalAlertResponse
)
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
    ExpiryAlertResponse
)


router = APIRouter(prefix="/assets", tags=["assets"])


# Insurance Policies
@router.post("/insurance", response_model=InsurancePolicyResponse)
async def create_insurance_policy(
    policy_data: InsurancePolicyCreate,
    current_user: User = Depends(require_permission("assets:write")),
    db: Session = Depends(get_db)
):
    """
    Create a new insurance policy

    Requires permission: assets:write
    """
    policy = InsurancePolicyService.create_policy(
        db=db,
        policy_type=policy_data.policy_type,
        provider=policy_data.provider,
        policy_number=policy_data.policy_number,
        coverage_amount=policy_data.coverage_amount,
        premium=policy_data.premium,
        premium_frequency=policy_data.premium_frequency,
        excess=policy_data.excess,
        renewal_date=policy_data.renewal_date,
        coverage_notes=policy_data.coverage_notes,
        document_id=policy_data.document_id,
        vehicle_id=policy_data.vehicle_id
    )

    response_dict = policy.to_dict()
    response_dict["days_until_renewal"] = policy.days_until_renewal()

    return InsurancePolicyResponse(**response_dict)


@router.get("/insurance", response_model=InsurancePolicyListResponse)
async def list_insurance_policies(
    policy_type: Optional[PolicyType] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all insurance policies"""
    policies = InsurancePolicyService.list_policies(
        db=db,
        policy_type=policy_type,
        limit=limit,
        offset=offset
    )

    policy_responses = []
    for p in policies:
        response_dict = p.to_dict()
        response_dict["days_until_renewal"] = p.days_until_renewal()
        policy_responses.append(InsurancePolicyResponse(**response_dict))

    return InsurancePolicyListResponse(
        policies=policy_responses,
        total=len(policies)
    )


@router.get("/insurance/{policy_id}", response_model=InsurancePolicyResponse)
async def get_insurance_policy(
    policy_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific insurance policy"""
    policy = InsurancePolicyService.get_policy(db, policy_id)

    response_dict = policy.to_dict()
    response_dict["days_until_renewal"] = policy.days_until_renewal()

    return InsurancePolicyResponse(**response_dict)


@router.put("/insurance/{policy_id}", response_model=InsurancePolicyResponse)
async def update_insurance_policy(
    policy_id: UUID,
    policy_data: InsurancePolicyUpdate,
    current_user: User = Depends(require_permission("assets:write")),
    db: Session = Depends(get_db)
):
    """Update an insurance policy"""
    policy = InsurancePolicyService.update_policy(
        db=db,
        policy_id=policy_id,
        policy_type=policy_data.policy_type,
        provider=policy_data.provider,
        policy_number=policy_data.policy_number,
        coverage_amount=policy_data.coverage_amount,
        premium=policy_data.premium,
        premium_frequency=policy_data.premium_frequency,
        excess=policy_data.excess,
        renewal_date=policy_data.renewal_date,
        coverage_notes=policy_data.coverage_notes,
        document_id=policy_data.document_id,
        vehicle_id=policy_data.vehicle_id
    )

    response_dict = policy.to_dict()
    response_dict["days_until_renewal"] = policy.days_until_renewal()

    return InsurancePolicyResponse(**response_dict)


@router.delete("/insurance/{policy_id}")
async def delete_insurance_policy(
    policy_id: UUID,
    current_user: User = Depends(require_permission("assets:write")),
    db: Session = Depends(get_db)
):
    """Delete an insurance policy"""
    InsurancePolicyService.delete_policy(db, policy_id)

    return {"message": "Insurance policy deleted successfully", "id": str(policy_id)}


@router.get("/insurance/alerts/renewals", response_model=list[RenewalAlertResponse])
async def get_renewal_alerts(
    days: int = Query(30, ge=1, le=365, description="Days before renewal to alert"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get insurance renewal alerts

    Returns policies due for renewal within specified days threshold
    """
    policies = InsurancePolicyService.get_renewal_alerts(db, days_threshold=days)

    alerts = [
        RenewalAlertResponse(
            policy_id=str(p.id),
            policy_type=p.policy_type,
            provider=p.provider,
            renewal_date=p.renewal_date.isoformat(),
            days_until_renewal=p.days_until_renewal(),
            premium=float(p.premium),
            premium_frequency=p.premium_frequency
        )
        for p in policies
    ]

    return alerts


@router.get("/insurance/summary/costs")
async def get_insurance_cost_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get insurance cost summary for budget integration

    Returns total monthly and annual insurance costs
    """
    return InsurancePolicyService.get_cost_summary(db)


# Documents
@router.post("/documents", response_model=DocumentResponse)
async def create_document(
    document_data: DocumentCreate,
    current_user: User = Depends(require_permission("assets:write")),
    db: Session = Depends(get_db)
):
    """
    Create a new document

    Requires permission: assets:write
    """
    document = DocumentService.create_document(
        db=db,
        document_type=document_data.document_type,
        title=document_data.title,
        file_id=document_data.file_id,
        description=document_data.description,
        category=document_data.category,
        tags=document_data.tags,
        uploaded_date=document_data.uploaded_date,
        expiry_date=document_data.expiry_date
    )

    response_dict = document.to_dict()
    response_dict["is_expired"] = document.is_expired()
    response_dict["days_until_expiry"] = document.days_until_expiry()

    return DocumentResponse(**response_dict)


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    document_type: Optional[DocumentType] = Query(None),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List documents with optional filters"""
    documents = DocumentService.list_documents(
        db=db,
        document_type=document_type,
        category=category,
        tag=tag,
        limit=limit,
        offset=offset
    )

    document_responses = []
    for d in documents:
        response_dict = d.to_dict()
        response_dict["is_expired"] = d.is_expired()
        response_dict["days_until_expiry"] = d.days_until_expiry()
        document_responses.append(DocumentResponse(**response_dict))

    return DocumentListResponse(
        documents=document_responses,
        total=len(documents)
    )


@router.get("/documents/search")
async def search_documents(
    q: str = Query(..., min_length=1, description="Search term"),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Search documents by title, description, category, or tags

    Returns matching documents ordered by upload date
    """
    documents = DocumentService.search_documents(db, search_term=q, limit=limit)

    document_responses = []
    for d in documents:
        response_dict = d.to_dict()
        response_dict["is_expired"] = d.is_expired()
        response_dict["days_until_expiry"] = d.days_until_expiry()
        document_responses.append(DocumentResponse(**response_dict))

    return DocumentListResponse(
        documents=document_responses,
        total=len(documents)
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    document = DocumentService.get_document(db, document_id)

    response_dict = document.to_dict()
    response_dict["is_expired"] = document.is_expired()
    response_dict["days_until_expiry"] = document.days_until_expiry()

    return DocumentResponse(**response_dict)


@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    document_data: DocumentUpdate,
    current_user: User = Depends(require_permission("assets:write")),
    db: Session = Depends(get_db)
):
    """Update a document"""
    document = DocumentService.update_document(
        db=db,
        document_id=document_id,
        document_type=document_data.document_type,
        title=document_data.title,
        description=document_data.description,
        category=document_data.category,
        tags=document_data.tags,
        expiry_date=document_data.expiry_date
    )

    response_dict = document.to_dict()
    response_dict["is_expired"] = document.is_expired()
    response_dict["days_until_expiry"] = document.days_until_expiry()

    return DocumentResponse(**response_dict)


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: UUID,
    current_user: User = Depends(require_permission("assets:write")),
    db: Session = Depends(get_db)
):
    """Delete a document (cascade deletes file)"""
    DocumentService.delete_document(db, document_id)

    return {"message": "Document deleted successfully", "id": str(document_id)}


@router.get("/documents/alerts/expiry", response_model=list[ExpiryAlertResponse])
async def get_expiry_alerts(
    days: int = Query(30, ge=1, le=365, description="Days before expiry to alert"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get document expiry alerts

    Returns documents expiring within specified days threshold
    """
    documents = DocumentService.get_expiry_alerts(db, days_threshold=days)

    alerts = [
        ExpiryAlertResponse(
            document_id=str(d.id),
            title=d.title,
            document_type=d.document_type,
            expiry_date=d.expiry_date.isoformat(),
            days_until_expiry=d.days_until_expiry()
        )
        for d in documents
    ]

    return alerts
