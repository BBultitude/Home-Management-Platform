"""
Budget Service
Handles budget calculations and transfer requirements
"""

from decimal import Decimal
from collections import defaultdict
from sqlalchemy.orm import Session

from app.models.income_source import IncomeSource, IncomeFrequency
from app.models.bank_account import BankAccount
from app.models.expense_category import ExpenseCategory
from app.models.expense import Expense, ExpenseFrequency


class BudgetService:
    """Service for budget calculations"""

    # Conversion factors to normalize all frequencies to monthly
    FREQUENCY_TO_MONTHLY = {
        IncomeFrequency.DAILY: Decimal("30"),
        IncomeFrequency.WEEKLY: Decimal("4.33"),
        IncomeFrequency.FORTNIGHTLY: Decimal("2.17"),
        IncomeFrequency.MONTHLY: Decimal("1"),
        IncomeFrequency.YEARLY: Decimal("0.0833"),
    }

    EXPENSE_FREQUENCY_TO_MONTHLY = {
        ExpenseFrequency.DAILY: Decimal("30"),
        ExpenseFrequency.WEEKLY: Decimal("4.33"),
        ExpenseFrequency.FORTNIGHTLY: Decimal("2.17"),
        ExpenseFrequency.MONTHLY: Decimal("1"),
        ExpenseFrequency.YEARLY: Decimal("0.0833"),
    }

    @staticmethod
    def normalize_to_frequency(
        amount: Decimal,
        from_frequency: IncomeFrequency | ExpenseFrequency,
        to_frequency: IncomeFrequency
    ) -> Decimal:
        """
        Normalize an amount from one frequency to another

        Args:
            amount: Original amount
            from_frequency: Source frequency
            to_frequency: Target frequency

        Returns:
            Normalized amount
        """
        # First convert to monthly
        if isinstance(from_frequency, IncomeFrequency):
            monthly_amount = amount * BudgetService.FREQUENCY_TO_MONTHLY[from_frequency]
        else:  # ExpenseFrequency
            monthly_amount = amount * BudgetService.EXPENSE_FREQUENCY_TO_MONTHLY[
                ExpenseFrequency(from_frequency.value)
            ]

        # Then convert from monthly to target frequency
        target_multiplier = BudgetService.FREQUENCY_TO_MONTHLY[to_frequency]
        return monthly_amount / target_multiplier

    @staticmethod
    def calculate_budget(
        db: Session,
        pay_frequency: IncomeFrequency
    ) -> dict:
        """
        Calculate budget transfers based on pay frequency

        Args:
            db: Database session
            pay_frequency: Frequency to normalize calculations to

        Returns:
            Dictionary with budget calculation results
        """
        # Get all income sources
        income_sources = db.query(IncomeSource).all()

        # Calculate total income normalized to pay frequency
        total_income = Decimal("0")
        for income in income_sources:
            normalized = BudgetService.normalize_to_frequency(
                income.amount,
                income.frequency,
                pay_frequency
            )
            total_income += normalized

        # Get all expenses with their categories and bank accounts
        expenses = db.query(Expense).join(ExpenseCategory).join(BankAccount).all()

        # Group expenses by bank account
        account_expenses = defaultdict(list)
        account_totals = defaultdict(lambda: Decimal("0"))

        for expense in expenses:
            category = expense.category
            account = category.bank_account

            # Normalize expense to pay frequency
            normalized_amount = BudgetService.normalize_to_frequency(
                expense.amount,
                ExpenseFrequency(expense.frequency.value),
                pay_frequency
            )

            account_expenses[account.id].append({
                "expense_name": expense.expense_name,
                "amount": float(normalized_amount)
            })
            account_totals[account.id] += normalized_amount

        # Build transfers list
        transfers = []
        total_expenses = Decimal("0")

        for account_id, expense_list in account_expenses.items():
            account = db.query(BankAccount).filter(BankAccount.id == account_id).first()
            transfer_amount = account_totals[account_id]
            total_expenses += transfer_amount

            transfers.append({
                "account_id": account.id,
                "account_name": account.account_name,
                "amount": float(transfer_amount),
                "expenses": [e["expense_name"] for e in expense_list]
            })

        # Calculate surplus/deficit
        surplus = total_income - total_expenses

        return {
            "pay_frequency": pay_frequency.value,
            "total_income": float(total_income),
            "total_expenses": float(total_expenses),
            "surplus": float(surplus),
            "transfers": transfers
        }

    @staticmethod
    def get_budget_summary(db: Session) -> dict:
        """
        Get monthly budget summary for dashboard

        Args:
            db: Database session

        Returns:
            Dictionary with monthly budget summary
        """
        # Get total monthly income
        income_sources = db.query(IncomeSource).all()
        total_monthly_income = Decimal("0")

        for income in income_sources:
            monthly = BudgetService.normalize_to_frequency(
                income.amount,
                income.frequency,
                IncomeFrequency.MONTHLY
            )
            total_monthly_income += monthly

        # Get total monthly expenses grouped by account
        expenses = db.query(Expense).join(ExpenseCategory).join(BankAccount).all()

        account_allocations = {}
        total_monthly_expenses = Decimal("0")

        for expense in expenses:
            category = expense.category
            account = category.bank_account

            monthly = BudgetService.normalize_to_frequency(
                expense.amount,
                ExpenseFrequency(expense.frequency.value),
                IncomeFrequency.MONTHLY
            )

            if account.account_name not in account_allocations:
                account_allocations[account.account_name] = Decimal("0")

            account_allocations[account.account_name] += monthly
            total_monthly_expenses += monthly

        # Convert to float for response
        account_allocations_float = {
            name: float(amount) for name, amount in account_allocations.items()
        }

        return {
            "total_monthly_income": float(total_monthly_income),
            "total_monthly_expenses": float(total_monthly_expenses),
            "monthly_surplus": float(total_monthly_income - total_monthly_expenses),
            "account_allocations": account_allocations_float
        }
