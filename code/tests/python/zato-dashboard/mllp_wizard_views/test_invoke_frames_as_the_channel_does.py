# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from json import loads
from threading import Thread

# Zato
from zato.admin.web.views.channel.hl7.mllp.invoke import invoke_channel
from zato.common.ext.bunch import Bunch
from zato.common.util.api import hex_sequence_to_bytes
from zato.common.util.tcp import get_free_port

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, strdict

# ################################################################################################################################
# ################################################################################################################################

# A channel framed unlike the MLLP defaults - the overlay's message is framed and its reply read the way this channel is
_channel_start_seq = '0b'
_channel_end_seq = '1c 0a'

_channel_id = '1'
_control_id = 'CTRL001'

_message = 'MSH|^~\\&|APP|FAC|RCV|RFAC|20260101000000||ADT^A01|{}|P|2.5\rPID|1||42'.format(_control_id)
_acknowledgment = 'MSH|^~\\&|RCV|RFAC|APP|FAC|20260101000000||ACK^A01|ACK001|P|2.5\rMSA|AA|{}'.format(_control_id)

_recv_buffer_size = 65536
_socket_timeout = 5.0

# ################################################################################################################################
# ################################################################################################################################

class _Listener:
    """ Answers one frame the way the shared listener answers for a channel with its own framing -
    the frame is complete at the channel's end sequence and the acknowledgment is framed the same way.
    """

    def __init__(self) -> 'None':
        self.port = get_free_port()
        self.start_bytes = hex_sequence_to_bytes(_channel_start_seq)
        self.end_bytes = hex_sequence_to_bytes(_channel_end_seq)
        self.received = b''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('127.0.0.1', self.port))
        self.sock.listen(1)
        self.sock.settimeout(_socket_timeout)
        self.thread = Thread(target=self._serve, daemon=True)
        self.thread.start()

    def _serve(self) -> 'None':
        connection, _ = self.sock.accept()
        connection.settimeout(_socket_timeout)
        try:
            while self.end_bytes not in self.received:
                chunk = connection.recv(_recv_buffer_size)
                if not chunk:
                    return
                self.received += chunk
            connection.sendall(self.start_bytes + _acknowledgment.encode('utf-8') + self.end_bytes)
        finally:
            connection.close()

    def close(self) -> 'None':
        self.thread.join(_socket_timeout)
        self.sock.close()

# ################################################################################################################################
# ################################################################################################################################

class _Response:
    def __init__(self, data:'any_') -> 'None':
        self.ok = True
        self.data = data

class _FakeClient:
    """ Answers the two calls the view makes - where the listener is and how the channel is framed.
    """
    address = 'http://127.0.0.1:17010'

    def __init__(self, port:'int') -> 'None':
        self.port = port

    def invoke(self, service:'str', request:'anydict') -> '_Response':
        if service == 'zato.server.invoker':
            return _Response(self.port)
        if service == 'zato.generic.connection.get-by-id':
            return _Response({'id': request['id'], 'start_seq': _channel_start_seq, 'end_seq': _channel_end_seq})
        raise Exception('Unexpected service `{}`'.format(service))

# ################################################################################################################################

def _build_request(port:'int') -> 'Bunch':
    out = Bunch()
    out.method = 'POST'
    out.POST = {'data-request': _message}
    out.zato = Bunch()
    out.zato.client = _FakeClient(port)
    return out

def _body(response:'any_') -> 'strdict':
    out = loads(response.content.decode('utf-8'))
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestInvokeFramesAsTheChannelDoes:
    """ The overlay stands in for a sender of the channel it was opened from, so its message is framed
    with that channel's sequences and the reply is read and shown with the same sequences taken off.
    """

    def test_the_message_is_framed_with_the_channels_sequences(self) -> 'None':
        listener = _Listener()
        try:
            _ = invoke_channel(_build_request(listener.port), id=_channel_id)
        finally:
            listener.close()

        assert listener.received == listener.start_bytes + _message.encode('utf-8') + listener.end_bytes

# ################################################################################################################################

    def test_the_acknowledgment_is_shown_without_the_channels_framing(self) -> 'None':
        listener = _Listener()
        try:
            response = invoke_channel(_build_request(listener.port), id=_channel_id)
        finally:
            listener.close()

        body = _body(response)

        assert response.status_code == 200
        assert body['data'] == _acknowledgment

# ################################################################################################################################
# ################################################################################################################################
