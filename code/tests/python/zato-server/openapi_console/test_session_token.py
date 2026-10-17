# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

# cryptography
from cryptography.fernet import Fernet

# Zato
from zato.common.bearer_token_verifier import BearerTokenVerifier
from zato.common.webapp.auth.auth_type import ConsoleAuthType
from zato.server.openapi_console.caller import ModuleCtx, resolve_session, sign_in

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_basic_auth_username = 'orders.client'
_basic_auth_password = 'password-0001'
_basic_auth_id = 101

_admin_username = 'admin.user'
_admin_password = 'password-0002'

_apikey_value = 'key-value-0001'
_apikey_id = 102

# A moment far enough past the issue of a token for the token to have expired
_seconds_past_expiry = ModuleCtx.Session_TTL + 60

# ################################################################################################################################
# ################################################################################################################################

def _make_server() -> 'MagicMock':
    """ A server with one Basic Auth and one API key definition, and a key of its own to encrypt session tokens with.
    """
    out = MagicMock()
    out.crypto_manager.secret_key = Fernet(Fernet.generate_key())

    url_data = out.url_data

    url_data.basic_auth_config = {
        'orders.basic.auth': {'config': {
            'id': _basic_auth_id,
            'username': _basic_auth_username,
            'password': _basic_auth_password,
            'is_active': True,
        }},
    }

    url_data.apikey_config = {
        'orders.apikey': {'config': {
            'id': _apikey_id,
            'username': 'Zato-Not-Used-0001',
            'password': _apikey_value,
            'is_active': True,
        }},
    }

    url_data.oauth_config = {}
    url_data.get_bearer_token_verifier.return_value = BearerTokenVerifier(MagicMock())

    return out

# ################################################################################################################################

def _make_fields(auth_type:'str', username:'str', password:'str') -> 'anydict':
    out = {
        'auth_type': auth_type,
        'username': username,
        'password': password,
    }

    return out

# ################################################################################################################################

def _is_admin(session:'MagicMock', username:'str', password:'str') -> 'bool':
    """ Stands in for the Dashboard's user table, which knows one admin.
    """
    out = username == _admin_username and password == _admin_password
    return out

# ################################################################################################################################

def _sign_in(server:'MagicMock', fields:'anydict') -> 'MagicMock':
    """ Signs in with the given fields and returns the stand-in for the admin check, which says how often it ran.
    """
    with patch('zato.server.openapi_console.caller.is_dashboard_admin', side_effect=_is_admin) as is_dashboard_admin:
        server.test_session_token = sign_in(server, fields)

    return is_dashboard_admin

# ################################################################################################################################
# ################################################################################################################################

class SignInTestCase(TestCase):

    def test_a_basic_auth_caller_receives_a_token(self) -> 'None':

        server = _make_server()
        _ = _sign_in(server, _make_fields(ConsoleAuthType.Basic_Auth, _basic_auth_username, _basic_auth_password))

        caller = resolve_session(server, server.test_session_token)

        if caller is None:
            self.fail('Expected a caller')

        self.assertFalse(caller.is_admin)
        self.assertSetEqual(caller.security_ids, {_basic_auth_id})

    def test_an_admin_receives_a_token(self) -> 'None':

        server = _make_server()
        _ = _sign_in(server, _make_fields(ConsoleAuthType.Basic_Auth, _admin_username, _admin_password))

        caller = resolve_session(server, server.test_session_token)

        if caller is None:
            self.fail('Expected a caller')

        self.assertTrue(caller.is_admin)

    def test_an_apikey_caller_is_never_checked_against_dashboard_users(self) -> 'None':

        server = _make_server()
        is_dashboard_admin = _sign_in(server, _make_fields(ConsoleAuthType.API_Key, '', _apikey_value))

        is_dashboard_admin.assert_not_called()
        self.assertIsNotNone(server.test_session_token)

    def test_wrong_credentials_receive_no_token(self) -> 'None':

        server = _make_server()
        _ = _sign_in(server, _make_fields(ConsoleAuthType.Basic_Auth, _basic_auth_username, 'password-0009'))

        self.assertIsNone(server.test_session_token)

    def test_the_token_does_not_reveal_the_credentials(self) -> 'None':

        server = _make_server()
        _ = _sign_in(server, _make_fields(ConsoleAuthType.Basic_Auth, _basic_auth_username, _basic_auth_password))

        self.assertNotIn(_basic_auth_password, server.test_session_token)
        self.assertNotIn(_basic_auth_username, server.test_session_token)

# ################################################################################################################################
# ################################################################################################################################

class ResolveSessionTestCase(TestCase):

    def test_an_admin_password_is_verified_at_sign_in_only(self) -> 'None':

        server = _make_server()
        is_dashboard_admin = _sign_in(server, _make_fields(ConsoleAuthType.Basic_Auth, _admin_username, _admin_password))

        with patch('zato.server.openapi_console.caller.is_dashboard_admin') as is_dashboard_admin_later:
            _ = resolve_session(server, server.test_session_token)
            _ = resolve_session(server, server.test_session_token)

        is_dashboard_admin.assert_called_once()
        is_dashboard_admin_later.assert_not_called()
        server.odb.session.assert_called_once()

    def test_a_definition_deactivated_after_sign_in_ends_the_session(self) -> 'None':

        server = _make_server()
        _ = _sign_in(server, _make_fields(ConsoleAuthType.API_Key, '', _apikey_value))

        server.url_data.apikey_config['orders.apikey']['config']['is_active'] = False

        self.assertIsNone(resolve_session(server, server.test_session_token))

    def test_a_changed_secret_ends_the_session(self) -> 'None':

        server = _make_server()
        _ = _sign_in(server, _make_fields(ConsoleAuthType.Basic_Auth, _basic_auth_username, _basic_auth_password))

        server.url_data.basic_auth_config['orders.basic.auth']['config']['password'] = 'password-0003'

        self.assertIsNone(resolve_session(server, server.test_session_token))

    def test_an_expired_token_identifies_no_one(self) -> 'None':

        server = _make_server()
        _ = _sign_in(server, _make_fields(ConsoleAuthType.Basic_Auth, _basic_auth_username, _basic_auth_password))

        # The token carries the time of its issue, which the check compares with the current time
        issued_at = server.crypto_manager.secret_key.extract_timestamp(server.test_session_token.encode('utf8'))

        with patch('cryptography.fernet.time') as fernet_time:
            fernet_time.time.return_value = issued_at + _seconds_past_expiry
            caller = resolve_session(server, server.test_session_token)

        self.assertIsNone(caller)

    def test_a_token_of_another_key_identifies_no_one(self) -> 'None':

        server = _make_server()
        _ = _sign_in(server, _make_fields(ConsoleAuthType.Basic_Auth, _basic_auth_username, _basic_auth_password))

        other_server = _make_server()

        self.assertIsNone(resolve_session(other_server, server.test_session_token))

    def test_another_value_encrypted_with_the_same_key_identifies_no_one(self) -> 'None':

        server = _make_server()
        token = server.crypto_manager.secret_key.encrypt(b'{"is_admin": true}').decode('utf8')

        self.assertIsNone(resolve_session(server, token))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
