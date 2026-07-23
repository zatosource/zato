# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.webapp.auth.config import build_auth_config, AuthType

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_all_env_keys = [
    'Zato_Dashboard_Auth_Type',
    'Zato_Dashboard_Auth_Entra_Tenant_Id',
    'Zato_Dashboard_Auth_Entra_Client_Id',
    'Zato_Dashboard_Auth_Entra_Client_Secret',
    'Zato_Dashboard_Auth_Entra_Redirect_URL',
    'Zato_Dashboard_Auth_Entra_Group_Admin',
    'Zato_Dashboard_Auth_Entra_Auto_Login',
    'Zato_Dashboard_Auth_Entra_Authority_URL',
]

# ################################################################################################################################

def _clear_environment(monkeypatch:'any_') -> 'None':
    for key in _all_env_keys:
        monkeypatch.delenv(key, raising=False)

# ################################################################################################################################
# ################################################################################################################################

class TestAuthConfig:

    def test_defaults(self:'any_', monkeypatch:'any_') -> 'None':
        _clear_environment(monkeypatch)

        config = build_auth_config()

        assert config.auth_type == AuthType.Built_In
        assert config.tenant_id == ''
        assert config.client_id == ''
        assert config.client_secret == ''
        assert config.redirect_url == ''
        assert config.authority_url == 'https://login.microsoftonline.com'
        assert config.group_admin == []
        assert config.auto_login is False

# ################################################################################################################################

    def test_entra_values_are_read(self:'any_', monkeypatch:'any_') -> 'None':
        _clear_environment(monkeypatch)

        monkeypatch.setenv('Zato_Dashboard_Auth_Type', 'entra')
        monkeypatch.setenv('Zato_Dashboard_Auth_Entra_Tenant_Id', 'test-tenant-id')
        monkeypatch.setenv('Zato_Dashboard_Auth_Entra_Client_Id', 'test-client-id')
        monkeypatch.setenv('Zato_Dashboard_Auth_Entra_Client_Secret', 'test-client-secret')
        monkeypatch.setenv('Zato_Dashboard_Auth_Entra_Redirect_URL', 'https://dashboard.example.com/accounts/login/callback/')
        monkeypatch.setenv('Zato_Dashboard_Auth_Entra_Authority_URL', 'https://login.example.com')

        config = build_auth_config()

        assert config.auth_type == AuthType.Entra
        assert config.tenant_id == 'test-tenant-id'
        assert config.client_id == 'test-client-id'
        assert config.client_secret == 'test-client-secret'
        assert config.redirect_url == 'https://dashboard.example.com/accounts/login/callback/'
        assert config.authority_url == 'https://login.example.com'

# ################################################################################################################################

    def test_group_lists_are_parsed(self:'any_', monkeypatch:'any_') -> 'None':
        _clear_environment(monkeypatch)

        monkeypatch.setenv('Zato_Dashboard_Auth_Entra_Group_Admin', 'group-one, group-two ,group-three')

        config = build_auth_config()

        assert config.group_admin == ['group-one', 'group-two', 'group-three']

# ################################################################################################################################

    def test_auto_login_is_parsed_as_a_boolean(self:'any_', monkeypatch:'any_') -> 'None':
        _clear_environment(monkeypatch)

        monkeypatch.setenv('Zato_Dashboard_Auth_Entra_Auto_Login', 'True')
        config = build_auth_config()
        assert config.auto_login is True

        monkeypatch.setenv('Zato_Dashboard_Auth_Entra_Auto_Login', 'false')
        config = build_auth_config()
        assert config.auto_login is False

# ################################################################################################################################
# ################################################################################################################################
