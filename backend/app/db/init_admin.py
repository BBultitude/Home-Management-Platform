"""
Initialize database with first admin user
Run this once to create the initial admin account
"""

import sys
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password


def create_admin_user():
    """Create the initial admin user"""
    db: Session = SessionLocal()

    try:
        # Check if any users exist
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"⚠️  Database already has {existing_users} user(s)")
            print("   Skipping admin creation")
            return

        # Create admin user
        # Password meets enhanced requirements: 12+ chars, uppercase, lowercase, digit, no weak patterns
        admin = User(
            username="admin",
            email="admin@localhost",
            hashed_password=hash_password("AdminHomeManager2026"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            mfa_enabled=False
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("✅ Admin user created successfully!")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print("   Password: AdminHomeManager2026")
        print("\n⚠️  IMPORTANT: Change this password immediately after first login!")

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
