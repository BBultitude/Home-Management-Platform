"""
Expense and Expense Category Services
Handles CRUD operations for expenses and categories
"""

from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.expense import Expense, ExpenseFrequency
from app.models.expense_category import ExpenseCategory
from app.models.bank_account import BankAccount

_CATEGORY_NOT_FOUND = "Expense category not found"


class ExpenseCategoryService:
    """Service for expense category operations"""

    @staticmethod
    def create_expense_category(
        db: Session,
        category_name: str,
        bank_account_id: int,
        color: Optional[str] = None
    ) -> ExpenseCategory:
        """
        Create a new expense category

        Args:
            db: Database session
            category_name: Name of category
            bank_account_id: Bank account ID
            color: Optional hex color code

        Returns:
            Created ExpenseCategory

        Raises:
            HTTPException: If bank account not found
        """
        # Verify bank account exists
        account = db.query(BankAccount).filter(BankAccount.id == bank_account_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank account not found"
            )

        category = ExpenseCategory(
            category_name=category_name,
            bank_account_id=bank_account_id,
            color=color
        )

        db.add(category)
        db.commit()
        db.refresh(category)

        return category

    @staticmethod
    def get_expense_category(db: Session, category_id: int) -> ExpenseCategory:
        """Get an expense category by ID"""
        category = db.query(ExpenseCategory).filter(ExpenseCategory.id == category_id).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=_CATEGORY_NOT_FOUND
            )

        return category

    @staticmethod
    def list_expense_categories(
        db: Session,
        bank_account_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[ExpenseCategory]:
        """List expense categories with optional bank account filter"""
        query = db.query(ExpenseCategory)

        if bank_account_id:
            query = query.filter(ExpenseCategory.bank_account_id == bank_account_id)

        query = query.order_by(ExpenseCategory.category_name)
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def update_expense_category(
        db: Session,
        category_id: int,
        category_name: Optional[str] = None,
        bank_account_id: Optional[int] = None,
        color: Optional[str] = None
    ) -> ExpenseCategory:
        """Update an expense category"""
        category = ExpenseCategoryService.get_expense_category(db, category_id)

        if category_name is not None:
            category.category_name = category_name

        if bank_account_id is not None:
            # Verify bank account exists
            account = db.query(BankAccount).filter(BankAccount.id == bank_account_id).first()
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Bank account not found"
                )
            category.bank_account_id = bank_account_id

        if color is not None:
            category.color = color

        db.commit()
        db.refresh(category)

        return category

    @staticmethod
    def delete_expense_category(db: Session, category_id: int) -> None:
        """Delete an expense category"""
        category = ExpenseCategoryService.get_expense_category(db, category_id)

        # Check if category has expenses
        if category.expenses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category with {len(category.expenses)} expenses. Delete expenses first."
            )

        db.delete(category)
        db.commit()


class ExpenseService:
    """Service for expense operations"""

    @staticmethod
    def create_expense(
        db: Session,
        expense_name: str,
        amount: Decimal,
        frequency: ExpenseFrequency,
        category_id: int,
        notes: Optional[str] = None
    ) -> Expense:
        """
        Create a new expense

        Args:
            db: Database session
            expense_name: Name of expense
            amount: Expense amount
            frequency: Payment frequency
            category_id: Expense category ID
            notes: Optional notes

        Returns:
            Created Expense

        Raises:
            HTTPException: If validation fails
        """
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than 0"
            )

        # Verify category exists
        category = db.query(ExpenseCategory).filter(ExpenseCategory.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=_CATEGORY_NOT_FOUND
            )

        expense = Expense(
            expense_name=expense_name,
            amount=amount,
            frequency=frequency,
            category_id=category_id,
            notes=notes
        )

        db.add(expense)
        db.commit()
        db.refresh(expense)

        return expense

    @staticmethod
    def get_expense(db: Session, expense_id: int) -> Expense:
        """Get an expense by ID"""
        expense = db.query(Expense).filter(Expense.id == expense_id).first()

        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found"
            )

        return expense

    @staticmethod
    def list_expenses(
        db: Session,
        category_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Expense]:
        """List expenses with optional category filter"""
        query = db.query(Expense)

        if category_id:
            query = query.filter(Expense.category_id == category_id)

        query = query.order_by(Expense.expense_name)
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def update_expense(
        db: Session,
        expense_id: int,
        expense_name: Optional[str] = None,
        amount: Optional[Decimal] = None,
        frequency: Optional[ExpenseFrequency] = None,
        category_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Expense:
        """Update an expense"""
        expense = ExpenseService.get_expense(db, expense_id)

        if expense_name is not None:
            expense.expense_name = expense_name

        if amount is not None:
            if amount <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Amount must be greater than 0"
                )
            expense.amount = amount

        if frequency is not None:
            expense.frequency = frequency

        if category_id is not None:
            # Verify category exists
            category = db.query(ExpenseCategory).filter(ExpenseCategory.id == category_id).first()
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=_CATEGORY_NOT_FOUND
                )
            expense.category_id = category_id

        if notes is not None:
            expense.notes = notes

        db.commit()
        db.refresh(expense)

        return expense

    @staticmethod
    def delete_expense(db: Session, expense_id: int) -> None:
        """Delete an expense"""
        expense = ExpenseService.get_expense(db, expense_id)

        db.delete(expense)
        db.commit()
