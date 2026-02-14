"""
Bank Account Model
Represents bank accounts for budget allocation
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class AccountType(str, Enum):
    """Bank account type"""
    CHECKING = "checking"
    SAVINGS = "savings"
    OFFSET = "offset"

    def __str__(self) -> str:
        return self.value


class BankAccount(Base):
    """
    Bank account for budget allocation

    Attributes:
        id: Primary key
        account_name: Name of account (e.g., "Everyday", "Bills", "Savings")
        account_type: Type of account
        current_balance: Optional current balance tracking
        created_at: Timestamp when created
        updated_at: Timestamp when last updated
    """
    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(
        SQLEnum(AccountType, values_callable=lambda x: [e.value for e in x], name="account_type"),
        nullable=False
    )
    current_balance: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    expense_categories = relationship("ExpenseCategory", back_populates="bank_account", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "account_name": self.account_name,
            "account_type": self.account_type.value,
            "current_balance": float(self.current_balance) if self.current_balance else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def __repr__(self) -> str:
        return f"<BankAccount(id={self.id}, name='{self.account_name}', type={self.account_type})>"
