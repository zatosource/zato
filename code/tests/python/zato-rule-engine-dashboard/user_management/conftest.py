# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The account helpers are local and use flat imports
_here = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_here, 'lib'))

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# The root account's password, set before the application boots
_root_password = 'root-password-' + CryptoManager.generate_hex_string()

# ################################################################################################################################
# ################################################################################################################################

# The application's own configuration - an in-memory database and the root account's password
os.environ['Zato_Rule_Engine_Dashboard_DB_URL'] = 'sqlite:///:memory:'
os.environ['Zato_Rule_Engine_Dashboard_Admin_Password'] = _root_password

# ################################################################################################################################

# The application boots at import time - Django, its tables and the root account -
# so that test modules can import Django models at their own module level.

# Zato
from zato.rule_engine_dashboard.app.bootstrap import bootstrap

bootstrap()

# Django
from django.test.utils import setup_test_environment

setup_test_environment()

# These imports only work once the application is up
from django.contrib.auth.models import User
from zato.rule_engine_dashboard.app.models import UserEvent
from zato.rule_engine_dashboard.app.user_rules import Root_Username

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def clean_database() -> 'any_':
    """ Removes everything a test created - all the users but the root account and the whole event trail.
    """
    yield

    _ = User.objects.exclude(username=Root_Username).delete()
    _ = UserEvent.objects.all().delete()

# ################################################################################################################################
# ################################################################################################################################
