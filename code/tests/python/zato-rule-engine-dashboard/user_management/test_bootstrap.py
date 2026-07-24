# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# pytest
import pytest

# Django
from django.contrib.auth.models import User

# Zato
from zato.rule_engine_dashboard.app.bootstrap import ensure_root_admin, Env_Admin_Password
from zato.rule_engine_dashboard.app.user_rules import Root_Username

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class TestEnsureRootAdmin:

    def test_root_account_exists_after_bootstrap(self:'any_') -> 'None':
        root = User.objects.get(username=Root_Username)

        assert root.is_superuser
        assert root.is_active
        assert root.check_password(os.environ[Env_Admin_Password])

# ################################################################################################################################

    def test_is_idempotent(self:'any_') -> 'None':

        # The account already exists, so repeated calls must change nothing
        ensure_root_admin()
        ensure_root_admin()

        count = User.objects.filter(username=Root_Username).count()
        assert count == 1

        # The password stayed what the environment configured at first start
        root = User.objects.get(username=Root_Username)
        assert root.check_password(os.environ[Env_Admin_Password])

# ################################################################################################################################

    def test_creation_requires_the_password_in_the_environment(self:'any_', monkeypatch:'any_') -> 'None':

        # Without the account and without the password there is nothing to create it from ..
        _ = User.objects.filter(username=Root_Username).delete()
        monkeypatch.delenv(Env_Admin_Password)

        with pytest.raises(Exception, match='Cannot create'):
            ensure_root_admin()

        # .. and with the password back, the account comes into being again.
        monkeypatch.undo()
        ensure_root_admin()

        assert User.objects.filter(username=Root_Username).exists()

# ################################################################################################################################
# ################################################################################################################################
