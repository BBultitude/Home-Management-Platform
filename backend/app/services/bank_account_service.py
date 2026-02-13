"""
Bank Account Service
Handles CRUD operations for bank accounts
"""

from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.bank_account import BankAccount, AccountType


class BankAccountService:
    """Service for bank account operations"""

    @staticmethod
    def create_bank_account(
        db: Session,
        account_name: str,
        account_type: AccountType,
        current_balance: Optional[Decimal] = None
    ) -> BankAccount:
        """
        Create a new bank account

        Args:
            db: Database session
            account_name: Name of account
            account_type: Type of account
            current_balance: Optional current balance

        Returns:
            Created BankAccount

        Raises:
            HTTPException: If validation fails
        """
        bank_account = BankAccount(
            account_name=account_name,
            account_type=account_type,
            current_balance=current_balance
        )

        db.add(bank_account)
        db.commit()
        db.refresh(bank_account)

        return bank_account

    @staticmethod
    def get_bank_account(db: Session, account_id: int) -> BankAccount:
        """
        Get a bank account by ID

        Args:
            db: Database session
            account_id: Bank account ID

        Returns:
            BankAccount

        Raises:
            HTTPException: If not found
        """
        account = db.query(BankAccount).filter(BankAccount.id == account_id).first()

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank account not found"
            )

        return account

    @staticmethod
    def list_bank_accounts(
        db: Session,
        limit: int = 100,
        offset: int = 0
    ) -> list[BankAccount]:
        """
        List all bank accounts

        Args:
            db: Database session
            limit: Maximum entries to return
            offset: Pagination offset

        Returns:
            List of BankAccount objects
        """
        query = db.query(BankAccount)
        query = query.order_by(BankAccount.account_name)
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def update_bank_account(
        db: Session,
        account_id: int,
        account_name: Optional[str] = None,
        account_type: Optional[AccountType] = None,
        current_balance: Optional[Decimal] = None
    ) -> BankAccount:
        """
        Update a bank account

        Args:
            db: Database session
            account_id: Bank account ID
            account_name: Updated name (optional)
            account_type: Updated type (optional)
            current_balance: Updated balance (optional)

        Returns:
            Updated BankAccount

        Raises:
            HTTPException: If not found
        """
        account = BankAccountService.get_bank_account(db, account_id)

        if account_name is not None:
            account.account_name = account_name

        if account_type is not None:
            account.account_type = account_type

        if current_balance is not None:
            account.current_balance = current_balance

        db.commit()
        db.refresh(account)

        return account

    @staticmethod
    def delete_bank_account(db: Session, account_id: int) -> None:
        """
        Delete a bank account

        Args:
            db: Database session
            account_id: Bank account ID

        Raises:
            HTTPException: If not found or has dependencies
        """
        account = BankAccountService.get_bank_account(db, account_id)

        # Check if account has expense categories
        if account.expense_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete account with {len(account.expense_categories)} expense categories. Delete categories first."
            )

        db.delete(account)
        db.commit()
