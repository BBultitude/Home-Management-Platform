"""
Tax WFH Entry model for tracking work-from-home hours
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, ForeignKey, Date, Numeric, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class TaxWFHEntry(Base):
    """
    Work-from-Home Entry for tax tracking

    Tracks daily WFH hours for ATO deduction purposes.
    Rate: $0.67 per hour (as of 2024 ATO guidelines)
    Unique constraint: one entry per user per day
    """
    __tablename__ = "tax_wfh_entries"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Foreign key to user (owner)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Entry data
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hours: Mapped[Decimal] = mapped_column(
        Numeric(4, 2),
        nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="tax_wfh_entries")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uq_tax_wfh_user_date'),
    )

    def __repr__(self) -> str:
        return f"<TaxWFHEntry(id={self.id}, user_id={self.user_id}, date={self.date}, hours={self.hours})>"

    @property
    def deduction_amount(self) -> Decimal:
        """Calculate ATO deduction amount at $0.67/hour"""
        return self.hours * Decimal("0.67")

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat(),
            "hours": float(self.hours),
            "notes": self.notes,
            "deduction_amount": float(self.deduction_amount),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
