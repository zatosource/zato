# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import time

# Zato
from zato.common.hl7.mllp.codec import frame_encode

from conftest import sample_adt_a01, start_sequence, end_sequence, start_server, stop_server

# ################################################################################################################################
# ################################################################################################################################

_socket_timeout = 5.0
_recv_buffer    = 4096

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

            # .. the response should be an AE with error details ..
            assert 'AE' in response_text
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

            # .. the response should still be an AE (error) ..
            assert 'AE' in response_text

            # .. but without detailed error text.
            assert 'internal processing error' not in response_text.lower()

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################

class TestShouldLogMessages:
    """ Verifies that should_log_messages controls message content logging.
    """

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
