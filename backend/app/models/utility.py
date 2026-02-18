"""
Utility Model
Represents utility cost tracking entries (electricity, gas, water, etc.)
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class UtilityType(str, Enum):
    """Types of utilities"""
    ELECTRICITY = "electricity"
    GAS = "gas"
    WATER = "water"
    RATES = "rates"  # Council rates/land tax

    def __str__(self) -> str:
        return self.value


class Utility(Base):
    """
    Utility cost tracking entry

    Attributes:
        id: Primary key
        utility_type: Type of utility
        provider: Provider name
        billing_period_start: Start date of billing period
        billing_period_end: End date of billing period
        usage: Usage amount (optional for fixed-cost utilities like rates)
        unit: Unit of measurement ("kWh", "bottles" for gas, "m³", None for rates)
        cost: Total cost for billing period
        cost_per_unit: Calculated cost per unit (None if no usage)
        solar_feed_in: Amount of electricity fed back to grid (kWh, electricity only)
        solar_feed_in_credit: Credit received for solar feed-in ($)
        attachment_id: Optional link to bill PDF file
        notes: Optional notes
        created_at: Timestamp when created
        updated_at: Timestamp when last updated
    """
    __tablename__ = "utilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    utility_type: Mapped[UtilityType] = mapped_column(
        SQLEnum(UtilityType, values_callable=lambda x: [e.value for e in x], name="utility_type"),
        nullable=False,
        index=True
    )
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    billing_period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    billing_period_end: Mapped[date] = mapped_column(Date, nullable=False)
    usage: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)  # Nullable for fixed-cost utilities (rates)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "kWh", "bottles", "m³", or None for rates
    cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cost_per_unit: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)  # Calculated if usage provided
    solar_feed_in: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)  # Electricity fed to grid (kWh)
    solar_feed_in_credit: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)  # Credit for feed-in ($)
    attachment_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True
    )
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "utility_type": self.utility_type.value,
            "provider": self.provider,
            "billing_period_start": self.billing_period_start.isoformat(),
            "billing_period_end": self.billing_period_end.isoformat(),
            "usage": float(self.usage) if self.usage is not None else None,
            "unit": self.unit,
            "cost": float(self.cost),
            "cost_per_unit": float(self.cost_per_unit) if self.cost_per_unit is not None else None,
            "solar_feed_in": float(self.solar_feed_in) if self.solar_feed_in is not None else None,
            "solar_feed_in_credit": float(self.solar_feed_in_credit) if self.solar_feed_in_credit is not None else None,
            "attachment_id": self.attachment_id,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def __repr__(self) -> str:
        return f"<Utility(id={self.id}, type={self.utility_type}, provider='{self.provider}', cost={self.cost})>"
