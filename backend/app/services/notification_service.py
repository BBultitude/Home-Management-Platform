"""
Notification Service
Manages user notifications for alerts, reminders, and system messages
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.notification import Notification, NotificationType, NotificationCategory


class NotificationService:
    """Service for notification operations"""

    @staticmethod
    def create_notification(
        db: Session,
        user_id: UUID,
        title: str,
        message: str,
        type: NotificationType = NotificationType.INFO,
        category: NotificationCategory = NotificationCategory.SYSTEM,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None
    ) -> Notification:
        """
        Create a new notification

        Args:
            db: Database session
            user_id: User ID to notify
            title: Notification title
            message: Notification message
            type: Notification type (info, warning, error, success, reminder)
            category: Notification category (system, tax, financial, etc.)
            action_url: Optional action URL
            action_label: Optional action button label

        Returns:
            Created Notification
        """
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            category=category,
            action_url=action_url,
            action_label=action_label
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    def get_notification(db: Session, notification_id: UUID, user_id: UUID) -> Notification:
        """Get a notification by ID (user-scoped)"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()

        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        return notification

    @staticmethod
    def list_notifications(
        db: Session,
        user_id: UUID,
        unread_only: bool = False,
        category: Optional[NotificationCategory] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Notification]:
        """
        List user notifications

        Args:
            db: Database session
            user_id: User ID
            unread_only: Filter to unread notifications only
            category: Filter by category
            limit: Maximum entries to return
            offset: Pagination offset

        Returns:
            List of Notification objects
        """
        query = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_dismissed == False
        )

        if unread_only:
            query = query.filter(Notification.is_read == False)

        if category:
            query = query.filter(Notification.category == category)

        query = query.order_by(Notification.created_at.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def get_unread_count(db: Session, user_id: UUID) -> int:
        """Get count of unread notifications for user"""
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_dismissed == False
        ).count()

    @staticmethod
    def mark_as_read(db: Session, notification_id: UUID, user_id: UUID) -> Notification:
        """Mark notification as read"""
        notification = NotificationService.get_notification(db, notification_id, user_id)

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(notification)

        return notification

    @staticmethod
    def mark_all_as_read(db: Session, user_id: UUID) -> int:
        """Mark all user notifications as read, returns count updated"""
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.now(timezone.utc)
        })

        db.commit()
        return count

    @staticmethod
    def dismiss_notification(db: Session, notification_id: UUID, user_id: UUID) -> None:
        """Dismiss (soft delete) a notification"""
        notification = NotificationService.get_notification(db, notification_id, user_id)

        notification.is_dismissed = True
        db.commit()

    @staticmethod
    def dismiss_all(db: Session, user_id: UUID) -> int:
        """Dismiss all user notifications, returns count dismissed"""
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_dismissed == False
        ).update({"is_dismissed": True})

        db.commit()
        return count

    @staticmethod
    def delete_notification(db: Session, notification_id: UUID, user_id: UUID) -> None:
        """Permanently delete a notification"""
        notification = NotificationService.get_notification(db, notification_id, user_id)

        db.delete(notification)
        db.commit()

    # ===== Notification Generators =====

    @staticmethod
    def generate_renewal_notifications(db: Session) -> int:
        """
        Generate notifications for upcoming insurance renewals
        Called by scheduled task

        Returns:
            Count of notifications created
        """
        from app.models.insurance_policy import InsurancePolicy
        from datetime import date, timedelta

        # Get all users (in practice, might want to batch this)
        from app.models.user import User
        users = db.query(User).filter(User.is_active == True).all()

        notifications_created = 0

        for user in users:
            # Get policies with renewal in next 30 days
            threshold_date = date.today() + timedelta(days=30)
            policies = db.query(InsurancePolicy).filter(
                InsurancePolicy.renewal_date <= threshold_date,
                InsurancePolicy.renewal_date >= date.today()
            ).all()

            for policy in policies:
                days = (policy.renewal_date - date.today()).days

                # Check if notification already exists for this policy
                existing = db.query(Notification).filter(
                    Notification.user_id == user.id,
                    Notification.category == NotificationCategory.ASSETS,
                    Notification.action_url == f"/assets/insurance/{policy.id}",
                    Notification.created_at >= datetime.now(timezone.utc) - timedelta(days=7)
                ).first()

                if not existing:
                    if days <= 7:
                        type = NotificationType.WARNING
                        title = f"Insurance renewal due in {days} days"
                    else:
                        type = NotificationType.REMINDER
                        title = f"Insurance renewal coming up"

                    NotificationService.create_notification(
                        db=db,
                        user_id=user.id,
                        title=title,
                        message=f"{policy.policy_type.value} policy '{policy.policy_name}' renews on {policy.renewal_date.strftime('%B %d, %Y')}",
                        type=type,
                        category=NotificationCategory.ASSETS,
                        action_url=f"/assets/insurance/{policy.id}",
                        action_label="View Policy"
                    )
                    notifications_created += 1

        return notifications_created

    @staticmethod
    def generate_document_expiry_notifications(db: Session) -> int:
        """
        Generate notifications for expiring documents
        Called by scheduled task

        Returns:
            Count of notifications created
        """
        from app.models.document import Document
        from datetime import date, timedelta

        from app.models.user import User
        users = db.query(User).filter(User.is_active == True).all()

        notifications_created = 0

        for user in users:
            threshold_date = date.today() + timedelta(days=30)
            documents = db.query(Document).filter(
                Document.expiry_date.isnot(None),
                Document.expiry_date <= threshold_date,
                Document.expiry_date >= date.today()
            ).all()

            for doc in documents:
                days = (doc.expiry_date - date.today()).days

                existing = db.query(Notification).filter(
                    Notification.user_id == user.id,
                    Notification.category == NotificationCategory.ASSETS,
                    Notification.action_url == f"/assets/documents/{doc.id}",
                    Notification.created_at >= datetime.now(timezone.utc) - timedelta(days=7)
                ).first()

                if not existing:
                    if days <= 7:
                        type = NotificationType.WARNING
                        title = f"Document expires in {days} days"
                    else:
                        type = NotificationType.REMINDER
                        title = f"Document expiring soon"

                    NotificationService.create_notification(
                        db=db,
                        user_id=user.id,
                        title=title,
                        message=f"{doc.document_type.value} '{doc.title}' expires on {doc.expiry_date.strftime('%B %d, %Y')}",
                        type=type,
                        category=NotificationCategory.ASSETS,
                        action_url=f"/assets/documents/{doc.id}",
                        action_label="View Document"
                    )
                    notifications_created += 1

        return notifications_created

    @staticmethod
    def generate_quote_expiry_notifications(db: Session) -> int:
        """
        Generate notifications for expiring quotes
        Called by scheduled task

        Returns:
            Count of notifications created
        """
        from app.models.quote import Quote
        from datetime import date, timedelta

        from app.models.user import User
        users = db.query(User).filter(User.is_active == True).all()

        notifications_created = 0

        for user in users:
            threshold_date = date.today() + timedelta(days=14)
            quotes = db.query(Quote).filter(
                Quote.expires_at.isnot(None),
                Quote.expires_at <= threshold_date,
                Quote.expires_at >= date.today(),
                Quote.is_selected == False  # Only notify on non-selected quotes
            ).all()

            for quote in quotes:
                days = (quote.expires_at - date.today()).days

                existing = db.query(Notification).filter(
                    Notification.user_id == user.id,
                    Notification.category == NotificationCategory.PROJECTS,
                    Notification.action_url.like(f"%/quotes/{quote.id}%"),
                    Notification.created_at >= datetime.now(timezone.utc) - timedelta(days=7)
                ).first()

                if not existing:
                    type = NotificationType.WARNING if days <= 7 else NotificationType.REMINDER

                    NotificationService.create_notification(
                        db=db,
                        user_id=user.id,
                        title=f"Quote expires in {days} days",
                        message=f"Quote from {quote.contractor_name} ({quote.contractor_email}) expires on {quote.expires_at.strftime('%B %d, %Y')}",
                        type=type,
                        category=NotificationCategory.PROJECTS,
                        action_url=f"/projects/quotes/{quote.id}",
                        action_label="View Quote"
                    )
                    notifications_created += 1

        return notifications_created
