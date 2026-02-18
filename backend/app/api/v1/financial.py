"""
Financial Management API endpoints
Handles income sources, bank accounts, expenses, utilities, and budget calculations
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db, require_permission
from app.models.user import User
from app.models.income_source import IncomeFrequency
from app.models.bank_account import AccountType
from app.models.expense import ExpenseFrequency
from app.models.utility import UtilityType
from app.services.income_source_service import IncomeSourceService
from app.services.budget_service import BudgetService
from app.services.utility_service import UtilityService
from app.services.bank_account_service import BankAccountService
from app.services.expense_service import ExpenseCategoryService, ExpenseService
from app.schemas.income_source import (
    IncomeSourceCreate,
    IncomeSourceUpdate,
    IncomeSourceResponse,
    IncomeSourceListResponse
)
from app.schemas.budget import (
    BudgetCalculationRequest,
    BudgetCalculationResponse,
    BudgetSummaryResponse
)
from app.schemas.utility import (
    UtilityCreate,
    UtilityUpdate,
    UtilityResponse,
    UtilityListResponse,
    UtilityStatsResponse,
    UtilityGraphsResponse
)
from app.schemas.bank_account import (
    BankAccountCreate,
    BankAccountUpdate,
    BankAccountResponse,
    BankAccountListResponse
)
from app.schemas.expense import (
    ExpenseCategoryCreate,
    ExpenseCategoryUpdate,
    ExpenseCategoryResponse,
    ExpenseCategoryListResponse,
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseListResponse
)


router = APIRouter(prefix="/financial", tags=["financial"])


# Income Sources
@router.post("/income", response_model=IncomeSourceResponse)
async def create_income_source(
    income_data: IncomeSourceCreate,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """
    Create a new income source

    Requires permission: financial:write
    """
    income = IncomeSourceService.create_income_source(
        db=db,
        source_name=income_data.source_name,
        amount=income_data.amount,
        frequency=income_data.frequency
    )

    return IncomeSourceResponse(
        id=income.id,
        source_name=income.source_name,
        amount=float(income.amount),
        frequency=income.frequency.value,
        created_at=income.created_at,
        updated_at=income.updated_at
    )


@router.get("/income", response_model=IncomeSourceListResponse)
async def list_income_sources(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all income sources"""
    income_sources = IncomeSourceService.list_income_sources(
        db=db,
        limit=limit,
        offset=offset
    )

    income_responses = [
        IncomeSourceResponse(
            id=i.id,
            source_name=i.source_name,
            amount=float(i.amount),
            frequency=i.frequency.value,
            created_at=i.created_at,
            updated_at=i.updated_at
        )
        for i in income_sources
    ]

    return IncomeSourceListResponse(
        income_sources=income_responses,
        total=len(income_sources)
    )


@router.get("/income/{income_id}", response_model=IncomeSourceResponse)
async def get_income_source(
    income_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific income source"""
    income = IncomeSourceService.get_income_source(db, income_id)

    return IncomeSourceResponse(
        id=income.id,
        source_name=income.source_name,
        amount=float(income.amount),
        frequency=income.frequency.value,
        created_at=income.created_at,
        updated_at=income.updated_at
    )


@router.put("/income/{income_id}", response_model=IncomeSourceResponse)
async def update_income_source(
    income_id: int,
    income_data: IncomeSourceUpdate,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """Update an income source"""
    income = IncomeSourceService.update_income_source(
        db=db,
        income_id=income_id,
        source_name=income_data.source_name,
        amount=income_data.amount,
        frequency=income_data.frequency
    )

    return IncomeSourceResponse(
        id=income.id,
        source_name=income.source_name,
        amount=float(income.amount),
        frequency=income.frequency.value,
        created_at=income.created_at,
        updated_at=income.updated_at
    )


@router.delete("/income/{income_id}")
async def delete_income_source(
    income_id: int,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """Delete an income source"""
    IncomeSourceService.delete_income_source(db, income_id)

    return {"message": "Income source deleted successfully", "id": income_id}


# Budget Calculations
@router.post("/budget/calculate", response_model=BudgetCalculationResponse)
async def calculate_budget(
    request: BudgetCalculationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Calculate budget transfers for specified pay frequency

    Returns transfer amounts needed per bank account
    """
    result = BudgetService.calculate_budget(db, request.pay_frequency)

    return BudgetCalculationResponse(**result)


@router.get("/budget/summary", response_model=BudgetSummaryResponse)
async def get_budget_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get monthly budget summary for dashboard

    Returns total income, expenses, and account allocations
    """
    result = BudgetService.get_budget_summary(db)

    return BudgetSummaryResponse(**result)


# Utilities
@router.post("/utilities", response_model=UtilityResponse)
async def create_utility(
    utility_data: UtilityCreate,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """
    Create a new utility entry

    Requires permission: financial:write
    """
    utility = UtilityService.create_utility(
        db=db,
        utility_type=utility_data.utility_type,
        provider=utility_data.provider,
        billing_period_start=utility_data.billing_period_start,
        billing_period_end=utility_data.billing_period_end,
        usage=utility_data.usage,
        unit=utility_data.unit,
        cost=utility_data.cost,
        solar_feed_in=utility_data.solar_feed_in,
        solar_feed_in_credit=utility_data.solar_feed_in_credit,
        attachment_id=utility_data.attachment_id,
        notes=utility_data.notes
    )

    return UtilityResponse(**utility.to_dict())


@router.get("/utilities", response_model=UtilityListResponse)
async def list_utilities(
    utility_type: Optional[UtilityType] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List utility entries with optional filters"""
    utilities = UtilityService.list_utilities(
        db=db,
        utility_type=utility_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )

    utility_responses = [UtilityResponse(**u.to_dict()) for u in utilities]

    return UtilityListResponse(
        utilities=utility_responses,
        total=len(utilities)
    )


@router.get("/utilities/{utility_id}", response_model=UtilityResponse)
async def get_utility(
    utility_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific utility entry"""
    utility = UtilityService.get_utility(db, utility_id)

    return UtilityResponse(**utility.to_dict())


@router.put("/utilities/{utility_id}", response_model=UtilityResponse)
async def update_utility(
    utility_id: int,
    utility_data: UtilityUpdate,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """Update a utility entry"""
    utility = UtilityService.update_utility(
        db=db,
        utility_id=utility_id,
        utility_type=utility_data.utility_type,
        provider=utility_data.provider,
        billing_period_start=utility_data.billing_period_start,
        billing_period_end=utility_data.billing_period_end,
        usage=utility_data.usage,
        unit=utility_data.unit,
        cost=utility_data.cost,
        solar_feed_in=utility_data.solar_feed_in,
        solar_feed_in_credit=utility_data.solar_feed_in_credit,
        attachment_id=utility_data.attachment_id,
        notes=utility_data.notes
    )

    return UtilityResponse(**utility.to_dict())


@router.delete("/utilities/{utility_id}")
async def delete_utility(
    utility_id: int,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """Delete a utility entry"""
    UtilityService.delete_utility(db, utility_id)

    return {"message": "Utility entry deleted successfully", "id": utility_id}


@router.get("/utilities/stats/{utility_type}", response_model=UtilityStatsResponse)
async def get_utility_stats(
    utility_type: UtilityType,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics for a utility type

    Returns average cost, total usage, and other metrics
    """
    stats = UtilityService.get_utility_stats(
        db=db,
        utility_type=utility_type,
        start_date=start_date,
        end_date=end_date
    )

    return UtilityStatsResponse(**stats)


@router.get("/utilities/graphs/{utility_type}", response_model=UtilityGraphsResponse)
async def get_utility_graphs(
    utility_type: UtilityType,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get graph data for a utility type

    Returns:
    - Monthly time-series data (cost, usage, cost per unit)
    - Provider comparison
    - Rolling 12-month averages
    """
    graphs = UtilityService.get_utility_graphs(
        db=db,
        utility_type=utility_type,
        start_date=start_date,
        end_date=end_date
    )

    return UtilityGraphsResponse(**graphs)


# Bank Accounts
@router.post("/bank-accounts", response_model=BankAccountResponse)
async def create_bank_account(
    account_data: BankAccountCreate,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """
    Create a new bank account

    Requires permission: financial:write
    """
    account = BankAccountService.create_bank_account(
        db=db,
        account_name=account_data.account_name,
        account_type=account_data.account_type,
        current_balance=account_data.current_balance
    )

    return BankAccountResponse(
        id=account.id,
        account_name=account.account_name,
        account_type=account.account_type.value,
        current_balance=float(account.current_balance) if account.current_balance else None,
        created_at=account.created_at,
        updated_at=account.updated_at
    )


@router.get("/bank-accounts", response_model=BankAccountListResponse)
async def list_bank_accounts(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all bank accounts"""
    accounts = BankAccountService.list_bank_accounts(
        db=db,
        limit=limit,
        offset=offset
    )

    account_responses = [
        BankAccountResponse(
            id=a.id,
            account_name=a.account_name,
            account_type=a.account_type.value,
            current_balance=float(a.current_balance) if a.current_balance else None,
            created_at=a.created_at,
            updated_at=a.updated_at
        )
        for a in accounts
    ]

    return BankAccountListResponse(
        accounts=account_responses,
        total=len(accounts)
    )


@router.get("/bank-accounts/{account_id}", response_model=BankAccountResponse)
async def get_bank_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific bank account"""
    account = BankAccountService.get_bank_account(db, account_id)

    return BankAccountResponse(
        id=account.id,
        account_name=account.account_name,
        account_type=account.account_type.value,
        current_balance=float(account.current_balance) if account.current_balance else None,
        created_at=account.created_at,
        updated_at=account.updated_at
    )


@router.put("/bank-accounts/{account_id}", response_model=BankAccountResponse)
async def update_bank_account(
    account_id: int,
    account_data: BankAccountUpdate,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """Update a bank account"""
    account = BankAccountService.update_bank_account(
        db=db,
        account_id=account_id,
        account_name=account_data.account_name,
        account_type=account_data.account_type,
        current_balance=account_data.current_balance
    )

    return BankAccountResponse(
        id=account.id,
        account_name=account.account_name,
        account_type=account.account_type.value,
        current_balance=float(account.current_balance) if account.current_balance else None,
        created_at=account.created_at,
        updated_at=account.updated_at
    )


@router.delete("/bank-accounts/{account_id}")
async def delete_bank_account(
    account_id: int,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """Delete a bank account"""
    BankAccountService.delete_bank_account(db, account_id)

    return {"message": "Bank account deleted successfully", "id": account_id}


# Expense Categories
@router.post("/expense-categories", response_model=ExpenseCategoryResponse)
async def create_expense_category(
    category_data: ExpenseCategoryCreate,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """
    Create a new expense category

    Requires permission: financial:write
    """
    category = ExpenseCategoryService.create_expense_category(
        db=db,
        category_name=category_data.category_name,
        bank_account_id=category_data.bank_account_id,
        color=category_data.color
    )

    return ExpenseCategoryResponse(
        id=category.id,
        category_name=category.category_name,
        bank_account_id=category.bank_account_id,
        color=category.color,
        created_at=category.created_at,
        updated_at=category.updated_at
    )


@router.get("/expense-categories", response_model=ExpenseCategoryListResponse)
async def list_expense_categories(
    bank_account_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List expense categories with optional bank account filter"""
    categories = ExpenseCategoryService.list_expense_categories(
        db=db,
        bank_account_id=bank_account_id,
        limit=limit,
        offset=offset
    )

    category_responses = [
        ExpenseCategoryResponse(
            id=c.id,
            category_name=c.category_name,
            bank_account_id=c.bank_account_id,
            color=c.color,
            created_at=c.created_at,
            updated_at=c.updated_at
        )
        for c in categories
    ]

    return ExpenseCategoryListResponse(
        categories=category_responses,
        total=len(categories)
    )


@router.get("/expense-categories/{category_id}", response_model=ExpenseCategoryResponse)
async def get_expense_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific expense category"""
    category = ExpenseCategoryService.get_expense_category(db, category_id)

    return ExpenseCategoryResponse(
        id=category.id,
        category_name=category.category_name,
        bank_account_id=category.bank_account_id,
        color=category.color,
        created_at=category.created_at,
        updated_at=category.updated_at
    )


@router.put("/expense-categories/{category_id}", response_model=ExpenseCategoryResponse)
async def update_expense_category(
    category_id: int,
    category_data: ExpenseCategoryUpdate,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """Update an expense category"""
    category = ExpenseCategoryService.update_expense_category(
        db=db,
        category_id=category_id,
        category_name=category_data.category_name,
        bank_account_id=category_data.bank_account_id,
        color=category_data.color
    )

    return ExpenseCategoryResponse(
        id=category.id,
        category_name=category.category_name,
        bank_account_id=category.bank_account_id,
        color=category.color,
        created_at=category.created_at,
        updated_at=category.updated_at
    )


@router.delete("/expense-categories/{category_id}")
async def delete_expense_category(
    category_id: int,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """Delete an expense category"""
    ExpenseCategoryService.delete_expense_category(db, category_id)

    return {"message": "Expense category deleted successfully", "id": category_id}


# Expenses
@router.post("/expenses", response_model=ExpenseResponse)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """
    Create a new expense

    Requires permission: financial:write
    """
    expense = ExpenseService.create_expense(
        db=db,
        expense_name=expense_data.expense_name,
        amount=expense_data.amount,
        frequency=expense_data.frequency,
        category_id=expense_data.category_id,
        notes=expense_data.notes
    )

    return ExpenseResponse(
        id=expense.id,
        expense_name=expense.expense_name,
        amount=float(expense.amount),
        frequency=expense.frequency.value,
        category_id=expense.category_id,
        notes=expense.notes,
        created_at=expense.created_at,
        updated_at=expense.updated_at
    )


@router.get("/expenses", response_model=ExpenseListResponse)
async def list_expenses(
    category_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List expenses with optional category filter"""
    expenses = ExpenseService.list_expenses(
        db=db,
        category_id=category_id,
        limit=limit,
        offset=offset
    )

    expense_responses = [
        ExpenseResponse(
            id=e.id,
            expense_name=e.expense_name,
            amount=float(e.amount),
            frequency=e.frequency.value,
            category_id=e.category_id,
            notes=e.notes,
            created_at=e.created_at,
            updated_at=e.updated_at
        )
        for e in expenses
    ]

    return ExpenseListResponse(
        expenses=expense_responses,
        total=len(expenses)
    )


@router.get("/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific expense"""
    expense = ExpenseService.get_expense(db, expense_id)

    return ExpenseResponse(
        id=expense.id,
        expense_name=expense.expense_name,
        amount=float(expense.amount),
        frequency=expense.frequency.value,
        category_id=expense.category_id,
        notes=expense.notes,
        created_at=expense.created_at,
        updated_at=expense.updated_at
    )


@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """Update an expense"""
    expense = ExpenseService.update_expense(
        db=db,
        expense_id=expense_id,
        expense_name=expense_data.expense_name,
        amount=expense_data.amount,
        frequency=expense_data.frequency,
        category_id=expense_data.category_id,
        notes=expense_data.notes
    )

    return ExpenseResponse(
        id=expense.id,
        expense_name=expense.expense_name,
        amount=float(expense.amount),
        frequency=expense.frequency.value,
        category_id=expense.category_id,
        notes=expense.notes,
        created_at=expense.created_at,
        updated_at=expense.updated_at
    )


@router.delete("/expenses/{expense_id}")
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(require_permission("financial:write")),
    db: Session = Depends(get_db)
):
    """Delete an expense"""
    ExpenseService.delete_expense(db, expense_id)

    return {"message": "Expense deleted successfully", "id": expense_id}
