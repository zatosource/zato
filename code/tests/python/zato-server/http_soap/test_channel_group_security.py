# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from unittest import main, TestCase
from unittest.mock import MagicMock

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.exception import Forbidden
from zato.server.connection.http_soap.channel import RequestDispatcher

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

_cid = 'zcid-test-0001'
_channel_name = 'test.channel'

_security_id = 201

_username = 'orders.client'
_password = 'password-0001'

_apikey_header = 'HTTP_X_API_KEY'
_apikey = 'key-value-0001'

# ################################################################################################################################
# ################################################################################################################################

def _make_dispatcher() -> 'RequestDispatcher':
    """ A dispatcher with everything but its url_data mocked away.
    """
    out = RequestDispatcher(
        server=MagicMock(),
        url_data=MagicMock(),
        request_handler=MagicMock(),
        return_tracebacks=False,
        default_error_message='Internal server error',
        http_methods_allowed=['GET', 'POST'],
    )

    return out

# ################################################################################################################################

def _make_basic_auth_header() -> 'str':
    """ The Authorization header a Basic Auth caller sends.
    """
    credentials = f'{_username}:{_password}'.encode('utf8')
    encoded = b64encode(credentials).decode('utf8')

    out = 'Basic ' + encoded

    return out

# ################################################################################################################################

def _make_ctx(apikey_header:'str | None'=None) -> 'MagicMock':
    """ A security groups context that accepts whatever credentials it is given.
    """
    out = MagicMock()
    out.apikey_header = apikey_header
    out.check_security_basic_auth.return_value = _security_id
    out.check_security_apikey.return_value = _security_id
    out.check_security_bearer_token.return_value = _security_id

    return out

# ################################################################################################################################

def _make_sec_def() -> 'stranydict':
    out = {
        'id': _security_id,
        'name': 'test.basic.auth',
        'username': _username,
        'sec_type': SEC_DEF_TYPE.BASIC_AUTH,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class MatchedCredentialWithoutADefinitionTestCase(TestCase):
    """ What happens when a credential matches but the definition behind it cannot be looked up.

    The definition is where the caller recorded in the audit event, the definition-level rate limit
    and self.channel.security all come from, so a request whose definition does not resolve has
    nowhere to take any of them from and ends here.
    """

# ################################################################################################################################

    def test_basic_auth_without_a_definition(self) -> 'None':
        dispatcher = _make_dispatcher()
        dispatcher.url_data.basic_auth_get_by_id.return_value = None

        ctx = _make_ctx()
        wsgi_environ = {'HTTP_AUTHORIZATION': _make_basic_auth_header()}

        with self.assertRaises(Forbidden):
            dispatcher.check_security_via_groups(_cid, _channel_name, ctx, wsgi_environ)

        # Nothing about the caller reached the WSGI environment
        self.assertNotIn('zato.sec_def', wsgi_environ)

# ################################################################################################################################

    def test_apikey_without_a_definition(self) -> 'None':
        dispatcher = _make_dispatcher()
        dispatcher.url_data.apikey_get_by_id.return_value = None

        ctx = _make_ctx(apikey_header=_apikey_header)
        wsgi_environ = {_apikey_header: _apikey}

        with self.assertRaises(Forbidden):
            dispatcher.check_security_via_groups(_cid, _channel_name, ctx, wsgi_environ)

        self.assertNotIn('zato.sec_def', wsgi_environ)

# ################################################################################################################################

    def test_bearer_token_without_a_definition(self) -> 'None':
        dispatcher = _make_dispatcher()
        dispatcher.url_data.oauth_get_by_id.return_value = None

        ctx = _make_ctx()
        wsgi_environ = {'HTTP_AUTHORIZATION': 'Bearer test-token-0001'}

        with self.assertRaises(Forbidden):
            dispatcher.check_security_via_groups(_cid, _channel_name, ctx, wsgi_environ)

        self.assertNotIn('zato.sec_def', wsgi_environ)

# ################################################################################################################################

    def test_a_definition_that_resolves_is_handed_on(self) -> 'None':
        dispatcher = _make_dispatcher()
        dispatcher.url_data.basic_auth_get_by_id.return_value = _make_sec_def()

        ctx = _make_ctx()
        wsgi_environ = {'HTTP_AUTHORIZATION': _make_basic_auth_header()}

        dispatcher.check_security_via_groups(_cid, _channel_name, ctx, wsgi_environ)

        self.assertIn('zato.sec_def', wsgi_environ)
        self.assertEqual(wsgi_environ['zato.sec_def']['id'], _security_id)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
