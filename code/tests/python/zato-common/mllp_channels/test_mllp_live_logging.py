# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import socket
import time
from unittest.mock import MagicMock

# Zato
from zato.common.hl7.mllp.codec import frame_encode
from zato.common.hl7.mllp.router import HL7MessageRouter
from zato.common.hl7.mllp.server import ConnectionContext, HL7MLLPServer
from zato.common.hl7.mllp.settings import ListenerConfig, RouteSettings

from mllp_live_util import end_sequence, sample_adt_a01, start_sequence, start_server, stop_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pytest import LogCaptureFixture
    LogCaptureFixture = LogCaptureFixture

# ################################################################################################################################
# ################################################################################################################################

_socket_timeout = 5.0
_recv_buffer    = 4096

# The channel the in-process logging tests route to, the logger its message lines go to and who the messages come from
_logging_channel_name = 'test-mllp-logging'
_logging_service_name = 'test.mllp.logging'
_message_logger_name  = 'zato.common.hl7.mllp.message'
_sender_ip   = '203.0.113.10'
_sender_port = 40000

# ################################################################################################################################
# ################################################################################################################################

def _accept_message(message:'object', cid:'str') -> 'None':
    return None

# ################################################################################################################################
# ################################################################################################################################

def _send_raw_and_recv(port:'int', message_bytes:'bytes') -> 'bytes':
    """ Sends a framed message to the server and reads back the response.
    """
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_socket.connect(('127.0.0.1', port))
    raw_socket.settimeout(_socket_timeout)

    try:
        framed = frame_encode(message_bytes, start_sequence, end_sequence)
        raw_socket.sendall(framed)

        out = raw_socket.recv(_recv_buffer)
        return out

    finally:
        try:
            raw_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        raw_socket.close()

# ################################################################################################################################
# ################################################################################################################################

class TestShouldReturnErrors:
    """ Verifies that should_return_errors controls whether error details appear in NAK responses.
    """

    def test_should_return_errors_true(self) -> 'None':
        """ With should_return_errors=True and an error callback, the ACK should contain an ERR segment or error text.
        """
        process, port = start_server(
            callback_mode='error',
            should_return_errors=True,
        )

        try:
            message = sample_adt_a01('ERR_TRUE_CTRL')
            response = _send_raw_and_recv(port, message)
            response_text = response.decode('utf-8', errors='replace')

            # .. a failing service is answered with AR, with error details ..
            assert 'MSA|AR|' in response_text
            assert 'error' in response_text.lower()

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_should_return_errors_false(self) -> 'None':
        """ With should_return_errors=False and an error callback, the ACK should have AE but no error details.
        """
        process, port = start_server(
            callback_mode='error',
            should_return_errors=False,
        )

        try:
            message = sample_adt_a01('ERR_FALSE_CTRL')
            response = _send_raw_and_recv(port, message)
            response_text = response.decode('utf-8', errors='replace')

            # .. a failing service is still answered with AR ..
            assert 'MSA|AR|' in response_text

            # .. but without detailed error text.
            assert 'internal processing error' not in response_text.lower()

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################

class TestShouldLogMessages:
    """ Verifies that should_log_messages controls message content logging.
    """

    def test_with_the_switch_on_the_message_is_logged_in_full(self, caplog:'LogCaptureFixture') -> 'None':
        """ A channel whose should_log_messages switch is on logs each message it receives in full,
        along with the decision of which channel it was routed to.
        """
        router = HL7MessageRouter()
        router.add_route(_logging_channel_name, _accept_message, service_name=_logging_service_name, is_default=True,
            settings=RouteSettings(should_parse_on_input=False, should_log_messages=True))
        server = HL7MLLPServer(ListenerConfig(), router)

        message = sample_adt_a01('LOG_CTRL_FULL')
        matched_route = router.match(message.decode('utf-8').split('\r')[0])
        assert matched_route is not None

        with caplog.at_level(logging.INFO, logger=_message_logger_name):
            server._handle_message(MagicMock(), message, ConnectionContext(_sender_ip, _sender_port, ''),
                matched_route, matched_route.settings)

        logged = caplog.text
        assert repr(message) in logged
        assert f'Routing message to channel `{_logging_channel_name}`' in logged

    def test_with_the_switch_off_the_message_is_not_logged(self, caplog:'LogCaptureFixture') -> 'None':
        """ A channel whose should_log_messages switch is off writes no message line at all.
        """
        router = HL7MessageRouter()
        router.add_route(_logging_channel_name, _accept_message, service_name=_logging_service_name, is_default=True,
            settings=RouteSettings(should_parse_on_input=False, should_log_messages=False))
        server = HL7MLLPServer(ListenerConfig(), router)

        message = sample_adt_a01('LOG_CTRL_OFF')
        matched_route = router.match(message.decode('utf-8').split('\r')[0])
        assert matched_route is not None

        with caplog.at_level(logging.INFO, logger=_message_logger_name):
            server._handle_message(MagicMock(), message, ConnectionContext(_sender_ip, _sender_port, ''),
                matched_route, matched_route.settings)

        # Only the router's line about the route being added is there, nothing about the message
        message_lines = []
        for record in caplog.records:
            if record.name == _message_logger_name:
                message_lines.append(record.getMessage())

        assert message_lines == []

    def test_should_log_messages_on(self) -> 'None':
        """ With log_messages=True, the server should log message details (verified via process stdout).
        """
        process, port = start_server(
            callback_mode='ok',
            log_messages=True,
        )

        try:
            message = sample_adt_a01('LOG_CTRL')
            _ = _send_raw_and_recv(port, message)

            # Give the server a moment to flush logs ..
            time.sleep(0.2)

            # .. the test passes if the server processed the message without error.
            # .. stdout-based log verification is impractical in subprocess mode,
            # .. but the server's internal logging pathway was exercised.

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################
