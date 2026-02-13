"""
Tests for Dashboard Service
"""

import pytest
from datetime import date, timedelta
from uuid import uuid4

from app.services.dashboard_service import DashboardService
from app.models.user import User, UserRole
from app.models.insurance_policy import InsurancePolicy, PolicyType, PremiumFrequency
from app.models.document import Document, DocumentType
from app.models.priority_item import PriorityItem, PriorityStatus
from app.models.project import Project, ProjectStatus
from app.models.week_plan import WeekPlan
from app.models.recipe import Recipe
from app.models.notification import Notification, NotificationType, NotificationCategory


class TestDashboardService:
    """Test cases for DashboardService"""

    def test_get_dashboard_summary(self, db_session, test_user):
        """Test getting complete dashboard summary"""
        summary = DashboardService.get_dashboard_summary(db=db_session, user_id=test_user.id)

        assert "alerts" in summary
        assert "priorities" in summary
        assert "projects" in summary
        assert "meal_plan" in summary
        assert "financial" in summary
        assert "notifications" in summary
        assert "quick_stats" in summary

    def test_get_alerts_widget(self, db_session):
        """Test getting alerts widget"""
        # Create insurance policy with upcoming renewal
        policy = InsurancePolicy(
            policy_name="Test Policy",
            policy_type=PolicyType.HOME,
            provider="Test Provider",
            policy_number="TEST123",
            premium_amount=1000.00,
            premium_frequency=PremiumFrequency.YEARLY,
            renewal_date=date.today() + timedelta(days=5)
        )
        db_session.add(policy)
        db_session.commit()

        alerts = DashboardService.get_alerts_widget(db_session)

        assert "insurance_renewals" in alerts
        assert "document_expiries" in alerts
        assert "quote_expiries" in alerts
        assert "total_alerts" in alerts

        assert alerts["insurance_renewals"]["urgent"] >= 1

    def test_get_priorities_widget(self, db_session):
        """Test getting priorities widget"""
        # Create priority items
        p1 = PriorityItem(
            name="High Priority",
            description="Test",
            severity=5,
            frequency=5,
            estimated_cost=1000.00,
            status=PriorityStatus.IDENTIFIED
        )
        PriorityItem.calculate_scores(p1)
        db_session.add(p1)
        db_session.commit()

        widget = DashboardService.get_priorities_widget(db_session, limit=10)

        assert "top_priorities" in widget
        assert "total_priorities" in widget
        assert widget["total_priorities"] >= 1

        if len(widget["top_priorities"]) > 0:
            assert "net_score" in widget["top_priorities"][0]

    def test_get_projects_widget(self, db_session):
        """Test getting projects widget"""
        # Create project
        project = Project(
            name="Test Project",
            description="Test description",
            status=ProjectStatus.IN_PROGRESS,
            estimated_cost=5000.00
        )
        db_session.add(project)
        db_session.commit()

        widget = DashboardService.get_projects_widget(db_session)

        assert "status_counts" in widget
        assert "active_projects" in widget

        assert widget["status_counts"]["in_progress"] >= 1

    def test_get_meal_plan_widget_no_plan(self, db_session):
        """Test getting meal plan widget when no plan exists"""
        widget = DashboardService.get_meal_plan_widget(db_session)

        assert "current_week" in widget
        assert widget["current_week"] is None

    def test_get_meal_plan_widget_with_plan(self, db_session):
        """Test getting meal plan widget with existing plan"""
        # Create recipe
        recipe = Recipe(name="Test Recipe", steps="Test steps")
        db_session.add(recipe)
        db_session.flush()

        # Create week plan for current week
        today = date.today()
        monday = WeekPlan.get_monday_of_week(today)

        plan = WeekPlan(
            week_starting=monday,
            monday_meal_id=recipe.id
        )
        db_session.add(plan)
        db_session.commit()

        widget = DashboardService.get_meal_plan_widget(db_session)

        assert widget["current_week"] is not None
        assert "meals" in widget["current_week"]
        assert len(widget["current_week"]["meals"]) == 7

    def test_get_financial_widget(self, db_session):
        """Test getting financial widget"""
        widget = DashboardService.get_financial_widget(db_session)

        assert "monthly_expenses" in widget
        assert "utility_costs_this_month" in widget
        assert "upcoming_insurance_premiums" in widget
        assert "month" in widget

        assert isinstance(widget["monthly_expenses"], float)

    def test_get_notifications_widget(self, db_session, test_user):
        """Test getting notifications widget"""
        # Create notifications
        notification = Notification(
            user_id=test_user.id,
            type=NotificationType.INFO,
            category=NotificationCategory.SYSTEM,
            title="Test Notification",
            message="Test message"
        )
        db_session.add(notification)
        db_session.commit()

        widget = DashboardService.get_notifications_widget(db=db_session, user_id=test_user.id, limit=5)

        assert "recent_notifications" in widget
        assert "unread_count" in widget

        assert widget["unread_count"] >= 1
        assert len(widget["recent_notifications"]) >= 1

    def test_get_quick_stats(self, db_session, test_user):
        """Test getting quick stats"""
        # Create a recipe
        recipe = Recipe(name="Test Recipe", steps="Test steps")
        db_session.add(recipe)
        db_session.commit()

        stats = DashboardService.get_quick_stats(db=db_session, user_id=test_user.id)

        assert "recipes_count" in stats
        assert "knowledge_articles_count" in stats
        assert "active_projects_count" in stats
        assert "priority_items_count" in stats
        assert "insurance_policies_count" in stats
        assert "unread_notifications_count" in stats

        assert stats["recipes_count"] >= 1

    def test_get_tax_summary_widget(self, db_session):
        """Test getting tax summary widget"""
        from app.models.tax_wfh import TaxWFHEntry

        # Create a WFH entry
        today = date.today()
        entry = TaxWFHEntry(
            date=today,
            hours_worked=8.0
        )
        db_session.add(entry)
        db_session.commit()

        widget = DashboardService.get_tax_summary_widget(db_session)

        assert "financial_year" in widget
        assert "wfh_deduction" in widget
        assert "travel_deduction" in widget
        assert "total_deduction" in widget
        assert "wfh_entries_count" in widget
        assert "travel_entries_count" in widget

        assert widget["wfh_entries_count"] >= 1
