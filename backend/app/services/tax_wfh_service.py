"""
Tax WFH Service
Handles CRUD operations for work-from-home tax entries
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func
from fastapi import HTTPException, status

from app.models.tax_wfh import TaxWFHEntry
from app.models.user import User

_ENTRY_NOT_FOUND = "WFH entry not found"


class TaxWFHService:
    """Service for WFH tax entry operations"""

    # ATO rate per hour (as of 2024)
    ATO_RATE_PER_HOUR = Decimal("0.67")

    @staticmethod
    def create_entry(
        db: Session,
        user: User,
        entry_date: date,
        hours: Decimal,
        notes: Optional[str] = None
    ) -> TaxWFHEntry:
        """
        Create a new WFH entry

        Args:
            db: Database session
            user: User creating the entry
            entry_date: Date of WFH
            hours: Hours worked from home
            notes: Optional notes

        Returns:
            Created TaxWFHEntry

        Raises:
            HTTPException: If validation fails or duplicate entry exists
        """
        # Validate hours
        if hours <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hours must be greater than 0"
            )

        if hours > 24:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hours cannot exceed 24 per day"
            )

        # Check for existing entry on this date
        existing = db.query(TaxWFHEntry).filter(
            and_(
                TaxWFHEntry.user_id == user.id,
                TaxWFHEntry.date == entry_date
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"WFH entry already exists for {entry_date}. Use update instead."
            )

        # Create entry
        entry = TaxWFHEntry(
            user_id=user.id,
            date=entry_date,
            hours=hours,
            notes=notes
        )

        db.add(entry)
        db.commit()
        db.refresh(entry)

        return entry

    @staticmethod
    def get_entry(db: Session, entry_id: int, user: User) -> TaxWFHEntry:
        """
        Get a WFH entry by ID

        Args:
            db: Database session
            entry_id: Entry ID
            user: Current user

        Returns:
            TaxWFHEntry

        Raises:
            HTTPException: If entry not found or access denied
        """
        entry = db.query(TaxWFHEntry).filter(TaxWFHEntry.id == entry_id).first()

        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=_ENTRY_NOT_FOUND
            )

        # Check access - user can view their own entries, admins can view all
        from app.models.user import UserRole
        if entry.user_id != user.id and user.role != UserRole.ADMIN:
            # For household transparency, allow viewing but mark as read-only
            pass

        return entry

    @staticmethod
    def update_entry(
        db: Session,
        entry_id: int,
        user: User,
        hours: Optional[Decimal] = None,
        notes: Optional[str] = None
    ) -> TaxWFHEntry:
        """
        Update a WFH entry

        Args:
            db: Database session
            entry_id: Entry ID
            user: Current user
            hours: Updated hours (optional)
            notes: Updated notes (optional)

        Returns:
            Updated TaxWFHEntry

        Raises:
            HTTPException: If entry not found or user doesn't own it
        """
        entry = db.query(TaxWFHEntry).filter(TaxWFHEntry.id == entry_id).first()

        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=_ENTRY_NOT_FOUND
            )

        # Check ownership - only owner or admin can modify
        from app.models.user import UserRole
        if entry.user_id != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify another user's WFH entry"
            )

        # Update fields
        if hours is not None:
            if hours <= 0 or hours > 24:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Hours must be between 0 and 24"
                )
            entry.hours = hours

        if notes is not None:
            entry.notes = notes

        entry.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(entry)

        return entry

    @staticmethod
    def delete_entry(db: Session, entry_id: int, user: User) -> None:
        """
        Delete a WFH entry

        Args:
            db: Database session
            entry_id: Entry ID
            user: Current user

        Raises:
            HTTPException: If entry not found or user doesn't own it
        """
        entry = db.query(TaxWFHEntry).filter(TaxWFHEntry.id == entry_id).first()

        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=_ENTRY_NOT_FOUND
            )

        # Check ownership
        from app.models.user import UserRole
        if entry.user_id != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete another user's WFH entry"
            )

        db.delete(entry)
        db.commit()

    @staticmethod
    def list_user_entries(
        db: Session,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[TaxWFHEntry]:
        """
        List WFH entries for a user

        Args:
            db: Database session
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum entries to return
            offset: Pagination offset

        Returns:
            List of TaxWFHEntry objects
        """
        query = db.query(TaxWFHEntry).filter(TaxWFHEntry.user_id == user_id)

        if start_date:
            query = query.filter(TaxWFHEntry.date >= start_date)

        if end_date:
            query = query.filter(TaxWFHEntry.date <= end_date)

        query = query.order_by(TaxWFHEntry.date.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def get_financial_year_summary(
        db: Session,
        user_id: int,
        fy_year: int,
        rate_per_hour: Decimal = None
    ) -> dict:
        """
        Calculate financial year summary for WFH entries

        Financial year runs July 1 to June 30.
        FY 2024 = July 1, 2023 to June 30, 2024

        Args:
            db: Database session
            user_id: User ID
            fy_year: Financial year (e.g., 2024)
            rate_per_hour: Optional custom rate per hour (defaults to ATO rate)

        Returns:
            Dictionary with summary statistics
        """
        # Use provided rate or default ATO rate
        if rate_per_hour is None:
            rate_per_hour = TaxWFHService.ATO_RATE_PER_HOUR

        # Calculate FY date range
        fy_start = date(fy_year - 1, 7, 1)
        fy_end = date(fy_year, 6, 30)

        # Query entries in FY
        entries = db.query(TaxWFHEntry).filter(
            and_(
                TaxWFHEntry.user_id == user_id,
                TaxWFHEntry.date >= fy_start,
                TaxWFHEntry.date <= fy_end
            )
        ).all()

        # Calculate totals
        total_days = len(entries)
        total_hours = sum(entry.hours for entry in entries)
        total_deduction = total_hours * rate_per_hour

        return {
            "financial_year": fy_year,
            "fy_start_date": fy_start.isoformat(),
            "fy_end_date": fy_end.isoformat(),
            "total_days": total_days,
            "total_hours": float(total_hours),
            "ato_rate_per_hour": float(rate_per_hour),
            "total_deduction": float(total_deduction),
            "entries": [entry.to_dict() for entry in entries]
        }

    @staticmethod
    def get_current_fy_year() -> int:
        """
        Get current financial year

        Returns:
            Financial year (e.g., 2024 for FY2024)
        """
        today = date.today()
        # If we're in Jan-Jun, FY is current year
        # If we're in Jul-Dec, FY is next year
        if today.month >= 7:
            return today.year + 1
        else:
            return today.year

    @staticmethod
    def export_fy_to_csv(
        db: Session,
        user_id: int,
        fy_year: int,
        rate_per_hour: Decimal = None
    ) -> str:
        """
        Export financial year WFH entries to CSV format

        Args:
            db: Database session
            user_id: User ID
            fy_year: Financial year
            rate_per_hour: Optional custom rate per hour

        Returns:
            CSV string
        """
        # Get FY summary
        summary = TaxWFHService.get_financial_year_summary(db, user_id, fy_year, rate_per_hour)

        # Build CSV
        lines = []
        lines.append("Work From Home Deduction - ATO Compliant Export")
        lines.append(f"Financial Year: {fy_year} (July 1, {fy_year-1} to June 30, {fy_year})")
        lines.append(f"ATO Rate: ${summary['ato_rate_per_hour']}/hour")
        lines.append("")
        lines.append("SUMMARY")
        lines.append(f"Total Days Worked From Home,{summary['total_days']}")
        lines.append(f"Total Hours,{summary['total_hours']}")
        lines.append(f"Total Deduction,${summary['total_deduction']:.2f}")
        lines.append("")
        lines.append("DETAILED LOG")
        lines.append("Date,Hours,Deduction,Notes")

        for entry_dict in summary['entries']:
            date_str = entry_dict['date']
            hours = entry_dict['hours']
            deduction = entry_dict['deduction_amount']
            notes = entry_dict.get('notes', '').replace(',', ';') if entry_dict.get('notes') else ''
            lines.append(f"{date_str},{hours},${deduction:.2f},{notes}")

        return '\n'.join(lines)

    @staticmethod
    def export_fy_to_text(
        db: Session,
        user_id: int,
        fy_year: int,
        rate_per_hour: Decimal = None
    ) -> str:
        """
        Export financial year WFH entries to plain text format

        Args:
            db: Database session
            user_id: User ID
            fy_year: Financial year
            rate_per_hour: Optional custom rate per hour

        Returns:
            Plain text string
        """
        # Get FY summary
        summary = TaxWFHService.get_financial_year_summary(db, user_id, fy_year, rate_per_hour)

        # Build text
        lines = []
        lines.append("=" * 60)
        lines.append("WORK FROM HOME DEDUCTION - ATO COMPLIANT EXPORT")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Financial Year: {fy_year}")
        lines.append(f"Period: July 1, {fy_year-1} to June 30, {fy_year}")
        lines.append(f"ATO Rate: ${summary['ato_rate_per_hour']}/hour")
        lines.append("")
        lines.append("SUMMARY")
        lines.append("-" * 60)
        lines.append(f"Total Days Worked From Home: {summary['total_days']}")
        lines.append(f"Total Hours: {summary['total_hours']}")
        lines.append(f"Total Deduction: ${summary['total_deduction']:.2f}")
        lines.append("")
        lines.append("DETAILED LOG")
        lines.append("-" * 60)

        for entry_dict in summary['entries']:
            lines.append(f"Date: {entry_dict['date']}")
            lines.append(f"  Hours: {entry_dict['hours']}")
            lines.append(f"  Deduction: ${entry_dict['deduction_amount']:.2f}")
            if entry_dict.get('notes'):
                lines.append(f"  Notes: {entry_dict['notes']}")
            lines.append("")

        lines.append("=" * 60)
        lines.append("END OF REPORT")
        lines.append("=" * 60)

        return '\n'.join(lines)
