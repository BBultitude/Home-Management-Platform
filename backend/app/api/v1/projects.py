"""
Projects & Tasks API endpoints
Handles priority items (repair prioritization), projects, and contractor quotes
"""

from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db, require_permission
from app.models.user import User
from app.models.priority_item import PriorityStatus
from app.models.project import ProjectStatus
from app.services.priority_item_service import PriorityItemService
from app.services.project_service import ProjectService
from app.services.quote_service import QuoteService
from app.schemas.priority_item import (
    PriorityItemCreate,
    PriorityItemUpdate,
    PriorityItemResponse,
    PriorityItemListResponse,
    ConvertToProjectRequest
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse
)
from app.schemas.quote import (
    QuoteCreate,
    QuoteUpdate,
    QuoteResponse,
    QuoteListResponse,
    QuoteComparisonResponse
)


router = APIRouter(prefix="/projects", tags=["projects"])


# Priority Items (Repair Prioritization)
@router.post("/priorities", response_model=PriorityItemResponse)
async def create_priority_item(
    item_data: PriorityItemCreate,
    current_user: Annotated[User, Depends(require_permission("projects:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Create a new priority item with cost-benefit scoring

    Automatically calculates:
    - Benefit Score: severity + frequency (2-10)
    - Cost Score: log10(cost) + 1 (1-5)
    - Net Score: benefit - cost_score (-3 to 9, higher = higher priority)

    Requires permission: projects:write
    """
    item = PriorityItemService.create_priority_item(
        db=db,
        description=item_data.description,
        cost=item_data.cost,
        severity=item_data.severity,
        frequency=item_data.frequency
    )

    return PriorityItemResponse(**item.to_dict())


@router.get("/priorities", response_model=PriorityItemListResponse)
async def list_priority_items(
    status: Annotated[Optional[PriorityStatus], Query(description="Filter by status")] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    List priority items sorted by net_score (highest priority first)

    Items are automatically sorted by priority (net_score DESC)
    """
    items = PriorityItemService.list_priority_items(
        db=db,
        status_filter=status,
        limit=limit,
        offset=offset
    )

    item_responses = [PriorityItemResponse(**i.to_dict()) for i in items]

    return PriorityItemListResponse(
        items=item_responses,
        total=len(items)
    )


@router.get("/priorities/{item_id}", response_model=PriorityItemResponse)
async def get_priority_item(
    item_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get a specific priority item"""
    item = PriorityItemService.get_priority_item(db, item_id)

    return PriorityItemResponse(**item.to_dict())


@router.put("/priorities/{item_id}", response_model=PriorityItemResponse)
async def update_priority_item(
    item_id: UUID,
    item_data: PriorityItemUpdate,
    current_user: Annotated[User, Depends(require_permission("projects:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Update a priority item

    Automatically recalculates scores if cost, severity, or frequency changed
    """
    item = PriorityItemService.update_priority_item(
        db=db,
        item_id=item_id,
        description=item_data.description,
        cost=item_data.cost,
        severity=item_data.severity,
        frequency=item_data.frequency,
        status_update=item_data.status
    )

    return PriorityItemResponse(**item.to_dict())


@router.delete("/priorities/{item_id}")
async def delete_priority_item(
    item_id: UUID,
    current_user: Annotated[User, Depends(require_permission("projects:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """Delete a priority item (cannot delete if converted to project)"""
    PriorityItemService.delete_priority_item(db, item_id)

    return {"message": "Priority item deleted successfully", "id": str(item_id)}


@router.post("/priorities/{item_id}/convert", response_model=ProjectResponse)
async def convert_priority_to_project(
    item_id: UUID,
    conversion_data: ConvertToProjectRequest,
    current_user: Annotated[User, Depends(require_permission("projects:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Convert a priority item to a project

    Creates a new project linked to the priority item and updates the priority item
    status to ConvertedToProject
    """
    project = PriorityItemService.convert_to_project(
        db=db,
        item_id=item_id,
        project_name=conversion_data.project_name,
        description=conversion_data.description,
        budget=conversion_data.budget,
        notes=conversion_data.notes
    )

    return ProjectResponse(**project.to_dict())


# Projects
@router.post("", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: Annotated[User, Depends(require_permission("projects:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Create a new project

    Can optionally link to a priority_item_id if this project originated from
    repair prioritization

    Requires permission: projects:write
    """
    project = ProjectService.create_project(
        db=db,
        project_name=project_data.project_name,
        description=project_data.description,
        priority_item_id=project_data.priority_item_id,
        project_status=project_data.status or ProjectStatus.PLANNED,
        start_date=project_data.start_date,
        completion_date=project_data.completion_date,
        budget=project_data.budget,
        actual_cost=project_data.actual_cost,
        notes=project_data.notes
    )

    return ProjectResponse(**project.to_dict())


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    status: Annotated[Optional[ProjectStatus], Query(description="Filter by status")] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """List projects with optional status filter"""
    projects = ProjectService.list_projects(
        db=db,
        status_filter=status,
        limit=limit,
        offset=offset
    )

    project_responses = [ProjectResponse(**p.to_dict()) for p in projects]

    return ProjectListResponse(
        projects=project_responses,
        total=len(projects)
    )


@router.get("/summary")
async def get_project_summary(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get project summary statistics

    Returns counts by status and budget totals
    """
    return ProjectService.get_project_summary(db)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get a specific project"""
    project = ProjectService.get_project(db, project_id)

    return ProjectResponse(**project.to_dict())


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    current_user: Annotated[User, Depends(require_permission("projects:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """Update a project"""
    project = ProjectService.update_project(
        db=db,
        project_id=project_id,
        project_name=project_data.project_name,
        description=project_data.description,
        project_status=project_data.status,
        start_date=project_data.start_date,
        completion_date=project_data.completion_date,
        budget=project_data.budget,
        actual_cost=project_data.actual_cost,
        notes=project_data.notes
    )

    return ProjectResponse(**project.to_dict())


@router.delete("/{project_id}")
async def delete_project(
    project_id: UUID,
    current_user: Annotated[User, Depends(require_permission("projects:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """Delete a project (cascade deletes quotes, unlinks priority item)"""
    ProjectService.delete_project(db, project_id)

    return {"message": "Project deleted successfully", "id": str(project_id)}


# Quotes
@router.post("/{project_id}/quotes", response_model=QuoteResponse)
async def create_quote(
    project_id: UUID,
    quote_data: QuoteCreate,
    current_user: Annotated[User, Depends(require_permission("projects:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Create a new quote for a project

    Requires permission: projects:write
    """
    # Override project_id from URL
    quote = QuoteService.create_quote(
        db=db,
        project_id=project_id,
        contractor_name=quote_data.contractor_name,
        contact_phone=quote_data.contact_phone,
        contact_email=quote_data.contact_email,
        quote_amount=quote_data.quote_amount,
        quote_date=quote_data.quote_date,
        expiry_date=quote_data.expiry_date,
        scope_of_work=quote_data.scope_of_work,
        selected=quote_data.selected,
        document_id=quote_data.document_id,
        notes=quote_data.notes
    )

    response_dict = quote.to_dict()
    response_dict["is_expired"] = quote.is_expired()
    response_dict["days_until_expiry"] = quote.days_until_expiry()

    return QuoteResponse(**response_dict)


@router.get("/{project_id}/quotes", response_model=QuoteListResponse)
async def list_project_quotes(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """List all quotes for a specific project"""
    quotes = QuoteService.list_quotes(db=db, project_id=project_id)

    quote_responses = []
    for q in quotes:
        response_dict = q.to_dict()
        response_dict["is_expired"] = q.is_expired()
        response_dict["days_until_expiry"] = q.days_until_expiry()
        quote_responses.append(QuoteResponse(**response_dict))

    return QuoteListResponse(
        quotes=quote_responses,
        total=len(quotes)
    )


@router.get("/{project_id}/quotes/compare", response_model=QuoteComparisonResponse)
async def compare_quotes(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get quote comparison for a project

    Returns all quotes with lowest and selected quotes highlighted
    """
    comparison = QuoteService.get_quote_comparison(db, project_id)

    # Add expiry info to quotes
    enhanced_quotes = []
    for q in comparison["quotes"]:
        response_dict = q.to_dict()
        response_dict["is_expired"] = q.is_expired()
        response_dict["days_until_expiry"] = q.days_until_expiry()
        enhanced_quotes.append(QuoteResponse(**response_dict))

    # Enhance lowest and selected quotes
    lowest_enhanced = None
    if comparison["lowest_quote"]:
        lowest_dict = comparison["lowest_quote"].to_dict()
        lowest_dict["is_expired"] = comparison["lowest_quote"].is_expired()
        lowest_dict["days_until_expiry"] = comparison["lowest_quote"].days_until_expiry()
        lowest_enhanced = QuoteResponse(**lowest_dict)

    selected_enhanced = None
    if comparison["selected_quote"]:
        selected_dict = comparison["selected_quote"].to_dict()
        selected_dict["is_expired"] = comparison["selected_quote"].is_expired()
        selected_dict["days_until_expiry"] = comparison["selected_quote"].days_until_expiry()
        selected_enhanced = QuoteResponse(**selected_dict)

    return QuoteComparisonResponse(
        project_id=comparison["project_id"],
        project_name=comparison["project_name"],
        quotes=enhanced_quotes,
        lowest_quote=lowest_enhanced,
        selected_quote=selected_enhanced
    )


@router.get("/quotes/{quote_id}", response_model=QuoteResponse)
async def get_quote(
    quote_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get a specific quote"""
    quote = QuoteService.get_quote(db, quote_id)

    response_dict = quote.to_dict()
    response_dict["is_expired"] = quote.is_expired()
    response_dict["days_until_expiry"] = quote.days_until_expiry()

    return QuoteResponse(**response_dict)


@router.put("/quotes/{quote_id}", response_model=QuoteResponse)
async def update_quote(
    quote_id: UUID,
    quote_data: QuoteUpdate,
    current_user: Annotated[User, Depends(require_permission("projects:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Update a quote

    If marking as selected, automatically unselects other quotes for same project
    """
    quote = QuoteService.update_quote(
        db=db,
        quote_id=quote_id,
        contractor_name=quote_data.contractor_name,
        contact_phone=quote_data.contact_phone,
        contact_email=quote_data.contact_email,
        quote_amount=quote_data.quote_amount,
        quote_date=quote_data.quote_date,
        expiry_date=quote_data.expiry_date,
        scope_of_work=quote_data.scope_of_work,
        selected=quote_data.selected,
        document_id=quote_data.document_id,
        notes=quote_data.notes
    )

    response_dict = quote.to_dict()
    response_dict["is_expired"] = quote.is_expired()
    response_dict["days_until_expiry"] = quote.days_until_expiry()

    return QuoteResponse(**response_dict)


@router.delete("/quotes/{quote_id}")
async def delete_quote(
    quote_id: UUID,
    current_user: Annotated[User, Depends(require_permission("projects:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """Delete a quote"""
    QuoteService.delete_quote(db, quote_id)

    return {"message": "Quote deleted successfully", "id": str(quote_id)}


@router.get("/quotes/alerts/expiry", response_model=list[QuoteResponse])
async def get_quote_expiry_alerts(
    days: Annotated[int, Query(ge=1, le=365, description="Days before expiry to alert")] = 30,
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get quote expiry alerts

    Returns quotes expiring within specified days threshold
    """
    quotes = QuoteService.get_expiry_alerts(db, days_threshold=days)

    alert_responses = []
    for q in quotes:
        response_dict = q.to_dict()
        response_dict["is_expired"] = q.is_expired()
        response_dict["days_until_expiry"] = q.days_until_expiry()
        alert_responses.append(QuoteResponse(**response_dict))

    return alert_responses
