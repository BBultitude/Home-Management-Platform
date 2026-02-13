"""
Unit tests for Role-Based Access Control (RBAC)
Tests permission checks, role requirements, and ownership validation
"""

import pytest
from fastapi import HTTPException, Request
from unittest.mock import Mock, MagicMock

from app.api.dependencies import (
    require_role,
    require_permission,
    require_tax_ownership,
    allow_tax_read,
    PERMISSION_MATRIX,
    get_current_active_user,
)
from app.models.user import User, UserRole


class TestRequireRole:
    """Test role requirement dependency"""

    def test_admin_role_check_success(self, admin_user: User):
        """Test that admin user passes admin role check"""
        checker = require_role(UserRole.ADMIN)
        result = checker(current_user=admin_user)
        assert result == admin_user

    def test_admin_role_check_failure(self, test_user: User):
        """Test that non-admin user fails admin role check"""
        checker = require_role(UserRole.ADMIN)

        with pytest.raises(HTTPException) as exc_info:
            checker(current_user=test_user)

        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in exc_info.value.detail

    def test_multi_role_check_success_admin(self, admin_user: User):
        """Test multi-role check passes for admin"""
        checker = require_role(UserRole.ADMIN, UserRole.EDITOR)
        result = checker(current_user=admin_user)
        assert result == admin_user

    def test_multi_role_check_success_editor(self):
        """Test multi-role check passes for editor"""
        editor = Mock(spec=User)
        editor.role = UserRole.EDITOR
        editor.is_active = True
        editor.is_deleted = False

        checker = require_role(UserRole.ADMIN, UserRole.EDITOR)
        result = checker(current_user=editor)
        assert result == editor

    def test_multi_role_check_failure_reader(self, test_user: User):
        """Test multi-role check fails for reader"""
        checker = require_role(UserRole.ADMIN, UserRole.EDITOR)

        with pytest.raises(HTTPException) as exc_info:
            checker(current_user=test_user)

        assert exc_info.value.status_code == 403


class TestRequirePermission:
    """Test permission-based access control"""

    def test_permission_check_admin_users_create(self, admin_user: User):
        """Test admin has users:create permission"""
        checker = require_permission("users:create")
        result = checker(current_user=admin_user)
        assert result == admin_user

    def test_permission_check_reader_users_create_denied(self, test_user: User):
        """Test reader does NOT have users:create permission"""
        checker = require_permission("users:create")

        with pytest.raises(HTTPException) as exc_info:
            checker(current_user=test_user)

        assert exc_info.value.status_code == 403
        assert "users:create" in exc_info.value.detail

    def test_permission_check_reader_tax_create(self, test_user: User):
        """Test reader HAS tax:create permission"""
        checker = require_permission("tax:create")
        result = checker(current_user=test_user)
        assert result == test_user

    def test_permission_check_undefined_permission(self, admin_user: User):
        """Test error when permission not defined in matrix"""
        checker = require_permission("nonexistent:permission")

        with pytest.raises(HTTPException) as exc_info:
            checker(current_user=admin_user)

        assert exc_info.value.status_code == 500
        assert "not defined" in exc_info.value.detail

    def test_permission_matrix_tax_view_own(self):
        """Test that all roles can view their own tax records"""
        assert UserRole.ADMIN in PERMISSION_MATRIX["tax:view_own"]
        assert UserRole.EDITOR in PERMISSION_MATRIX["tax:view_own"]
        assert UserRole.READER in PERMISSION_MATRIX["tax:view_own"]

    def test_permission_matrix_tax_view_all_admin_only(self):
        """Test that only admin can view all tax records"""
        assert PERMISSION_MATRIX["tax:view_all"] == [UserRole.ADMIN]

    def test_permission_matrix_files_upload_all_roles(self):
        """Test that all roles can upload files"""
        assert UserRole.ADMIN in PERMISSION_MATRIX["files:upload"]
        assert UserRole.EDITOR in PERMISSION_MATRIX["files:upload"]
        assert UserRole.READER in PERMISSION_MATRIX["files:upload"]

    def test_permission_matrix_audit_view_all_admin_only(self):
        """Test that only admin can view all audit logs"""
        assert PERMISSION_MATRIX["audit:view_all"] == [UserRole.ADMIN]


class TestTaxOwnershipAndReadAccess:
    """Test tax record ownership validation"""

    @pytest.mark.asyncio
    async def test_admin_can_access_any_tax_record(self, admin_user: User, test_db):
        """Test admin can access any tax record"""
        checker = require_tax_ownership("tax_id")

        # Mock request with tax_id path parameter
        request = Mock(spec=Request)
        request.path_params = {"tax_id": 123}

        result = await checker(
            request=request,
            current_user=admin_user,
            db=test_db
        )

        assert result == admin_user

    @pytest.mark.asyncio
    async def test_user_access_with_missing_tax_id_parameter(self, test_user: User, test_db):
        """Test error when tax_id parameter missing"""
        checker = require_tax_ownership("tax_id")

        # Mock request WITHOUT tax_id
        request = Mock(spec=Request)
        request.path_params = {}

        with pytest.raises(HTTPException) as exc_info:
            await checker(
                request=request,
                current_user=test_user,
                db=test_db
            )

        assert exc_info.value.status_code == 400
        assert "Missing path parameter" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_custom_tax_id_parameter_name(self, admin_user: User, test_db):
        """Test custom parameter name for tax record ID"""
        checker = require_tax_ownership("wfh_id")

        request = Mock(spec=Request)
        request.path_params = {"wfh_id": 456}

        result = await checker(
            request=request,
            current_user=admin_user,
            db=test_db
        )

        assert result == admin_user

    @pytest.mark.asyncio
    async def test_allow_tax_read_admin(self, admin_user: User, test_db):
        """Test admin can read any tax record"""
        checker = allow_tax_read("tax_id")

        request = Mock(spec=Request)
        request.path_params = {"tax_id": 789}

        result = await checker(
            request=request,
            current_user=admin_user,
            db=test_db
        )

        assert result == admin_user


class TestPermissionMatrix:
    """Test permission matrix completeness"""

    def test_all_user_management_permissions_defined(self):
        """Test all user management permissions exist"""
        required_permissions = [
            "users:create",
            "users:update",
            "users:delete",
            "users:list",
            "users:view_all",
        ]

        for perm in required_permissions:
            assert perm in PERMISSION_MATRIX, f"Missing permission: {perm}"

    def test_all_tax_permissions_defined(self):
        """Test all tax permissions exist"""
        required_permissions = [
            "tax:create",
            "tax:update_own",
            "tax:delete_own",
            "tax:view_own",
            "tax:view_all",
            "tax:update_any",
            "tax:delete_any",
        ]

        for perm in required_permissions:
            assert perm in PERMISSION_MATRIX, f"Missing permission: {perm}"

    def test_all_file_permissions_defined(self):
        """Test all file permissions exist"""
        required_permissions = [
            "files:upload",
            "files:download_own",
            "files:download_any",
            "files:delete_own",
            "files:delete_any",
        ]

        for perm in required_permissions:
            assert perm in PERMISSION_MATRIX, f"Missing permission: {perm}"

    def test_all_audit_permissions_defined(self):
        """Test all audit permissions exist"""
        required_permissions = [
            "audit:view_all",
            "audit:view_own_tax",
        ]

        for perm in required_permissions:
            assert perm in PERMISSION_MATRIX, f"Missing permission: {perm}"

    def test_all_permissions_have_valid_roles(self):
        """Test all permissions map to valid UserRole values"""
        valid_roles = [UserRole.ADMIN, UserRole.EDITOR, UserRole.READER]

        for permission, roles in PERMISSION_MATRIX.items():
            assert isinstance(roles, list), f"{permission} roles must be a list"
            assert len(roles) > 0, f"{permission} must have at least one role"

            for role in roles:
                assert role in valid_roles, f"Invalid role {role} for {permission}"

    def test_admin_only_permissions(self):
        """Test permissions that should be admin-only"""
        admin_only = [
            "users:create",
            "users:update",
            "users:delete",
            "users:list",
            "users:view_all",
            "tax:view_all",
            "tax:update_any",
            "tax:delete_any",
            "files:download_any",
            "files:delete_any",
            "audit:view_all",
        ]

        for perm in admin_only:
            assert PERMISSION_MATRIX[perm] == [UserRole.ADMIN], \
                f"{perm} should be admin-only"

    def test_all_roles_can_create_tax_records(self):
        """Test all users can create their own tax records"""
        assert len(PERMISSION_MATRIX["tax:create"]) == 3
        assert UserRole.ADMIN in PERMISSION_MATRIX["tax:create"]
        assert UserRole.EDITOR in PERMISSION_MATRIX["tax:create"]
        assert UserRole.READER in PERMISSION_MATRIX["tax:create"]


class TestGetCurrentActiveUser:
    """Test active user validation"""

    def test_active_user_passes(self, test_user: User):
        """Test that active user passes validation"""
        result = get_current_active_user(current_user=test_user)
        assert result == test_user

    def test_inactive_user_fails(self):
        """Test that inactive user fails validation"""
        inactive_user = Mock(spec=User)
        inactive_user.is_active = False
        inactive_user.is_deleted = False

        with pytest.raises(HTTPException) as exc_info:
            get_current_active_user(current_user=inactive_user)

        assert exc_info.value.status_code == 403
        assert "Inactive user" in exc_info.value.detail

    def test_deleted_user_fails(self):
        """Test that deleted user fails validation"""
        deleted_user = Mock(spec=User)
        deleted_user.is_active = True
        deleted_user.is_deleted = True

        with pytest.raises(HTTPException) as exc_info:
            get_current_active_user(current_user=deleted_user)

        assert exc_info.value.status_code == 403
        assert "deleted" in exc_info.value.detail


class TestEdgeCases:
    """Test RBAC edge cases"""

    def test_empty_role_requirement_list(self):
        """Test error handling for empty role list"""
        # This should not happen in practice, but test defensive coding
        checker = require_role()

        with pytest.raises(Exception):
            # Should raise an error or return a checker that denies everyone
            checker(current_user=Mock(spec=User))

    def test_permission_check_preserves_user_object(self, admin_user: User):
        """Test that permission check returns the same user object"""
        checker = require_permission("users:create")
        result = checker(current_user=admin_user)

        # Should return exact same object, not a copy
        assert result is admin_user

    def test_role_check_preserves_user_object(self, admin_user: User):
        """Test that role check returns the same user object"""
        checker = require_role(UserRole.ADMIN)
        result = checker(current_user=admin_user)

        # Should return exact same object, not a copy
        assert result is admin_user
