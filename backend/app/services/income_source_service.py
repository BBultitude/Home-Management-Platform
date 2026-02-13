"""
Income Source Service
Handles CRUD operations for income sources
"""

from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.income_source import IncomeSource, IncomeFrequency


class IncomeSourceService:
    """Service for income source operations"""

    @staticmethod
    def create_income_source(
        db: Session,
        source_name: str,
        amount: Decimal,
        frequency: IncomeFrequency
    ) -> IncomeSource:
        """
        Create a new income source

        Args:
            db: Database session
            source_name: Name of income source
            amount: Income amount
            frequency: Payment frequency

        Returns:
            Created IncomeSource

        Raises:
            HTTPException: If validation fails
        """
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than 0"
            )

        income_source = IncomeSource(
            source_name=source_name,
            amount=amount,
            frequency=frequency
        )

        db.add(income_source)
        db.commit()
        db.refresh(income_source)

        return income_source

    @staticmethod
    def get_income_source(db: Session, income_id: int) -> IncomeSource:
        """
        Get an income source by ID

        Args:
            db: Database session
            income_id: Income source ID

        Returns:
            IncomeSource

        Raises:
            HTTPException: If not found
        """
        income_source = db.query(IncomeSource).filter(IncomeSource.id == income_id).first()

        if not income_source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Income source not found"
            )

        return income_source

    @staticmethod
    def list_income_sources(
        db: Session,
        limit: int = 100,
        offset: int = 0
    ) -> list[IncomeSource]:
        """
        List all income sources

        Args:
            db: Database session
            limit: Maximum entries to return
            offset: Pagination offset

        Returns:
            List of IncomeSource objects
        """
        query = db.query(IncomeSource)
        query = query.order_by(IncomeSource.created_at.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def update_income_source(
        db: Session,
        income_id: int,
        source_name: Optional[str] = None,
        amount: Optional[Decimal] = None,
        frequency: Optional[IncomeFrequency] = None
    ) -> IncomeSource:
        """
        Update an income source

        Args:
            db: Database session
            income_id: Income source ID
            source_name: Updated name (optional)
            amount: Updated amount (optional)
            frequency: Updated frequency (optional)

        Returns:
            Updated IncomeSource

        Raises:
            HTTPException: If not found or validation fails
        """
        income_source = IncomeSourceService.get_income_source(db, income_id)

        if source_name is not None:
            income_source.source_name = source_name

        if amount is not None:
            if amount <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Amount must be greater than 0"
                )
            income_source.amount = amount

        if frequency is not None:
            income_source.frequency = frequency

        db.commit()
        db.refresh(income_source)

        return income_source

    @staticmethod
    def delete_income_source(db: Session, income_id: int) -> None:
        """
        Delete an income source

        Args:
            db: Database session
            income_id: Income source ID

        Raises:
            HTTPException: If not found
        """
        income_source = IncomeSourceService.get_income_source(db, income_id)

        db.delete(income_source)
        db.commit()
