"""
Authentication service for user management and session handling
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password as _verify_password, create_access_token
from app.core.config import settings


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: UserRole = UserRole.READER
    ) -> User:
        """
        Create a new user (admin-only operation)

        Args:
            db: Database session
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)
            full_name: User's full name
            role: User role (default: Reader)

        Returns:
            Created user object

        Raises:
            HTTPException: If username or email already exists
        """
        # Check if username exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Check if email exists
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        # Create user
        hashed_pwd = hash_password(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_pwd,
            full_name=full_name,
            role=role,
            is_active=True,
            mfa_enabled=False
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(
        db: Session,
        username: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate user with username and password

        Args:
            db: Database session
            username: Username
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.username == username).first()

        if not user:
            return None

        if not user.is_active:
            return None

        if user.is_deleted:
            return None

        if not _verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def create_session_token(user: User) -> str:
        """
        Create JWT session token for authenticated user

        Args:
            user: User object

        Returns:
            JWT token string
        """
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value,
            "type": "access"
        }
        return create_access_token(token_data)

    @staticmethod
    def create_mfa_pending_token(user: User) -> str:
        """
        Create temporary JWT token for MFA pending state

        This token is valid for 5 minutes and allows the user to complete
        MFA verification after successful password authentication.

        Args:
            user: User object

        Returns:
            Temporary JWT token string
        """
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "type": "mfa_pending"
        }
        # 5 minute expiry for MFA completion
        expires_delta = timedelta(minutes=5)
        return create_access_token(token_data, expires_delta)

    @staticmethod
    def update_last_login(db: Session, user: User) -> None:
        """
        Update user's last login timestamp

        Args:
            db: Database session
            user: User object
        """
        user.last_login = datetime.now(timezone.utc)
        db.commit()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return _verify_password(plain_password, hashed_password)

    @staticmethod
    def change_password(
        db: Session,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user's password

        Args:
            db: Database session
            user: User object
            current_password: Current password (for verification)
            new_password: New password

        Returns:
            True if password changed successfully

        Raises:
            HTTPException: If current password is incorrect
        """
        # Verify current password
        if not _verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Hash and update new password
        user.hashed_password = hash_password(new_password)
        db.commit()
        return True

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object or None
        """
        return db.query(User).filter(
            User.id == user_id,
            User.is_active == True,
            User.is_deleted == False
        ).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Get user by username

        Args:
            db: Database session
            username: Username

        Returns:
            User object or None
        """
        return db.query(User).filter(
            User.username == username,
            User.is_active == True,
            User.is_deleted == False
        ).first()
