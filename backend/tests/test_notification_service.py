"""
Tests for Notification Service
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.notification_service import NotificationService
from app.models.notification import Notification, NotificationType, NotificationCategory
from app.models.user import User, UserRole
from app.models.insurance_policy import InsurancePolicy, PolicyType, PremiumFrequency
from app.models.document import Document, DocumentType
from app.models.quote import Quote


class TestNotificationService:
    """Test cases for NotificationService"""

    def test_create_notification(self, db_session, test_user):
        """Test creating a notification"""
        notification = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="Test Notification",
            message="This is a test message",
            type=NotificationType.INFO,
            category=NotificationCategory.SYSTEM
        )

        assert notification.id is not None
        assert notification.user_id == test_user.id
        assert notification.title == "Test Notification"
        assert notification.message == "This is a test message"
        assert notification.type == NotificationType.INFO
        assert notification.category == NotificationCategory.SYSTEM
        assert notification.is_read is False
        assert notification.is_dismissed is False

    def test_create_notification_with_action(self, db_session, test_user):
        """Test creating notification with action URL"""
        notification = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="Action Needed",
            message="Click to view",
            action_url="/test/123",
            action_label="View Item"
        )

        assert notification.action_url == "/test/123"
        assert notification.action_label == "View Item"

    def test_get_notification(self, db_session, test_user):
        """Test getting a notification"""
        notification = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="Test",
            message="Test message"
        )

        retrieved = NotificationService.get_notification(
            db=db_session,
            notification_id=notification.id,
            user_id=test_user.id
        )

        assert retrieved.id == notification.id
        assert retrieved.title == "Test"

    def test_get_notification_wrong_user(self, db_session, test_user):
        """Test getting notification with wrong user ID raises error"""
        notification = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="Test",
            message="Test message"
        )

        other_user_id = uuid4()

        with pytest.raises(Exception):
            NotificationService.get_notification(
                db=db_session,
                notification_id=notification.id,
                user_id=other_user_id
            )

    def test_list_notifications(self, db_session, test_user):
        """Test listing notifications"""
        # Create multiple notifications
        for i in range(5):
            NotificationService.create_notification(
                db=db_session,
                user_id=test_user.id,
                title=f"Test {i}",
                message=f"Message {i}"
            )

        notifications = NotificationService.list_notifications(
            db=db_session,
            user_id=test_user.id
        )

        assert len(notifications) == 5

    def test_list_notifications_unread_only(self, db_session, test_user):
        """Test listing only unread notifications"""
        # Create some notifications
        n1 = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="Unread",
            message="Unread message"
        )

        n2 = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="Read",
            message="Read message"
        )

        # Mark one as read
        NotificationService.mark_as_read(db=db_session, notification_id=n2.id, user_id=test_user.id)

        # Get unread only
        unread = NotificationService.list_notifications(
            db=db_session,
            user_id=test_user.id,
            unread_only=True
        )

        assert len(unread) == 1
        assert unread[0].id == n1.id

    def test_list_notifications_by_category(self, db_session, test_user):
        """Test filtering notifications by category"""
        NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="System",
            message="System message",
            category=NotificationCategory.SYSTEM
        )

        NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="Financial",
            message="Financial message",
            category=NotificationCategory.FINANCIAL
        )

        financial = NotificationService.list_notifications(
            db=db_session,
            user_id=test_user.id,
            category=NotificationCategory.FINANCIAL
        )

        assert len(financial) == 1
        assert financial[0].category == NotificationCategory.FINANCIAL

    def test_get_unread_count(self, db_session, test_user):
        """Test getting unread count"""
        # Create notifications
        n1 = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="Test 1",
            message="Message 1"
        )

        NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="Test 2",
            message="Message 2"
        )

        # Check count
        count = NotificationService.get_unread_count(db=db_session, user_id=test_user.id)
        assert count == 2

        # Mark one as read
        NotificationService.mark_as_read(db=db_session, notification_id=n1.id, user_id=test_user.id)

        # Check count again
        count = NotificationService.get_unread_count(db=db_session, user_id=test_user.id)
        assert count == 1

    def test_mark_as_read(self, db_session, test_user):
        """Test marking notification as read"""
        notification = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="Test",
            message="Test message"
        )

        assert notification.is_read is False
        assert notification.read_at is None

        updated = NotificationService.mark_as_read(
            db=db_session,
            notification_id=notification.id,
            user_id=test_user.id
        )

        assert updated.is_read is True
        assert updated.read_at is not None

    def test_mark_all_as_read(self, db_session, test_user):
        """Test marking all notifications as read"""
        # Create multiple notifications
        for i in range(3):
            NotificationService.create_notification(
                db=db_session,
                user_id=test_user.id,
                title=f"Test {i}",
                message=f"Message {i}"
            )

        # Mark all as read
        count = NotificationService.mark_all_as_read(db=db_session, user_id=test_user.id)
        assert count == 3

        # Verify all are read
        unread_count = NotificationService.get_unread_count(db=db_session, user_id=test_user.id)
        assert unread_count == 0

    def test_dismiss_notification(self, db_session, test_user):
        """Test dismissing a notification"""
        notification = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="Test",
            message="Test message"
        )

        NotificationService.dismiss_notification(
            db=db_session,
            notification_id=notification.id,
            user_id=test_user.id
        )

        db_session.refresh(notification)
        assert notification.is_dismissed is True

    def test_dismiss_all(self, db_session, test_user):
        """Test dismissing all notifications"""
        # Create multiple notifications
        for i in range(3):
            NotificationService.create_notification(
                db=db_session,
                user_id=test_user.id,
                title=f"Test {i}",
                message=f"Message {i}"
            )

        # Dismiss all
        count = NotificationService.dismiss_all(db=db_session, user_id=test_user.id)
        assert count == 3

        # Verify not returned in list (dismissed notifications excluded)
        notifications = NotificationService.list_notifications(
            db=db_session,
            user_id=test_user.id
        )
        assert len(notifications) == 0

    def test_delete_notification(self, db_session, test_user):
        """Test permanently deleting a notification"""
        notification = NotificationService.create_notification(
            db=db_session,
            user_id=test_user.id,
            title="Test",
            message="Test message"
        )

        notification_id = notification.id

        NotificationService.delete_notification(
            db=db_session,
            notification_id=notification_id,
            user_id=test_user.id
        )

        # Verify it's gone
        with pytest.raises(Exception):
            NotificationService.get_notification(
                db=db_session,
                notification_id=notification_id,
                user_id=test_user.id
            )

    def test_generate_renewal_notifications(self, db_session, test_user):
        """Test generating insurance renewal notifications"""
        from datetime import date

        # Create insurance policy with upcoming renewal
        policy = InsurancePolicy(
            policy_type=PolicyType.HOME,
            provider="Test Provider",
            policy_number="TEST123",
            premium=1000.00,
            premium_frequency=PremiumFrequency.ANNUALLY,
            renewal_date=date.today() + timedelta(days=15)
        )
        db_session.add(policy)
        db_session.commit()

        # Generate notifications
        count = NotificationService.generate_renewal_notifications(db_session)

        # Should create notification for test_user
        assert count >= 1

        # Verify notification exists
        notifications = NotificationService.list_notifications(
            db=db_session,
            user_id=test_user.id,
            category=NotificationCategory.ASSETS
        )

        assert len(notifications) >= 1

    def test_generate_document_expiry_notifications(self, db_session, test_user):
        """Test generating document expiry notifications"""
        from datetime import date
        from app.models.file import File, FileCategory

        # Create file record required by Document FK
        file_record = File(
            uploaded_by=test_user.id,
            filename="test.pdf",
            original_filename="test.pdf",
            file_path="/uploads/other/test_doc.pdf",
            mime_type="application/pdf",
            file_size=1024,
            category=FileCategory.OTHER
        )
        db_session.add(file_record)
        db_session.flush()

        # Create document with upcoming expiry
        doc = Document(
            title="Test Document",
            document_type=DocumentType.CONTRACT,
            expiry_date=date.today() + timedelta(days=20),
            file_id=file_record.id
        )
        db_session.add(doc)
        db_session.commit()

        # Generate notifications
        count = NotificationService.generate_document_expiry_notifications(db_session)

        assert count >= 1

    def test_generate_quote_expiry_notifications(self, db_session, test_user):
        """Test generating quote expiry notifications"""
        from datetime import date
        from app.models.project import Project

        # Create project required by Quote FK
        project = Project(
            project_name="Test Project for Quote"
        )
        db_session.add(project)
        db_session.flush()

        # Create quote with upcoming expiry
        quote = Quote(
            project_id=project.id,
            contractor_name="Test Contractor",
            contact_email="test@example.com",
            quote_amount=5000.00,
            quote_date=date.today(),
            expiry_date=date.today() + timedelta(days=10),
            selected=False
        )
        db_session.add(quote)
        db_session.commit()

        # Generate notifications
        count = NotificationService.generate_quote_expiry_notifications(db_session)

        assert count >= 1
