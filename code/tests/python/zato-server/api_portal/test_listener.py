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
from zato.server.api_portal.listener import _handle_sign_in, handle_message, is_expired, ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

_stream_name = ModuleCtx.Request_Stream
_msg_id = '1700000000000-0'
_correlation_id = 'correlation-0001'

# How far the portal's deadline is from now in the tests, in seconds
_deadline_offset = 60.0

# ################################################################################################################################
# ################################################################################################################################

def _make_fields(expires_at:'float') -> 'anydict':
    """ A command as it arrives from the portal, whose reply the portal waits for until the given time.
    """
    out = {
        'command': 'invoke',
        'correlation_id': _correlation_id,
        'expires_at': str(expires_at),
    }

    return out

# ################################################################################################################################

def _handle(fields:'anydict') -> 'any_':
    """ Handles a command with a handler that replies at once, and returns the handler and the Redis connection.
    """
    handler = MagicMock(return_value={'correlation_id': _correlation_id, 'status': 'ok', 'data': ''})
    redis_conn = MagicMock()

    with patch.dict('zato.server.api_portal.listener._command_handlers', {'invoke': handler}):
        handle_message(MagicMock(), redis_conn, _stream_name, _msg_id, fields)

    return handler, redis_conn

# ################################################################################################################################
# ################################################################################################################################

class ExpiryTestCase(TestCase):
    """ A command is expired once the portal has stopped waiting for its reply.
    """

# ################################################################################################################################

    def test_before_the_deadline(self) -> 'None':
        now = time()
        fields = _make_fields(now + _deadline_offset)

        self.assertFalse(is_expired(fields, now))

# ################################################################################################################################

    def test_after_the_deadline(self) -> 'None':
        now = time()
        fields = _make_fields(now - _deadline_offset)

        self.assertTrue(is_expired(fields, now))

# ################################################################################################################################
# ################################################################################################################################

class HandleMessageTestCase(TestCase):
    """ A command is run and replied to while the portal waits for it, and it is never run afterwards.
    """

# ################################################################################################################################

    def test_a_current_command_is_run_and_replied_to(self) -> 'None':
        now = time()
        handler, redis_conn = _handle(_make_fields(now + _deadline_offset))

        handler.assert_called_once()
        redis_conn.xadd.assert_called_once()
        redis_conn.xack.assert_called_once_with(_stream_name, ModuleCtx.Consumer_Group, _msg_id)

# ################################################################################################################################

    def test_a_handled_command_is_removed_from_the_stream(self) -> 'None':
        now = time()
        _, redis_conn = _handle(_make_fields(now + _deadline_offset))

        redis_conn.xdel.assert_called_once_with(_stream_name, _msg_id)

# ################################################################################################################################

    def test_an_expired_command_is_removed_from_the_stream(self) -> 'None':
        now = time()
        _, redis_conn = _handle(_make_fields(now - _deadline_offset))

        redis_conn.xdel.assert_called_once_with(_stream_name, _msg_id)

# ################################################################################################################################

    def test_an_expired_command_is_not_run(self) -> 'None':
        now = time()
        handler, redis_conn = _handle(_make_fields(now - _deadline_offset))

        handler.assert_not_called()
        redis_conn.xadd.assert_not_called()

# ################################################################################################################################

    def test_an_expired_command_is_acknowledged(self) -> 'None':
        now = time()
        _, redis_conn = _handle(_make_fields(now - _deadline_offset))

        redis_conn.xack.assert_called_once_with(_stream_name, ModuleCtx.Consumer_Group, _msg_id)

# ################################################################################################################################

    def test_a_failing_command_replies_with_an_error(self) -> 'None':
        now = time()
        fields = _make_fields(now + _deadline_offset)

        handler = MagicMock(side_effect=Exception('Test error message'))
        redis_conn = MagicMock()

        with patch.dict('zato.server.api_portal.listener._command_handlers', {'invoke': handler}):
            handle_message(MagicMock(), redis_conn, _stream_name, _msg_id, fields)

        call = redis_conn.xadd.call_args
        reply = call.args[1]

        self.assertEqual(reply, {'correlation_id': _correlation_id, 'status': 'error', 'data': ''})

# ################################################################################################################################
# ################################################################################################################################

class SignInTestCase(TestCase):
    """ A sign-in replies with the session token that the server issued, or with a rejection.
    """

# ################################################################################################################################

    def _sign_in(self, session_token:'any_') -> 'anydict':

        fields = _make_fields(time() + _deadline_offset)
        fields['command'] = 'sign_in'

        with patch('zato.server.api_portal.listener.sign_in', return_value=session_token):
            out = _handle_sign_in(MagicMock(), fields)

        return out

# ################################################################################################################################

    def test_accepted_credentials_receive_a_session_token(self) -> 'None':
        reply = self._sign_in('session-token-0001')
        self.assertEqual(reply, {'correlation_id': _correlation_id, 'status': 'ok', 'data': 'session-token-0001'})

# ################################################################################################################################

    def test_rejected_credentials_are_unauthorized(self) -> 'None':
        reply = self._sign_in(None)
        self.assertEqual(reply, {'correlation_id': _correlation_id, 'status': 'unauthorized', 'data': ''})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
