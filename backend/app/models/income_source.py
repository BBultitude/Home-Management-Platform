"""
Income Source Model
Represents household income sources for budget planning
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class IncomeFrequency(str, Enum):
    """Income payment frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    FORTNIGHTLY = "fortnightly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class IncomeSource(Base):
    """
    Income source for household budget planning

    Attributes:
        id: Primary key
        source_name: Name of income source (e.g., "Salary", "Rental Income")
        amount: Income amount in the specified frequency
        frequency: How often income is received
        created_at: Timestamp when created
        updated_at: Timestamp when last updated
    """
    __tablename__ = "income_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    frequency: Mapped[IncomeFrequency] = mapped_column(
        SQLEnum(IncomeFrequency, name="income_frequency"),
        nullable=False
    )
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
            "source_name": self.source_name,
            "amount": float(self.amount),
            "frequency": self.frequency.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def __repr__(self) -> str:
        return f"<IncomeSource(id={self.id}, name='{self.source_name}', amount={self.amount}, frequency={self.frequency})>"
