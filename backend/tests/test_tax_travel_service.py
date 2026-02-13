"""
Tests for Tax Travel service
"""

import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.services.tax_travel_service import TaxTravelService
from app.models.tax_travel import TaxTravelEntry
from app.models.user import User, UserRole


class TestCreateEntry:
    """Test creating travel entries"""

    def test_create_entry_success(self, test_db: Session, test_user: User):
        """Successfully create a travel entry"""
        entry = TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            purpose="Client meeting",
            start_location="Office",
            end_location="Client site",
            distance_km=Decimal("45.5"),
            notes="Highway route"
        )

        assert entry.id is not None
        assert entry.user_id == test_user.id
        assert entry.date == date(2024, 1, 15)
        assert entry.purpose == "Client meeting"
        assert entry.distance_km == Decimal("45.5")
        assert entry.notes == "Highway route"

    def test_create_entry_invalid_distance_zero(self, test_db: Session, test_user: User):
        """Cannot create entry with zero distance"""
        with pytest.raises(HTTPException) as exc_info:
            TaxTravelService.create_entry(
                db=test_db,
                user=test_user,
                entry_date=date(2024, 1, 15),
                purpose="Test",
                start_location="A",
                end_location="B",
                distance_km=Decimal("0")
            )
        assert exc_info.value.status_code == 400
        assert "greater than 0" in exc_info.value.detail

    def test_create_entry_invalid_distance_too_large(self, test_db: Session, test_user: User):
        """Cannot create entry with unreasonably large distance"""
        with pytest.raises(HTTPException) as exc_info:
            TaxTravelService.create_entry(
                db=test_db,
                user=test_user,
                entry_date=date(2024, 1, 15),
                purpose="Test",
                start_location="A",
                end_location="B",
                distance_km=Decimal("15000")
            )
        assert exc_info.value.status_code == 400
        assert "unreasonably large" in exc_info.value.detail


class TestGetEntry:
    """Test getting travel entries"""

    def test_get_entry_owner(self, test_db: Session, test_user: User):
        """Owner can get their entry"""
        entry = TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            purpose="Meeting",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )

        retrieved = TaxTravelService.get_entry(test_db, entry.id, test_user)
        assert retrieved.id == entry.id

    def test_get_entry_not_found(self, test_db: Session, test_user: User):
        """Get non-existent entry returns 404"""
        with pytest.raises(HTTPException) as exc_info:
            TaxTravelService.get_entry(test_db, 99999, test_user)
        assert exc_info.value.status_code == 404


class TestUpdateEntry:
    """Test updating travel entries"""

    def test_update_entry_distance(self, test_db: Session, test_user: User):
        """Successfully update entry distance"""
        entry = TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            purpose="Meeting",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )

        updated = TaxTravelService.update_entry(
            db=test_db,
            entry_id=entry.id,
            user=test_user,
            distance_km=Decimal("50.0")
        )

        assert updated.distance_km == Decimal("50.0")

    def test_update_entry_purpose(self, test_db: Session, test_user: User):
        """Successfully update entry purpose"""
        entry = TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            purpose="Meeting",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )

        updated = TaxTravelService.update_entry(
            db=test_db,
            entry_id=entry.id,
            user=test_user,
            purpose="Updated meeting"
        )

        assert updated.purpose == "Updated meeting"

    def test_update_entry_not_owner(self, test_db: Session, test_user: User):
        """Non-owner cannot update entry"""
        entry = TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            purpose="Meeting",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )

        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed",
            full_name="Other User",
            role=UserRole.READER
        )
        test_db.add(other_user)
        test_db.commit()

        with pytest.raises(HTTPException) as exc_info:
            TaxTravelService.update_entry(
                db=test_db,
                entry_id=entry.id,
                user=other_user,
                distance_km=Decimal("100.0")
            )
        assert exc_info.value.status_code == 403


class TestDeleteEntry:
    """Test deleting travel entries"""

    def test_delete_entry_success(self, test_db: Session, test_user: User):
        """Successfully delete entry"""
        entry = TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            purpose="Meeting",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )
        entry_id = entry.id

        TaxTravelService.delete_entry(test_db, entry_id, test_user)

        deleted = test_db.query(TaxTravelEntry).filter(TaxTravelEntry.id == entry_id).first()
        assert deleted is None

    def test_delete_entry_not_owner(self, test_db: Session, test_user: User):
        """Non-owner cannot delete entry"""
        entry = TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            purpose="Meeting",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )

        other_user = User(
            username="otheruser",
            email="other@example.com",
            hashed_password="hashed",
            full_name="Other User",
            role=UserRole.READER
        )
        test_db.add(other_user)
        test_db.commit()

        with pytest.raises(HTTPException) as exc_info:
            TaxTravelService.delete_entry(test_db, entry.id, other_user)
        assert exc_info.value.status_code == 403


class TestListEntries:
    """Test listing travel entries"""

    def test_list_user_entries(self, test_db: Session, test_user: User):
        """List user's entries"""
        TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            purpose="Meeting 1",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )
        TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 16),
            purpose="Meeting 2",
            start_location="C",
            end_location="D",
            distance_km=Decimal("30.0")
        )

        entries = TaxTravelService.list_user_entries(test_db, test_user.id)
        assert len(entries) == 2

    def test_list_with_date_filter(self, test_db: Session, test_user: User):
        """List entries with date filter"""
        TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 15),
            purpose="Meeting 1",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )
        TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 20),
            purpose="Meeting 2",
            start_location="C",
            end_location="D",
            distance_km=Decimal("30.0")
        )
        TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 1, 25),
            purpose="Meeting 3",
            start_location="E",
            end_location="F",
            distance_km=Decimal("20.0")
        )

        entries = TaxTravelService.list_user_entries(
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
        # Create entries in FY2024
        TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2023, 7, 15),
            purpose="Meeting 1",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )
        TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2023, 12, 10),
            purpose="Meeting 2",
            start_location="C",
            end_location="D",
            distance_km=Decimal("30.0")
        )
        TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2024, 3, 20),
            purpose="Meeting 3",
            start_location="E",
            end_location="F",
            distance_km=Decimal("24.5")
        )

        summary = TaxTravelService.get_financial_year_summary(
            test_db,
            test_user.id,
            fy_year=2024,
            rate_per_km=Decimal("0.85")
        )

        assert summary["financial_year"] == 2024
        assert summary["total_trips"] == 3
        assert summary["total_km"] == 100.0  # 45.5 + 30 + 24.5
        assert summary["total_deduction"] == pytest.approx(85.0, rel=0.01)  # 100 * 0.85

    def test_fy_summary_custom_rate(self, test_db: Session, test_user: User):
        """Calculate FY summary with custom rate"""
        TaxTravelService.create_entry(
            db=test_db,
            user=test_user,
            entry_date=date(2023, 7, 15),
            purpose="Meeting",
            start_location="A",
            end_location="B",
            distance_km=Decimal("100.0")
        )

        summary = TaxTravelService.get_financial_year_summary(
            test_db,
            test_user.id,
            fy_year=2024,
            rate_per_km=Decimal("0.72")
        )

        assert summary["total_km"] == 100.0
        assert summary["rate_per_km"] == 0.72
        assert summary["total_deduction"] == pytest.approx(72.0, rel=0.01)
