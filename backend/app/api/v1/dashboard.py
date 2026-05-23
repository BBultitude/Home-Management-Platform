"""
Dashboard & Notifications API endpoints
Provides dashboard data aggregation, notifications, and global search
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db, require_permission
from app.models.user import User
from app.services.dashboard_service import DashboardService
from app.services.notification_service import NotificationService
from app.services.global_search_service import GlobalSearchService
from app.schemas.dashboard import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkReadRequest,
    DashboardSummaryResponse,
    GlobalSearchResponse,
    QuickSearchResponse,
    TaxSummaryWidget
)
from app.models.notification import NotificationType, NotificationCategory


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# ===== Dashboard Endpoints =====

@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Get comprehensive dashboard summary

    Returns all widget data for the dashboard
    """
    summary = DashboardService.get_dashboard_summary(db, current_user.id)
    return summary


@router.get("/alerts")
async def get_alerts_widget(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get alerts widget (renewals, expiries)"""
    return DashboardService.get_alerts_widget(db)


@router.get("/priorities")
async def get_priorities_widget(
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get top priority items widget"""
    return DashboardService.get_priorities_widget(db, limit)


@router.get("/projects")
async def get_projects_widget(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get projects summary widget"""
    return DashboardService.get_projects_widget(db)


@router.get("/meal-plan")
async def get_meal_plan_widget(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get current week meal plan widget"""
    return DashboardService.get_meal_plan_widget(db)


@router.get("/financial")
async def get_financial_widget(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get financial summary widget"""
    return DashboardService.get_financial_widget(db)


@router.get("/tax-summary", response_model=TaxSummaryWidget)
async def get_tax_summary_widget(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get tax summary widget for current FY"""
    return DashboardService.get_tax_summary_widget(db)


@router.get("/quick-stats")
async def get_quick_stats(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get quick statistics for dashboard header"""
    return DashboardService.get_quick_stats(db, current_user.id)


# ===== Notification Endpoints =====

@router.post("/notifications", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: Annotated[User, Depends(require_permission("admin:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Create a notification (admin only)

    Requires permission: admin:write
    """
    notification = NotificationService.create_notification(
        db=db,
        user_id=current_user.id,
        title=notification_data.title,
        message=notification_data.message,
        type=NotificationType(notification_data.type),
        category=NotificationCategory(notification_data.category),
        action_url=notification_data.action_url,
        action_label=notification_data.action_label
    )

    return NotificationResponse(**notification.to_dict())


@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: Annotated[bool, Query(description="Show only unread notifications")] = False,
    category: Annotated[Optional[str], Query(description="Filter by category")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """List user notifications"""
    category_filter = NotificationCategory(category) if category else None

    notifications = NotificationService.list_notifications(
        db=db,
        user_id=current_user.id,
        unread_only=unread_only,
        category=category_filter,
        limit=limit,
        offset=offset
    )

    unread_count = NotificationService.get_unread_count(db, current_user.id)

    return NotificationListResponse(
        notifications=[NotificationResponse(**n.to_dict()) for n in notifications],
        total=len(notifications),
        unread_count=unread_count
    )


@router.get("/notifications/unread-count")
async def get_unread_count(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Get count of unread notifications"""
    count = NotificationService.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.post("/notifications/mark-read")
async def mark_notifications_read(
    request: NotificationMarkReadRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Mark notifications as read"""
    if request.notification_ids is None:
        # Mark all as read
        count = NotificationService.mark_all_as_read(db, current_user.id)
        return {"message": f"Marked {count} notifications as read"}
    else:
        # Mark specific notifications as read
        from uuid import UUID
        for notification_id in request.notification_ids:
            NotificationService.mark_as_read(db, UUID(notification_id), current_user.id)

        return {"message": f"Marked {len(request.notification_ids)} notifications as read"}


@router.delete("/notifications/{notification_id}")
async def dismiss_notification(
    notification_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Dismiss (soft delete) a notification"""
    from uuid import UUID
    NotificationService.dismiss_notification(db, UUID(notification_id), current_user.id)
    return {"message": "Notification dismissed"}


@router.delete("/notifications")
async def dismiss_all_notifications(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Dismiss all notifications"""
    count = NotificationService.dismiss_all(db, current_user.id)
    return {"message": f"Dismissed {count} notifications"}


# ===== Global Search Endpoints =====

@router.get("/search", response_model=GlobalSearchResponse)
async def global_search(
    q: Annotated[str, Query(..., min_length=2, description="Search query")],
    modules: Annotated[Optional[str], Query(description="Comma-separated list of modules to search")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Global search across all modules

    Modules: recipes, knowledge, projects, priorities, assets, financial
    """
    module_list = None
    if modules:
        module_list = [m.strip() for m in modules.split(",")]

    results = GlobalSearchService.search_all(
        db=db,
        query=q,
        limit=limit,
        modules=module_list
    )

    return results


@router.get("/search/quick", response_model=QuickSearchResponse)
async def quick_search(
    q: Annotated[str, Query(..., min_length=2, description="Search query")],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Quick search for autocomplete

    Returns top results across all modules
    """
    results = GlobalSearchService.quick_search(db, q, limit)

    return QuickSearchResponse(
        query=q,
        results=results,
        total=len(results)
    )


# ===== Notification Generation Endpoints (Admin/System) =====

@router.post("/notifications/generate/renewals")
async def generate_renewal_notifications(
    current_user: Annotated[User, Depends(require_permission("admin:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Generate insurance renewal notifications (admin only)

    Called by scheduled task
    """
    count = NotificationService.generate_renewal_notifications(db)
    return {"message": f"Generated {count} renewal notifications"}


@router.post("/notifications/generate/documents")
async def generate_document_expiry_notifications(
    current_user: Annotated[User, Depends(require_permission("admin:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Generate document expiry notifications (admin only)

    Called by scheduled task
    """
    count = NotificationService.generate_document_expiry_notifications(db)
    return {"message": f"Generated {count} document expiry notifications"}


@router.post("/notifications/generate/quotes")
async def generate_quote_expiry_notifications(
    current_user: Annotated[User, Depends(require_permission("admin:write"))],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Generate quote expiry notifications (admin only)

    Called by scheduled task
    """
    count = NotificationService.generate_quote_expiry_notifications(db)
    return {"message": f"Generated {count} quote expiry notifications"}
