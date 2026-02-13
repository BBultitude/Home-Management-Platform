"""
Budget Schemas
Pydantic models for budget calculation responses
"""

from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.income_source import IncomeFrequency
from app.models.expense import ExpenseFrequency


class AccountTransfer(BaseModel):
    """Transfer amount needed for a specific account"""
    account_id: int
    account_name: str
    amount: float
    expenses: list[str]  # List of expense names


class BudgetCalculationRequest(BaseModel):
    """Request schema for budget calculation"""
    pay_frequency: IncomeFrequency = Field(..., description="Pay frequency to normalize to")

    model_config = ConfigDict(from_attributes=True)


class BudgetCalculationResponse(BaseModel):
    """Response schema for budget calculation"""
    pay_frequency: str
    total_income: float
    total_expenses: float
    surplus: float
    transfers: list[AccountTransfer]

    model_config = ConfigDict(from_attributes=True)


class BudgetSummaryResponse(BaseModel):
    """Summary of budget for dashboard widget"""
    total_monthly_income: float
    total_monthly_expenses: float
    monthly_surplus: float
    account_allocations: dict[str, float]  # account_name -> amount
