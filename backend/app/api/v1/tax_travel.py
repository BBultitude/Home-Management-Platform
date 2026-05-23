"""
Tax Travel Entry API endpoints
"""

from datetime import date
from decimal import Decimal
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db, require_permission
from app.models.user import User
from app.services.tax_travel_service import TaxTravelService
from app.services.audit_service import AuditService
from app.schemas.tax_travel import (
    TaxTravelEntryCreate,
    TaxTravelEntryUpdate,
    TaxTravelEntryResponse,
    TaxTravelEntryListResponse,
    TaxTravelDeleteResponse,
    TaxTravelFYSummaryResponse
)


router = APIRouter(prefix="/tax/travel", tags=["tax-travel"])

# Default ATO rate per km
DEFAULT_RATE_PER_KM = Decimal("0.85")


def get_client_info(request: Request) -> tuple[str, str]:
    """Extract IP address and user agent from request"""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    return ip_address, user_agent


@router.post("", response_model=TaxTravelEntryResponse)
async def create_travel_entry(
    request: Request,
    entry_data: TaxTravelEntryCreate,
    rate_per_km: Annotated[Decimal, Query(DEFAULT_RATE_PER_KM, description="Rate per kilometer for deduction calculation")],
    current_user: Annotated[User, Depends(require_permission("tax:create"))],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Create a new travel entry

    Requires permission: tax:create
    """
    # Create entry
    entry = TaxTravelService.create_entry(
        db=db,
        user=current_user,
        entry_date=entry_data.date,
        purpose=entry_data.purpose,
        start_location=entry_data.start_location,
        end_location=entry_data.end_location,
        distance_km=entry_data.distance_km,
        notes=entry_data.notes
    )

    # Log audit event
    ip_address, user_agent = get_client_info(request)
    AuditService.log_tax_travel_create(
        db=db,
        user=current_user,
        ip_address=ip_address,
        user_agent=user_agent,
        tax_id=entry.id,
        details={
            "date": entry.date.isoformat(),
            "purpose": entry.purpose,
            "distance_km": float(entry.distance_km),
            "deduction": float(entry.calculate_deduction(rate_per_km))
        }
    )

    return TaxTravelEntryResponse(
        id=entry.id,
        user_id=entry.user_id,
        date=entry.date,
        purpose=entry.purpose,
        start_location=entry.start_location,
        end_location=entry.end_location,
        distance_km=float(entry.distance_km),
        notes=entry.notes,
        deduction_amount=float(entry.calculate_deduction(rate_per_km)),
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )


@router.get("", response_model=TaxTravelEntryListResponse)
async def list_travel_entries(
    start_date: Annotated[Optional[date], Query(None)],
    end_date: Annotated[Optional[date], Query(None)],
    rate_per_km: Annotated[Decimal, Query(DEFAULT_RATE_PER_KM, description="Rate per kilometer for deduction calculation")],
    limit: Annotated[int, Query(100, ge=1, le=500)],
    offset: Annotated[int, Query(0, ge=0)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    List current user's travel entries

    Optionally filter by date range.
    """
    entries = TaxTravelService.list_user_entries(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )

    entry_responses = [
        TaxTravelEntryResponse(
            id=e.id,
            user_id=e.user_id,
            date=e.date,
            purpose=e.purpose,
            start_location=e.start_location,
            end_location=e.end_location,
            distance_km=float(e.distance_km),
            notes=e.notes,
            deduction_amount=float(e.calculate_deduction(rate_per_km)),
            created_at=e.created_at,
            updated_at=e.updated_at
        )
        for e in entries
    ]

    return TaxTravelEntryListResponse(
        entries=entry_responses,
        total=len(entries),
        start_date=start_date,
        end_date=end_date
    )


@router.get("/users/{user_id}", response_model=TaxTravelEntryListResponse)
async def list_user_travel_entries(
    user_id: int,
    start_date: Annotated[Optional[date], Query(None)],
    end_date: Annotated[Optional[date], Query(None)],
    rate_per_km: Annotated[Decimal, Query(DEFAULT_RATE_PER_KM, description="Rate per kilometer for deduction calculation")],
    limit: Annotated[int, Query(100, ge=1, le=500)],
    offset: Annotated[int, Query(0, ge=0)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    List another user's travel entries (household transparency)

    All authenticated users can view other users' entries (read-only).
    """
    entries = TaxTravelService.list_user_entries(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )

    entry_responses = [
        TaxTravelEntryResponse(
            id=e.id,
            user_id=e.user_id,
            date=e.date,
            purpose=e.purpose,
            start_location=e.start_location,
            end_location=e.end_location,
            distance_km=float(e.distance_km),
            notes=e.notes,
            deduction_amount=float(e.calculate_deduction(rate_per_km)),
            created_at=e.created_at,
            updated_at=e.updated_at
        )
        for e in entries
    ]

    return TaxTravelEntryListResponse(
        entries=entry_responses,
        total=len(entries),
        start_date=start_date,
        end_date=end_date
    )


@router.get("/{entry_id}", response_model=TaxTravelEntryResponse)
async def get_travel_entry(
    entry_id: int,
    rate_per_km: Annotated[Decimal, Query(DEFAULT_RATE_PER_KM, description="Rate per kilometer for deduction calculation")],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get a specific travel entry

    Users can view their own entries and other users' entries (household transparency).
    """
    entry = TaxTravelService.get_entry(db, entry_id, current_user)

    return TaxTravelEntryResponse(
        id=entry.id,
        user_id=entry.user_id,
        date=entry.date,
        purpose=entry.purpose,
        start_location=entry.start_location,
        end_location=entry.end_location,
        distance_km=float(entry.distance_km),
        notes=entry.notes,
        deduction_amount=float(entry.calculate_deduction(rate_per_km)),
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )


@router.put("/{entry_id}", response_model=TaxTravelEntryResponse)
async def update_travel_entry(
    request: Request,
    entry_id: int,
    entry_data: TaxTravelEntryUpdate,
    rate_per_km: Annotated[Decimal, Query(DEFAULT_RATE_PER_KM, description="Rate per kilometer for deduction calculation")],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Update a travel entry

    Only the owner or admin can update an entry.
    """
    # Update entry
    entry = TaxTravelService.update_entry(
        db=db,
        entry_id=entry_id,
        user=current_user,
        purpose=entry_data.purpose,
        start_location=entry_data.start_location,
        end_location=entry_data.end_location,
        distance_km=entry_data.distance_km,
        notes=entry_data.notes
    )

    # Log audit event
    ip_address, user_agent = get_client_info(request)
    changes = {}
    if entry_data.purpose is not None:
        changes["purpose"] = entry_data.purpose
    if entry_data.start_location is not None:
        changes["start_location"] = entry_data.start_location
    if entry_data.end_location is not None:
        changes["end_location"] = entry_data.end_location
    if entry_data.distance_km is not None:
        changes["distance_km"] = float(entry_data.distance_km)
    if entry_data.notes is not None:
        changes["notes"] = entry_data.notes

    from app.models.audit_log import EventType, Severity
    AuditService.log_event(
        db=db,
        event_type=EventType.TAX_TRAVEL_UPDATE,
        user_id=current_user.id,
        username=current_user.username,
        ip_address=ip_address,
        user_agent=user_agent,
        resource_type="tax_travel",
        resource_id=entry.id,
        details={"changes": changes},
        severity=Severity.INFO
    )

    return TaxTravelEntryResponse(
        id=entry.id,
        user_id=entry.user_id,
        date=entry.date,
        purpose=entry.purpose,
        start_location=entry.start_location,
        end_location=entry.end_location,
        distance_km=float(entry.distance_km),
        notes=entry.notes,
        deduction_amount=float(entry.calculate_deduction(rate_per_km)),
        created_at=entry.created_at,
        updated_at=entry.updated_at
    )


@router.delete("/{entry_id}", response_model=TaxTravelDeleteResponse)
async def delete_travel_entry(
    request: Request,
    entry_id: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Delete a travel entry

    Only the owner or admin can delete an entry.
    """
    # Get entry for audit logging (before deletion)
    entry = TaxTravelService.get_entry(db, entry_id, current_user)
    entry_date = entry.date
    entry_distance = entry.distance_km

    # Delete entry
    TaxTravelService.delete_entry(db, entry_id, current_user)

    # Log audit event
    ip_address, user_agent = get_client_info(request)
    from app.models.audit_log import EventType, Severity
    AuditService.log_event(
        db=db,
        event_type=EventType.TAX_TRAVEL_DELETE,
        user_id=current_user.id,
        username=current_user.username,
        ip_address=ip_address,
        user_agent=user_agent,
        resource_type="tax_travel",
        resource_id=entry_id,
        details={
            "date": entry_date.isoformat(),
            "distance_km": float(entry_distance)
        },
        severity=Severity.WARNING
    )

    return TaxTravelDeleteResponse(
        message="Travel entry deleted successfully",
        entry_id=entry_id
    )


@router.get("/summary/fy/{fy_year}", response_model=TaxTravelFYSummaryResponse)
async def get_fy_summary(
    fy_year: int,
    rate_per_km: Annotated[Decimal, Query(DEFAULT_RATE_PER_KM, description="Rate per kilometer for deduction calculation")],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get financial year summary for current user's travel entries

    Financial year runs July 1 to June 30.
    FY 2024 = July 1, 2023 to June 30, 2024
    """
    summary = TaxTravelService.get_financial_year_summary(
        db=db,
        user_id=current_user.id,
        fy_year=fy_year,
        rate_per_km=rate_per_km
    )

    return TaxTravelFYSummaryResponse(**summary)


@router.get("/export/fy/{fy_year}/csv")
async def export_fy_csv(
    request: Request,
    fy_year: int,
    rate_per_km: Annotated[Decimal, Query(DEFAULT_RATE_PER_KM, description="Rate per kilometer for deduction calculation")],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Export financial year travel entries to CSV format

    Returns ATO-compliant CSV file for tax lodgement.
    """
    # Generate CSV
    csv_content = TaxTravelService.export_fy_to_csv(db, current_user.id, fy_year, rate_per_km)

    # Log audit event
    ip_address, user_agent = get_client_info(request)
    from app.models.audit_log import EventType, Severity
    AuditService.log_event(
        db=db,
        event_type=EventType.TAX_TRAVEL_EXPORT,
        user_id=current_user.id,
        username=current_user.username,
        ip_address=ip_address,
        user_agent=user_agent,
        resource_type="tax_travel",
        resource_id=None,
        details={"fy_year": fy_year, "format": "csv", "rate_per_km": float(rate_per_km)},
        severity=Severity.INFO
    )

    # Return CSV file
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=travel_fy{fy_year}.csv"
        }
    )


@router.get("/export/fy/{fy_year}/text")
async def export_fy_text(
    request: Request,
    fy_year: int,
    rate_per_km: Annotated[Decimal, Query(DEFAULT_RATE_PER_KM, description="Rate per kilometer for deduction calculation")],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Export financial year travel entries to plain text format

    Returns ATO-compliant text file for tax lodgement.
    """
    # Generate text
    text_content = TaxTravelService.export_fy_to_text(db, current_user.id, fy_year, rate_per_km)

    # Log audit event
    ip_address, user_agent = get_client_info(request)
    from app.models.audit_log import EventType, Severity
    AuditService.log_event(
        db=db,
        event_type=EventType.TAX_TRAVEL_EXPORT,
        user_id=current_user.id,
        username=current_user.username,
        ip_address=ip_address,
        user_agent=user_agent,
        resource_type="tax_travel",
        resource_id=None,
        details={"fy_year": fy_year, "format": "text", "rate_per_km": float(rate_per_km)},
        severity=Severity.INFO
    )

    # Return text file
    return Response(
        content=text_content,
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=travel_fy{fy_year}.txt"
        }
    )
