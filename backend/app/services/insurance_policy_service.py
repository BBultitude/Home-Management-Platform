"""
Insurance Policy Service
Handles CRUD operations and renewal alerts for insurance policies
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.insurance_policy import InsurancePolicy, PolicyType, PremiumFrequency


class InsurancePolicyService:
    """Service for insurance policy operations"""

    @staticmethod
    def create_policy(
        db: Session,
        policy_type: PolicyType,
        provider: str,
        premium: Decimal,
        premium_frequency: PremiumFrequency,
        renewal_date: date,
        policy_number: Optional[str] = None,
        coverage_amount: Optional[Decimal] = None,
        excess: Optional[Decimal] = None,
        coverage_notes: Optional[str] = None,
        document_id: Optional[UUID] = None,
        vehicle_id: Optional[UUID] = None
    ) -> InsurancePolicy:
        """Create a new insurance policy"""
        if premium <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Premium must be greater than 0"
            )

        if renewal_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Renewal date cannot be in the past"
            )

        policy = InsurancePolicy(
            policy_type=policy_type.value,
            provider=provider,
            policy_number=policy_number,
            coverage_amount=coverage_amount,
            premium=premium,
            premium_frequency=premium_frequency.value,
            excess=excess,
            renewal_date=renewal_date,
            coverage_notes=coverage_notes,
            document_id=document_id,
            vehicle_id=vehicle_id
        )

        db.add(policy)
        db.commit()
        db.refresh(policy)

        return policy

    @staticmethod
    def get_policy(db: Session, policy_id: UUID) -> InsurancePolicy:
        """Get an insurance policy by ID"""
        policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()

        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Insurance policy not found"
            )

        return policy

    @staticmethod
    def list_policies(
        db: Session,
        policy_type: Optional[PolicyType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[InsurancePolicy]:
        """List insurance policies with optional filters"""
        query = db.query(InsurancePolicy)

        if policy_type:
            query = query.filter(InsurancePolicy.policy_type == policy_type.value)

        query = query.order_by(InsurancePolicy.renewal_date)
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def update_policy(
        db: Session,
        policy_id: UUID,
        policy_type: Optional[PolicyType] = None,
        provider: Optional[str] = None,
        policy_number: Optional[str] = None,
        coverage_amount: Optional[Decimal] = None,
        premium: Optional[Decimal] = None,
        premium_frequency: Optional[PremiumFrequency] = None,
        excess: Optional[Decimal] = None,
        renewal_date: Optional[date] = None,
        coverage_notes: Optional[str] = None,
        document_id: Optional[UUID] = None,
        vehicle_id: Optional[UUID] = None
    ) -> InsurancePolicy:
        """Update an insurance policy"""
        policy = InsurancePolicyService.get_policy(db, policy_id)

        if policy_type is not None:
            policy.policy_type = policy_type.value

        if provider is not None:
            policy.provider = provider

        if policy_number is not None:
            policy.policy_number = policy_number

        if coverage_amount is not None:
            policy.coverage_amount = coverage_amount

        if premium is not None:
            if premium <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Premium must be greater than 0"
                )
            policy.premium = premium

        if premium_frequency is not None:
            policy.premium_frequency = premium_frequency.value

        if excess is not None:
            policy.excess = excess

        if renewal_date is not None:
            if renewal_date < date.today():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Renewal date cannot be in the past"
                )
            policy.renewal_date = renewal_date

        if coverage_notes is not None:
            policy.coverage_notes = coverage_notes

        if document_id is not None:
            policy.document_id = document_id

        if vehicle_id is not None:
            policy.vehicle_id = vehicle_id

        policy.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(policy)

        return policy

    @staticmethod
    def delete_policy(db: Session, policy_id: UUID) -> None:
        """Delete an insurance policy"""
        policy = InsurancePolicyService.get_policy(db, policy_id)

        db.delete(policy)
        db.commit()

    @staticmethod
    def get_renewal_alerts(db: Session, days_threshold: int = 30) -> list[InsurancePolicy]:
        """
        Get policies with upcoming renewals

        Args:
            db: Database session
            days_threshold: Number of days before renewal to alert (default 30)

        Returns:
            List of policies due for renewal within threshold
        """
        today = date.today()
        threshold_date = date.fromordinal(today.toordinal() + days_threshold)

        policies = db.query(InsurancePolicy).filter(
            InsurancePolicy.renewal_date >= today,
            InsurancePolicy.renewal_date <= threshold_date
        ).order_by(InsurancePolicy.renewal_date).all()

        return policies

    @staticmethod
    def get_cost_summary(db: Session) -> dict:
        """
        Get monthly insurance cost summary for budget integration

        Returns:
            Dictionary with total monthly and annual costs
        """
        policies = db.query(InsurancePolicy).all()

        monthly_cost = Decimal("0")
        annual_cost = Decimal("0")

        for policy in policies:
            if policy.premium_frequency == "Monthly":
                monthly_cost += policy.premium
                annual_cost += policy.premium * 12
            else:  # Annually
                monthly_cost += policy.premium / 12
                annual_cost += policy.premium

        return {
            "total_monthly_cost": float(monthly_cost),
            "total_annual_cost": float(annual_cost),
            "policy_count": len(policies)
        }
