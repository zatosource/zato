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

from mllp_live_util import end_sequence, sample_adt_a01, start_sequence, start_server, stop_server

# ################################################################################################################################
# ################################################################################################################################

_socket_timeout = 5.0
_recv_buffer    = 4096

# The deadline the route under test gives an idle connection, far below the listener's own
_route_idle_timeout = 1.0

# How long the connection is left silent, past the route's deadline but well within the listener's
_silence_seconds = 2.5

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
# ################################################################################################################################

class TestRouteIdleTimeout:
    """ Verifies that once a message has matched a route, the wait for the next message down
    the same connection is the matched channel's own idle deadline rather than the listener's.
    """

    def test_idle_connection_closed_after_route_deadline(self) -> 'None':
        """ Two messages in quick succession both go through, then the connection goes quiet
        for longer than the route allows and the server closes it.
        """
        process, port = start_server(
            callback_mode='ok',
            idle_timeout=_route_idle_timeout,
        )

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', port))
        raw_socket.settimeout(_socket_timeout)

        try:
            # A first message matches the route, so from here on the connection is read
            # under that route's own idle deadline ..
            response_1 = _send_and_recv_on_socket(raw_socket, sample_adt_a01('IDLE_CTRL_001'))
            assert 'AA' in response_1.decode('utf-8', errors='replace')

            # .. a second message inside the deadline still goes through ..
            response_2 = _send_and_recv_on_socket(raw_socket, sample_adt_a01('IDLE_CTRL_002'))
            assert 'AA' in response_2.decode('utf-8', errors='replace')

            # .. then nothing is sent for longer than the route allows ..
            time.sleep(_silence_seconds)

            # .. and by now the server has closed the connection.
            remaining = raw_socket.recv(_recv_buffer)
            assert remaining == b''

        finally:
            try:
                raw_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            raw_socket.close()

            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################
