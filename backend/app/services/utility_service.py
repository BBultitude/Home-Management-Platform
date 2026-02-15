"""
Utility Service
Handles CRUD operations and statistics for utility cost tracking
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from fastapi import HTTPException, status

from app.models.utility import Utility, UtilityType


class UtilityService:
    """Service for utility operations"""

    @staticmethod
    def create_utility(
        db: Session,
        utility_type: UtilityType,
        provider: str,
        billing_period_start: date,
        billing_period_end: date,
        usage: Decimal,
        unit: str,
        cost: Decimal,
        attachment_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Utility:
        """Create a new utility entry"""
        if usage <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usage must be greater than 0"
            )

        if cost <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cost must be greater than 0"
            )

        if billing_period_end <= billing_period_start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )

        # Calculate cost per unit
        cost_per_unit = cost / usage

        utility = Utility(
            utility_type=utility_type,
            provider=provider,
            billing_period_start=billing_period_start,
            billing_period_end=billing_period_end,
            usage=usage,
            unit=unit,
            cost=cost,
            cost_per_unit=cost_per_unit,
            attachment_id=attachment_id,
            notes=notes
        )

        db.add(utility)
        db.commit()
        db.refresh(utility)

        return utility

    @staticmethod
    def get_utility(db: Session, utility_id: int) -> Utility:
        """Get a utility by ID"""
        utility = db.query(Utility).filter(Utility.id == utility_id).first()

        if not utility:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utility entry not found"
            )

        return utility

    @staticmethod
    def list_utilities(
        db: Session,
        utility_type: Optional[UtilityType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Utility]:
        """List utilities with optional filters"""
        query = db.query(Utility)

        if utility_type:
            query = query.filter(Utility.utility_type == utility_type)

        if start_date:
            query = query.filter(Utility.billing_period_start >= start_date)

        if end_date:
            query = query.filter(Utility.billing_period_end <= end_date)

        query = query.order_by(Utility.billing_period_start.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def update_utility(
        db: Session,
        utility_id: int,
        utility_type: Optional[UtilityType] = None,
        provider: Optional[str] = None,
        billing_period_start: Optional[date] = None,
        billing_period_end: Optional[date] = None,
        usage: Optional[Decimal] = None,
        unit: Optional[str] = None,
        cost: Optional[Decimal] = None,
        attachment_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Utility:
        """Update a utility entry"""
        utility = UtilityService.get_utility(db, utility_id)

        if utility_type is not None:
            utility.utility_type = utility_type

        if provider is not None:
            utility.provider = provider

        if billing_period_start is not None:
            utility.billing_period_start = billing_period_start

        if billing_period_end is not None:
            utility.billing_period_end = billing_period_end

        if usage is not None:
            if usage <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Usage must be greater than 0"
                )
            utility.usage = usage

        if unit is not None:
            utility.unit = unit

        if cost is not None:
            if cost <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cost must be greater than 0"
                )
            utility.cost = cost

        # Recalculate cost per unit if usage or cost changed
        if usage is not None or cost is not None:
            utility.cost_per_unit = utility.cost / utility.usage

        if attachment_id is not None:
            utility.attachment_id = attachment_id

        if notes is not None:
            utility.notes = notes

        utility.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(utility)

        return utility

    @staticmethod
    def delete_utility(db: Session, utility_id: int) -> None:
        """Delete a utility entry"""
        utility = UtilityService.get_utility(db, utility_id)

        db.delete(utility)
        db.commit()

    @staticmethod
    def get_utility_stats(
        db: Session,
        utility_type: UtilityType,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Get statistics for a utility type

        Args:
            db: Database session
            utility_type: Type of utility
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dictionary with utility statistics
        """
        query = db.query(
            func.avg(Utility.cost).label('avg_cost'),
            func.sum(Utility.usage).label('total_usage'),
            func.sum(Utility.cost).label('total_cost'),
            func.count(Utility.id).label('count'),
            func.min(Utility.billing_period_start).label('period_start'),
            func.max(Utility.billing_period_end).label('period_end')
        ).filter(Utility.utility_type == utility_type)

        if start_date:
            query = query.filter(Utility.billing_period_start >= start_date)

        if end_date:
            query = query.filter(Utility.billing_period_end <= end_date)

        result = query.first()

        return {
            "utility_type": utility_type.value,
            "average_cost": float(result.avg_cost) if result.avg_cost else 0.0,
            "total_usage": float(result.total_usage) if result.total_usage else 0.0,
            "total_cost": float(result.total_cost) if result.total_cost else 0.0,
            "entry_count": result.count,
            "period_start": result.period_start,
            "period_end": result.period_end
        }

    @staticmethod
    def get_utility_graphs(
        db: Session,
        utility_type: UtilityType,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Get graph data for a utility type

        Returns:
        - Monthly time-series data (cost, usage, cost per unit)
        - Provider comparison
        - Rolling 12-month averages

        Args:
            db: Database session
            utility_type: Type of utility
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Dictionary with graph data
        """
        # Base query for the utility type
        base_query = db.query(Utility).filter(Utility.utility_type == utility_type)

        if start_date:
            base_query = base_query.filter(Utility.billing_period_start >= start_date)

        if end_date:
            base_query = base_query.filter(Utility.billing_period_end <= end_date)

        # Get all entries for processing
        all_entries = base_query.order_by(Utility.billing_period_start).all()

        # Monthly aggregation
        monthly_query = db.query(
            func.to_char(Utility.billing_period_start, 'YYYY-MM').label('month'),
            func.sum(Utility.cost).label('total_cost'),
            func.sum(Utility.usage).label('total_usage'),
            func.avg(Utility.cost_per_unit).label('avg_cost_per_unit'),
            func.count(Utility.id).label('count')
        ).filter(Utility.utility_type == utility_type)

        if start_date:
            monthly_query = monthly_query.filter(Utility.billing_period_start >= start_date)

        if end_date:
            monthly_query = monthly_query.filter(Utility.billing_period_end <= end_date)

        monthly_query = monthly_query.group_by('month').order_by('month')
        monthly_results = monthly_query.all()

        monthly_data = [
            {
                "month": row.month,
                "cost": float(row.total_cost) if row.total_cost else 0.0,
                "usage": float(row.total_usage) if row.total_usage else 0.0,
                "cost_per_unit": float(row.avg_cost_per_unit) if row.avg_cost_per_unit else 0.0,
                "entry_count": row.count
            }
            for row in monthly_results
        ]

        # Provider comparison
        provider_query = db.query(
            Utility.provider,
            func.sum(Utility.cost).label('total_cost'),
            func.sum(Utility.usage).label('total_usage'),
            func.avg(Utility.cost_per_unit).label('avg_cost_per_unit'),
            func.count(Utility.id).label('count'),
            func.min(Utility.billing_period_start).label('period_start'),
            func.max(Utility.billing_period_end).label('period_end')
        ).filter(Utility.utility_type == utility_type)

        if start_date:
            provider_query = provider_query.filter(Utility.billing_period_start >= start_date)

        if end_date:
            provider_query = provider_query.filter(Utility.billing_period_end <= end_date)

        provider_query = provider_query.group_by(Utility.provider).order_by(func.sum(Utility.cost).desc())
        provider_results = provider_query.all()

        provider_comparison = [
            {
                "provider": row.provider,
                "total_cost": float(row.total_cost) if row.total_cost else 0.0,
                "total_usage": float(row.total_usage) if row.total_usage else 0.0,
                "average_cost_per_unit": float(row.avg_cost_per_unit) if row.avg_cost_per_unit else 0.0,
                "entry_count": row.count,
                "period_start": row.period_start,
                "period_end": row.period_end
            }
            for row in provider_results
        ]

        # Calculate 12-month rolling averages (use last 12 months of monthly data)
        rolling_12_month_avg_cost = 0.0
        rolling_12_month_avg_usage = 0.0

        if monthly_data:
            # Take last 12 months (or all if less than 12)
            recent_months = monthly_data[-12:]
            if recent_months:
                rolling_12_month_avg_cost = sum(m["cost"] for m in recent_months) / len(recent_months)
                rolling_12_month_avg_usage = sum(m["usage"] for m in recent_months) / len(recent_months)

        return {
            "utility_type": utility_type.value,
            "monthly_data": monthly_data,
            "provider_comparison": provider_comparison,
            "rolling_12_month_avg_cost": rolling_12_month_avg_cost,
            "rolling_12_month_avg_usage": rolling_12_month_avg_usage,
            "total_entries": len(all_entries)
        }
