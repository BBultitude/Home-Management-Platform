"""
Expense Model
Represents individual expenses in the budget
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ExpenseFrequency(str, Enum):
    """Expense payment frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    FORTNIGHTLY = "fortnightly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

    def __str__(self) -> str:
        return self.value


class Expense(Base):
    """
    Individual expense in household budget

    Attributes:
        id: Primary key
        expense_name: Name of expense (e.g., "Monthly Rent", "Weekly Groceries")
        amount: Expense amount in the specified frequency
        frequency: How often expense occurs
        category_id: Link to expense category (and thus bank account)
        notes: Optional notes
        created_at: Timestamp when created
        updated_at: Timestamp when last updated
    """
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    expense_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    frequency: Mapped[ExpenseFrequency] = mapped_column(
        SQLEnum(ExpenseFrequency, values_callable=lambda x: [e.value for e in x], name="expense_frequency"),
        nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("expense_categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    category = relationship("ExpenseCategory", back_populates="expenses")

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "expense_name": self.expense_name,
            "amount": float(self.amount),
            "frequency": self.frequency.value,
            "category_id": self.category_id,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def __repr__(self) -> str:
        return f"<Expense(id={self.id}, name='{self.expense_name}', amount={self.amount}, frequency={self.frequency})>"
