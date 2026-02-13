"""
Tax Travel Entry model for tracking work-related vehicle travel
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, DateTime, Integer, ForeignKey, Date, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class TaxTravelEntry(Base):
    """
    Work Travel Entry for tax tracking

    Tracks work-related vehicle travel for ATO logbook purposes.
    User must provide per-km rate (varies by vehicle).
    """
    __tablename__ = "tax_travel_entries"

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
    purpose: Mapped[str] = mapped_column(String(255), nullable=False)
    start_location: Mapped[str] = mapped_column(String(255), nullable=False)
    end_location: Mapped[str] = mapped_column(String(255), nullable=False)
    distance_km: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
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
    user: Mapped["User"] = relationship("User", back_populates="tax_travel_entries")

    def __repr__(self) -> str:
        return f"<TaxTravelEntry(id={self.id}, user_id={self.user_id}, date={self.date}, distance_km={self.distance_km})>"

    def calculate_deduction(self, rate_per_km: Decimal) -> Decimal:
        """Calculate deduction amount based on user-provided rate"""
        return self.distance_km * rate_per_km

    def to_dict(self, rate_per_km: Decimal | None = None) -> dict:
        """Convert to dictionary for API responses"""
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat(),
            "purpose": self.purpose,
            "start_location": self.start_location,
            "end_location": self.end_location,
            "distance_km": float(self.distance_km),
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

        if rate_per_km is not None:
            result["deduction_amount"] = float(self.calculate_deduction(rate_per_km))

        return result
