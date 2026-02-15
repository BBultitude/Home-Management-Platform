#!/usr/bin/env python3
"""
Reset user password
Usage: python reset_password.py <username> <new_password>
"""

import sys
import os

# Add app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.security import hash_password
from app.core.config import settings

def reset_password(username: str, new_password: str):
    """Reset password for a user"""
    # Create database connection using the same config as the app
    # This properly reads the password from Docker secrets
    engine = create_engine(settings.database_url_with_password)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Find user
        user = db.query(User).filter(User.username == username).first()

        if not user:
            print(f"❌ User '{username}' not found")
            return False

        # Hash new password using the same function as the rest of the app
        user.hashed_password = hash_password(new_password)

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
