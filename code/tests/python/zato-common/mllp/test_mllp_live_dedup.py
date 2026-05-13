# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket

# Zato
from zato.common.hl7.mllp.codec import frame_encode

from conftest import sample_adt_a01, start_sequence, end_sequence, start_server, stop_server

# ################################################################################################################################
# ################################################################################################################################

_socket_timeout = 5.0
_recv_buffer    = 4096

# ################################################################################################################################
# ################################################################################################################################

def _send_and_recv_on_socket(raw_socket:'socket.socket', message_bytes:'bytes') -> 'bytes':
    """ Sends a framed message on an existing socket and reads back the response.
    """
    framed = frame_encode(message_bytes, start_sequence, end_sequence)
    raw_socket.sendall(framed)
    out = raw_socket.recv(_recv_buffer)
    return out

# ################################################################################################################################

def _count_echo_lines(process:'object') -> 'int':
    """ Stops the server and counts all ECHO: lines from its stdout.
    Must be called exactly once per test, as it terminates the process.
    """
    stop_server(process) # type: ignore[arg-type]

    remaining_output = process.stdout.read() # type: ignore[union-attr]

    count = 0

    for line in remaining_output.splitlines():
        if line.startswith('ECHO:'):
            count += 1

    return count

# ################################################################################################################################
# ################################################################################################################################

class TestDedupDuplicateSkipped:
    """ Verifies that a duplicate message (same MSH-10) within the TTL window
    gets an AA ACK but does not trigger the service callback.
    """

    def test_duplicate_message_skipped(self) -> 'None':
        """ Send same message twice with same MSH-10, verify both get AA
        but the echo callback only fires once.
        """
        process, port = start_server(
            callback_mode='echo',
            dedup_ttl_value=60,
            dedup_ttl_unit='minutes',
        )

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', port))
        raw_socket.settimeout(_socket_timeout)

        try:
            message = sample_adt_a01('DEDUP_CTRL_001')

            # First send - should be delivered to the service
            response_1 = _send_and_recv_on_socket(raw_socket, message)
            response_1_text = response_1.decode('utf-8', errors='replace')
            assert 'AA' in response_1_text

            # Second send - should be acknowledged but not delivered
            response_2 = _send_and_recv_on_socket(raw_socket, message)
            response_2_text = response_2.decode('utf-8', errors='replace')
            assert 'AA' in response_2_text

        finally:
            try:
                raw_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            raw_socket.close()

        echo_count = _count_echo_lines(process)
        assert echo_count == 1

# ################################################################################################################################
# ################################################################################################################################

class TestDedupDifferentIDs:
    """ Verifies that messages with different MSH-10 values are both delivered.
    """

    def test_different_control_ids_both_delivered(self) -> 'None':
        """ Send two messages with different MSH-10, verify both trigger the callback.
        """
        process, port = start_server(
            callback_mode='echo',
            dedup_ttl_value=60,
            dedup_ttl_unit='minutes',
        )

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', port))
        raw_socket.settimeout(_socket_timeout)

        try:
            message_a = sample_adt_a01('DEDUP_A')
            message_b = sample_adt_a01('DEDUP_B')

            response_a = _send_and_recv_on_socket(raw_socket, message_a)
            assert 'AA' in response_a.decode('utf-8', errors='replace')

            response_b = _send_and_recv_on_socket(raw_socket, message_b)
            assert 'AA' in response_b.decode('utf-8', errors='replace')

        finally:
            try:
                raw_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            raw_socket.close()

        echo_count = _count_echo_lines(process)
        assert echo_count == 2

# ################################################################################################################################
# ################################################################################################################################

class TestDedupDisabled:
    """ Verifies that without dedup config, duplicate messages are both delivered.
    """

    def test_dedup_disabled(self) -> 'None':
        """ Start server without dedup flags, send same message twice,
        verify callback fires twice.
        """
        process, port = start_server(
            callback_mode='echo',
        )

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', port))
        raw_socket.settimeout(_socket_timeout)

        try:
            message = sample_adt_a01('NODEDUP_CTRL')

            response_1 = _send_and_recv_on_socket(raw_socket, message)
            assert 'AA' in response_1.decode('utf-8', errors='replace')

            response_2 = _send_and_recv_on_socket(raw_socket, message)
            assert 'AA' in response_2.decode('utf-8', errors='replace')

        finally:
            try:
                raw_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            raw_socket.close()

        echo_count = _count_echo_lines(process)
        assert echo_count == 2

# ################################################################################################################################
# ################################################################################################################################
