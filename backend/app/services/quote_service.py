"""
Quote Service
Handles CRUD operations for contractor quotes
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.quote import Quote
from app.models.project import Project


def _validate_quote_amount(quote_amount: Decimal) -> None:
    if quote_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quote amount must be greater than 0"
        )


def _deselect_other_quotes(db: Session, quote: Quote) -> None:
    db.query(Quote).filter(
        Quote.project_id == quote.project_id,
        Quote.id != quote.id
    ).update({"selected": False})


class QuoteService:
    """Service for quote operations"""

    @staticmethod
    def create_quote(
        db: Session,
        project_id: UUID,
        contractor_name: str,
        quote_amount: Decimal,
        quote_date: date,
        contact_phone: Optional[str] = None,
        contact_email: Optional[str] = None,
        expiry_date: Optional[date] = None,
        scope_of_work: Optional[str] = None,
        selected: bool = False,
        document_id: Optional[UUID] = None,
        notes: Optional[str] = None
    ) -> Quote:
        """Create a new quote"""
        # Verify project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        if quote_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quote amount must be greater than 0"
            )

        if expiry_date and expiry_date < quote_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expiry date cannot be before quote date"
            )

        quote = Quote(
            project_id=project_id,
            contractor_name=contractor_name,
            contact_phone=contact_phone,
            contact_email=contact_email,
            quote_amount=quote_amount,
            quote_date=quote_date,
            expiry_date=expiry_date,
            scope_of_work=scope_of_work,
            selected=selected,
            document_id=document_id,
            notes=notes
        )

        db.add(quote)
        db.commit()
        db.refresh(quote)

        return quote

    @staticmethod
    def get_quote(db: Session, quote_id: UUID) -> Quote:
        """Get a quote by ID"""
        quote = db.query(Quote).filter(Quote.id == quote_id).first()

        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found"
            )

        return quote

    @staticmethod
    def list_quotes(
        db: Session,
        project_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Quote]:
        """List quotes with optional project filter"""
        query = db.query(Quote)

        if project_id:
            query = query.filter(Quote.project_id == project_id)

        query = query.order_by(Quote.quote_date.desc())
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def update_quote(
        db: Session,
        quote_id: UUID,
        contractor_name: Optional[str] = None,
        contact_phone: Optional[str] = None,
        contact_email: Optional[str] = None,
        quote_amount: Optional[Decimal] = None,
        quote_date: Optional[date] = None,
        expiry_date: Optional[date] = None,
        scope_of_work: Optional[str] = None,
        selected: Optional[bool] = None,
        document_id: Optional[UUID] = None,
        notes: Optional[str] = None
    ) -> Quote:
        """Update a quote"""
        quote = QuoteService.get_quote(db, quote_id)

        if contractor_name is not None:
            quote.contractor_name = contractor_name

        if contact_phone is not None:
            quote.contact_phone = contact_phone

        if contact_email is not None:
            quote.contact_email = contact_email

        if quote_amount is not None:
            _validate_quote_amount(quote_amount)
            quote.quote_amount = quote_amount

        if quote_date is not None:
            quote.quote_date = quote_date

        if expiry_date is not None:
            quote.expiry_date = expiry_date

        # Validate date logic
        if quote.expiry_date and quote.expiry_date < quote.quote_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expiry date cannot be before quote date"
            )

        if scope_of_work is not None:
            quote.scope_of_work = scope_of_work

        if selected is not None:
            if selected:
                _deselect_other_quotes(db, quote)
            quote.selected = selected

        if document_id is not None:
            quote.document_id = document_id

        if notes is not None:
            quote.notes = notes

        db.commit()
        db.refresh(quote)

        return quote

    @staticmethod
    def delete_quote(db: Session, quote_id: UUID) -> None:
        """Delete a quote"""
        quote = QuoteService.get_quote(db, quote_id)

        db.delete(quote)
        db.commit()

    @staticmethod
    def get_quote_comparison(db: Session, project_id: UUID) -> dict:
        """
        Get quote comparison for a project

        Returns:
            Dictionary with all quotes, lowest quote, and selected quote
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )

        quotes = db.query(Quote).filter(Quote.project_id == project_id).all()

        if not quotes:
            return {
                "project_id": str(project_id),
                "project_name": project.project_name,
                "quotes": [],
                "lowest_quote": None,
                "selected_quote": None
            }

        # Find lowest and selected quotes
        lowest_quote = min(quotes, key=lambda q: q.quote_amount)
        selected_quote = next((q for q in quotes if q.selected), None)

        return {
            "project_id": str(project_id),
            "project_name": project.project_name,
            "quotes": quotes,
            "lowest_quote": lowest_quote,
            "selected_quote": selected_quote
        }

    @staticmethod
    def get_expiry_alerts(db: Session, days_threshold: int = 30) -> list[Quote]:
        """
        Get quotes with upcoming expiry dates

        Args:
            db: Database session
            days_threshold: Number of days before expiry to alert (default 30)

        Returns:
            List of quotes expiring within threshold
        """
        today = date.today()
        threshold_date = date.fromordinal(today.toordinal() + days_threshold)

        quotes = db.query(Quote).filter(
            Quote.expiry_date.isnot(None),
            Quote.expiry_date >= today,
            Quote.expiry_date <= threshold_date
        ).order_by(Quote.expiry_date).all()

        return quotes
