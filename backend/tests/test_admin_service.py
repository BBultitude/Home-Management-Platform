"""
Tests for Admin Service
"""

import pytest
from uuid import uuid4

from app.services.admin_service import AdminService
from app.models.user import User, UserRole
from app.services.auth_service import AuthService

TEST_PASSWORD_ADMIN = "AdminPass123!@#"  # Test-only credential
TEST_PASSWORD_EDITOR = "EditorPass123!@#"  # Test-only credential
TEST_PASSWORD_READER = "ReaderPass123!@#"  # Test-only credential
TEST_PASSWORD_ANOTHER_ADMIN = "AnotherAdmin123!@#"  # Test-only credential


class TestAdminService:
    """Test cases for AdminService"""

    @pytest.fixture
    def admin_user(self, db_session):
        """Create admin user"""
        user = AuthService.create_user(
            db=db_session,
            username="admin_test",
            email="admin@test.com",
            password=TEST_PASSWORD_ADMIN,
            full_name="Admin User",
            role=UserRole.ADMIN
        )
        return user

    @pytest.fixture
    def editor_user(self, db_session):
        """Create editor user"""
        user = AuthService.create_user(
            db=db_session,
            username="editor_test",
            email="editor@test.com",
            password=TEST_PASSWORD_EDITOR,
            full_name="Editor User",
            role=UserRole.EDITOR
        )
        return user

    @pytest.fixture
    def reader_user(self, db_session):
        """Create reader user"""
        user = AuthService.create_user(
            db=db_session,
            username="reader_test",
            email="reader@test.com",
            password=TEST_PASSWORD_READER,
            full_name="Reader User",
            role=UserRole.READER
        )
        return user

    def test_list_users(self, db_session, admin_user, editor_user, reader_user):
        """Test listing all users"""
        users = AdminService.list_users(db=db_session)

        assert len(users) >= 3
        usernames = [u.username for u in users]
        assert "admin_test" in usernames
        assert "editor_test" in usernames
        assert "reader_test" in usernames

    def test_list_users_with_search(self, db_session, admin_user, editor_user):
        """Test searching users"""
        users = AdminService.list_users(db=db_session, search="admin")

        assert len(users) >= 1
        assert any(u.username == "admin_test" for u in users)

    def test_list_users_filter_by_role(self, db_session, admin_user, editor_user, reader_user):
        """Test filtering users by role"""
        editors = AdminService.list_users(db=db_session, role=UserRole.EDITOR)

        assert all(u.role == UserRole.EDITOR for u in editors)
        assert any(u.username == "editor_test" for u in editors)

    def test_list_users_filter_by_active(self, db_session, admin_user):
        """Test filtering users by active status"""
        # Deactivate admin_user
        admin_user.is_active = False
        db_session.commit()

        active_users = AdminService.list_users(db=db_session, is_active=True)
        inactive_users = AdminService.list_users(db=db_session, is_active=False)

        assert all(u.is_active for u in active_users)
        assert all(not u.is_active for u in inactive_users)
        assert any(u.username == "admin_test" for u in inactive_users)

    def test_get_user_count(self, db_session, admin_user, editor_user, reader_user):
        """Test getting user count"""
        count = AdminService.get_user_count(db=db_session)
        assert count >= 3

        editor_count = AdminService.get_user_count(db=db_session, role=UserRole.EDITOR)
        assert editor_count >= 1

    def test_get_user_by_id(self, db_session, editor_user):
        """Test getting user by ID"""
        user = AdminService.get_user_by_id(db=db_session, user_id=editor_user.id)

        assert user.id == editor_user.id
        assert user.username == "editor_test"

    def test_get_user_by_id_not_found(self, db_session):
        """Test getting non-existent user raises error"""
        with pytest.raises(Exception):
            AdminService.get_user_by_id(db=db_session, user_id=uuid4())

    def test_update_user(self, db_session, admin_user, editor_user):
        """Test updating user details"""
        updated = AdminService.update_user(
            db=db_session,
            user_id=editor_user.id,
            admin_user=admin_user,
            full_name="Updated Name"
        )

        assert updated.full_name == "Updated Name"
        assert updated.username == "editor_test"  # Unchanged

    def test_update_user_username(self, db_session, admin_user, editor_user):
        """Test updating username"""
        updated = AdminService.update_user(
            db=db_session,
            user_id=editor_user.id,
            admin_user=admin_user,
            username="new_username"
        )

        assert updated.username == "new_username"

    def test_update_user_email(self, db_session, admin_user, editor_user):
        """Test updating email"""
        updated = AdminService.update_user(
            db=db_session,
            user_id=editor_user.id,
            admin_user=admin_user,
            email="newemail@test.com"
        )

        assert updated.email == "newemail@test.com"

    def test_update_user_duplicate_username(self, db_session, admin_user, editor_user, reader_user):
        """Test updating to duplicate username raises error"""
        with pytest.raises(Exception):
            AdminService.update_user(
                db=db_session,
                user_id=editor_user.id,
                admin_user=admin_user,
                username="reader_test"  # Already exists
            )

    def test_update_user_duplicate_email(self, db_session, admin_user, editor_user, reader_user):
        """Test updating to duplicate email raises error"""
        with pytest.raises(Exception):
            AdminService.update_user(
                db=db_session,
                user_id=editor_user.id,
                admin_user=admin_user,
                email="reader@test.com"  # Already exists
            )

    def test_update_user_role(self, db_session, admin_user, editor_user):
        """Test updating user role"""
        updated = AdminService.update_user_role(
            db=db_session,
            user_id=editor_user.id,
            admin_user=admin_user,
            new_role=UserRole.READER
        )

        assert updated.role == UserRole.READER

    def test_update_user_role_cannot_change_own(self, db_session, admin_user):
        """Test admin cannot change their own role"""
        with pytest.raises(Exception):
            AdminService.update_user_role(
                db=db_session,
                user_id=admin_user.id,
                admin_user=admin_user,
                new_role=UserRole.EDITOR
            )

    def test_update_user_role_cannot_remove_last_admin(self, db_session, admin_user):
        """Test cannot remove last admin role"""
        # Create another admin to act as the performer
        another_admin = AuthService.create_user(
            db=db_session,
            username="another_admin",
            email="another@admin.com",
            password=TEST_PASSWORD_ANOTHER_ADMIN,
            role=UserRole.ADMIN
        )

        # Try to change admin_user role (should fail - last admin)
        with pytest.raises(Exception):
            AdminService.update_user_role(
                db=db_session,
                user_id=admin_user.id,
                admin_user=another_admin,
                new_role=UserRole.EDITOR
            )

    def test_toggle_user_active(self, db_session, admin_user, editor_user):
        """Test activating/deactivating user"""
        # Deactivate
        updated = AdminService.toggle_user_active(
            db=db_session,
            user_id=editor_user.id,
            admin_user=admin_user,
            is_active=False
        )

        assert updated.is_active is False

        # Reactivate
        updated = AdminService.toggle_user_active(
            db=db_session,
            user_id=editor_user.id,
            admin_user=admin_user,
            is_active=True
        )

        assert updated.is_active is True

    def test_toggle_user_active_cannot_deactivate_self(self, db_session, admin_user):
        """Test admin cannot deactivate themselves"""
        with pytest.raises(Exception):
            AdminService.toggle_user_active(
                db=db_session,
                user_id=admin_user.id,
                admin_user=admin_user,
                is_active=False
            )

    def test_toggle_user_active_cannot_deactivate_last_admin(self, db_session, admin_user):
        """Test cannot deactivate last admin"""
        another_admin = AuthService.create_user(
            db=db_session,
            username="another_admin",
            email="another@admin.com",
            password=TEST_PASSWORD_ANOTHER_ADMIN,
            role=UserRole.ADMIN
        )

        with pytest.raises(Exception):
            AdminService.toggle_user_active(
                db=db_session,
                user_id=admin_user.id,
                admin_user=another_admin,
                is_active=False
            )

    def test_delete_user(self, db_session, admin_user, editor_user):
        """Test deleting user"""
        user_id = editor_user.id

        AdminService.delete_user(
            db=db_session,
            user_id=user_id,
            admin_user=admin_user
        )

        # Verify user is deleted
        with pytest.raises(Exception):
            AdminService.get_user_by_id(db=db_session, user_id=user_id)

    def test_delete_user_cannot_delete_self(self, db_session, admin_user):
        """Test admin cannot delete themselves"""
        with pytest.raises(Exception):
            AdminService.delete_user(
                db=db_session,
                user_id=admin_user.id,
                admin_user=admin_user
            )

    def test_delete_user_cannot_delete_last_admin(self, db_session, admin_user):
        """Test cannot delete last admin"""
        another_admin = AuthService.create_user(
            db=db_session,
            username="another_admin",
            email="another@admin.com",
            password=TEST_PASSWORD_ANOTHER_ADMIN,
            role=UserRole.ADMIN
        )

        with pytest.raises(Exception):
            AdminService.delete_user(
                db=db_session,
                user_id=admin_user.id,
                admin_user=another_admin
            )

    def test_reset_user_mfa(self, db_session, admin_user, editor_user):
        """Test resetting user MFA"""
        # Enable MFA for editor first
        editor_user.mfa_enabled = True
        db_session.commit()

        result = AdminService.reset_user_mfa(
            db=db_session,
            user_id=editor_user.id,
            admin_user=admin_user
        )

        assert "secret" in result
        assert "qr_code" in result
        assert "message" in result

        # Verify MFA is disabled
        db_session.refresh(editor_user)
        assert editor_user.mfa_enabled is False

    def test_get_system_stats(self, db_session, admin_user, editor_user, reader_user):
        """Test getting system statistics"""
        stats = AdminService.get_system_stats(db_session)

        assert "users" in stats
        assert "security" in stats
        assert "activity" in stats

        assert stats["users"]["total"] >= 3
        assert stats["users"]["active"] >= 0
        assert "by_role" in stats["users"]

    def test_get_user_statistics(self, db_session, admin_user):
        """Test getting user-specific statistics"""
        stats = AdminService.get_user_statistics(db=db_session, user_id=admin_user.id)

        assert "user_id" in stats
        assert "username" in stats
        assert "activity" in stats
        assert "account" in stats

        assert stats["username"] == "admin_test"
        assert stats["activity"]["total_actions"] >= 0
