"""
Unit tests for Audit Service
Tests audit logging functionality and query methods
"""

import pytest
from datetime import datetime, timedelta

from app.services.audit_service import AuditService
from app.models.audit_log import EventType, Severity, AuditLog
from app.models.user import User


class TestAuthenticationEventLogging:
    """Test authentication event logging"""

    def test_log_login_success(self, test_db, test_user: User):
        """Test logging successful login"""
        log = AuditService.log_login_success(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            mfa_used=False
        )

        assert log.id is not None
        assert log.event_type == EventType.LOGIN_SUCCESS
        assert log.user_id == test_user.id
        assert log.username == test_user.username
        assert log.ip_address == "192.168.1.1"
        assert log.user_agent == "Mozilla/5.0"
        assert log.details["mfa_used"] is False
        assert log.severity == Severity.INFO

    def test_log_login_failed(self, test_db):
        """Test logging failed login"""
        log = AuditService.log_login_failed(
            db=test_db,
            username="nonexistent",
            ip_address="192.168.1.100",
            user_agent="BadBot/1.0",
            reason="Invalid credentials"
        )

        assert log.event_type == EventType.LOGIN_FAILED
        assert log.username == "nonexistent"
        assert log.details["reason"] == "Invalid credentials"
        assert log.severity == Severity.WARNING

    def test_log_logout(self, test_db, test_user: User):
        """Test logging logout"""
        log = AuditService.log_logout(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )

        assert log.event_type == EventType.LOGOUT
        assert log.user_id == test_user.id
        assert log.severity == Severity.INFO


class TestMFAEventLogging:
    """Test MFA event logging"""

    def test_log_mfa_setup(self, test_db, test_user: User):
        """Test logging MFA setup"""
        log = AuditService.log_mfa_setup(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )

        assert log.event_type == EventType.MFA_SETUP
        assert log.user_id == test_user.id

    def test_log_mfa_enabled(self, test_db, test_user: User):
        """Test logging MFA enabled"""
        log = AuditService.log_mfa_enabled(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )

        assert log.event_type == EventType.MFA_ENABLED
        assert log.details["security_enhanced"] is True

    def test_log_mfa_disabled(self, test_db, test_user: User):
        """Test logging MFA disabled"""
        log = AuditService.log_mfa_disabled(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            devices_revoked=3
        )

        assert log.event_type == EventType.MFA_DISABLED
        assert log.details["devices_revoked"] == 3
        assert log.severity == Severity.WARNING

    def test_log_mfa_verified(self, test_db, test_user: User):
        """Test logging MFA verification"""
        log = AuditService.log_mfa_verified(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            trusted_device=True
        )

        assert log.event_type == EventType.MFA_VERIFIED
        assert log.details["trusted_device"] is True


class TestUserManagementEventLogging:
    """Test user management event logging"""

    def test_log_user_created(self, test_db, admin_user: User, test_user: User):
        """Test logging user creation"""
        log = AuditService.log_user_created(
            db=test_db,
            admin_user=admin_user,
            new_user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )

        assert log.event_type == EventType.USER_CREATE
        assert log.user_id == admin_user.id
        assert log.resource_type == "user"
        assert log.resource_id == str(test_user.id)
        assert log.details["created_username"] == test_user.username

    def test_log_user_updated(self, test_db, admin_user: User, test_user: User):
        """Test logging user update"""
        changes = {"role": "Editor", "email": "new@example.com"}

        log = AuditService.log_user_updated(
            db=test_db,
            admin_user=admin_user,
            updated_user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            changes=changes
        )

        assert log.event_type == EventType.USER_UPDATE
        assert log.details["changes"] == changes

    def test_log_user_deleted(self, test_db, admin_user: User, test_user: User):
        """Test logging user deletion"""
        log = AuditService.log_user_deleted(
            db=test_db,
            admin_user=admin_user,
            deleted_user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )

        assert log.event_type == EventType.USER_DELETE
        assert log.severity == Severity.WARNING

    def test_log_password_changed(self, test_db, test_user: User):
        """Test logging password change"""
        log = AuditService.log_password_changed(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            changed_by_admin=False
        )

        assert log.event_type == EventType.PASSWORD_CHANGE
        assert log.details["changed_by_admin"] is False


class TestFileEventLogging:
    """Test file event logging"""

    def test_log_file_upload(self, test_db, test_user: User):
        """Test logging file upload"""
        log = AuditService.log_file_upload(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            file_id=123,
            filename="receipt.pdf",
            file_size=102400,
            mime_type="application/pdf"
        )

        assert log.event_type == EventType.FILE_UPLOAD
        assert log.resource_type == "file"
        assert log.resource_id == str(123)
        assert log.details["filename"] == "receipt.pdf"
        assert log.details["size_bytes"] == 102400

    def test_log_file_download(self, test_db, test_user: User):
        """Test logging file download"""
        log = AuditService.log_file_download(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            file_id=123,
            filename="receipt.pdf"
        )

        assert log.event_type == EventType.FILE_DOWNLOAD
        assert log.resource_id == str(123)

    def test_log_file_deleted(self, test_db, test_user: User):
        """Test logging file deletion"""
        log = AuditService.log_file_deleted(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            file_id=123,
            filename="receipt.pdf"
        )

        assert log.event_type == EventType.FILE_DELETE
        assert log.severity == Severity.WARNING


class TestTaxEventLogging:
    """Test tax record event logging"""

    def test_log_tax_wfh_create(self, test_db, test_user: User):
        """Test logging WFH tax record creation"""
        details = {"year": 2024, "days": 200}

        log = AuditService.log_tax_wfh_create(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            tax_id=456,
            details=details
        )

        assert log.event_type == EventType.TAX_WFH_CREATE
        assert log.resource_type == "tax_wfh"
        assert log.resource_id == str(456)
        assert log.details["year"] == 2024

    def test_log_tax_travel_create(self, test_db, test_user: User):
        """Test logging travel tax record creation"""
        details = {"year": 2024, "km": 5000}

        log = AuditService.log_tax_travel_create(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            tax_id=789,
            details=details
        )

        assert log.event_type == EventType.TAX_TRAVEL_CREATE
        assert log.resource_type == "tax_travel"
        assert log.resource_id == str(789)


class TestAuditLogQueries:
    """Test audit log query methods"""

    def test_get_all_logs_empty(self, test_db):
        """Test getting all logs when none exist"""
        logs = AuditService.get_all_logs(test_db)
        assert len(logs) == 0

    def test_get_all_logs_with_data(self, test_db, test_user: User):
        """Test getting all logs"""
        # Create some logs
        AuditService.log_login_success(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        AuditService.log_logout(
            db=test_db,
            user=test_user,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )

        logs = AuditService.get_all_logs(test_db)
        assert len(logs) == 2

    def test_get_all_logs_with_limit(self, test_db, test_user: User):
        """Test pagination with limit"""
        # Create 5 logs
        for i in range(5):
            AuditService.log_login_success(
                db=test_db,
                user=test_user,
                ip_address=f"192.168.1.{i}",
                user_agent="Mozilla/5.0"
            )

        logs = AuditService.get_all_logs(test_db, limit=3)
        assert len(logs) == 3

    def test_get_all_logs_filter_by_event_type(self, test_db, test_user: User):
        """Test filtering by event type"""
        AuditService.log_login_success(test_db, test_user, "192.168.1.1", "Mozilla/5.0")
        AuditService.log_logout(test_db, test_user, "192.168.1.1", "Mozilla/5.0")
        AuditService.log_mfa_setup(test_db, test_user, "192.168.1.1", "Mozilla/5.0")

        logs = AuditService.get_all_logs(test_db, event_type=EventType.LOGIN_SUCCESS)
        assert len(logs) == 1
        assert logs[0].event_type == EventType.LOGIN_SUCCESS

    def test_get_all_logs_filter_by_user_id(self, test_db, test_user: User, admin_user: User):
        """Test filtering by user ID"""
        AuditService.log_login_success(test_db, test_user, "192.168.1.1", "Mozilla/5.0")
        AuditService.log_login_success(test_db, admin_user, "192.168.1.2", "Mozilla/5.0")

        logs = AuditService.get_all_logs(test_db, user_id=test_user.id)
        assert len(logs) == 1
        assert logs[0].user_id == test_user.id

    def test_get_all_logs_filter_by_severity(self, test_db, test_user: User):
        """Test filtering by severity"""
        AuditService.log_login_success(test_db, test_user, "192.168.1.1", "Mozilla/5.0")  # INFO
        AuditService.log_login_failed(test_db, "hacker", "192.168.1.100", "BadBot", "Brute force")  # WARNING

        logs = AuditService.get_all_logs(test_db, severity=Severity.WARNING)
        assert len(logs) == 1
        assert logs[0].severity == Severity.WARNING

    def test_get_user_tax_logs_empty(self, test_db, test_user: User):
        """Test getting user tax logs when none exist"""
        logs = AuditService.get_user_tax_logs(test_db, test_user.id)
        assert len(logs) == 0

    def test_get_user_tax_logs_with_data(self, test_db, test_user: User):
        """Test getting user tax logs"""
        # Create tax logs
        AuditService.log_tax_wfh_create(
            test_db, test_user, "192.168.1.1", "Mozilla/5.0", 123, {}
        )
        AuditService.log_tax_travel_create(
            test_db, test_user, "192.168.1.1", "Mozilla/5.0", 456, {}
        )
        # Create non-tax log
        AuditService.log_login_success(
            test_db, test_user, "192.168.1.1", "Mozilla/5.0"
        )

        logs = AuditService.get_user_tax_logs(test_db, test_user.id)
        assert len(logs) == 2
        assert all(log.event_type.value.startswith("TAX_") for log in logs)

    def test_get_user_tax_logs_only_own_records(self, test_db, test_user: User, admin_user: User):
        """Test that user only sees their own tax logs"""
        AuditService.log_tax_wfh_create(
            test_db, test_user, "192.168.1.1", "Mozilla/5.0", 123, {}
        )
        AuditService.log_tax_wfh_create(
            test_db, admin_user, "192.168.1.2", "Mozilla/5.0", 456, {}
        )

        logs = AuditService.get_user_tax_logs(test_db, test_user.id)
        assert len(logs) == 1
        assert logs[0].user_id == test_user.id


class TestAuditLogCleanup:
    """Test audit log retention and cleanup"""

    def test_cleanup_old_logs_none_old(self, test_db, test_user: User):
        """Test cleanup when no logs are old"""
        AuditService.log_login_success(test_db, test_user, "192.168.1.1", "Mozilla/5.0")

        deleted = AuditService.cleanup_old_logs(test_db, retention_days=30)
        assert deleted == 0

    def test_cleanup_old_logs_with_old_records(self, test_db, test_user: User):
        """Test cleanup of old non-tax logs"""
        # Create an old log
        log = AuditService.log_login_success(test_db, test_user, "192.168.1.1", "Mozilla/5.0")

        # Manually set timestamp to 3 years ago
        log.timestamp = datetime.utcnow() - timedelta(days=1095)
        test_db.commit()

        # Cleanup logs older than 2 years
        deleted = AuditService.cleanup_old_logs(test_db, retention_days=730)
        assert deleted == 1

    def test_cleanup_preserves_tax_logs(self, test_db, test_user: User):
        """Test that tax logs are not deleted by regular cleanup"""
        # Create old tax log
        log = AuditService.log_tax_wfh_create(
            test_db, test_user, "192.168.1.1", "Mozilla/5.0", 123, {}
        )
        log.timestamp = datetime.utcnow() - timedelta(days=1095)  # 3 years ago
        test_db.commit()

        # Regular cleanup (2 years) should NOT delete tax logs
        deleted = AuditService.cleanup_old_logs(test_db, retention_days=730)
        assert deleted == 0

        # Tax logs still exist
        logs = test_db.query(AuditLog).all()
        assert len(logs) == 1

    def test_cleanup_old_tax_logs(self, test_db, test_user: User):
        """Test cleanup of very old tax logs (>5 years)"""
        # Create very old tax log
        log = AuditService.log_tax_wfh_create(
            test_db, test_user, "192.168.1.1", "Mozilla/5.0", 123, {}
        )
        log.timestamp = datetime.utcnow() - timedelta(days=2000)  # ~5.5 years
        test_db.commit()

        # Cleanup tax logs older than 5 years
        deleted = AuditService.cleanup_old_tax_logs(test_db, retention_days=1825)
        assert deleted == 1

    def test_cleanup_respects_5_year_retention(self, test_db, test_user: User):
        """Test that tax logs are kept for 5 years"""
        # Create tax log 4 years old
        log = AuditService.log_tax_wfh_create(
            test_db, test_user, "192.168.1.1", "Mozilla/5.0", 123, {}
        )
        log.timestamp = datetime.utcnow() - timedelta(days=1460)  # 4 years
        test_db.commit()

        # Should NOT be deleted (still within 5 years)
        deleted = AuditService.cleanup_old_tax_logs(test_db, retention_days=1825)
        assert deleted == 0
