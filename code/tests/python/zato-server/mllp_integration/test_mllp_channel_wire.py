# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import socket
import time

# Zato
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode

# ################################################################################################################################
# ################################################################################################################################

_start_sequence   = b'\x0b'
_end_sequence     = b'\x1c\x0d'
_socket_timeout   = 5.0
_recv_buffer_size = 4096
_max_message_size = 2_000_000

_connection_type_channel = 'channel-hl7-mllp'
_generic_service_name    = 'zato.generic.connection'

_listener_bind_wait_seconds = 2

# ################################################################################################################################
# ################################################################################################################################

def _build_adt_a01(control_id:'str', sender_application:'str'='TestSend', sender_facility:'str'='TestFac') -> 'bytes':
    """ Builds a standard ADT^A01 message as UTF-8 bytes.
    """
    message = (
        f'MSH|^~\\&|{sender_application}|{sender_facility}|ZatoRecv|ZatoFac|20260507120000||ADT^A01|{control_id}|P|2.5\r'
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

        # Frame and send ..
        framed_message = frame_encode(payload_bytes, _start_sequence, _end_sequence)
        raw_socket.sendall(framed_message)

        # .. read the ACK using FrameDecoder ..
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

class TestMLLPChannelWire:
    """ Wire-level tests for MLLP inbound channels running inside a live Zato server.
    """

    created_channel_id:'int' = 0
    error_channel_id:'int' = 0

# ################################################################################################################################

    def test_01_create_echo_channel(self, zato_client:'object', channel_port:'int') -> 'None':
        """ Creates an MLLP channel bound to the echo service.
        """
        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-mllp-wire-echo',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.echo',
            address=f'127.0.0.1:{channel_port}',
            pool_size=1,
        )

        assert 'id' in response
        assert response['name'] == 'test-mllp-wire-echo'

        self.__class__.created_channel_id = response['id']

        # Wait for the MLLP listener to bind
        time.sleep(_listener_bind_wait_seconds)

# ################################################################################################################################

    def test_02_send_adt_a01_gets_aa_ack(self, channel_port:'int') -> 'None':
        """ Sends a standard ADT^A01 and verifies the ACK contains AA with correct MSA-2.
        """
        message_bytes = _build_adt_a01('WIRE001')
        ack_bytes = _send_and_receive('127.0.0.1', channel_port, message_bytes)
        segments = _parse_ack_segments(ack_bytes)

        # Verify the MSH segment ..
        msh_segment = segments[0]
        assert msh_segment.startswith('MSH|^~\\&|')
        assert '||ACK|' in msh_segment

        # .. verify sender/receiver are swapped ..
        msh_fields = msh_segment.split('|')
        assert msh_fields[2] == 'ZatoRecv'
        assert msh_fields[4] == 'TestSend'

        # .. verify the MSA segment ..
        msa_segment = _find_segment(segments, 'MSA|')
        assert msa_segment
        assert msa_segment.startswith('MSA|AA|WIRE001')

# ################################################################################################################################

    def test_03_service_received_full_message(self, zato_client:'object') -> 'None':
        """ Verifies the echo service actually received the full HL7 message text.
        """
        response = zato_client.invoke('test.hl7.mllp.inspect') # type: ignore[union-attr]

        # The inspect service returns JSON with a 'messages' list ..
        if isinstance(response, str):
            data = json.loads(response)
        else:
            data = response

        messages = data['messages']
        assert len(messages) >= 1

        last_message = messages[-1]

        # Verify the full message content was preserved ..
        assert 'MSH|^~\\&|TestSend|TestFac' in last_message
        assert 'PID|||12345^^^MRN||Doe^John' in last_message
        assert 'PV1||I|ICU^Room1' in last_message

        # Verify segments are separated by \r ..
        assert '\r' in last_message

# ################################################################################################################################

    def test_04_msa2_correlation_matches_msh10(self, channel_port:'int') -> 'None':
        """ Verifies MSA-2 in the ACK exactly matches the MSH-10 of the sent message.
        """
        message_bytes = _build_adt_a01('CORR-7890')
        ack_bytes = _send_and_receive('127.0.0.1', channel_port, message_bytes)
        segments = _parse_ack_segments(ack_bytes)

        # Verify the MSA segment contains the exact control ID ..
        msa_segment = _find_segment(segments, 'MSA|')
        msa_fields = msa_segment.split('|')
        assert msa_fields[1] == 'AA'
        assert msa_fields[2] == 'CORR-7890'

        # Verify the ACK's own MSH-10 contains the expected prefix ..
        msh_fields = segments[0].split('|')
        ack_control_id = msh_fields[9]
        assert ack_control_id.startswith('ACK-CORR-7890-')

# ################################################################################################################################

    def test_05_persistent_connection_two_messages(self, channel_port:'int') -> 'None':
        """ Sends two messages on the same TCP connection and verifies both get correct ACKs.
        """
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.settimeout(_socket_timeout)
        raw_socket.connect(('127.0.0.1', channel_port))

        try:
            decoder = FrameDecoder(_start_sequence, _end_sequence, _max_message_size)

            # Send first message ..
            message_one = _build_adt_a01('PERSIST-001')
            raw_socket.sendall(frame_encode(message_one, _start_sequence, _end_sequence))

            # .. read first ACK ..
            while True:
                chunk = raw_socket.recv(_recv_buffer_size)
                decoder.feed(chunk)
                ack_one_bytes = decoder.next_message()

                if ack_one_bytes is not None:
                    break

            ack_one_segments = _parse_ack_segments(ack_one_bytes)
            msa_one = _find_segment(ack_one_segments, 'MSA|')
            assert 'MSA|AA|PERSIST-001' in msa_one

            # .. send second message on the same connection ..
            message_two = _build_adt_a01('PERSIST-002')
            raw_socket.sendall(frame_encode(message_two, _start_sequence, _end_sequence))

            # .. read second ACK ..
            while True:
                chunk = raw_socket.recv(_recv_buffer_size)
                decoder.feed(chunk)
                ack_two_bytes = decoder.next_message()

                if ack_two_bytes is not None:
                    break

            ack_two_segments = _parse_ack_segments(ack_two_bytes)
            msa_two = _find_segment(ack_two_segments, 'MSA|')
            assert 'MSA|AA|PERSIST-002' in msa_two

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_06_lf_line_endings_normalized(self, zato_client:'object', channel_port:'int') -> 'None':
        """ Sends a message with LF line endings and verifies the ACK and that the service received CR separators.
        """

        # Build message with \n separators instead of \r ..
        message_text = (
            'MSH|^~\\&|LFApp|LFFac|ZatoRecv|ZatoFac|20260507120000||ADT^A01|LFTEST001|P|2.5\n'
            'PID|||99999^^^MRN||Smith^Jane||19900101|F\n'
            'PV1||I|Ward^Bed2'
        )
        message_bytes = message_text.encode('utf-8')

        # Send and verify ACK ..
        ack_bytes = _send_and_receive('127.0.0.1', channel_port, message_bytes)
        segments = _parse_ack_segments(ack_bytes)
        msa_segment = _find_segment(segments, 'MSA|')
        assert 'MSA|AA|LFTEST001' in msa_segment

        # Verify the service received the message with \r separators ..
        response = zato_client.invoke('test.hl7.mllp.inspect') # type: ignore[union-attr]

        if isinstance(response, str):
            data = json.loads(response)
        else:
            data = response

        messages = data['messages']

        # Find the message with our control ID ..
        found = False

        for message in messages:
            if 'LFTEST001' in message:
                assert '\r' in message
                found = True
                break

        assert found

# ################################################################################################################################

    def test_07_concatenated_frames_produce_two_acks(self, channel_port:'int') -> 'None':
        """ Sends two concatenated MLLP frames in one sendall and verifies two ACKs are received.
        """
        message_a = _build_adt_a01('CONCAT-A')
        message_b = _build_adt_a01('CONCAT-B')

        frame_a = frame_encode(message_a, _start_sequence, _end_sequence)
        frame_b = frame_encode(message_b, _start_sequence, _end_sequence)

        concatenated = frame_a + frame_b

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.settimeout(_socket_timeout)
        raw_socket.connect(('127.0.0.1', channel_port))

        try:
            raw_socket.sendall(concatenated)

            decoder = FrameDecoder(_start_sequence, _end_sequence, _max_message_size)
            acks_received = []

            # Read until we have two ACKs ..
            deadline = time.monotonic() + _socket_timeout

            while len(acks_received) < 2:

                if time.monotonic() > deadline:
                    break

                chunk = raw_socket.recv(_recv_buffer_size)

                if not chunk:
                    break

                decoder.feed(chunk)

                while True:
                    ack_bytes = decoder.next_message()

                    if ack_bytes is None:
                        break

                    acks_received.append(ack_bytes)

            assert len(acks_received) == 2

            segments_a = _parse_ack_segments(acks_received[0])
            msa_a = _find_segment(segments_a, 'MSA|')
            assert 'MSA|AA|CONCAT-A' in msa_a

            segments_b = _parse_ack_segments(acks_received[1])
            msa_b = _find_segment(segments_b, 'MSA|')
            assert 'MSA|AA|CONCAT-B' in msa_b

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_08_service_error_returns_ae_ack(self, zato_client:'object', error_channel_port:'int') -> 'None':
        """ Creates a channel pointing to the error service and verifies AE ACK is returned.
        """

        # Create a channel that uses the error service ..
        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-mllp-wire-error',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.error',
            address=f'127.0.0.1:{error_channel_port}',
            pool_size=1,
        )

        assert 'id' in response
        self.__class__.error_channel_id = response['id']

        time.sleep(_listener_bind_wait_seconds)

        # Send a message and verify AE ACK ..
        message_bytes = _build_adt_a01('ERR-001')
        ack_bytes = _send_and_receive('127.0.0.1', error_channel_port, message_bytes)
        segments = _parse_ack_segments(ack_bytes)

        # Verify MSA shows AE ..
        msa_segment = _find_segment(segments, 'MSA|')
        assert 'MSA|AE|ERR-001' in msa_segment

        # Verify ERR segment is present ..
        err_segment = _find_segment(segments, 'ERR|')
        assert err_segment
        assert '207^Application internal error^HL70357' in err_segment
        assert 'Internal processing error' in err_segment

        # Clean up the error channel ..
        zato_client.delete(f'{_generic_service_name}.delete', id=self.__class__.error_channel_id) # type: ignore[union-attr]

# ################################################################################################################################

    def test_09_large_message_accepted(self, channel_port:'int') -> 'None':
        """ Sends a ~500 KB HL7 message and verifies it gets an AA ACK.
        """

        # Build a large message with many OBX segments ..
        segments_list = [
            'MSH|^~\\&|TestSend|TestFac|ZatoRecv|ZatoFac|20260507120000||ADT^A01|LARGE-001|P|2.5',
            'PID|||12345^^^MRN||Doe^John||19800101|M',
        ]

        padding_text = 'A' * 1000

        for index in range(500):
            obx_segment = f'OBX|{index + 1}|TX|NOTE||{padding_text}'
            segments_list.append(obx_segment)

        message_text = '\r'.join(segments_list)
        message_bytes = message_text.encode('utf-8')

        ack_bytes = _send_and_receive('127.0.0.1', channel_port, message_bytes)
        segments = _parse_ack_segments(ack_bytes)

        msa_segment = _find_segment(segments, 'MSA|')
        assert 'MSA|AA|LARGE-001' in msa_segment

# ################################################################################################################################

    def test_10_delete_channel_closes_port(self, zato_client:'object', channel_port:'int') -> 'None':
        """ Deletes the echo channel and verifies the port is no longer listening.
        """
        zato_client.delete( # type: ignore[union-attr]
            f'{_generic_service_name}.delete',
            id=self.__class__.created_channel_id,
        )

        time.sleep(1)

        # Attempt to connect to the port - it should be refused ..
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(2.0)

        connection_refused = False

        try:
            test_socket.connect(('127.0.0.1', channel_port))
        except (ConnectionRefusedError, OSError):
            connection_refused = True
        finally:
            test_socket.close()

        assert connection_refused

# ################################################################################################################################
# ################################################################################################################################
