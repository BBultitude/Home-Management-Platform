"""
Tax WFH Entry API endpoints
"""

from datetime import date
from decimal import Decimal
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db, require_permission
from app.models.user import User
from app.services.tax_wfh_service import TaxWFHService
from app.services.audit_service import AuditService
from app.schemas.tax_wfh import (
    TaxWFHEntryCreate,
    TaxWFHEntryUpdate,
    TaxWFHEntryResponse,
    TaxWFHEntryListResponse,
    TaxWFHDeleteResponse,
    TaxWFHFYSummaryResponse
)


router = APIRouter(prefix="/tax/wfh", tags=["tax-wfh"])


def get_client_info(request: Request) -> tuple[str, str]:
    """Extract IP address and user agent from request"""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    return ip_address, user_agent


@router.post("", response_model=TaxWFHEntryResponse)
async def create_wfh_entry(
    request: Request,
    entry_data: TaxWFHEntryCreate,
    current_user: Annotated[User, Depends(require_permission("tax:create"))],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Create a new WFH entry

    Requires permission: tax:create
    """
    # Create entry
    entry = TaxWFHService.create_entry(
        db=db,
        user=current_user,
        entry_date=entry_data.date,
        hours=entry_data.hours,
        notes=entry_data.notes
    )

    # Log audit event
    ip_address, user_agent = get_client_info(request)
    AuditService.log_tax_wfh_create(
        db=db,
        user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
        tax_id=entry.id,
        details={
            "date": entry.date.isoformat(),
            "hours": float(entry.hours),
            "deduction": float(entry.deduction_amount)
        }
    )

    return TaxWFHEntryResponse(
        id=entry.id,
        user_id=entry.user_id,
        date=entry.date,
        hours=float(entry.hours),
        notes=entry.notes,
        deduction_amount=float(entry.deduction_amount),
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )


@router.get("", response_model=TaxWFHEntryListResponse)
async def list_wfh_entries(
    start_date: Annotated[Optional[date], Query()] = None,
    end_date: Annotated[Optional[date], Query()] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    List current user's WFH entries

    Optionally filter by date range.
    """
    entries = TaxWFHService.list_user_entries(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )

    entry_responses = [
        TaxWFHEntryResponse(
            id=e.id,
            user_id=e.user_id,
            date=e.date,
            hours=float(e.hours),
            notes=e.notes,
            deduction_amount=float(e.deduction_amount),
            created_at=e.created_at,
            updated_at=e.updated_at
        )
        for e in entries
    ]

    return TaxWFHEntryListResponse(
        entries=entry_responses,
        total=len(entries),
        start_date=start_date,
        end_date=end_date
    )


@router.get("/users/{user_id}", response_model=TaxWFHEntryListResponse)
async def list_user_wfh_entries(
    user_id: int,
    start_date: Annotated[Optional[date], Query()] = None,
    end_date: Annotated[Optional[date], Query()] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    List another user's WFH entries (household transparency)

    All authenticated users can view other users' entries (read-only).
    """
    entries = TaxWFHService.list_user_entries(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )

    entry_responses = [
        TaxWFHEntryResponse(
            id=e.id,
            user_id=e.user_id,
            date=e.date,
            hours=float(e.hours),
            notes=e.notes,
            deduction_amount=float(e.deduction_amount),
            created_at=e.created_at,
            updated_at=e.updated_at
        )
        for e in entries
    ]

    return TaxWFHEntryListResponse(
        entries=entry_responses,
        total=len(entries),
        start_date=start_date,
        end_date=end_date
    )


@router.get("/{entry_id}", response_model=TaxWFHEntryResponse)
async def get_wfh_entry(
    entry_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get a specific WFH entry

    Users can view their own entries and other users' entries (household transparency).
    """
    entry = TaxWFHService.get_entry(db, entry_id, current_user)

    return TaxWFHEntryResponse(
        id=entry.id,
        user_id=entry.user_id,
        date=entry.date,
        hours=float(entry.hours),
        notes=entry.notes,
        deduction_amount=float(entry.deduction_amount),
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )


@router.put("/{entry_id}", response_model=TaxWFHEntryResponse)
async def update_wfh_entry(
    request: Request,
    entry_id: int,
    entry_data: TaxWFHEntryUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Update a WFH entry

    Only the owner or admin can update an entry.
    """
    # Update entry
    entry = TaxWFHService.update_entry(
        db=db,
        entry_id=entry_id,
        user=current_user,
        hours=entry_data.hours,
        notes=entry_data.notes
    )

    # Log audit event
    ip_address, user_agent = get_client_info(request)
    changes = {}
    if entry_data.hours is not None:
        changes["hours"] = float(entry_data.hours)
    if entry_data.notes is not None:
        changes["notes"] = entry_data.notes

    # Note: Need to add TAX_WFH_UPDATE event type
    # For now, use generic log_event
    from app.models.audit_log import EventType, Severity
    AuditService.log_event(
        db=db,
        event_type=EventType.TAX_WFH_UPDATE,
        user_id=current_user.id,
        username=current_user.username,
        ip_address=ip_address,
        user_agent=user_agent,
        resource_type="tax_wfh",
        resource_id=entry.id,
        details={"changes": changes},
        severity=Severity.INFO
    )

    return TaxWFHEntryResponse(
        id=entry.id,
        user_id=entry.user_id,
        date=entry.date,
        hours=float(entry.hours),
        notes=entry.notes,
        deduction_amount=float(entry.deduction_amount),
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )


@router.delete("/{entry_id}", response_model=TaxWFHDeleteResponse)
async def delete_wfh_entry(
    request: Request,
    entry_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Delete a WFH entry

    Only the owner or admin can delete an entry.
    """
    # Get entry for audit logging (before deletion)
    entry = TaxWFHService.get_entry(db, entry_id, current_user)
    entry_date = entry.date
    entry_hours = entry.hours

    # Delete entry
    TaxWFHService.delete_entry(db, entry_id, current_user)

    # Log audit event
    ip_address, user_agent = get_client_info(request)
    from app.models.audit_log import EventType, Severity
    AuditService.log_event(
        db=db,
        event_type=EventType.TAX_WFH_DELETE,
        user_id=current_user.id,
        username=current_user.username,
        ip_address=ip_address,
        user_agent=user_agent,
        resource_type="tax_wfh",
        resource_id=entry_id,
        details={
            "date": entry_date.isoformat(),
            "hours": float(entry_hours)
        },
        severity=Severity.WARNING
    )

    return TaxWFHDeleteResponse(
        message="WFH entry deleted successfully",
        entry_id=entry_id
    )


@router.get("/summary/fy/{fy_year}", response_model=TaxWFHFYSummaryResponse)
async def get_fy_summary(
    fy_year: int,
    rate_per_hour: Annotated[Decimal, Query(description="Rate per hour for deduction calculation")] = Decimal("0.67"),
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get financial year summary for current user's WFH entries

    Financial year runs July 1 to June 30.
    FY 2024 = July 1, 2023 to June 30, 2024
    """
    summary = TaxWFHService.get_financial_year_summary(
        db=db,
        user_id=current_user.id,
        fy_year=fy_year,
        rate_per_hour=rate_per_hour
    )

    return TaxWFHFYSummaryResponse(**summary)


@router.get("/export/fy/{fy_year}/csv")
async def export_fy_csv(
    request: Request,
    fy_year: int,
    rate_per_hour: Annotated[Decimal, Query(description="Rate per hour for deduction calculation")] = Decimal("0.67"),
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Export financial year WFH entries to CSV format

    Returns ATO-compliant CSV file for tax lodgement.
    """
    # Generate CSV
    csv_content = TaxWFHService.export_fy_to_csv(db, current_user.id, fy_year, rate_per_hour)

    # Log audit event
    ip_address, user_agent = get_client_info(request)
    from app.models.audit_log import EventType, Severity
    AuditService.log_event(
        db=db,
        event_type=EventType.TAX_WFH_EXPORT,
        user_id=current_user.id,
        username=current_user.username,
        ip_address=ip_address,
        user_agent=user_agent,
        resource_type="tax_wfh",
        resource_id=None,
        details={"fy_year": fy_year, "format": "csv"},
        severity=Severity.INFO
    )

    # Return CSV file
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=wfh_fy{fy_year}.csv"
        }
    )


@router.get("/export/fy/{fy_year}/text")
async def export_fy_text(
    request: Request,
    fy_year: int,
    rate_per_hour: Annotated[Decimal, Query(description="Rate per hour for deduction calculation")] = Decimal("0.67"),
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Export financial year WFH entries to plain text format

    Returns ATO-compliant text file for tax lodgement.
    """
    # Generate text
    text_content = TaxWFHService.export_fy_to_text(db, current_user.id, fy_year, rate_per_hour)

    # Log audit event
    ip_address, user_agent = get_client_info(request)
    from app.models.audit_log import EventType, Severity
    AuditService.log_event(
        db=db,
        event_type=EventType.TAX_WFH_EXPORT,
        user_id=current_user.id,
        username=current_user.username,
        ip_address=ip_address,
        user_agent=user_agent,
        resource_type="tax_wfh",
        resource_id=None,
        details={"fy_year": fy_year, "format": "text"},
        severity=Severity.INFO
    )

    # Return text file
    return Response(
        content=text_content,
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=wfh_fy{fy_year}.txt"
        }
    )
