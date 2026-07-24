# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# Django
from django.contrib.auth.models import User

# Zato
from zato.rule_engine_dashboard.app import user_rules
from zato.rule_engine_dashboard.app.user_rules import Root_Username, UserManagementError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The rules are pure functions over user objects, so unsaved instances are all they need

def _new_admin() -> 'any_':
    out = User(username='test.admin', is_superuser=True)
    return out

# ################################################################################################################################

def _new_user() -> 'any_':
    out = User(username='test.user')
    return out

# ################################################################################################################################

def _new_root() -> 'any_':
    out = User(username=Root_Username, is_superuser=True)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRootProtections:

    def test_no_admin_can_touch_the_root_account(self:'any_') -> 'None':
        admin = _new_admin()

        rules = [
            user_rules.ensure_can_update_profile,
            user_rules.ensure_can_set_role,
            user_rules.ensure_can_set_active,
            user_rules.ensure_can_delete,
            user_rules.ensure_can_change_password,
        ]

        for rule in rules:
            with pytest.raises(UserManagementError):
                rule(admin, Root_Username)

# ################################################################################################################################

    def test_root_cannot_edit_its_own_profile(self:'any_') -> 'None':
        root = _new_root()

        with pytest.raises(UserManagementError):
            user_rules.ensure_can_update_profile(root, Root_Username)

# ################################################################################################################################

    def test_root_cannot_change_its_own_password(self:'any_') -> 'None':
        root = _new_root()

        with pytest.raises(UserManagementError):
            user_rules.ensure_can_change_password(root, Root_Username)

# ################################################################################################################################

    def test_root_username_can_never_be_created_again(self:'any_') -> 'None':
        admin = _new_admin()

        with pytest.raises(UserManagementError):
            user_rules.ensure_can_create(admin, Root_Username)

# ################################################################################################################################
# ################################################################################################################################

class TestAdminPowers:

    def test_admin_manages_anyone_else(self:'any_') -> 'None':
        admin = _new_admin()
        user = _new_user()

        # None of these raises, which is the whole assertion
        user_rules.ensure_can_create(admin, user.username)
        user_rules.ensure_can_update_profile(admin, user.username)
        user_rules.ensure_can_set_role(admin, user.username)
        user_rules.ensure_can_set_active(admin, user.username)
        user_rules.ensure_can_delete(admin, user.username)
        user_rules.ensure_can_change_password(admin, user.username)

# ################################################################################################################################

    def test_admin_manages_its_own_profile_and_password(self:'any_') -> 'None':
        admin = _new_admin()

        # Neither of these raises, which is the whole assertion
        user_rules.ensure_can_update_profile(admin, admin.username)
        user_rules.ensure_can_change_password(admin, admin.username)

# ################################################################################################################################

    def test_admin_cannot_change_its_own_role(self:'any_') -> 'None':
        admin = _new_admin()

        with pytest.raises(UserManagementError):
            user_rules.ensure_can_set_role(admin, admin.username)

# ################################################################################################################################

    def test_admin_cannot_disable_itself(self:'any_') -> 'None':
        admin = _new_admin()

        with pytest.raises(UserManagementError):
            user_rules.ensure_can_set_active(admin, admin.username)

# ################################################################################################################################

    def test_admin_cannot_delete_itself(self:'any_') -> 'None':
        admin = _new_admin()

        with pytest.raises(UserManagementError):
            user_rules.ensure_can_delete(admin, admin.username)

# ################################################################################################################################
# ################################################################################################################################

class TestRegularUserRestrictions:

    def test_user_manages_its_own_profile_and_password(self:'any_') -> 'None':
        user = _new_user()

        # Neither of these raises, which is the whole assertion
        user_rules.ensure_can_update_profile(user, user.username)
        user_rules.ensure_can_change_password(user, user.username)

# ################################################################################################################################

    def test_user_cannot_create_accounts(self:'any_') -> 'None':
        user = _new_user()

        with pytest.raises(UserManagementError):
            user_rules.ensure_can_create(user, 'test.new.user')

# ################################################################################################################################

    def test_user_cannot_touch_anyone_else(self:'any_') -> 'None':
        user = _new_user()
        admin = _new_admin()

        rules = [
            user_rules.ensure_can_update_profile,
            user_rules.ensure_can_set_role,
            user_rules.ensure_can_set_active,
            user_rules.ensure_can_delete,
            user_rules.ensure_can_change_password,
        ]

        for rule in rules:
            with pytest.raises(UserManagementError):
                rule(user, admin.username)

# ################################################################################################################################
# ################################################################################################################################
