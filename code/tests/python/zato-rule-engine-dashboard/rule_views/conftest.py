# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import tempfile

# The shared test documents live in a local lib directory with flat imports.
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

# One file-backed SQLite database shared by Django's own tables and the rule engine's SQL backend.
_db_name = 'zato-rule-views-test-' + CryptoManager.generate_hex_string() + '.db'
_db_path = os.path.join(tempfile.gettempdir(), _db_name)

# The root account's password, set before the application boots
_root_password = 'root-password-' + CryptoManager.generate_hex_string()

os.environ['Zato_Rule_Engine_Dashboard_DB_URL'] = f'sqlite:///{_db_path}'
os.environ['Zato_Rule_Engine_Dashboard_Admin_Password'] = _root_password

# ################################################################################################################################

# The application boots at import time - Django, its tables, the root account and the rule
# engine's storage - so that test modules can import Django pieces at their own module level.

# Zato
from zato.rule_engine_dashboard.app.bootstrap import bootstrap

bootstrap()

# Django
from django.test import Client
from django.test.utils import setup_test_environment

setup_test_environment()

# These imports only work once the application is up
from django.contrib.auth.models import User
from zato.common.rule_engine.sql import create_schema, drop_schema
from zato.rule_engine_dashboard.app.storage import get_backend, get_engine

# ################################################################################################################################
# ################################################################################################################################

# The one account every test signs in with.
_username = 'anna.k'
_user = User.objects.create_user(_username)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def clean_up_environment() -> 'any_':
    """ Removes the shared database file once the whole suite is done.
    """
    yield

    os.remove(_db_path)

# ################################################################################################################################

@pytest.fixture(autouse=True)
def clean_rule_tables() -> 'any_':
    """ Gives every test empty rule-engine tables.
    """
    yield

    engine = get_engine()
    drop_schema(engine)
    create_schema(engine)

# ################################################################################################################################

@pytest.fixture
def client() -> 'any_':
    """ A signed-in test client.
    """
    out = Client()
    out.force_login(_user)

    return out

# ################################################################################################################################

@pytest.fixture
def backend() -> 'any_':
    """ The application's own SQL facade, for arranging data directly.
    """
    out = get_backend()
    return out

# ################################################################################################################################

@pytest.fixture
def username() -> 'str':
    """ The name every signed-in request acts under.
    """
    return _username

# ################################################################################################################################
# ################################################################################################################################
