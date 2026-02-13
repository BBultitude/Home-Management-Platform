"""
Bank Account Schemas
Pydantic models for bank account API requests and responses
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.bank_account import AccountType


class BankAccountCreate(BaseModel):
    """Schema for creating a bank account"""
    account_name: str = Field(..., min_length=1, max_length=255, description="Name of account")
    account_type: AccountType = Field(..., description="Type of account")
    current_balance: Optional[Decimal] = Field(None, description="Current balance (optional)")

    model_config = ConfigDict(from_attributes=True)


class BankAccountUpdate(BaseModel):
    """Schema for updating a bank account"""
    account_name: Optional[str] = Field(None, min_length=1, max_length=255)
    account_type: Optional[AccountType] = None
    current_balance: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)


class BankAccountResponse(BaseModel):
    """Schema for bank account response"""
    id: int
    account_name: str
    account_type: str
    current_balance: Optional[float]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BankAccountListResponse(BaseModel):
    """Schema for list of bank accounts"""
    accounts: list[BankAccountResponse]
    total: int
