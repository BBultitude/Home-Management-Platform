"""
Dashboard Service
Aggregates data from all modules for dashboard widgets
"""

from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.insurance_policy import InsurancePolicy
from app.models.document import Document
from app.models.priority_item import PriorityItem, PriorityStatus
from app.models.project import Project, ProjectStatus
from app.models.quote import Quote
from app.models.week_plan import WeekPlan
from app.models.expense import Expense
from app.models.notification import Notification


class DashboardService:
    """Service for dashboard data aggregation"""

    @staticmethod
    def get_dashboard_summary(db: Session, user_id: UUID) -> dict:
        """
        Get comprehensive dashboard summary

        Returns:
            Dictionary with all dashboard widget data
        """
        return {
            "alerts": DashboardService.get_alerts_widget(db),
            "priorities": DashboardService.get_priorities_widget(db),
            "projects": DashboardService.get_projects_widget(db),
            "meal_plan": DashboardService.get_meal_plan_widget(db),
            "financial": DashboardService.get_financial_widget(db),
            "notifications": DashboardService.get_notifications_widget(db, user_id),
            "quick_stats": DashboardService.get_quick_stats(db, user_id),
        }

    @staticmethod
    def get_alerts_widget(db: Session) -> dict:
        """
        Get alerts widget data (renewals, expiries)

        Returns:
            Dictionary with insurance renewals and document expiries
        """
        today = date.today()
        threshold_30 = today + timedelta(days=30)
        threshold_7 = today + timedelta(days=7)

        # Insurance renewals
        renewals_urgent = db.query(InsurancePolicy).filter(
            InsurancePolicy.renewal_date.between(today, threshold_7)
        ).count()

        renewals_upcoming = db.query(InsurancePolicy).filter(
            InsurancePolicy.renewal_date.between(threshold_7, threshold_30)
        ).count()

        # Document expiries
        docs_urgent = db.query(Document).filter(
            Document.expiry_date.isnot(None),
            Document.expiry_date.between(today, threshold_7)
        ).count()

        docs_upcoming = db.query(Document).filter(
            Document.expiry_date.isnot(None),
            Document.expiry_date.between(threshold_7, threshold_30)
        ).count()

        # Quote expiries
        quotes_expiring = db.query(Quote).filter(
            Quote.expires_at.isnot(None),
            Quote.expires_at.between(today, threshold_30),
            Quote.is_selected == False
        ).count()

        return {
            "insurance_renewals": {
                "urgent": renewals_urgent,  # Within 7 days
                "upcoming": renewals_upcoming  # 7-30 days
            },
            "document_expiries": {
                "urgent": docs_urgent,
                "upcoming": docs_upcoming
            },
            "quote_expiries": quotes_expiring,
            "total_alerts": renewals_urgent + docs_urgent + quotes_expiring
        }

    @staticmethod
    def get_priorities_widget(db: Session, limit: int = 10) -> dict:
        """
        Get top priority items widget

        Args:
            db: Database session
            limit: Number of top priorities to return

        Returns:
            Dictionary with top priority items sorted by net_score
        """
        top_priorities = db.query(PriorityItem).filter(
            PriorityItem.status == PriorityStatus.IDENTIFIED
        ).order_by(
            PriorityItem.net_score.desc()
        ).limit(limit).all()

        return {
            "top_priorities": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "net_score": p.net_score,
                    "benefit_score": p.benefit_score,
                    "cost_score": p.cost_score,
                    "estimated_cost": float(p.estimated_cost)
                }
                for p in top_priorities
            ],
            "total_priorities": db.query(PriorityItem).filter(
                PriorityItem.status == PriorityStatus.IDENTIFIED
            ).count()
        }

    @staticmethod
    def get_projects_widget(db: Session) -> dict:
        """
        Get projects widget data

        Returns:
            Dictionary with project counts by status
        """
        status_counts = {}
        for status in ProjectStatus:
            count = db.query(Project).filter(Project.status == status).count()
            status_counts[status.value] = count

        active_projects = db.query(Project).filter(
            Project.status.in_([ProjectStatus.APPROVED, ProjectStatus.IN_PROGRESS])
        ).order_by(Project.created_at.desc()).limit(5).all()

        return {
            "status_counts": status_counts,
            "active_projects": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "status": p.status.value,
                    "estimated_cost": float(p.estimated_cost) if p.estimated_cost else None,
                    "created_at": p.created_at.isoformat()
                }
                for p in active_projects
            ]
        }

    @staticmethod
    def get_meal_plan_widget(db: Session) -> dict:
        """
        Get current week meal plan widget

        Returns:
            Dictionary with current week's meal plan or null if none
        """
        today = date.today()
        monday = WeekPlan.get_monday_of_week(today)

        plan = db.query(WeekPlan).filter(WeekPlan.week_starting == monday).first()

        if not plan:
            return {"current_week": None}

        # Build meals list with names
        meals = []
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for day in days:
            day_attr = f"{day.lower()}_meal_id"
            meal_id = getattr(plan, day_attr)

            meal_name = None
            if meal_id:
                meal_attr = f"{day.lower()}_meal"
                meal = getattr(plan, meal_attr)
                if meal:
                    meal_name = meal.name

            meals.append({
                "day": day,
                "meal_id": str(meal_id) if meal_id else None,
                "meal_name": meal_name
            })

        return {
            "current_week": {
                "week_starting": plan.week_starting.isoformat(),
                "meals": meals,
                "has_shopping_list": any(m["meal_id"] for m in meals)
            }
        }

    @staticmethod
    def get_financial_widget(db: Session) -> dict:
        """
        Get financial summary widget

        Returns:
            Dictionary with financial overview
        """
        # Get this month's expenses
        today = date.today()
        month_start = date(today.year, today.month, 1)
        next_month = month_start + timedelta(days=32)
        month_end = date(next_month.year, next_month.month, 1) - timedelta(days=1)

        # Monthly expenses total
        monthly_expenses = db.query(func.sum(Expense.amount)).filter(
            Expense.expense_date.between(month_start, month_end)
        ).scalar() or 0

        # Upcoming insurance premiums (next 30 days)
        threshold_30 = today + timedelta(days=30)
        upcoming_premiums = db.query(func.sum(InsurancePolicy.premium_amount)).filter(
            InsurancePolicy.renewal_date.between(today, threshold_30)
        ).scalar() or 0

        return {
            "monthly_expenses": float(monthly_expenses),
            "upcoming_insurance_premiums": float(upcoming_premiums),
            "month": today.strftime("%B %Y")
        }

    @staticmethod
    def get_notifications_widget(db: Session, user_id: UUID, limit: int = 5) -> dict:
        """
        Get recent notifications widget

        Args:
            db: Database session
            user_id: User ID
            limit: Number of notifications to return

        Returns:
            Dictionary with recent notifications and unread count
        """
        recent = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_dismissed == False
        ).order_by(
            Notification.created_at.desc()
        ).limit(limit).all()

        unread_count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.is_dismissed == False
        ).count()

        return {
            "recent_notifications": [
                {
                    "id": str(n.id),
                    "type": n.type.value,
                    "title": n.title,
                    "message": n.message,
                    "is_read": n.is_read,
                    "created_at": n.created_at.isoformat()
                }
                for n in recent
            ],
            "unread_count": unread_count
        }

    @staticmethod
    def get_quick_stats(db: Session, user_id: UUID) -> dict:
        """
        Get quick statistics for dashboard header

        Returns:
            Dictionary with quick stats (counts, totals)
        """
        from app.models.recipe import Recipe
        from app.models.knowledge_article import KnowledgeArticle
        from app.models.tax_wfh import TaxWFHEntry

        return {
            "recipes_count": db.query(Recipe).count(),
            "knowledge_articles_count": db.query(KnowledgeArticle).count(),
            "active_projects_count": db.query(Project).filter(
                Project.status.in_([ProjectStatus.APPROVED, ProjectStatus.IN_PROGRESS])
            ).count(),
            "priority_items_count": db.query(PriorityItem).filter(
                PriorityItem.status == PriorityStatus.IDENTIFIED
            ).count(),
            "insurance_policies_count": db.query(InsurancePolicy).count(),
            "unread_notifications_count": db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False,
                Notification.is_dismissed == False
            ).count()
        }

    @staticmethod
    def get_tax_summary_widget(db: Session) -> dict:
        """
        Get tax summary widget for current financial year

        Returns:
            Dictionary with WFH and travel totals for current FY
        """
        from app.models.tax_wfh import TaxWFHEntry
        from app.models.tax_travel import TaxTravelEntry
        from app.services.tax_wfh_service import TaxWFHService
        from app.services.tax_travel_service import TaxTravelService

        # Get current FY dates
        today = date.today()
        if today.month >= 7:
            fy_start = date(today.year, 7, 1)
            fy_end = date(today.year + 1, 6, 30)
        else:
            fy_start = date(today.year - 1, 7, 1)
            fy_end = date(today.year, 6, 30)

        # Get WFH summary
        wfh_entries = db.query(TaxWFHEntry).filter(
            TaxWFHEntry.date.between(fy_start, fy_end)
        ).all()
        wfh_total = TaxWFHService._calculate_ato_total(wfh_entries)

        # Get Travel summary
        travel_entries = db.query(TaxTravelEntry).filter(
            TaxTravelEntry.date.between(fy_start, fy_end)
        ).all()
        travel_total = sum(entry.distance_km for entry in travel_entries) * TaxTravelService.ATO_RATE_PER_KM

        return {
            "financial_year": f"{fy_start.year}-{fy_end.year}",
            "wfh_deduction": float(wfh_total),
            "travel_deduction": float(travel_total),
            "total_deduction": float(wfh_total + travel_total),
            "wfh_entries_count": len(wfh_entries),
            "travel_entries_count": len(travel_entries)
        }
