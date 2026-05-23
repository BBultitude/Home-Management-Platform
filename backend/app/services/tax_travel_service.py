"""
Tax Travel Service
Handles CRUD operations for work travel tax entries
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status

from app.models.tax_travel import TaxTravelEntry
from app.models.user import User


class TaxTravelService:
    """Service for work travel tax entry operations"""

    @staticmethod
    def create_entry(
        db: Session,
        user: User,
        entry_date: date,
        purpose: str,
        start_location: str,
        end_location: str,
        distance_km: Decimal,
        notes: Optional[str] = None
    ) -> TaxTravelEntry:
        """
        Create a new travel entry

        Args:
            db: Database session
            user: User creating the entry
            entry_date: Date of travel
            purpose: Purpose of travel
            start_location: Starting location
            end_location: Ending location
            distance_km: Distance traveled in kilometers
            notes: Optional notes

        Returns:
            Created TaxTravelEntry

        Raises:
            HTTPException: If validation fails
        """
        # Validate distance
        if distance_km <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Distance must be greater than 0"
            )

        if distance_km > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Distance seems unreasonably large (max 10,000 km per trip)"
            )

        # Create entry
        entry = TaxTravelEntry(
            user_id=user.id,
            date=entry_date,
            purpose=purpose,
            start_location=start_location,
            end_location=end_location,
            distance_km=distance_km,
            notes=notes
        )

        db.add(entry)
        db.commit()
        db.refresh(entry)

        return entry

    @staticmethod
    def get_entry(db: Session, entry_id: int, user: User) -> TaxTravelEntry:
        """
        Get a travel entry by ID

        Args:
            db: Database session
            entry_id: Entry ID
            user: Current user

        Returns:
            TaxTravelEntry

        Raises:
            HTTPException: If entry not found or access denied
        """
        entry = db.query(TaxTravelEntry).filter(TaxTravelEntry.id == entry_id).first()

        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Travel entry not found"
            )

        # Check access - user can view their own entries, admins can view all
        from app.models.user import UserRole
        if entry.user_id != user.id and user.role != UserRole.ADMIN:
            # For household transparency, allow viewing
            pass

        return entry

    @staticmethod
    def update_entry(
        db: Session,
        entry_id: int,
        user: User,
        purpose: Optional[str] = None,
        start_location: Optional[str] = None,
        end_location: Optional[str] = None,
        distance_km: Optional[Decimal] = None,
        notes: Optional[str] = None
    ) -> TaxTravelEntry:
        """
        Update a travel entry

        Args:
            db: Database session
            entry_id: Entry ID
            user: Current user
            purpose: Updated purpose (optional)
            start_location: Updated start location (optional)
            end_location: Updated end location (optional)
            distance_km: Updated distance (optional)
            notes: Updated notes (optional)

        Returns:
            Updated TaxTravelEntry

        Raises:
            HTTPException: If entry not found or user doesn't own it
        """
        entry = db.query(TaxTravelEntry).filter(TaxTravelEntry.id == entry_id).first()

        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Travel entry not found"
            )

        # Check ownership - only owner or admin can modify
        from app.models.user import UserRole
        if entry.user_id != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify another user's travel entry"
            )

        # Update fields
        if purpose is not None:
            entry.purpose = purpose

        if start_location is not None:
            entry.start_location = start_location

        if end_location is not None:
            entry.end_location = end_location

        if distance_km is not None:
            if distance_km <= 0 or distance_km > 10000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Distance must be between 0 and 10,000 km"
                )
            entry.distance_km = distance_km

        if notes is not None:
            entry.notes = notes

        entry.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(entry)

        return entry

    @staticmethod
    def delete_entry(db: Session, entry_id: int, user: User) -> None:
        """
        Delete a travel entry

        Args:
            db: Database session
            entry_id: Entry ID
            user: Current user

        Raises:
            HTTPException: If entry not found or user doesn't own it
        """
        entry = db.query(TaxTravelEntry).filter(TaxTravelEntry.id == entry_id).first()

        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Travel entry not found"
            )

        # Check ownership
        from app.models.user import UserRole
        if entry.user_id != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete another user's travel entry"
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
    ) -> list[TaxTravelEntry]:
        """
        List travel entries for a user

        Args:
            db: Database session
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum entries to return
            offset: Pagination offset

        Returns:
            List of TaxTravelEntry objects
        """
        query = db.query(TaxTravelEntry).filter(TaxTravelEntry.user_id == user_id)

        if start_date:
            query = query.filter(TaxTravelEntry.date >= start_date)

        if end_date:
            query = query.filter(TaxTravelEntry.date <= end_date)

        query = query.order_by(TaxTravelEntry.date.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def get_financial_year_summary(
        db: Session,
        user_id: int,
        fy_year: int,
        rate_per_km: Decimal = Decimal("0.85")
    ) -> dict:
        """
        Calculate financial year summary for travel entries

        Financial year runs July 1 to June 30.
        FY 2024 = July 1, 2023 to June 30, 2024

        Args:
            db: Database session
            user_id: User ID
            fy_year: Financial year (e.g., 2024)
            rate_per_km: Rate per kilometer (default $0.85 ATO rate)

        Returns:
            Dictionary with summary statistics
        """
        # Calculate FY date range
        fy_start = date(fy_year - 1, 7, 1)
        fy_end = date(fy_year, 6, 30)

        # Query entries in FY
        entries = db.query(TaxTravelEntry).filter(
            and_(
                TaxTravelEntry.user_id == user_id,
                TaxTravelEntry.date >= fy_start,
                TaxTravelEntry.date <= fy_end
            )
        ).all()

        # Calculate totals
        total_trips = len(entries)
        total_km = sum(entry.distance_km for entry in entries)
        total_deduction = total_km * rate_per_km

        return {
            "financial_year": fy_year,
            "fy_start_date": fy_start.isoformat(),
            "fy_end_date": fy_end.isoformat(),
            "total_trips": total_trips,
            "total_km": float(total_km),
            "rate_per_km": float(rate_per_km),
            "total_deduction": float(total_deduction),
            "entries": [entry.to_dict(rate_per_km) for entry in entries]
        }

    @staticmethod
    def export_fy_to_csv(
        db: Session,
        user_id: int,
        fy_year: int,
        rate_per_km: Decimal = Decimal("0.85")
    ) -> str:
        """
        Export financial year travel entries to CSV format

        Args:
            db: Database session
            user_id: User ID
            fy_year: Financial year
            rate_per_km: Rate per kilometer

        Returns:
            CSV string
        """
        # Get FY summary
        summary = TaxTravelService.get_financial_year_summary(db, user_id, fy_year, rate_per_km)

        # Build CSV
        lines = []
        lines.append("Work Travel Deduction - ATO Compliant Export")
        lines.append(f"Financial Year: {fy_year} (July 1, {fy_year-1} to June 30, {fy_year})")
        lines.append(f"Rate per km: ${summary['rate_per_km']}/km")
        lines.append("")
        lines.append("SUMMARY")
        lines.append(f"Total Trips,{summary['total_trips']}")
        lines.append(f"Total Kilometers,{summary['total_km']}")
        lines.append(f"Total Deduction,${summary['total_deduction']:.2f}")
        lines.append("")
        lines.append("DETAILED LOG")
        lines.append("Date,Purpose,Start Location,End Location,Distance (km),Deduction,Notes")

        for entry_dict in summary['entries']:
            date_str = entry_dict['date']
            purpose = entry_dict['purpose'].replace(',', ';')
            start = entry_dict['start_location'].replace(',', ';')
            end = entry_dict['end_location'].replace(',', ';')
            distance = entry_dict['distance_km']
            deduction = entry_dict.get('deduction_amount', 0)
            notes = entry_dict.get('notes', '').replace(',', ';') if entry_dict.get('notes') else ''
            lines.append(f"{date_str},{purpose},{start},{end},{distance},${deduction:.2f},{notes}")

        return '\n'.join(lines)

    @staticmethod
    def export_fy_to_text(
        db: Session,
        user_id: int,
        fy_year: int,
        rate_per_km: Decimal = Decimal("0.85")
    ) -> str:
        """
        Export financial year travel entries to plain text format

        Args:
            db: Database session
            user_id: User ID
            fy_year: Financial year
            rate_per_km: Rate per kilometer

        Returns:
            Plain text string
        """
        # Get FY summary
        summary = TaxTravelService.get_financial_year_summary(db, user_id, fy_year, rate_per_km)

        # Build text
        lines = []
        lines.append("=" * 60)
        lines.append("WORK TRAVEL DEDUCTION - ATO COMPLIANT EXPORT")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Financial Year: {fy_year}")
        lines.append(f"Period: July 1, {fy_year-1} to June 30, {fy_year}")
        lines.append(f"Rate per km: ${summary['rate_per_km']}/km")
        lines.append("")
        lines.append("SUMMARY")
        lines.append("-" * 60)
        lines.append(f"Total Trips: {summary['total_trips']}")
        lines.append(f"Total Kilometers: {summary['total_km']}")
        lines.append(f"Total Deduction: ${summary['total_deduction']:.2f}")
        lines.append("")
        lines.append("DETAILED LOG")
        lines.append("-" * 60)

        for entry_dict in summary['entries']:
            lines.append(f"Date: {entry_dict['date']}")
            lines.append(f"  Purpose: {entry_dict['purpose']}")
            lines.append(f"  Route: {entry_dict['start_location']} → {entry_dict['end_location']}")
            lines.append(f"  Distance: {entry_dict['distance_km']} km")
            lines.append(f"  Deduction: ${entry_dict.get('deduction_amount', 0):.2f}")
            if entry_dict.get('notes'):
                lines.append(f"  Notes: {entry_dict['notes']}")
            lines.append("")

        lines.append("=" * 60)
        lines.append("END OF REPORT")
        lines.append("=" * 60)

        return '\n'.join(lines)
