"""
Tests for Tax WFH service
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.tax_wfh_service import TaxWFHService
from app.models.tax_wfh import TaxWFHEntry
from app.models.user import User, UserRole

TEST_HASHED_PASSWORD = "hashed"  # Test-only placeholder for hashed_password field


class TestCreateEntry:
    """Test creating WFH entries"""

    def test_create_entry_success(self, test_db: Session, test_user: User):
        """Successfully create a WFH entry"""
        entry = TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            hours=Decimal("8.00"),
            notes="Full day from home"
        )

        assert entry.id is not None
        assert entry.user_id == test_user.id
        assert entry.date == date(2024, 1, 15)
        assert entry.hours == Decimal("8.00")
        assert entry.notes == "Full day from home"
        assert entry.deduction_amount == Decimal("5.36")  # 8 * 0.67

    def test_create_entry_invalid_hours_zero(self, test_db: Session, test_user: User):
        """Cannot create entry with zero hours"""
        with pytest.raises(HTTPException) as exc_info:
            TaxWFHService.create_entry(
                db=test_db,
                user=test_user,
                entry_date=date(2024, 1, 15),
                hours=Decimal("0"),
                notes=None
            )
        assert exc_info.value.status_code == 400
        assert "greater than 0" in exc_info.value.detail

    def test_create_entry_invalid_hours_exceeds_24(self, test_db: Session, test_user: User):
        """Cannot create entry with more than 24 hours"""
        with pytest.raises(HTTPException) as exc_info:
            TaxWFHService.create_entry(
                db=test_db,
                user=test_user,
                entry_date=date(2024, 1, 15),
                hours=Decimal("25"),
                notes=None
            )
        assert exc_info.value.status_code == 400
        assert "cannot exceed 24" in exc_info.value.detail

    def test_create_entry_duplicate_date(self, test_db: Session, test_user: User):
        """Cannot create duplicate entry for same date"""
        # Create first entry
        TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )

        # Try to create duplicate
        with pytest.raises(HTTPException) as exc_info:
            TaxWFHService.create_entry(
                db=test_db,
                user=test_user,
                entry_date=date(2024, 1, 15),
                hours=Decimal("4.00")
            )
        assert exc_info.value.status_code == 409
        assert "already exists" in exc_info.value.detail


class TestGetEntry:
    """Test getting WFH entries"""

    def test_get_entry_owner(self, test_db: Session, test_user: User):
        """Owner can get their entry"""
        # Create entry
        entry = TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )

        # Get entry
        retrieved = TaxWFHService.get_entry(test_db, entry.id, test_user)
        assert retrieved.id == entry.id
        assert retrieved.user_id == test_user.id

    def test_get_entry_not_found(self, test_db: Session, test_user: User):
        """Get non-existent entry returns 404"""
        with pytest.raises(HTTPException) as exc_info:
            TaxWFHService.get_entry(test_db, 99999, test_user)
        assert exc_info.value.status_code == 404


class TestUpdateEntry:
    """Test updating WFH entries"""

    def test_update_entry_hours(self, test_db: Session, test_user: User):
        """Successfully update entry hours"""
        # Create entry
        entry = TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )

        # Update hours
        updated = TaxWFHService.update_entry(
            db=test_db,
            entry_id=entry.id,
            user=test_user,
            hours=Decimal("6.50")
        )

        assert updated.hours == Decimal("6.50")
        assert updated.deduction_amount == Decimal("4.355")  # 6.5 * 0.67

    def test_update_entry_notes(self, test_db: Session, test_user: User):
        """Successfully update entry notes"""
        # Create entry
        entry = TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )

        # Update notes
        updated = TaxWFHService.update_entry(
            db=test_db,
            entry_id=entry.id,
            user=test_user,
            notes="Updated notes"
        )

        assert updated.notes == "Updated notes"

    def test_update_entry_not_owner(self, test_db: Session, test_user: User):
        """Non-owner cannot update entry"""
        # Create entry as test_user
        entry = TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )

        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=TEST_HASHED_PASSWORD,
            full_name="Other User",
            role=UserRole.READER
        )
        test_db.add(other_user)
        test_db.commit()

        # Try to update as other user
        with pytest.raises(HTTPException) as exc_info:
            TaxWFHService.update_entry(
                db=test_db,
                entry_id=entry.id,
                user=other_user,
                hours=Decimal("4.00")
            )
        assert exc_info.value.status_code == 403


class TestDeleteEntry:
    """Test deleting WFH entries"""

    def test_delete_entry_success(self, test_db: Session, test_user: User):
        """Successfully delete entry"""
        # Create entry
        entry = TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )
        entry_id = entry.id

        # Delete entry
        TaxWFHService.delete_entry(test_db, entry_id, test_user)

        # Verify deleted
        deleted = test_db.query(TaxWFHEntry).filter(TaxWFHEntry.id == entry_id).first()
        assert deleted is None

    def test_delete_entry_not_owner(self, test_db: Session, test_user: User):
        """Non-owner cannot delete entry"""
        # Create entry
        entry = TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )

        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password=TEST_HASHED_PASSWORD,
            full_name="Other User",
            role=UserRole.READER
        )
        test_db.add(other_user)
        test_db.commit()

        # Try to delete as other user
        with pytest.raises(HTTPException) as exc_info:
            TaxWFHService.delete_entry(test_db, entry.id, other_user)
        assert exc_info.value.status_code == 403


class TestListEntries:
    """Test listing WFH entries"""

    def test_list_user_entries(self, test_db: Session, test_user: User):
        """List user's entries"""
        # Create multiple entries
        TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )
        TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 16),
            hours=Decimal("6.50")
        )

        # List entries
        entries = TaxWFHService.list_user_entries(test_db, test_user.id)
        assert len(entries) == 2

    def test_list_with_date_filter(self, test_db: Session, test_user: User):
        """List entries with date filter"""
        # Create entries
        TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )
        TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 20),
            hours=Decimal("6.50")
        )
        TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 25),
            hours=Decimal("7.00")
        )

        # Filter by date range
        entries = TaxWFHService.list_user_entries(
            test_db,
            test_user.id,
            start_date=date(2024, 1, 18),
            end_date=date(2024, 1, 22)
        )
        assert len(entries) == 1
        assert entries[0].date == date(2024, 1, 20)


class TestFYSummary:
    """Test financial year summary"""

    def test_fy_summary_calculation(self, test_db: Session, test_user: User):
        """Calculate FY summary correctly"""
        # Create entries in FY2024 (July 1, 2023 to June 30, 2024)
        TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2023, 7, 15),
            hours=Decimal("8.00")
        )
        TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2023, 12, 10),
            hours=Decimal("6.50")
        )
        TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 3, 20),
            hours=Decimal("7.00")
        )

        # Get FY2024 summary
        summary = TaxWFHService.get_financial_year_summary(
            test_db,
            test_user.id,
            fy_year=2024
        )

        assert summary["financial_year"] == 2024
        assert summary["total_days"] == 3
        assert summary["total_hours"] == pytest.approx(21.5)  # 8 + 6.5 + 7
        assert summary["total_deduction"] == pytest.approx(14.405, rel=0.01)  # 21.5 * 0.67

    def test_fy_summary_excludes_other_years(self, test_db: Session, test_user: User):
        """FY summary only includes entries in that FY"""
        # Create entry in FY2023
        TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2023, 3, 15),
            hours=Decimal("8.00")
        )

        # Create entry in FY2024
        TaxWFHService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2023, 7, 15),
            hours=Decimal("6.00")
        )

        # Get FY2024 summary
        summary = TaxWFHService.get_financial_year_summary(
            test_db,
            test_user.id,
            fy_year=2024
        )

        assert summary["total_days"] == 1
        assert summary["total_hours"] == pytest.approx(6.0)

    def test_get_current_fy_year(self):
        """Get current FY year correctly"""
        # This test depends on current date
        # Just verify it returns an integer year
        fy_year = TaxWFHService.get_current_fy_year()
        assert isinstance(fy_year, int)
        assert fy_year >= 2024
