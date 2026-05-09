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

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

_socket_timeout = 5.0
_recv_buffer    = 4096

# ################################################################################################################################
# ################################################################################################################################

class TestEncodingISO88591:
    """ Verifies that a server started with ISO-8859-1 encoding accepts messages encoded in that charset.
    """

    def test_encoding_iso_8859_1(self, make_client:'callable_') -> 'None':
        """ Start server with ISO-8859-1 encoding, send a message with accented characters, verify AA ACK.
        """
        process, port = start_server(
            default_character_encoding='iso-8859-1',
        )

        try:
            client = make_client(port)

            # Build a message with an ISO-8859-1 character (accented e) ..
            message_text = (
                'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|ISO_CTRL|P|2.5\r'
                'PID|||12345^^^MRN||M\xfcller^Hans||19800101|M'
            )
            message_bytes = message_text.encode('iso-8859-1')

            result = client.send(message_bytes, control_id='ISO_CTRL')

            assert result.is_accepted is True
            assert result.ack_code == 'AA'

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################

class TestRecvTimeout:
    """ Verifies that the receive timeout is per-recv, not per-connection.
    """

    def test_recv_timeout_connection_survives(self) -> 'None':
        """ Start server with a short recv timeout, open a connection, idle, then send - connection stays alive.
        """
        process, port = start_server(
            recv_timeout=1.0,
        )

        try:
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            raw_socket.connect(('127.0.0.1', port))
            raw_socket.settimeout(_socket_timeout)

            try:

                # Idle for longer than the recv timeout ..
                import time
                time.sleep(1.5)

                # .. send a valid framed message - the connection should still be alive ..
                message = sample_adt_a01('TIMEOUT_CTRL')
                framed = frame_encode(message, start_sequence, end_sequence)
                raw_socket.sendall(framed)

                # .. read back the ACK.
                response = raw_socket.recv(_recv_buffer)

                assert len(response) > 0

            finally:
                try:
                    raw_socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                raw_socket.close()

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################

class TestMaxMsgSize:
    """ Verifies that messages exceeding max_msg_size are rejected.
    """

    def test_max_msg_size_exceeded(self) -> 'None':
        """ Start server with max_msg_size=100, send a 200-byte message, verify the server rejects it.
        """
        process, port = start_server(
            max_msg_size=100,
        )

        try:
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            raw_socket.connect(('127.0.0.1', port))
            raw_socket.settimeout(_socket_timeout)

            try:

                # Build a message that exceeds the 100-byte limit ..
                oversized_msh = 'MSH|^~\\&|' + 'X' * 200 + '||ADT^A01|BIG_CTRL|P|2.5'
                framed = frame_encode(oversized_msh.encode('utf-8'), start_sequence, end_sequence)
                raw_socket.sendall(framed)

                # .. the server should either close the connection or send no ACK ..
                raw_socket.settimeout(2.0)

                try:
                    response = raw_socket.recv(_recv_buffer)
                except socket.timeout:
                    response = b''

                # .. a well-behaved rejection means either empty response (connection closed)
                # .. or no valid AA ACK.
                if response:
                    response_text = response.decode('utf-8', errors='replace')
                    assert 'AA' not in response_text

            finally:
                try:
                    raw_socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                raw_socket.close()

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_max_msg_size_within_limit(self, make_client:'callable_') -> 'None':
        """ Start server with max_msg_size=100000, send a small message, verify AA.
        """
        process, port = start_server(
            max_msg_size=100000,
        )

        try:
            client = make_client(port)
            message = sample_adt_a01('SMALL_CTRL')
            result = client.send(message, control_id='SMALL_CTRL')

            assert result.is_accepted is True
            assert result.ack_code == 'AA'

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################
