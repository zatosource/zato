# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The account helpers are local, the Entra test server library is shared with the main dashboard's
# suite and the TLS material builder with the soap suite - all of them use flat imports.
_here = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_here, 'lib'))
sys.path.insert(0, os.path.join(_here, '..', '..', 'zato-dashboard', 'auth', 'lib'))
sys.path.insert(0, os.path.join(_here, '..', '..', 'zato-common', 'soap', 'lib'))

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################

from entra_test_config import TestConfig
from entra_test_server import EntraTestServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# Where the application's Entra callback lives under the test client's host
_redirect_url = 'http://testserver/login/callback/'

# The root account's password, set before the application boots
_root_password = 'root-password-' + CryptoManager.generate_hex_string()

# ################################################################################################################################
# ################################################################################################################################

# The identity provider starts first so that its address can go into the environment,
# which the auth configuration module reads once, when it is first imported.
_server = EntraTestServer(TestConfig.tenant_id, TestConfig.client_id, TestConfig.client_secret)
_server.start()

os.environ['Zato_Dashboard_Auth_Type'] = 'entra'
os.environ['Zato_Dashboard_Auth_Entra_Tenant_Id'] = TestConfig.tenant_id
os.environ['Zato_Dashboard_Auth_Entra_Client_Id'] = TestConfig.client_id
os.environ['Zato_Dashboard_Auth_Entra_Client_Secret'] = TestConfig.client_secret
os.environ['Zato_Dashboard_Auth_Entra_Redirect_URL'] = _redirect_url
os.environ['Zato_Dashboard_Auth_Entra_Group_Admin'] = TestConfig.group_admin
os.environ['Zato_Dashboard_Auth_Entra_Auto_Login'] = 'false'
os.environ['Zato_Dashboard_Auth_Entra_Authority_URL'] = _server.address

# MSAL and the JWKS fetches must trust the test server's certificate
os.environ['REQUESTS_CA_BUNDLE'] = _server.ca_path

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

@pytest.fixture(scope='session', autouse=True)
def clean_up_environment() -> 'any_':
    """ Stops the identity provider once the whole suite is done.
    """
    yield

    _server.stop()

# ################################################################################################################################

@pytest.fixture(autouse=True)
def clean_database() -> 'any_':
    """ Removes everything a test created - all the users but the root account and the whole event trail.
    """
    yield

    _ = User.objects.exclude(username=Root_Username).delete()
    _ = UserEvent.objects.all().delete()

# ################################################################################################################################

@pytest.fixture
def entra_server() -> 'any_':
    """ Returns the identity provider, put back into its successful default state.
    """
    _server.reset()
    _server.set_user(TestConfig.user_principal_name, TestConfig.user_display_name, [TestConfig.group_admin])

    yield _server

# ################################################################################################################################
# ################################################################################################################################
