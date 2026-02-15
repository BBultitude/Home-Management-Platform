#!/usr/bin/env python3
"""
Create Admin User Script
Creates an admin user for the Home Management Platform
"""
import sys
import os
from getpass import getpass

# Add the app directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def create_admin_user(username: str, email: str, password: str, full_name: str = "System Administrator"):
    """Create an admin user"""
    db = SessionLocal()

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ Error: User with email '{email}' already exists!")
            print(f"   Current role: {existing_user.role}")
            print(f"   Active: {existing_user.is_active}")
            return False

        # Create admin user
        admin = User(
            username=username,
            email=email,
            hashed_password=hash_password(password), 
            full_name=full_name,
            role="ADMIN",
            is_active=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("✅ Admin user created successfully!")
        print(f"   Email: {admin.email}")
        print(f"   Name: {admin.full_name}")
        print(f"   Role: {admin.role}")
        print(f"   ID: {admin.id}")
        print()
        print("⚠️  IMPORTANT: Change the password after first login!")

        return True

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        return False
    finally:
        db.close()


def main():
    """Main function - interactive or command-line args"""
    print("=" * 60)
    print("Home Management Platform - Admin User Creation")
    print("=" * 60)
    print()

    # Check if arguments provided
    if len(sys.argv) >= 4:
        # Command-line mode
        username = sys.argv[1]
        email = sys.argv[2]
        password = sys.argv[3]
        full_name = sys.argv[4] if len(sys.argv) >= 5 else "System Administrator"
    else:
        # Interactive mode
        print("Create a new admin user:")
        print()
        username = input("Username: ").strip()
        if not username:
            print("❌ Username is required!")
            sys.exit(1)

        email = input("Email address: ").strip()

        if not email:
            print("❌ Email is required!")
            sys.exit(1)

        password = getpass("Password (input hidden): ").strip()
        password_confirm = getpass("Confirm password: ").strip()

        if password != password_confirm:
            print("❌ Passwords do not match!")
            sys.exit(1)

        if len(password) < 8:
            print("⚠️  Warning: Password is shorter than 8 characters")
            confirm = input("Continue anyway? (y/N): ").strip().lower()
            if confirm != 'y':
                print("Cancelled.")
                sys.exit(0)

        full_name = input("Full name (default: System Administrator): ").strip()
        if not full_name:
            full_name = "System Administrator"

        print()

    # Create the user
    success = create_admin_user(username, email, password, full_name)

    if success:
        print()
        print("You can now login with:")
        print(f"  Email: {email}")
        print(f"  Password: {'*' * len(password)}")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
