# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import MagicMock

# Zato
from zato.common.bearer_token_verifier import BearerTokenVerifier
from zato.server.api_portal.caller import validate_api_key, validate_bearer_token, validate_credentials

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strnone

# ################################################################################################################################
# ################################################################################################################################

_basic_auth_name = 'orders.basic.auth'
_basic_auth_username = 'orders.client'
_basic_auth_password = 'password-0001'
_basic_auth_id = 101

_apikey_name = 'orders.apikey'
_apikey_username = 'Zato-Not-Used-0001'
_apikey_value = 'key-value-0001'
_apikey_id = 102

_apikey_second_name = 'orders.apikey.second'
_apikey_second_id = 105

_bearer_name = 'orders.bearer'
_bearer_username = 'orders.bearer.client'
_bearer_password = 'password-0002'
_bearer_id = 103

_bearer_static_name = 'orders.bearer.static'
_bearer_static_token = 'token-value-0001'
_bearer_static_id = 104

_bearer_static_second_name = 'orders.bearer.static.second'
_bearer_static_second_id = 106

# ################################################################################################################################
# ################################################################################################################################

def _make_sec_def(
    id:'int',
    name:'str',
    username:'strnone',
    password:'strnone',
    is_active:'bool'=True,
    ) -> 'stranydict':

    out = {
        'config': {
            'id': id,
            'name': name,
            'username': username,
            'password': password,
            'is_active': is_active,
        }
    }

    return out

# ################################################################################################################################

def _make_server(basic_auth_config:'stranydict', apikey_config:'stranydict', oauth_config:'stranydict') -> 'MagicMock':
    """ A server whose definitions are the ones given, with a database that no check is to read.
    """
    out = MagicMock()

    url_data = out.url_data
    url_data.basic_auth_config = basic_auth_config
    url_data.apikey_config = apikey_config
    url_data.oauth_config = oauth_config

    # Static tokens are compared in memory, so the verifier never reaches its cache
    url_data.get_bearer_token_verifier.return_value = BearerTokenVerifier(MagicMock())

    return out

# ################################################################################################################################

def _make_default_server() -> 'MagicMock':
    """ A server with one definition of each type the portal accepts.
    """
    basic_auth_config = {
        _basic_auth_name: _make_sec_def(_basic_auth_id, _basic_auth_name, _basic_auth_username, _basic_auth_password),
    }

    apikey_config = {
        _apikey_name: _make_sec_def(_apikey_id, _apikey_name, _apikey_username, _apikey_value),
    }

    oauth_config = {
        _bearer_name: _make_sec_def(_bearer_id, _bearer_name, _bearer_username, _bearer_password),
    }

    out = _make_server(basic_auth_config, apikey_config, oauth_config)

    return out

# ################################################################################################################################
# ################################################################################################################################

class ValidateCredentialsTestCase(TestCase):

    def test_a_basic_auth_caller_is_resolved(self) -> 'None':

        server = _make_default_server()

        result = validate_credentials(server, _basic_auth_username, _basic_auth_password)
        self.assertSetEqual(result, {_basic_auth_id})

        # The definitions are checked in memory, so the database is left alone
        server.odb.session.assert_not_called()

    def test_a_bearer_token_client_is_resolved(self) -> 'None':

        server = _make_default_server()

        result = validate_credentials(server, _bearer_username, _bearer_password)
        self.assertSetEqual(result, {_bearer_id})

    def test_a_username_of_both_types_resolves_to_both(self) -> 'None':

        basic_auth_config = {
            _basic_auth_name: _make_sec_def(_basic_auth_id, _basic_auth_name, _basic_auth_username, _basic_auth_password),
        }

        oauth_config = {
            _bearer_name: _make_sec_def(_bearer_id, _bearer_name, _basic_auth_username, _basic_auth_password),
        }

        server = _make_server(basic_auth_config, {}, oauth_config)

        result = validate_credentials(server, _basic_auth_username, _basic_auth_password)
        self.assertSetEqual(result, {_basic_auth_id, _bearer_id})

    def test_an_apikey_definition_name_is_not_a_username(self) -> 'None':

        server = _make_default_server()

        result = validate_credentials(server, _apikey_name, _apikey_value)
        self.assertSetEqual(result, set())

    def test_a_wrong_password_is_refused(self) -> 'None':

        server = _make_default_server()

        result = validate_credentials(server, _basic_auth_username, 'password-0009')
        self.assertSetEqual(result, set())

    def test_an_unknown_username_is_refused(self) -> 'None':

        server = _make_default_server()

        result = validate_credentials(server, 'no.such.client', _basic_auth_password)
        self.assertSetEqual(result, set())

    def test_an_inactive_definition_is_refused(self) -> 'None':

        basic_auth_config = {
            _basic_auth_name: _make_sec_def(_basic_auth_id, _basic_auth_name, _basic_auth_username,
                _basic_auth_password, is_active=False),
        }

        server = _make_server(basic_auth_config, {}, {})

        result = validate_credentials(server, _basic_auth_username, _basic_auth_password)
        self.assertSetEqual(result, set())

    def test_definitions_without_a_username_or_a_secret_are_skipped(self) -> 'None':

        oauth_config = {
            _bearer_static_name: _make_sec_def(_bearer_static_id, _bearer_static_name, None, None),
            _bearer_name: _make_sec_def(_bearer_id, _bearer_name, _bearer_username, None),
        }

        server = _make_server({}, {}, oauth_config)

        result = validate_credentials(server, _bearer_username, _bearer_password)
        self.assertSetEqual(result, set())

# ################################################################################################################################
# ################################################################################################################################

class ValidateAPIKeyTestCase(TestCase):

    def test_an_apikey_caller_signs_in_with_the_key_alone(self) -> 'None':

        server = _make_default_server()

        result = validate_api_key(server, _apikey_value)
        self.assertSetEqual(result, {_apikey_id})

    def test_a_key_of_two_definitions_resolves_to_both(self) -> 'None':

        apikey_config = {
            _apikey_name: _make_sec_def(_apikey_id, _apikey_name, _apikey_username, _apikey_value),
            _apikey_second_name: _make_sec_def(_apikey_second_id, _apikey_second_name, _apikey_username, _apikey_value),
        }

        server = _make_server({}, apikey_config, {})

        result = validate_api_key(server, _apikey_value)
        self.assertSetEqual(result, {_apikey_id, _apikey_second_id})

    def test_a_wrong_apikey_is_refused(self) -> 'None':

        server = _make_default_server()

        result = validate_api_key(server, 'key-value-0009')
        self.assertSetEqual(result, set())

    def test_an_inactive_apikey_definition_is_refused(self) -> 'None':

        apikey_config = {
            _apikey_name: _make_sec_def(_apikey_id, _apikey_name, _apikey_username, _apikey_value, is_active=False),
        }

        server = _make_server({}, apikey_config, {})

        result = validate_api_key(server, _apikey_value)
        self.assertSetEqual(result, set())

# ################################################################################################################################
# ################################################################################################################################

def _make_static_token_def(id:'int', name:'str', static_token:'str', is_active:'bool'=True) -> 'stranydict':
    """ A Bearer token definition that accepts the given static token inbound.
    """
    out = _make_sec_def(id, name, '', static_token, is_active=is_active)
    out['config']['static_token'] = static_token

    return out

# ################################################################################################################################

def _make_bearer_server(static_token:'str', is_active:'bool'=True) -> 'MagicMock':
    """ A server with one outgoing-only Bearer token definition and one that accepts the given static token inbound.
    """
    oauth_config = {
        _bearer_name: _make_sec_def(_bearer_id, _bearer_name, _bearer_username, _bearer_password),
        _bearer_static_name: _make_static_token_def(_bearer_static_id, _bearer_static_name, static_token, is_active),
    }

    out = _make_server({}, {}, oauth_config)

    return out

# ################################################################################################################################
# ################################################################################################################################

class ValidateBearerTokenTestCase(TestCase):

    def test_a_token_caller_signs_in_with_the_token_alone(self) -> 'None':

        server = _make_bearer_server(_bearer_static_token)

        result = validate_bearer_token(server, _bearer_static_token)
        self.assertSetEqual(result, {_bearer_static_id})

    def test_a_token_of_two_definitions_resolves_to_both(self) -> 'None':

        oauth_config = {
            _bearer_static_name: _make_static_token_def(_bearer_static_id, _bearer_static_name, _bearer_static_token),
            _bearer_static_second_name: _make_static_token_def(
                _bearer_static_second_id, _bearer_static_second_name, _bearer_static_token),
        }

        server = _make_server({}, {}, oauth_config)

        result = validate_bearer_token(server, _bearer_static_token)
        self.assertSetEqual(result, {_bearer_static_id, _bearer_static_second_id})

    def test_a_wrong_token_is_refused(self) -> 'None':

        server = _make_bearer_server(_bearer_static_token)

        result = validate_bearer_token(server, 'token-value-0009')
        self.assertSetEqual(result, set())

    def test_a_client_secret_is_not_a_token(self) -> 'None':

        server = _make_bearer_server(_bearer_static_token)

        result = validate_bearer_token(server, _bearer_password)
        self.assertSetEqual(result, set())

    def test_an_inactive_token_definition_is_refused(self) -> 'None':

        server = _make_bearer_server(_bearer_static_token, is_active=False)

        result = validate_bearer_token(server, _bearer_static_token)
        self.assertSetEqual(result, set())

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
