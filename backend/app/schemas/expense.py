"""
Expense and Expense Category Schemas
Pydantic models for expense API requests and responses
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.expense import ExpenseFrequency


class ExpenseCategoryCreate(BaseModel):
    """Schema for creating an expense category"""
    category_name: str = Field(..., min_length=1, max_length=255, description="Name of category")
    bank_account_id: int = Field(..., description="Bank account ID this category belongs to")
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Hex color code")

    model_config = ConfigDict(from_attributes=True)


class ExpenseCategoryUpdate(BaseModel):
    """Schema for updating an expense category"""
    category_name: Optional[str] = Field(None, min_length=1, max_length=255)
    bank_account_id: Optional[int] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")

    model_config = ConfigDict(from_attributes=True)


class ExpenseCategoryResponse(BaseModel):
    """Schema for expense category response"""
    id: int
    category_name: str
    bank_account_id: int
    color: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseCreate(BaseModel):
    """Schema for creating an expense"""
    expense_name: str = Field(..., min_length=1, max_length=255, description="Name of expense")
    amount: Decimal = Field(..., gt=0, description="Expense amount")
    frequency: ExpenseFrequency = Field(..., description="Payment frequency")
    category_id: int = Field(..., description="Expense category ID")
    notes: Optional[str] = Field(None, max_length=1000)

    model_config = ConfigDict(from_attributes=True)


class ExpenseUpdate(BaseModel):
    """Schema for updating an expense"""
    expense_name: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0)
    frequency: Optional[ExpenseFrequency] = None
    category_id: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=1000)

    model_config = ConfigDict(from_attributes=True)


class ExpenseResponse(BaseModel):
    """Schema for expense response"""
    id: int
    expense_name: str
    amount: float
    frequency: str
    category_id: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpenseListResponse(BaseModel):
    """Schema for list of expenses"""
    expenses: list[ExpenseResponse]
    total: int


class ExpenseCategoryListResponse(BaseModel):
    """Schema for list of expense categories"""
    categories: list[ExpenseCategoryResponse]
    total: int
