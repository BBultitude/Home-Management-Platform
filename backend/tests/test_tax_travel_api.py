"""
Integration tests for Tax Travel API endpoints
"""

import pytest
from datetime import date
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.tax_travel import TaxTravelEntry


class TestCreateTravelEntry:
    """Test POST /tax/travel"""

    def test_create_entry_success(self, client: TestClient, test_user: User):
        """Successfully create travel entry"""
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        response = client.post(
            "/api/v1/tax/travel",
            json={
                "date": "2024-01-15",
                "purpose": "Client meeting",
                "start_location": "Office",
                "end_location": "Client site",
                "distance_km": 45.5,
                "notes": "Highway route"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["date"] == "2024-01-15"
        assert data["purpose"] == "Client meeting"
        assert data["distance_km"] == 45.5
        assert data["deduction_amount"] == pytest.approx(38.675, rel=0.01)  # 45.5 * 0.85

    def test_create_entry_unauthorized(self, client: TestClient):
        """Cannot create entry without authentication"""
        response = client.post(
            "/api/v1/tax/travel",
            json={
                "date": "2024-01-15",
                "purpose": "Meeting",
                "start_location": "A",
                "end_location": "B",
                "distance_km": 45.5
            }
        )
        assert response.status_code == 401


class TestListTravelEntries:
    """Test GET /tax/travel"""

    def test_list_entries(self, client: TestClient, test_user: User, test_db: Session):
        """List user's travel entries"""
        entry1 = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2024, 1, 15),
            purpose="Meeting 1",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )
        entry2 = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2024, 1, 16),
            purpose="Meeting 2",
            start_location="C",
            end_location="D",
            distance_km=Decimal("30.0")
        )
        test_db.add_all([entry1, entry2])
        test_db.commit()

        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        response = client.get("/api/v1/tax/travel")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 2
        assert len(data["entries"]) == 2

    def test_list_with_date_filter(self, client: TestClient, test_user: User, test_db: Session):
        """List entries with date filter"""
        entry1 = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2024, 1, 15),
            purpose="Meeting 1",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )
        entry2 = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2024, 1, 20),
            purpose="Meeting 2",
            start_location="C",
            end_location="D",
            distance_km=Decimal("30.0")
        )
        entry3 = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2024, 1, 25),
            purpose="Meeting 3",
            start_location="E",
            end_location="F",
            distance_km=Decimal("20.0")
        )
        test_db.add_all([entry1, entry2, entry3])
        test_db.commit()

        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        response = client.get("/api/v1/tax/travel?start_date=2024-01-18&end_date=2024-01-22")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert data["entries"][0]["date"] == "2024-01-20"


class TestGetTravelEntry:
    """Test GET /tax/travel/{entry_id}"""

    def test_get_entry_success(self, client: TestClient, test_user: User, test_db: Session):
        """Get travel entry by ID"""
        entry = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2024, 1, 15),
            purpose="Meeting",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )
        test_db.add(entry)
        test_db.commit()

        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        response = client.get(f"/api/v1/tax/travel/{entry.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == entry.id
        assert data["purpose"] == "Meeting"

    def test_get_entry_not_found(self, client: TestClient, test_user: User):
        """Get non-existent entry returns 404"""
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        response = client.get("/api/v1/tax/travel/99999")
        assert response.status_code == 404


class TestUpdateTravelEntry:
    """Test PUT /tax/travel/{entry_id}"""

    def test_update_entry_success(self, client: TestClient, test_user: User, test_db: Session):
        """Successfully update travel entry"""
        entry = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2024, 1, 15),
            purpose="Meeting",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )
        test_db.add(entry)
        test_db.commit()

        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        response = client.put(
            f"/api/v1/tax/travel/{entry.id}",
            json={"distance_km": 50.0, "notes": "Updated route"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["distance_km"] == 50.0
        assert data["notes"] == "Updated route"


class TestDeleteTravelEntry:
    """Test DELETE /tax/travel/{entry_id}"""

    def test_delete_entry_success(self, client: TestClient, test_user: User, test_db: Session):
        """Successfully delete travel entry"""
        entry = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2024, 1, 15),
            purpose="Meeting",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )
        test_db.add(entry)
        test_db.commit()
        entry_id = entry.id

        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        response = client.delete(f"/api/v1/tax/travel/{entry_id}")
        assert response.status_code == 200
        assert response.json()["entry_id"] == entry_id

        deleted = test_db.query(TaxTravelEntry).filter(TaxTravelEntry.id == entry_id).first()
        assert deleted is None


class TestFYSummary:
    """Test GET /tax/travel/summary/fy/{fy_year}"""

    def test_fy_summary(self, client: TestClient, test_user: User, test_db: Session):
        """Get financial year summary"""
        entry1 = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2023, 7, 15),
            purpose="Meeting 1",
            start_location="A",
            end_location="B",
            distance_km=Decimal("45.5")
        )
        entry2 = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2023, 12, 10),
            purpose="Meeting 2",
            start_location="C",
            end_location="D",
            distance_km=Decimal("30.0")
        )
        entry3 = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2024, 3, 20),
            purpose="Meeting 3",
            start_location="E",
            end_location="F",
            distance_km=Decimal("24.5")
        )
        test_db.add_all([entry1, entry2, entry3])
        test_db.commit()

        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        response = client.get("/api/v1/tax/travel/summary/fy/2024")
        assert response.status_code == 200

        data = response.json()
        assert data["financial_year"] == 2024
        assert data["total_trips"] == 3
        assert data["total_km"] == pytest.approx(100.0, rel=0.01)
        assert data["total_deduction"] == pytest.approx(85.0, rel=0.01)  # 100 * 0.85


class TestTravelExport:
    """Test GET /tax/travel/export/fy/{fy_year}/csv and /text"""

    def test_export_csv(self, client: TestClient, test_user: User, test_db: Session):
        """Export travel entries to CSV format"""
        # Create entries in FY2024
        entry1 = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2023, 7, 15),
            purpose="Client meeting",
            start_location="Office",
            end_location="Client site",
            distance_km=Decimal("45.5"),
            notes="Highway route"
        )
        entry2 = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2024, 1, 10),
            purpose="Site visit",
            start_location="Office",
            end_location="Project site",
            distance_km=Decimal("30.0")
        )
        test_db.add_all([entry1, entry2])
        test_db.commit()

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Export to CSV
        response = client.get("/api/v1/tax/travel/export/fy/2024/csv")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        assert "travel_fy2024.csv" in response.headers["content-disposition"]

        content = response.text
        assert "Work Travel Deduction - ATO Compliant Export" in content
        assert "Financial Year: 2024" in content
        assert "Rate per km: $0.85/km" in content
        assert "Date,Purpose,Start Location,End Location,Distance (km),Deduction,Notes" in content
        assert "2023-07-15" in content
        assert "Client meeting" in content
        assert "2024-01-10" in content
        assert "Site visit" in content

    def test_export_csv_custom_rate(self, client: TestClient, test_user: User, test_db: Session):
        """Export with custom rate per km"""
        # Create entry
        entry = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2023, 7, 15),
            purpose="Meeting",
            start_location="A",
            end_location="B",
            distance_km=Decimal("100.0")
        )
        test_db.add(entry)
        test_db.commit()

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Export with custom rate
        response = client.get("/api/v1/tax/travel/export/fy/2024/csv?rate_per_km=0.90")
        assert response.status_code == 200

        content = response.text
        assert "Rate per km: $0.9/km" in content
        assert "$90.00" in content  # 100 * 0.90

    def test_export_text(self, client: TestClient, test_user: User, test_db: Session):
        """Export travel entries to text format"""
        # Create entries in FY2024
        entry1 = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2023, 7, 15),
            purpose="Client meeting",
            start_location="Office",
            end_location="Client site",
            distance_km=Decimal("45.5"),
            notes="Highway route"
        )
        entry2 = TaxTravelEntry(
            user_id=test_user.id,
            date=date(2024, 1, 10),
            purpose="Site visit",
            start_location="Office",
            end_location="Project site",
            distance_km=Decimal("30.0")
        )
        test_db.add_all([entry1, entry2])
        test_db.commit()

        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Export to text
        response = client.get("/api/v1/tax/travel/export/fy/2024/text")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        assert "travel_fy2024.txt" in response.headers["content-disposition"]

        content = response.text
        assert "WORK TRAVEL DEDUCTION - ATO COMPLIANT EXPORT" in content
        assert "Financial Year: 2024" in content
        assert "Period: July 1, 2023 to June 30, 2024" in content
        assert "Rate per km: $0.85/km" in content
        assert "Date: 2023-07-15" in content
        assert "Purpose: Client meeting" in content
        assert "Route: Office → Client site" in content
        assert "Distance: 45.5 km" in content
        assert "Notes: Highway route" in content

    def test_export_empty_fy(self, client: TestClient, test_user: User):
        """Export empty financial year returns valid format"""
        # Login
        client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "TestPassword123"}
        )

        # Export FY with no entries
        response = client.get("/api/v1/tax/travel/export/fy/2025/csv")
        assert response.status_code == 200

        content = response.text
        assert "Total Trips,0" in content
        assert "Total Kilometers,0" in content
