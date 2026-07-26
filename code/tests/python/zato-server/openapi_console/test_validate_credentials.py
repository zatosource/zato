# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import MagicMock

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.defaults import default_cluster_id
from zato.server.openapi_console.spec import validate_credentials

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict

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

_bearer_name = 'orders.bearer'
_bearer_username = 'orders.bearer.client'
_bearer_password = 'password-0002'
_bearer_id = 103

# ################################################################################################################################
# ################################################################################################################################

class _CountingDict(dict):
    """ A dict that says which keys were asked for.
    """
    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)
        self.keys_read = []

    def get(self, key:'any_', default:'any_'=None) -> 'any_':
        self.keys_read.append(key)
        return super().get(key, default)

# ################################################################################################################################
# ################################################################################################################################

class _FakeQuery:
    """ Answers with the rows the database is standing in for.
    """
    def __init__(self, rows:'anylist') -> 'None':
        self.rows = rows

    def filter(self, *ignored:'any_') -> '_FakeQuery':
        return self

    def all(self) -> 'anylist':
        return self.rows

# ################################################################################################################################

class _FakeSession:

    def __init__(self, rows:'anylist') -> 'None':
        self.rows = rows
        self.query_count = 0

    def query(self, *ignored:'any_') -> '_FakeQuery':
        self.query_count += 1
        return _FakeQuery(self.rows)

    def close(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

def _make_sec_def(id:'int', name:'str', username:'str', password:'str', is_active:'bool'=True) -> 'stranydict':
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

def _make_server(
    basic_auth_config:'stranydict',
    apikey_config:'stranydict',
    oauth_config:'stranydict',
    rows:'anylist'
) -> 'MagicMock':
    """ A server whose definitions and database rows are the ones given.
    """
    session = _FakeSession(rows)

    out = MagicMock()
    out.cluster_id = default_cluster_id
    out.odb.session.return_value = session

    url_data = out.config_manager.request_dispatcher.url_data
    url_data.basic_auth_config = basic_auth_config
    url_data.apikey_config = apikey_config
    url_data.oauth_config = oauth_config

    out.test_session = session

    return out

# ################################################################################################################################

def _make_default_server(rows:'anylist') -> 'MagicMock':
    """ A server with one definition of each type the console accepts.
    """
    basic_auth_config = _CountingDict({
        _basic_auth_name: _make_sec_def(_basic_auth_id, _basic_auth_name, _basic_auth_username, _basic_auth_password),
    })

    apikey_config = _CountingDict({
        _apikey_name: _make_sec_def(_apikey_id, _apikey_name, _apikey_username, _apikey_value),
    })

    oauth_config = _CountingDict({
        _bearer_name: _make_sec_def(_bearer_id, _bearer_name, _bearer_username, _bearer_password),
    })

    out = _make_server(basic_auth_config, apikey_config, oauth_config, rows)

    return out

# ################################################################################################################################
# ################################################################################################################################

class ValidateCredentialsTestCase(TestCase):

    def test_a_basic_auth_caller_is_resolved(self):

        rows = [(SEC_DEF_TYPE.BASIC_AUTH, _basic_auth_name)]
        server = _make_default_server(rows)

        result = validate_credentials(server, _basic_auth_username, _basic_auth_password)
        self.assertEqual(result, _basic_auth_id)

    def test_an_apikey_caller_signs_in_with_the_definition_name(self):

        server = _make_default_server([])

        result = validate_credentials(server, _apikey_name, _apikey_value)
        self.assertEqual(result, _apikey_id)

        # An API key definition is reached by name alone, so the database is left alone
        self.assertEqual(server.test_session.query_count, 0)

    def test_a_bearer_token_caller_is_resolved(self):

        rows = [(SEC_DEF_TYPE.OAUTH, _bearer_name)]
        server = _make_default_server(rows)

        result = validate_credentials(server, _bearer_username, _bearer_password)
        self.assertEqual(result, _bearer_id)

    def test_the_username_is_resolved_in_one_read(self):

        rows = [(SEC_DEF_TYPE.BASIC_AUTH, _basic_auth_name)]
        server = _make_default_server(rows)

        _ = validate_credentials(server, _basic_auth_username, _basic_auth_password)

        # One read for both types the username can belong to ..
        self.assertEqual(server.test_session.query_count, 1)

        # .. and only the definition it resolved to is looked at.
        basic_auth_config = server.config_manager.request_dispatcher.url_data.basic_auth_config
        self.assertListEqual(basic_auth_config.keys_read, [_basic_auth_name])

    def test_a_wrong_password_is_refused(self):

        rows = [(SEC_DEF_TYPE.BASIC_AUTH, _basic_auth_name)]
        server = _make_default_server(rows)

        result = validate_credentials(server, _basic_auth_username, 'password-0009')
        self.assertIsNone(result)

    def test_a_wrong_apikey_is_refused(self):

        server = _make_default_server([])

        result = validate_credentials(server, _apikey_name, 'key-value-0009')
        self.assertIsNone(result)

    def test_an_unknown_username_is_refused(self):

        server = _make_default_server([])

        result = validate_credentials(server, 'no.such.client', _basic_auth_password)
        self.assertIsNone(result)

        # Nothing resolved, so no definition was looked at
        url_data = server.config_manager.request_dispatcher.url_data
        self.assertListEqual(url_data.basic_auth_config.keys_read, [])
        self.assertListEqual(url_data.oauth_config.keys_read, [])

    def test_an_inactive_definition_is_refused(self):

        basic_auth_config = _CountingDict({
            _basic_auth_name: _make_sec_def(_basic_auth_id, _basic_auth_name, _basic_auth_username,
                _basic_auth_password, is_active=False),
        })

        rows = [(SEC_DEF_TYPE.BASIC_AUTH, _basic_auth_name)]
        server = _make_server(basic_auth_config, _CountingDict({}), _CountingDict({}), rows)

        result = validate_credentials(server, _basic_auth_username, _basic_auth_password)
        self.assertIsNone(result)

    def test_an_inactive_apikey_definition_is_refused(self):

        apikey_config = _CountingDict({
            _apikey_name: _make_sec_def(_apikey_id, _apikey_name, _apikey_username, _apikey_value, is_active=False),
        })

        server = _make_server(_CountingDict({}), apikey_config, _CountingDict({}), [])

        result = validate_credentials(server, _apikey_name, _apikey_value)
        self.assertIsNone(result)

    def test_a_definition_carrying_another_username_is_refused(self):

        # What the database resolved has to be what the definition carries
        basic_auth_config = _CountingDict({
            _basic_auth_name: _make_sec_def(_basic_auth_id, _basic_auth_name, 'orders.client.renamed',
                _basic_auth_password),
        })

        rows = [(SEC_DEF_TYPE.BASIC_AUTH, _basic_auth_name)]
        server = _make_server(basic_auth_config, _CountingDict({}), _CountingDict({}), rows)

        result = validate_credentials(server, _basic_auth_username, _basic_auth_password)
        self.assertIsNone(result)

    def test_a_row_with_no_definition_in_memory_is_refused(self):

        rows = [(SEC_DEF_TYPE.BASIC_AUTH, 'deleted.definition')]
        server = _make_default_server(rows)

        result = validate_credentials(server, _basic_auth_username, _basic_auth_password)
        self.assertIsNone(result)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
