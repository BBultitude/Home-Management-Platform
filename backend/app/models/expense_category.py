"""
Expense Category Model
Represents expense categories linked to bank accounts
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ExpenseCategory(Base):
    """
    Expense category for budget planning

    Links expenses to specific bank accounts for transfer calculations

    Attributes:
        id: Primary key
        category_name: Name of category (e.g., "Rent", "Groceries", "Insurance")
        bank_account_id: Which account pays for this category
        color: Optional color for UI visualization
        created_at: Timestamp when created
        updated_at: Timestamp when last updated
    """
    __tablename__ = "expense_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bank_account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bank_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)  # Hex color #RRGGBB
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    bank_account = relationship("BankAccount", back_populates="expense_categories")
    expenses = relationship("Expense", back_populates="category", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "category_name": self.category_name,
            "bank_account_id": self.bank_account_id,
            "color": self.color,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def __repr__(self) -> str:
        return f"<ExpenseCategory(id={self.id}, name='{self.category_name}', account_id={self.bank_account_id})>"
