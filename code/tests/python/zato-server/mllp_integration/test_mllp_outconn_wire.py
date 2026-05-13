# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
import time

# Zato
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import BackendHandle

# ################################################################################################################################
# ################################################################################################################################

_start_sequence   = b'\x0b'
_end_sequence     = b'\x1c\x0d'
_socket_timeout   = 5.0
_recv_buffer_size = 4096
_max_message_size = 2_000_000

_connection_type_channel = 'channel-hl7-mllp'
_connection_type_outconn = 'outconn-hl7-mllp'
_generic_service_name    = 'zato.generic.connection'

_listener_bind_wait_seconds = 2

# ################################################################################################################################
# ################################################################################################################################

def _build_adt_a01(control_id:'str') -> 'bytes':
    """ Builds a standard ADT^A01 message as UTF-8 bytes.
    """
    message = (
        f'MSH|^~\\&|TestSend|TestFac|ZatoRecv|ZatoFac|20260507120000||ADT^A01|{control_id}|P|2.5\r'
        f'PID|||12345^^^MRN||Doe^John||19800101|M\r'
        f'PV1||I|ICU^Room1'
    )

    out = message.encode('utf-8')
    return out

# ################################################################################################################################
# ################################################################################################################################

def _send_and_receive(host:'str', port:'int', payload_bytes:'bytes') -> 'bytes':
    """ Opens a raw TCP socket, sends an MLLP-framed message, and reads the ACK response.
    """

    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_socket.settimeout(_socket_timeout)
    raw_socket.connect((host, port))

    try:

        framed_message = frame_encode(payload_bytes, _start_sequence, _end_sequence)
        raw_socket.sendall(framed_message)

        decoder = FrameDecoder(_start_sequence, _end_sequence, _max_message_size)

        while True:
            chunk = raw_socket.recv(_recv_buffer_size)

            if not chunk:
                raise RuntimeError('Connection closed before receiving a complete ACK')

            decoder.feed(chunk)
            message = decoder.next_message()

            if message is not None:
                out = message
                break

        return out

    finally:
        raw_socket.close()

# ################################################################################################################################
# ################################################################################################################################

def _parse_ack_segments(ack_bytes:'bytes') -> 'list[str]':
    """ Decodes ACK bytes to a string and splits into segments.
    """
    ack_text = ack_bytes.decode('utf-8')

    out = ack_text.split('\r')
    return out

# ################################################################################################################################
# ################################################################################################################################

def _find_segment(segments:'list[str]', prefix:'str') -> 'str':
    """ Returns the first segment starting with the given prefix.
    """

    out = ''

    for segment in segments:
        if segment.startswith(prefix):
            out = segment
            break

    return out

# ################################################################################################################################
# ################################################################################################################################

def _find_free_port() -> 'int':
    """ Binds to port 0 to get an OS-assigned free port, then releases it.
    """
    temporary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temporary_socket.bind(('127.0.0.1', 0))

    _, port = temporary_socket.getsockname()

    temporary_socket.close()

    return port

# ################################################################################################################################
# ################################################################################################################################

class TestMLLPOutconnWire:
    """ Wire-level tests for MLLP outbound connections running inside a live Zato server.
    """

    outconn_id:'int' = 0
    forward_channel_id:'int' = 0
    dead_outconn_id:'int' = 0
    dead_channel_id:'int' = 0

# ################################################################################################################################

    def test_01_create_outconn(self, zato_client:'object', backend_port:'int', mllp_backend:'BackendHandle') -> 'None':
        """ Creates an MLLP outconn pointing to the standalone backend.
        """
        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-mllp-wire-outconn',
            type_=_connection_type_outconn,
            is_active=True,
            is_internal=False,
            is_channel=False,
            is_outconn=True,
            address=f'127.0.0.1:{backend_port}',
            pool_size=1,
        )

        assert 'id' in response
        assert response['name'] == 'test-mllp-wire-outconn'

        self.__class__.outconn_id = response['id']

# ################################################################################################################################

    def test_02_create_forward_channel(self, zato_client:'object', forward_channel_port:'int') -> 'None':
        """ Creates an MLLP channel that forwards messages through the outconn.
        """
        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-mllp-wire-forward',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.forward',
            address=f'127.0.0.1:{forward_channel_port}',
            pool_size=1,
        )

        assert 'id' in response
        self.__class__.forward_channel_id = response['id']

        time.sleep(_listener_bind_wait_seconds)

# ################################################################################################################################

    def test_03_forward_via_outconn_gets_aa(self, forward_channel_port:'int') -> 'None':
        """ Sends a message to the forward channel and verifies AA ACK (backend accepted it).
        """
        message_bytes = _build_adt_a01('FWD-001')
        ack_bytes = _send_and_receive('127.0.0.1', forward_channel_port, message_bytes)
        segments = _parse_ack_segments(ack_bytes)

        msa_segment = _find_segment(segments, 'MSA|')
        assert 'MSA|AA|FWD-001' in msa_segment

# ################################################################################################################################

    def test_04_backend_received_forwarded_message(self, mllp_backend:'BackendHandle') -> 'None':
        """ Verifies the standalone backend received the forwarded message.
        """

        # Give the backend a moment to flush its output ..
        time.sleep(0.5)

        # The backend in echo mode writes ECHO:{message_text} to stdout ..
        found = False

        for line in mllp_backend.received_lines:
            if line.startswith('ECHO:'):
                if 'FWD-001' in line:
                    if 'ADT^A01' in line:
                        found = True
                        break

        assert found

# ################################################################################################################################

    def test_05_delete_outconn_and_channel(self, zato_client:'object') -> 'None':
        """ Deletes the forward channel and the outconn, then verifies via get-list.
        """

        # Delete the forward channel ..
        zato_client.delete( # type: ignore[union-attr]
            f'{_generic_service_name}.delete',
            id=self.__class__.forward_channel_id,
        )

        # .. delete the outconn ..
        zato_client.delete( # type: ignore[union-attr]
            f'{_generic_service_name}.delete',
            id=self.__class__.outconn_id,
        )

        time.sleep(1)

        # .. verify the channel is gone ..
        channel_data, _ = zato_client.get_list( # type: ignore[union-attr]
            f'{_generic_service_name}.get-list',
            cluster_id=1,
            type_=_connection_type_channel,
        )

        channel_names = []

        for item in channel_data:
            channel_names.append(item['name'])

        assert 'test-mllp-wire-forward' not in channel_names

        # .. verify the outconn is gone ..
        outconn_data, _ = zato_client.get_list( # type: ignore[union-attr]
            f'{_generic_service_name}.get-list',
            cluster_id=1,
            type_=_connection_type_outconn,
        )

        outconn_names = []

        for item in outconn_data:
            outconn_names.append(item['name'])

        assert 'test-mllp-wire-outconn' not in outconn_names

# ################################################################################################################################

    def test_06_outconn_to_dead_port_returns_ae(self, zato_client:'object') -> 'None':
        """ Creates an outconn pointing to a dead port and verifies AE ACK when the forward service tries to use it.
        """

        dead_port = _find_free_port()
        dead_channel_port = _find_free_port()

        # Create an outconn pointing to the dead port ..
        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-mllp-wire-outconn',
            type_=_connection_type_outconn,
            is_active=True,
            is_internal=False,
            is_channel=False,
            is_outconn=True,
            address=f'127.0.0.1:{dead_port}',
            pool_size=1,
        )

        assert 'id' in response
        self.__class__.dead_outconn_id = response['id']

        # .. create a forward channel that will use this dead outconn ..
        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-mllp-wire-forward-dead',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.forward',
            address=f'127.0.0.1:{dead_channel_port}',
            pool_size=1,
        )

        assert 'id' in response
        self.__class__.dead_channel_id = response['id']

        time.sleep(_listener_bind_wait_seconds)

        # .. send a message and expect AE ACK ..
        message_bytes = _build_adt_a01('DEAD-001')
        ack_bytes = _send_and_receive('127.0.0.1', dead_channel_port, message_bytes)
        segments = _parse_ack_segments(ack_bytes)

        msa_segment = _find_segment(segments, 'MSA|')
        assert 'MSA|AE|DEAD-001' in msa_segment

        err_segment = _find_segment(segments, 'ERR|')
        assert err_segment
        assert 'Internal processing error' in err_segment

        # .. clean up ..
        zato_client.delete( # type: ignore[union-attr]
            f'{_generic_service_name}.delete',
            id=self.__class__.dead_channel_id,
        )

        zato_client.delete( # type: ignore[union-attr]
            f'{_generic_service_name}.delete',
            id=self.__class__.dead_outconn_id,
        )

# ################################################################################################################################
# ################################################################################################################################
