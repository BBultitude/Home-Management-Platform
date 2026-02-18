#!/usr/bin/env python3
"""
Emergency MFA Disable Script
BREAK-GLASS ONLY - Use when locked out of account

This script:
1. Disables MFA for a specified user
2. Revokes all trusted devices
3. Allows emergency access to account

Usage:
  python3 disable_mfa.py <username>

Example:
  python3 disable_mfa.py admin
  python3 disable_mfa.py Bryan
"""

import sys
import os

# Add app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.trusted_device import TrustedDevice
from app.core.config import settings


def disable_mfa_emergency(username: str):
    """Emergency MFA disable for locked-out users"""

    # Create database connection using the same config as the app
    engine = create_engine(settings.database_url_with_password)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Find user
        user = db.query(User).filter(User.username == username).first()

        if not user:
            print(f"❌ User '{username}' not found")
            return False

        if not user.mfa_enabled:
            print(f"⚠️  MFA is already disabled for user '{username}'")
            print(f"   Username: {username}")
            print(f"   Role: {user.role.value}")
            print(f"   Active: {user.is_active}")
            return True

        # Disable MFA
        user.mfa_enabled = False
        user.mfa_secret = None

        # Revoke all trusted devices
        device_count = db.query(TrustedDevice).filter(
            TrustedDevice.user_id == user.id
        ).delete()

        # Commit changes
        db.commit()

        print("=" * 60)
        print("✅ EMERGENCY MFA DISABLE SUCCESSFUL")
        print("=" * 60)
        print(f"   Username: {username}")
        print(f"   Role: {user.role.value}")
        print(f"   Active: {user.is_active}")
        print(f"   MFA Enabled: {user.mfa_enabled}")
        print(f"   Trusted Devices Revoked: {device_count}")
        print()
        print("⚠️  SECURITY WARNING:")
        print("   - User can now login with password only")
        print("   - Recommend re-enabling MFA after access restored")
        print("   - User should re-setup MFA in Settings")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"❌ Error disabling MFA: {e}")
        db.rollback()
        return False

    finally:
        db.close()


def main():
    """Main function"""
    print("=" * 60)
    print("🚨 EMERGENCY MFA DISABLE SCRIPT")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This script should only be used when locked out")
    print("   of an account due to MFA issues (lost device, etc.)")
    print()

    # Check arguments
    if len(sys.argv) != 2:
        print("Usage: python3 disable_mfa.py <username>")
        print()
        print("Example:")
        print("  python3 disable_mfa.py admin")
        print("  python3 disable_mfa.py Bryan")
        sys.exit(1)

    username = sys.argv[1]

    # Confirm action
    print(f"You are about to DISABLE MFA for user: {username}")
    print()
    confirm = input("Are you sure? Type 'YES' to confirm: ").strip()

    if confirm != "YES":
        print("❌ Operation cancelled")
        sys.exit(0)

    print()
    success = disable_mfa_emergency(username)

    if success:
        print()
        print("Next steps:")
        print("1. User can now login with username + password only")
        print("2. Have user go to Settings → Security")
        print("3. Re-enable MFA for security")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
