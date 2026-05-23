"""
Integration tests for Tax WFH API endpoints
"""

import pytest
from datetime import date
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.tax_wfh import TaxWFHEntry


class TestCreateWFHEntry:
    """Test POST /tax/wfh"""

    def test_create_entry_success(self, client: TestClient, test_user: User):
        """Successfully create WFH entry"""
        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Create entry
        response = client.post(
            "/api/v1/tax/wfh",
            json={
                "date": "2024-01-15",
                "hours": 8.0,
                "notes": "Full day from home"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["date"] == "2024-01-15"
        assert data["hours"] == pytest.approx(8.0)
        assert data["notes"] == "Full day from home"
        assert data["deduction_amount"] == pytest.approx(5.36, rel=0.01)  # 8 * 0.67

    def test_create_entry_unauthorized(self, client: TestClient):
        """Cannot create entry without authentication"""
        response = client.post(
            "/api/v1/tax/wfh",
            json={
                "date": "2024-01-15",
                "hours": 8.0
            }
        )
        assert response.status_code == 401

    def test_create_entry_invalid_hours(self, client: TestClient, test_user: User):
        """Cannot create entry with invalid hours"""
        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Try to create with 0 hours
        response = client.post(
            "/api/v1/tax/wfh",
            json={
                "date": "2024-01-15",
                "hours": 0
            }
        )
        assert response.status_code == 422  # Validation error

    def test_create_entry_duplicate(self, client: TestClient, test_user: User, test_db: Session):
        """Cannot create duplicate entry for same date"""
        # Create first entry directly in DB
        entry = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )
        test_db.add(entry)
        test_db.commit()

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Try to create duplicate
        response = client.post(
            "/api/v1/tax/wfh",
            json={
                "date": "2024-01-15",
                "hours": 4.0
            }
        )
        assert response.status_code == 409


class TestListWFHEntries:
    """Test GET /tax/wfh"""

    def test_list_entries(self, client: TestClient, test_user: User, test_db: Session):
        """List user's WFH entries"""
        # Create entries
        entry1 = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )
        entry2 = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2024, 1, 16),
            hours=Decimal("6.50")
        )
        test_db.add_all([entry1, entry2])
        test_db.commit()

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # List entries
        response = client.get("/api/v1/tax/wfh")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 2
        assert len(data["entries"]) == 2

    def test_list_with_date_filter(self, client: TestClient, test_user: User, test_db: Session):
        """List entries with date filter"""
        # Create entries
        entry1 = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )
        entry2 = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2024, 1, 20),
            hours=Decimal("6.50")
        )
        entry3 = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2024, 1, 25),
            hours=Decimal("7.00")
        )
        test_db.add_all([entry1, entry2, entry3])
        test_db.commit()

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # List with date filter
        response = client.get("/api/v1/tax/wfh?start_date=2024-01-18&end_date=2024-01-22")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert data["entries"][0]["date"] == "2024-01-20"


class TestGetWFHEntry:
    """Test GET /tax/wfh/{entry_id}"""

    def test_get_entry_success(self, client: TestClient, test_user: User, test_db: Session):
        """Get WFH entry by ID"""
        # Create entry
        entry = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2024, 1, 15),
            hours=Decimal("8.00"),
            notes="Test entry"
        )
        test_db.add(entry)
        test_db.commit()

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Get entry
        response = client.get(f"/api/v1/tax/wfh/{entry.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == entry.id
        assert data["date"] == "2024-01-15"
        assert data["hours"] == pytest.approx(8.0)

    def test_get_entry_not_found(self, client: TestClient, test_user: User):
        """Get non-existent entry returns 404"""
        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        response = client.get("/api/v1/tax/wfh/99999")
        assert response.status_code == 404


class TestUpdateWFHEntry:
    """Test PUT /tax/wfh/{entry_id}"""

    def test_update_entry_success(self, client: TestClient, test_user: User, test_db: Session):
        """Successfully update WFH entry"""
        # Create entry
        entry = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )
        test_db.add(entry)
        test_db.commit()

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Update entry
        response = client.put(
            f"/api/v1/tax/wfh/{entry.id}",
            json={"hours": 6.5, "notes": "Updated notes"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["hours"] == pytest.approx(6.5)
        assert data["notes"] == "Updated notes"


class TestDeleteWFHEntry:
    """Test DELETE /tax/wfh/{entry_id}"""

    def test_delete_entry_success(self, client: TestClient, test_user: User, test_db: Session):
        """Successfully delete WFH entry"""
        # Create entry
        entry = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2024, 1, 15),
            hours=Decimal("8.00")
        )
        test_db.add(entry)
        test_db.commit()
        entry_id = entry.id

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Delete entry
        response = client.delete(f"/api/v1/tax/wfh/{entry_id}")
        assert response.status_code == 200
        assert response.json()["entry_id"] == entry_id

        # Verify deleted
        deleted = test_db.query(TaxWFHEntry).filter(TaxWFHEntry.id == entry_id).first()
        assert deleted is None


class TestFYSummary:
    """Test GET /tax/wfh/summary/fy/{fy_year}"""

    def test_fy_summary(self, client: TestClient, test_user: User, test_db: Session):
        """Get financial year summary"""
        # Create entries in FY2024 (July 1, 2023 to June 30, 2024)
        entry1 = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2023, 7, 15),
            hours=Decimal("8.00")
        )
        entry2 = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2023, 12, 10),
            hours=Decimal("6.50")
        )
        entry3 = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2024, 3, 20),
            hours=Decimal("7.00")
        )
        test_db.add_all([entry1, entry2, entry3])
        test_db.commit()

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Get FY summary
        response = client.get("/api/v1/tax/wfh/summary/fy/2024")
        assert response.status_code == 200

        data = response.json()
        assert data["financial_year"] == 2024
        assert data["total_days"] == 3
        assert data["total_hours"] == pytest.approx(21.5, rel=0.01)
        assert data["total_deduction"] == pytest.approx(14.405, rel=0.01)


class TestWFHExport:
    """Test GET /tax/wfh/export/fy/{fy_year}/csv and /text"""

    def test_export_csv(self, client: TestClient, test_user: User, test_db: Session):
        """Export WFH entries to CSV format"""
        # Create entries in FY2024
        entry1 = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2023, 7, 15),
            hours=Decimal("8.00"),
            notes="Full day"
        )
        entry2 = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2024, 1, 10),
            hours=Decimal("6.50")
        )
        test_db.add_all([entry1, entry2])
        test_db.commit()

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Export to CSV
        response = client.get("/api/v1/tax/wfh/export/fy/2024/csv")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        assert "wfh_fy2024.csv" in response.headers["content-disposition"]

        content = response.text
        assert "Work From Home Deduction - ATO Compliant Export" in content
        assert "Financial Year: 2024" in content
        assert "ATO Rate: $0.67/hour" in content
        assert "Date,Hours,Deduction,Notes" in content
        assert "2023-07-15" in content
        assert "2024-01-10" in content

    def test_export_text(self, client: TestClient, test_user: User, test_db: Session):
        """Export WFH entries to text format"""
        # Create entries in FY2024
        entry1 = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2023, 7, 15),
            hours=Decimal("8.00"),
            notes="Full day"
        )
        entry2 = TaxWFHEntry(
            user_id=test_user.id,
            date=date(2024, 1, 10),
            hours=Decimal("6.50")
        )
        test_db.add_all([entry1, entry2])
        test_db.commit()

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Export to text
        response = client.get("/api/v1/tax/wfh/export/fy/2024/text")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        assert "wfh_fy2024.txt" in response.headers["content-disposition"]

        content = response.text
        assert "WORK FROM HOME DEDUCTION - ATO COMPLIANT EXPORT" in content
        assert "Financial Year: 2024" in content
        assert "Period: July 1, 2023 to June 30, 2024" in content
        assert "ATO Rate: $0.67/hour" in content
        assert "Date: 2023-07-15" in content
        assert "Hours: 8" in content
        assert "Notes: Full day" in content

    def test_export_empty_fy(self, client: TestClient, test_user: User):
        """Export empty financial year returns valid format"""
        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Export FY with no entries
        response = client.get("/api/v1/tax/wfh/export/fy/2025/csv")
        assert response.status_code == 200

        content = response.text
        assert "Total Days Worked From Home,0" in content
        assert "Total Hours,0" in content
