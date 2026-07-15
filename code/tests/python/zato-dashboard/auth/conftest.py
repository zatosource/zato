# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import shutil
import sys
import tempfile

# The test server library uses flat imports and the TLS material builder is shared with the soap suite.
_here = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(_here, 'lib'))
sys.path.insert(0, os.path.join(_here, '..', '..', 'zato-common', 'soap', 'lib'))

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.crypto.const import well_known_data

# ################################################################################################################################

from entra_test_config import TestConfig
from entra_test_server import EntraTestServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

def _set_up_django(config_dir:'str') -> 'None':
    """ Boots Django against an in-memory database, the same way 'zato start' boots it
    against a real one - through update_globals and the settings module.
    """

    # Django
    import django
    from django.core.management import call_command
    from django.test.utils import setup_test_environment

    # Zato
    from zato.admin.zato_settings import update_globals

    # The crypto material the settings loader insists on ..
    secret_key = CryptoManager.generate_key()
    crypto_manager = CryptoManager.from_secret_key(secret_key)
    encrypted_well_known = crypto_manager.encrypt(well_known_data, needs_str=True)

    # .. the settings database lives under the config directory ..
    repo_dir = os.path.join(config_dir, 'config', 'repo')
    os.makedirs(repo_dir, exist_ok=True)

    admin_invoke_password = 'test-admin-invoke-' + CryptoManager.generate_hex_string()
    django_secret_key = CryptoManager.generate_password(to_str=True)

    config = {
        'zato_secret_key': secret_key.decode('utf8'),
        'well_known_data': encrypted_well_known,
        'SECRET_KEY': django_secret_key,
        'ADMIN_INVOKE_NAME': 'admin.invoke',
        'ADMIN_INVOKE_PASSWORD': admin_invoke_password,
        'config_dir': config_dir,
        'db_type': 'sqlite',
        'DATABASE_NAME': ':memory:',
        'DATABASE_USER': '',
        'DATABASE_PASSWORD': '',
        'DATABASE_HOST': '',
        'DATABASE_PORT': '',
        'DATABASE_OPTIONS': {},
    }

    _ = update_globals(config, needs_crypto=False)

    # .. now Django can start ..
    os.environ['DJANGO_SETTINGS_MODULE'] = 'zato.admin.settings'
    django.setup()

    # .. the test client's host name must be allowed ..
    setup_test_environment()

    # .. and the in-memory database receives all the tables.
    _ = call_command('migrate', run_syncdb=True, verbosity=0)

# ################################################################################################################################
# ################################################################################################################################

# The server starts and Django boots at import time so that test modules can import
# Django models at their own module level, before any fixture runs.

_server = EntraTestServer(TestConfig.tenant_id, TestConfig.client_id, TestConfig.client_secret)
_server.start()

# The dashboard reads all of this once, when the auth module is first imported ..
os.environ['Zato_Dashboard_Auth_Type'] = 'entra'
os.environ['Zato_Dashboard_Auth_Entra_Tenant_Id'] = TestConfig.tenant_id
os.environ['Zato_Dashboard_Auth_Entra_Client_Id'] = TestConfig.client_id
os.environ['Zato_Dashboard_Auth_Entra_Client_Secret'] = TestConfig.client_secret
os.environ['Zato_Dashboard_Auth_Entra_Redirect_URL'] = TestConfig.redirect_url
os.environ['Zato_Dashboard_Auth_Entra_Group_Admin'] = TestConfig.group_admin
os.environ['Zato_Dashboard_Auth_Entra_Auto_Login'] = 'false'
os.environ['Zato_Dashboard_Auth_Entra_Authority_URL'] = _server.address

# .. MSAL and the dashboard's JWKS fetches must trust the test server's certificate ..
os.environ['REQUESTS_CA_BUNDLE'] = _server.ca_path

# .. and Django comes up now.
_config_dir = tempfile.mkdtemp(prefix='zato_dashboard_auth_test_')
_set_up_django(_config_dir)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def clean_up_environment() -> 'any_':
    """ Stops the server and removes the temporary directory once the whole suite is done.
    """
    yield

    _server.stop()
    shutil.rmtree(_config_dir, ignore_errors=True)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def entra_server() -> 'any_':
    """ Returns the test server, put back into its successful default state before every test.
    """
    _server.reset()
    _server.set_user(TestConfig.user_principal_name, TestConfig.user_display_name, [TestConfig.group_admin])

    yield _server

# ################################################################################################################################
# ################################################################################################################################
