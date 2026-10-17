# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import time
from unittest import main, TestCase
from unittest.mock import MagicMock, patch

# Zato
from zato.openapi.console.client import ModuleCtx, OpenAPIConsoleClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from unittest.mock import MagicMock as MagicMockType
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# How long the console waits for the document behind sign-in and page loads, in seconds
_expected_spec_timeout = 10.0

# How long the console waits for an endpoint invoked through the console, in seconds
_expected_invoke_timeout = 120.0

# How far apart the moment a test reads the clock and the moment the client reads it may be, in seconds
_clock_tolerance = 5.0

_credentials = {'auth_type': 'basic_auth', 'username': 'orders.client', 'password': 'password-0001'}
_session_token = 'session-token-0001'

# The IDs that Redis gives the messages of a test
_request_id = '1700000000000-0'
_other_reply_id = '1700000000001-0'
_reply_id = '1700000000002-0'

# ################################################################################################################################
# ################################################################################################################################

class ClientExpiryTestCase(TestCase):
    """ Each command the console sends says when the console stops waiting for its reply.
    """

# ################################################################################################################################

    def _make_client(self) -> 'tuple[OpenAPIConsoleClient, MagicMockType]':
        """ Returns a client over a mocked Redis connection, together with that connection.
        """
        redis_conn = MagicMock()
        redis_conn.xrevrange.return_value = []
        redis_conn.xadd.return_value = _request_id

        client = OpenAPIConsoleClient(redis_conn)

        return client, redis_conn

# ################################################################################################################################

    def _get_sent_fields(self, redis_conn:'MagicMockType') -> 'anydict':
        """ Returns the fields that went onto the request stream.
        """
        call = redis_conn.xadd.call_args
        out = call.args[1]

        return out

# ################################################################################################################################

    def _get_wait_timeout(self, wait_for_reply:'MagicMockType') -> 'float':
        """ Returns how long the client waited for the reply.
        """
        call = wait_for_reply.call_args
        out = call.args[2]

        return out

# ################################################################################################################################

    def _assert_expires_in(self, fields:'anydict', now:'float', expected:'float') -> 'None':
        expires_in = fields['expires_at'] - now

        self.assertGreaterEqual(expires_in, expected - _clock_tolerance)
        self.assertLessEqual(expires_in, expected + _clock_tolerance)

# ################################################################################################################################

    def test_the_timeouts(self) -> 'None':
        self.assertEqual(ModuleCtx.Reply_Timeout, _expected_spec_timeout)
        self.assertEqual(ModuleCtx.Invoke_Reply_Timeout, _expected_invoke_timeout)

# ################################################################################################################################

    def test_the_document_is_waited_for_ten_seconds(self) -> 'None':
        client, redis_conn = self._make_client()
        now = time()

        with patch.object(OpenAPIConsoleClient, '_wait_for_reply', return_value=None) as wait_for_reply:
            _ = client.get_spec(_session_token)

        fields = self._get_sent_fields(redis_conn)

        self._assert_expires_in(fields, now, _expected_spec_timeout)
        self.assertEqual(self._get_wait_timeout(wait_for_reply), _expected_spec_timeout)

# ################################################################################################################################

    def test_an_invocation_is_waited_for_two_minutes(self) -> 'None':
        client, redis_conn = self._make_client()
        now = time()

        with patch.object(OpenAPIConsoleClient, '_wait_for_reply', return_value=None) as wait_for_reply:
            _ = client.invoke(_session_token, 'GET', '/api/orders', '', '{}', '', '10.151.12.1')

        fields = self._get_sent_fields(redis_conn)

        self._assert_expires_in(fields, now, _expected_invoke_timeout)
        self.assertEqual(self._get_wait_timeout(wait_for_reply), _expected_invoke_timeout)

# ################################################################################################################################

    def test_sign_in_is_waited_for_ten_seconds(self) -> 'None':
        client, redis_conn = self._make_client()
        now = time()

        with patch.object(OpenAPIConsoleClient, '_wait_for_reply', return_value=None) as wait_for_reply:
            _ = client.sign_in(_credentials)

        fields = self._get_sent_fields(redis_conn)

        self.assertEqual(fields['command'], 'sign_in')
        self._assert_expires_in(fields, now, _expected_spec_timeout)
        self.assertEqual(self._get_wait_timeout(wait_for_reply), _expected_spec_timeout)

# ################################################################################################################################

    def test_later_commands_carry_the_session_token_alone(self) -> 'None':
        client, redis_conn = self._make_client()

        with patch.object(OpenAPIConsoleClient, '_wait_for_reply', return_value=None):
            _ = client.get_spec(_session_token)

        fields = self._get_sent_fields(redis_conn)

        self.assertEqual(fields['session_token'], _session_token)
        self.assertNotIn('password', fields)
        self.assertNotIn('username', fields)

# ################################################################################################################################
# ################################################################################################################################

class ClientStreamRetentionTestCase(TestCase):
    """ Commands and replies are removed from their streams once they are of no further use.
    """

# ################################################################################################################################

    def _make_client(self, correlation_id:'str') -> 'tuple[OpenAPIConsoleClient, MagicMockType]':
        """ Returns a client over a mocked Redis connection, whose reply stream holds a reply to another request
        followed by a reply with the given correlation ID.
        """
        redis_conn = MagicMock()
        redis_conn.xrevrange.return_value = []
        redis_conn.xadd.return_value = _request_id
        redis_conn.xread.return_value = [
            ['reply-stream', [
                [_other_reply_id, {'correlation_id': 'correlation-other'}],
                [_reply_id, {'correlation_id': correlation_id, 'status': 'ok', 'data': '{}'}],
            ]],
        ]

        client = OpenAPIConsoleClient(redis_conn)

        return client, redis_conn

# ################################################################################################################################

    def test_a_reply_is_removed_once_read(self) -> 'None':
        client, redis_conn = self._make_client('correlation-0001')

        with patch('zato.openapi.console.client.CryptoManager.generate_hex_string', return_value='correlation-0001'):
            _ = client.get_spec(_session_token)

        # Replies to other requests are left for their own readers
        redis_conn.xdel.assert_called_once_with(ModuleCtx.Reply_Stream, _reply_id)

# ################################################################################################################################

    def test_a_request_no_server_replied_to_is_removed(self) -> 'None':
        client, redis_conn = self._make_client('correlation-other-request')

        with patch.object(ModuleCtx, 'Reply_Timeout', 0.0):
            _ = client.get_spec(_session_token)

        redis_conn.xdel.assert_called_once_with(ModuleCtx.Request_Stream, _request_id)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
