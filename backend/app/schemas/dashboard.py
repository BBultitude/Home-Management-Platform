"""
Dashboard and Notifications Schemas
Pydantic models for dashboard, notifications, and global search
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# ===== Notification Schemas =====

class NotificationCreate(BaseModel):
    """Schema for creating a notification"""
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    type: str = Field("info", description="Notification type: info, warning, error, success, reminder")
    category: str = Field("system", description="Category: system, tax, financial, assets, projects, knowledge, meals")
    action_url: Optional[str] = Field(None, max_length=500)
    action_label: Optional[str] = Field(None, max_length=100)

    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(BaseModel):
    """Schema for notification response"""
    id: str
    user_id: str
    type: str
    category: str
    title: str
    message: str
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    is_read: bool
    is_dismissed: bool
    created_at: str
    read_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Schema for list of notifications"""
    notifications: list[NotificationResponse]
    total: int
    unread_count: int


class NotificationMarkReadRequest(BaseModel):
    """Schema for marking notifications as read"""
    notification_ids: Optional[list[str]] = Field(None, description="Specific notification IDs (null = all)")


# ===== Dashboard Schemas =====

class AlertsWidget(BaseModel):
    """Schema for alerts widget"""
    insurance_renewals: dict
    document_expiries: dict
    quote_expiries: int
    total_alerts: int


class PrioritiesWidget(BaseModel):
    """Schema for priorities widget"""
    top_priorities: list[dict]
    total_priorities: int


class ProjectsWidget(BaseModel):
    """Schema for projects widget"""
    status_counts: dict
    active_projects: list[dict]


class MealPlanWidget(BaseModel):
    """Schema for meal plan widget"""
    current_week: Optional[dict] = None


class FinancialWidget(BaseModel):
    """Schema for financial widget"""
    monthly_expenses: float
    upcoming_insurance_premiums: float
    month: str


class NotificationsWidget(BaseModel):
    """Schema for notifications widget"""
    recent_notifications: list[dict]
    unread_count: int


class QuickStats(BaseModel):
    """Schema for quick stats"""
    recipes_count: int
    knowledge_articles_count: int
    active_projects_count: int
    priority_items_count: int
    insurance_policies_count: int
    unread_notifications_count: int


class TaxSummaryWidget(BaseModel):
    """Schema for tax summary widget"""
    financial_year: str
    wfh_deduction: float
    travel_deduction: float
    total_deduction: float
    wfh_entries_count: int
    travel_entries_count: int


class DashboardSummaryResponse(BaseModel):
    """Schema for complete dashboard summary"""
    alerts: AlertsWidget
    priorities: PrioritiesWidget
    projects: ProjectsWidget
    meal_plan: MealPlanWidget
    financial: FinancialWidget
    notifications: NotificationsWidget
    quick_stats: QuickStats


# ===== Global Search Schemas =====

class SearchResultItem(BaseModel):
    """Schema for a single search result"""
    id: str
    type: str
    title: str
    subtitle: str
    url: str
    module: str


class GlobalSearchResponse(BaseModel):
    """Schema for global search results"""
    query: str
    total_results: int
    results: dict  # Dict of module name -> list of results


class QuickSearchResponse(BaseModel):
    """Schema for quick search results"""
    query: str
    results: list[SearchResultItem]
    total: int
