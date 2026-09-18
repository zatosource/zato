# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from threading import Thread

# pytest
import pytest

# Zato
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_Host = '127.0.0.1'

_Start_Sequence = b'\x0b'
_End_Sequence   = b'\x1c\x0d'

# A ping that hangs is a broken test rather than a slow one
_Connect_Timeout = 2

# How long the listener waits for the client to say something before concluding that it never will
_Listener_Read_Timeout = 0.5

# A host name that no resolver answers for
_Unresolvable_Host = 'no-such-host.invalid'

# ################################################################################################################################
# ################################################################################################################################

class _Listener:
    """ A plain TCP listener that accepts one connection and records how many bytes arrived on it,
    which is how the test tells a ping that only connected from one that sent something.
    """

    def __init__(self) -> 'None':
        self.port = get_free_port()
        self.received = b''
        self.was_accepted = False

        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((_Host, self.port))
        self._server.listen(1)
        self._server.settimeout(_Connect_Timeout)

        self._thread = Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self) -> 'None':

        # One connection is all a ping makes ..
        conn, _ = self._server.accept()
        self.was_accepted = True

        # .. and whatever the client sends before closing is what it sent, an empty read meaning nothing at all
        conn.settimeout(_Listener_Read_Timeout)
        try:
            self.received = conn.recv(1024)
        except socket.timeout:
            pass
        finally:
            conn.close()

    def close(self) -> 'None':
        self._thread.join(_Connect_Timeout)
        self._server.close()

# ################################################################################################################################
# ################################################################################################################################

def _build_client(host:'str', port:'int') -> 'HL7MLLPClient':
    out = HL7MLLPClient(host, port, _Start_Sequence, _End_Sequence, connect_timeout=_Connect_Timeout)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestClientPing:
    """ The ping opens a connection and closes it again, which is all a live check needs and
    nothing a receiving system would act on.
    """

    def test_a_ping_connects_and_sends_nothing(self) -> 'None':

        listener = _Listener()
        try:
            client = _build_client(_Host, listener.port)
            client.ping()
        finally:
            listener.close()

        assert listener.was_accepted, 'The ping should have connected to the listener'
        assert listener.received == b'', f'The ping should have sent nothing, the listener got: {listener.received!r}'

# ################################################################################################################################

    def test_a_ping_fails_when_nothing_listens(self) -> 'None':

        client = _build_client(_Host, get_free_port())

        with pytest.raises(ConnectionRefusedError):
            client.ping()

# ################################################################################################################################

    def test_a_ping_fails_on_a_host_that_does_not_resolve(self) -> 'None':

        client = _build_client(_Unresolvable_Host, get_free_port())

        with pytest.raises(socket.gaierror):
            client.ping()

# ################################################################################################################################
# ################################################################################################################################
