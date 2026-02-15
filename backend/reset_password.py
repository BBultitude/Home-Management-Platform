#!/usr/bin/env python3
"""
Reset user password
Usage: python reset_password.py <username> <new_password>
"""

import sys
import os
from argon2 import PasswordHasher

# Add app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User

# Get database URL from environment or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://homeuser:homepassword@localhost:5432/homedb')

def reset_password(username: str, new_password: str):
    """Reset password for a user"""
    # Create database connection
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Find user
        user = db.query(User).filter(User.username == username).first()

        if not user:
            print(f"❌ User '{username}' not found")
            return False

        # Hash new password
        ph = PasswordHasher()
        user.password_hash = ph.hash(new_password)

        # Commit changes
        db.commit()

        print(f"✅ Password reset successfully for user '{username}'")
        print(f"   Username: {username}")
        print(f"   Role: {user.role}")
        print(f"   Active: {user.is_active}")
        return True

    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        db.rollback()
        return False

    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reset_password.py <username> <new_password>")
        print("\nExample:")
        print("  python reset_password.py admin newpassword123")
        sys.exit(1)

    username = sys.argv[1]
    new_password = sys.argv[2]

    if len(new_password) < 12:
        print("❌ Password must be at least 12 characters long")
        sys.exit(1)

    success = reset_password(username, new_password)
    sys.exit(0 if success else 1)
