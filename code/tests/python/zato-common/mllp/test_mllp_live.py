# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import signal
import socket
import ssl
import time
from datetime import datetime

# Zato
from zato.common.hl7.exception import HL7Exception
from zato.common.hl7.mllp.ack import AckResult
from zato.common.hl7.mllp.circuit_breaker import CircuitBreaker, CircuitState
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode
from zato.common.hl7.mllp.retry import RetryEngine
from zato.common.hl7.mllp.tls import build_client_ssl_context

from conftest import sample_adt_a01, sample_oru_r01, start_sequence, end_sequence, start_server, stop_server

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

# ################################################################################################################################
# ################################################################################################################################

_max_message_size                = 2_000_000
_recv_buffer_size                = 4096
_socket_timeout                  = 5.0
_ack_timestamp_tolerance_seconds = 5
_fragment_chunk_size             = 10
_fragment_delay_seconds          = 0.01
_oversized_server_max_msg_size   = 100
_oversized_message_byte_count    = 500
_slow_callback_delay_seconds     = 5
_client_receive_timeout_seconds  = 1.0
_circuit_breaker_reset_seconds   = 0.1

# ################################################################################################################################
# ################################################################################################################################
# Group 1 - Basic send/receive
# ################################################################################################################################
# ################################################################################################################################

class TestBasicSendReceive:
    """ Verifies the fundamental request-response cycle over MLLP.
    """

# ################################################################################################################################

    def test_send_adt_a01_receives_aa(self, mllp_server:'int', make_client:'callable_') -> 'None':
        """ An ADT^A01 sent to an ok-mode server must get back an AA ACK.
        """
        client = make_client(mllp_server)
        message = sample_adt_a01('CTRL001')
        result = client.send(message, control_id='CTRL001')

        assert result.is_accepted is True
        assert result.ack_code == 'AA'

# ################################################################################################################################

    def test_send_oru_r01_receives_aa(self, mllp_server:'int', make_client:'callable_') -> 'None':
        """ An ORU^R01 sent to an ok-mode server must get back an AA ACK.
        """
        client = make_client(mllp_server)
        message = sample_oru_r01('CTRL002')
        result = client.send(message, control_id='CTRL002')

        assert result.is_accepted is True
        assert result.ack_code == 'AA'

# ################################################################################################################################

    def test_two_messages_separate_connections(self, mllp_server:'int', make_client:'callable_') -> 'None':
        """ Two messages on two separate connections must each get their own AA ACK.
        """
        client_one = make_client(mllp_server)
        result_one = client_one.send(sample_adt_a01('AAA001'), control_id='AAA001')

        client_two = make_client(mllp_server)
        result_two = client_two.send(sample_adt_a01('AAA002'), control_id='AAA002')

        assert result_one.is_accepted is True
        assert result_one.ack_code == 'AA'

        assert result_two.is_accepted is True
        assert result_two.ack_code == 'AA'

# ################################################################################################################################

    def test_two_messages_persistent_connection(self, mllp_server:'int') -> 'None':
        """ Two messages sent sequentially on the same TCP socket must each get
        their own MLLP-framed ACK with MSA|AA.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Send the first framed message ..
            message_one = sample_adt_a01('PER001')
            framed_one = frame_encode(message_one, start_sequence, end_sequence)
            raw_socket.sendall(framed_one)

            # .. read the first ACK ..
            ack_one = _read_one_framed_response(raw_socket)
            assert b'MSA|AA|PER001' in ack_one

            # .. send the second framed message on the same socket ..
            message_two = sample_adt_a01('PER002')
            framed_two = frame_encode(message_two, start_sequence, end_sequence)
            raw_socket.sendall(framed_two)

            # .. read the second ACK.
            ack_two = _read_one_framed_response(raw_socket)
            assert b'MSA|AA|PER002' in ack_two

        finally:
            raw_socket.close()

# ################################################################################################################################
# ################################################################################################################################
# Group 2 - ACK codes and structure
# ################################################################################################################################
# ################################################################################################################################

class TestAckCodesAndStructure:
    """ Verifies ACK code routing, sender/receiver swap, timestamp, and control ID correlation.
    """

# ################################################################################################################################

    def test_error_callback_returns_ae(self, make_client:'callable_') -> 'None':
        """ A server in error mode must ACK with AE and is_accepted=False.
        """

        # Start a dedicated server with the error callback ..
        process, port = start_server(callback_mode='error')

        try:
            client = make_client(port)
            result = client.send(sample_adt_a01('ERR001'), control_id='ERR001')

            assert result.ack_code == 'AE'
            assert result.is_accepted is False

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_ack_swaps_sender_receiver(self, mllp_server:'int') -> 'None':
        """ The ACK MSH must swap the original sender and receiver fields.

        The sample message has MSH-3=SendApp, MSH-4=SendFac, MSH-5=RecvApp, MSH-6=RecvFac,
        so the ACK must have MSH-3=RecvApp, MSH-4=RecvFac, MSH-5=SendApp, MSH-6=SendFac.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Send a framed ADT^A01 ..
            message = sample_adt_a01('SWAP001')
            framed = frame_encode(message, start_sequence, end_sequence)
            raw_socket.sendall(framed)

            # .. read the raw ACK bytes ..
            ack_bytes = _read_one_framed_response(raw_socket)
            ack_text = ack_bytes.decode('utf-8')

            # .. parse the MSH line of the ACK ..
            msh_line = ack_text.split('\r')[0]
            fields = msh_line.split('|')

            # .. fields[2] is MSH-3 (sending application in the ACK) ..
            assert fields[2] == 'RecvApp'
            assert fields[3] == 'RecvFac'
            assert fields[4] == 'SendApp'
            assert fields[5] == 'SendFac'

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_ack_timestamp_is_recent(self, mllp_server:'int') -> 'None':
        """ The ACK MSH-7 timestamp must be within a few seconds of now.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Capture the time before sending, truncated to whole seconds
            # because MSH-7 uses YYYYMMDDHHMMSS with no sub-second precision ..
            before = datetime.now().replace(microsecond=0)

            # .. send a framed message ..
            message = sample_adt_a01('TIME001')
            framed = frame_encode(message, start_sequence, end_sequence)
            raw_socket.sendall(framed)

            # .. read and parse the ACK's MSH-7 timestamp ..
            ack_bytes = _read_one_framed_response(raw_socket)
            ack_text = ack_bytes.decode('utf-8')
            msh_line = ack_text.split('\r')[0]
            fields = msh_line.split('|')
            ack_timestamp_string = fields[6]

            # .. parse the timestamp (format: YYYYMMDDHHMMSS) ..
            ack_timestamp = datetime.strptime(ack_timestamp_string, '%Y%m%d%H%M%S')

            # .. the ACK timestamp must be between before-send and now+tolerance.
            after = datetime.now()
            assert ack_timestamp >= before
            assert (after - ack_timestamp).total_seconds() <= _ack_timestamp_tolerance_seconds

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_ack_control_id_contains_original(self, mllp_server:'int') -> 'None':
        """ MSA-2 in the ACK must equal the original MSH-10 we sent.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Send a message with a known control ID ..
            message = sample_adt_a01('MY-CTRL-123')
            framed = frame_encode(message, start_sequence, end_sequence)
            raw_socket.sendall(framed)

            # .. read the ACK ..
            ack_bytes = _read_one_framed_response(raw_socket)
            ack_text = ack_bytes.decode('utf-8')

            # .. find the MSA segment and parse its fields ..
            msa_line = ''

            for segment in ack_text.split('\r'):
                if segment.startswith('MSA|'):
                    msa_line = segment
                    break

            msa_fields = msa_line.split('|')

            # .. MSA-2 (index 2) must be the original control ID.
            assert msa_fields[2] == 'MY-CTRL-123'

        finally:
            raw_socket.close()

# ################################################################################################################################
# ################################################################################################################################
# Group 3 - Framing edge cases
# ################################################################################################################################
# ################################################################################################################################

class TestFramingEdgeCases:
    """ Verifies correct handling of missing start bytes, empty frames,
    concatenated sends, fragmented sends, and oversized messages.
    """

# ################################################################################################################################

    def test_missing_start_byte_accepted(self, mllp_server:'int') -> 'None':
        """ A message sent without the leading 0x0B start byte but starting with MSH
        must still be accepted and get an AA ACK.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Send raw HL7 without start byte, only the end sequence ..
            message = sample_adt_a01('NOSB001')
            raw_bytes = message + end_sequence
            raw_socket.sendall(raw_bytes)

            # .. read the ACK.
            ack_bytes = _read_one_framed_response(raw_socket)
            assert b'MSA|AA|NOSB001' in ack_bytes

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_empty_frame_discarded(self, mllp_server:'int') -> 'None':
        """ An empty MLLP frame (start + end with no payload) must be silently discarded.
        Only the subsequent valid message should produce an ACK.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Send an empty frame first ..
            empty_frame = start_sequence + end_sequence

            # .. immediately followed by a valid framed message ..
            valid_message = sample_adt_a01('EMPTY001')
            valid_frame = frame_encode(valid_message, start_sequence, end_sequence)

            raw_socket.sendall(empty_frame + valid_frame)

            # .. we should get exactly one ACK for the valid message.
            ack_bytes = _read_one_framed_response(raw_socket)
            assert b'MSA|AA|EMPTY001' in ack_bytes

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_two_messages_single_tcp_send(self, mllp_server:'int') -> 'None':
        """ Two complete MLLP-framed messages sent in a single sendall call
        must each produce their own ACK with the correct MSA-2 correlation.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Concatenate two framed messages into one TCP write ..
            message_one = sample_adt_a01('BATCH001')
            message_two = sample_adt_a01('BATCH002')
            framed_one = frame_encode(message_one, start_sequence, end_sequence)
            framed_two = frame_encode(message_two, start_sequence, end_sequence)

            raw_socket.sendall(framed_one + framed_two)

            # .. read two separate ACK frames ..
            ack_one = _read_one_framed_response(raw_socket)
            ack_two = _read_one_framed_response(raw_socket)

            assert b'MSA|AA|BATCH001' in ack_one
            assert b'MSA|AA|BATCH002' in ack_two

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_fragmented_send(self, mllp_server:'int') -> 'None':
        """ A framed message sent in tiny chunks with delays between them
        must still be reassembled correctly and produce an AA ACK.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Build a framed message and send it in small fragments ..
            message = sample_adt_a01('FRAG001')
            framed = frame_encode(message, start_sequence, end_sequence)

            offset = 0

            while offset < len(framed):
                end_offset = offset + _fragment_chunk_size
                chunk = framed[offset:end_offset]
                raw_socket.sendall(chunk)
                time.sleep(_fragment_delay_seconds)
                offset = end_offset

            # .. read the ACK.
            ack_bytes = _read_one_framed_response(raw_socket)
            assert b'MSA|AA|FRAG001' in ack_bytes

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_oversized_message_rejected(self) -> 'None':
        """ A message exceeding the server's max_msg_size must be dropped
        (the server discards the frame and the client gets no ACK).
        """

        # Start a server with a very small max message size ..
        process, port = start_server(max_msg_size=_oversized_server_max_msg_size)

        try:

            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            raw_socket.connect(('127.0.0.1', port))
            raw_socket.settimeout(2.0)

            try:

                # Build a message that exceeds the server's limit ..
                padding = b'X' * _oversized_message_byte_count
                oversized_message = sample_adt_a01('OVER001') + padding
                framed = frame_encode(oversized_message, start_sequence, end_sequence)
                raw_socket.sendall(framed)

                # .. the server should drop the frame,
                # so reading should time out or the connection should close.
                try:
                    response = raw_socket.recv(_recv_buffer_size)

                    # If we got data, the server should not have sent an ACK for this
                    if response:
                        assert b'MSA|AA|OVER001' not in response

                except socket.timeout:
                    pass

            finally:
                raw_socket.close()

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################
# Group 4 - Pre-processing quirks
# ################################################################################################################################
# ################################################################################################################################

class TestPreprocessingQuirks:
    """ Verifies tolerance for real-world invalid HL7 messages.
    Each test crafts a raw byte payload exercising a specific quirk category.
    """

# ################################################################################################################################

    def test_quirk_a_lf_line_endings(self, mllp_server:'int') -> 'None':
        """ A message using LF (\\n) instead of CR for segment separators must be accepted.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Build a message with LF line endings ..
            message_text = (
                'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|LF001|P|2.5\n'
                'PID|||12345^^^MRN||Doe^John||19800101|M\n'
                'PV1||I|ICU^Room1'
            )
            framed = frame_encode(message_text.encode('utf-8'), start_sequence, end_sequence)
            raw_socket.sendall(framed)

            # .. the server should normalize LF to CR and ACK successfully.
            ack_bytes = _read_one_framed_response(raw_socket)
            assert b'MSA|AA|LF001' in ack_bytes

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_quirk_a_crlf_line_endings(self, mllp_server:'int') -> 'None':
        """ A message using CRLF (\\r\\n) instead of bare CR for segment separators must be accepted.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Build a message with CRLF line endings ..
            message_text = (
                'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|CRLF001|P|2.5\r\n'
                'PID|||12345^^^MRN||Doe^John||19800101|M\r\n'
                'PV1||I|ICU^Room1'
            )
            framed = frame_encode(message_text.encode('utf-8'), start_sequence, end_sequence)
            raw_socket.sendall(framed)

            ack_bytes = _read_one_framed_response(raw_socket)
            assert b'MSA|AA|CRLF001' in ack_bytes

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_quirk_b_short_msh2(self, mllp_server:'int') -> 'None':
        """ A message with only 2 encoding characters in MSH-2 (e.g. '^~')
        must be padded to the standard '^~\\&' and accepted.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # MSH-2 has only two encoding chars instead of the standard four ..
            message_text = (
                'MSH|^~|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|SHORT001|P|2.5\r'
                'PID|||12345^^^MRN||Doe^John||19800101|M\r'
                'PV1||I|ICU^Room1'
            )
            framed = frame_encode(message_text.encode('utf-8'), start_sequence, end_sequence)
            raw_socket.sendall(framed)

            ack_bytes = _read_one_framed_response(raw_socket)
            assert b'MSA|AA|SHORT001' in ack_bytes

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_quirk_b_nonstandard_delimiters(self, mllp_server:'int') -> 'None':
        """ A message with all four delimiters non-standard (e.g. '#!@$')
        must be rewritten to the standard delimiters and accepted.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # All four encoding characters are non-standard ..
            message_text = (
                'MSH|#!@$|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT#A01|DELIM001|P|2.5\r'
                'PID|||12345###MRN||Doe#John||19800101|M\r'
                'PV1||I|ICU#Room1'
            )
            framed = frame_encode(message_text.encode('utf-8'), start_sequence, end_sequence)
            raw_socket.sendall(framed)

            ack_bytes = _read_one_framed_response(raw_socket)
            assert b'MSA|AA|DELIM001' in ack_bytes

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_quirk_l_truncated_msh(self, mllp_server:'int') -> 'None':
        """ A message starting with 'SH|' (missing the leading M) must be repaired and accepted.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Missing leading 'M' from MSH ..
            message_text = (
                'SH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|TRUNC001|P|2.5\r'
                'PID|||12345^^^MRN||Doe^John||19800101|M\r'
                'PV1||I|ICU^Room1'
            )
            framed = frame_encode(message_text.encode('utf-8'), start_sequence, end_sequence)
            raw_socket.sendall(framed)

            ack_bytes = _read_one_framed_response(raw_socket)
            assert b'MSA|AA|TRUNC001' in ack_bytes

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_quirk_l_junk_prefix(self, mllp_server:'int') -> 'None':
        """ A message with junk before the MSH segment must have the junk stripped and be accepted.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Junk bytes before the actual MSH segment ..
            message_text = (
                'ORU_R01|MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|JUNK001|P|2.5\r'
                'PID|||12345^^^MRN||Doe^John||19800101|M\r'
                'PV1||I|ICU^Room1'
            )
            framed = frame_encode(message_text.encode('utf-8'), start_sequence, end_sequence)
            raw_socket.sendall(framed)

            ack_bytes = _read_one_framed_response(raw_socket)
            assert b'MSA|AA|JUNK001' in ack_bytes

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_quirk_o_concatenated_messages(self, mllp_server:'int') -> 'None':
        """ A single MLLP frame containing two complete HL7 messages (two MSH lines)
        must produce two separate ACK frames.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Two complete messages concatenated inside one MLLP frame ..
            message_one = (
                'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|CAT001|P|2.5\r'
                'PID|||12345^^^MRN||Doe^John||19800101|M'
            )
            message_two = (
                '\rMSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|CAT002|P|2.5\r'
                'PID|||67890^^^MRN||Smith^Jane||19900515|F'
            )
            combined = message_one + message_two
            framed = frame_encode(combined.encode('utf-8'), start_sequence, end_sequence)
            raw_socket.sendall(framed)

            # Both ACKs may arrive in a single TCP segment, so a shared decoder
            # is needed to avoid losing the second ACK's bytes.
            ack_one, ack_two = _read_two_framed_responses(raw_socket)

            assert b'MSA|AA|CAT001' in ack_one
            assert b'MSA|AA|CAT002' in ack_two

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_quirk_r_msh18_encoding(self, mllp_server:'int') -> 'None':
        """ A message encoded in ISO-8859-1 with MSH-18=8859/1 and non-ASCII characters
        must be decoded correctly and accepted.
        """

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', mllp_server))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Build a message with ISO-8859-1 encoding.
            # MSH-18 is field index 17 after the field separator.
            # PID-5 contains German umlauts encoded as ISO-8859-1 bytes.
            message_text = (
                'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|ENC001|P|2.5|||||||||8859/1\r'
                'PID|||12345^^^MRN||M\xe4ller^H\xf6lzer||19800101|M\r'
                'PV1||I|ICU^Room1'
            )

            # Encode using ISO-8859-1 so the byte values match the declared encoding ..
            raw_bytes = message_text.encode('iso-8859-1')
            framed = frame_encode(raw_bytes, start_sequence, end_sequence)
            raw_socket.sendall(framed)

            # .. the server should decode using MSH-18 and ACK successfully.
            ack_bytes = _read_one_framed_response(raw_socket)
            assert b'MSA|AA|ENC001' in ack_bytes

        finally:
            raw_socket.close()

# ################################################################################################################################
# ################################################################################################################################
# Group 5 - TLS and mTLS
# ################################################################################################################################
# ################################################################################################################################

class TestTlsAndMtls:
    """ Verifies TLS and mutual TLS (mTLS) handshakes and communication.
    """

# ################################################################################################################################

    def test_tls_plain(self, tls_certs:'dict[str, str]', make_client:'callable_') -> 'None':
        """ A TLS server with verify=none must accept a client that only trusts the CA
        (no client cert required).
        """

        # Start a server with TLS but no client verification ..
        process, port = start_server(
            tls_cert=tls_certs['server_cert'],
            tls_key=tls_certs['server_key'],
            tls_ca=tls_certs['ca'],
            tls_verify='none',
        )

        try:

            # Build a client SSL context that trusts the CA ..
            ssl_context = build_client_ssl_context(ca_file=tls_certs['ca'])

            client = make_client(port, ssl_context=ssl_context)
            result = client.send(sample_adt_a01('TLS001'), control_id='TLS001')

            assert result.is_accepted is True
            assert result.ack_code == 'AA'

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_mtls_with_client_cert(self, mllp_tls_server:'int', tls_certs:'dict[str, str]',
        make_client:'callable_') -> 'None':
        """ A TLS server with verify=required must accept a client that presents a valid cert.
        """

        # Build a client SSL context with both CA trust and client certificate ..
        ssl_context = build_client_ssl_context(
            ca_file=tls_certs['ca'],
            cert_file=tls_certs['client_cert'],
            key_file=tls_certs['client_key'],
        )

        client = make_client(mllp_tls_server, ssl_context=ssl_context)
        result = client.send(sample_adt_a01('MTLS001'), control_id='MTLS001')

        assert result.is_accepted is True
        assert result.ack_code == 'AA'

# ################################################################################################################################

    def test_mtls_without_client_cert_rejected(self, mllp_tls_server:'int',
        tls_certs:'dict[str, str]') -> 'None':
        """ A TLS server with verify=required must reject a client without a client certificate.
        The rejection may happen during the handshake or on the first data exchange.
        """

        # Build a client SSL context that trusts the CA but provides no client cert ..
        ssl_context = build_client_ssl_context(ca_file=tls_certs['ca'])

        raw_socket = socket.create_connection(('127.0.0.1', mllp_tls_server), timeout=_socket_timeout)

        try:

            # The rejection may come during wrap_socket or on first send/recv,
            # depending on the TLS implementation and timing.
            try:
                tls_socket = ssl_context.wrap_socket(raw_socket, server_hostname='127.0.0.1')

                # If handshake succeeded, the server will reject on data exchange ..
                message = sample_adt_a01('NOPE001')
                framed = frame_encode(message, start_sequence, end_sequence)
                tls_socket.sendall(framed)

                # .. reading the response should fail.
                response = tls_socket.recv(_recv_buffer_size)

                # If we got an empty response, the server closed the connection
                assert response == b'', 'Expected empty response or SSLError'

            except (ssl.SSLError, ConnectionResetError, BrokenPipeError):
                pass

        finally:
            raw_socket.close()

# ################################################################################################################################

    def test_tls_minimum_version(self, tls_certs:'dict[str, str]') -> 'None':
        """ A client attempting TLS 1.1 (below the server's minimum of 1.2)
        must fail the handshake.
        """

        # Start a TLS server with the standard minimum version ..
        process, port = start_server(
            tls_cert=tls_certs['server_cert'],
            tls_key=tls_certs['server_key'],
            tls_ca=tls_certs['ca'],
            tls_verify='none',
        )

        try:

            # Build a client context that caps at TLS 1.1 ..
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.load_verify_locations(cafile=tls_certs['ca'])
            ssl_context.maximum_version = ssl.TLSVersion.TLSv1_1

            raw_socket = socket.create_connection(('127.0.0.1', port), timeout=_socket_timeout)

            try:

                # The handshake should fail because TLS 1.1 is below the server minimum.
                try:
                    _ = ssl_context.wrap_socket(raw_socket, server_hostname='127.0.0.1')
                    assert False, 'Expected ssl.SSLError for TLS version mismatch'
                except ssl.SSLError:
                    pass

            finally:
                raw_socket.close()

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################
# Group 6 - Timeouts and errors
# ################################################################################################################################
# ################################################################################################################################

class TestTimeoutsAndErrors:
    """ Verifies correct behavior for slow callbacks, unreachable ports, and mid-connection kills.
    """

# ################################################################################################################################

    def test_slow_callback_timeout(self, make_client:'callable_') -> 'None':
        """ A server with a slow callback must cause the client to raise HL7Exception
        when the client's receive timeout is shorter than the callback delay.
        """

        # Start a server that sleeps for 5 seconds before ACKing ..
        process, port = start_server(
            callback_mode='slow',
            callback_delay=_slow_callback_delay_seconds,
        )

        try:

            client = make_client(port)

            # Override the client's receive timeout to be shorter than the delay ..
            client.receive_timeout = _client_receive_timeout_seconds

            raised = False

            try:
                _ = client.send(sample_adt_a01('SLOW001'), control_id='SLOW001')
            except HL7Exception as exception:
                raised = True
                assert 'Timed out' in str(exception)

            assert raised is True

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_connect_to_closed_port(self, make_client:'callable_') -> 'None':
        """ Connecting to a port that is not listening must raise ConnectionRefusedError.
        """

        # Bind a socket to get a free port, then close it immediately ..
        temporary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temporary_socket.bind(('127.0.0.1', 0))
        unused_port = temporary_socket.getsockname()[1]
        temporary_socket.close()

        client = make_client(unused_port)

        raised = False

        try:
            _ = client.send(sample_adt_a01('NOPE001'), control_id='NOPE001')
        except ConnectionRefusedError:
            raised = True

        assert raised is True

# ################################################################################################################################

    def test_server_killed_mid_connection(self) -> 'None':
        """ Killing the server mid-connection must cause the client socket to
        get an empty recv or a connection error.
        """

        process, port = start_server(callback_mode='slow', callback_delay=30)

        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw_socket.connect(('127.0.0.1', port))
        raw_socket.settimeout(_socket_timeout)

        try:

            # Send just the start byte and part of a message, but not the end sequence ..
            partial_data = start_sequence + b'MSH|^~\\&|Partial'
            raw_socket.sendall(partial_data)

            # .. kill the server with SIGKILL ..
            process.send_signal(signal.SIGKILL)
            process.wait()

            # .. attempt to read should fail or return empty bytes.
            try:
                response = raw_socket.recv(_recv_buffer_size)
                assert response == b''
            except (ConnectionResetError, ConnectionError, BrokenPipeError):
                pass

        finally:
            raw_socket.close()

# ################################################################################################################################
# ################################################################################################################################
# Group 7 - Retry engine in-process
# ################################################################################################################################
# ################################################################################################################################

class TestRetryEngine:
    """ Verifies retry logic, DLQ routing, and backoff delays using mock send callables.
    No subprocess needed - tests RetryEngine directly.
    """

# ################################################################################################################################

    def test_retry_ar_then_aa(self) -> 'None':
        """ When the send function returns AR twice then AA, the engine must succeed
        after 2 retries.
        """

        call_count = 0

        def mock_send(payload:'bytes') -> 'AckResult':
            nonlocal call_count
            call_count += 1

            out = AckResult()

            # First two calls return AR (retryable) ..
            if call_count <= 2:
                out.ack_code = 'AR'
                out.should_retry = True
                out.error_text = 'Application reject (AR)'

            # .. third call returns AA.
            else:
                out.ack_code = 'AA'
                out.is_accepted = True

            return out

        dlq_payloads:'list[bytes]' = []

        def mock_dlq(payload:'bytes', error_text:'str', retry_count:'int') -> 'None':
            dlq_payloads.append(payload)

        engine = RetryEngine(
            send_func=mock_send,
            dlq_func=mock_dlq,
            max_retries=5,
            backoff_base=0.001,
            jitter_percent=0,
            sleep_func=_noop_sleep,
        )

        result = engine.send_with_retry(b'test-payload')

        assert result.is_sent is True
        assert result.retry_count == 2
        assert len(dlq_payloads) == 0

# ################################################################################################################################

    def test_ae_routes_to_dlq_immediately(self) -> 'None':
        """ When the send function returns AE (application error), the engine must
        route to DLQ immediately with zero retries.
        """

        def mock_send(payload:'bytes') -> 'AckResult':
            out = AckResult()
            out.ack_code = 'AE'
            out.error_text = 'Application error (AE)'
            return out

        dlq_payloads:'list[bytes]' = []

        def mock_dlq(payload:'bytes', error_text:'str', retry_count:'int') -> 'None':
            dlq_payloads.append(payload)

        engine = RetryEngine(
            send_func=mock_send,
            dlq_func=mock_dlq,
            max_retries=5,
            backoff_base=0.001,
            jitter_percent=0,
            sleep_func=_noop_sleep,
        )

        result = engine.send_with_retry(b'test-payload')

        assert result.sent_to_dlq is True
        assert result.retry_count == 0
        assert len(dlq_payloads) == 1

# ################################################################################################################################

    def test_max_retries_exhausted_goes_to_dlq(self) -> 'None':
        """ When the send function always returns AR and max_retries is exhausted,
        the engine must route to DLQ.
        """

        def mock_send(payload:'bytes') -> 'AckResult':
            out = AckResult()
            out.ack_code = 'AR'
            out.should_retry = True
            out.error_text = 'Application reject (AR)'
            return out

        dlq_payloads:'list[bytes]' = []

        def mock_dlq(payload:'bytes', error_text:'str', retry_count:'int') -> 'None':
            dlq_payloads.append(payload)

        engine = RetryEngine(
            send_func=mock_send,
            dlq_func=mock_dlq,
            max_retries=3,
            backoff_base=0.001,
            jitter_percent=0,
            sleep_func=_noop_sleep,
        )

        result = engine.send_with_retry(b'test-payload')

        # retry_count reflects the last attempt index (0-based):
        # attempt 0 (initial), 1, 2, 3 -> then attempt increments to 4 which exceeds max_retries,
        # but retry_count was set to 3 before the increment.
        assert result.sent_to_dlq is True
        assert result.retry_count == 3
        assert len(dlq_payloads) == 1

# ################################################################################################################################

    def test_backoff_delays_are_exponential(self) -> 'None':
        """ The backoff delays must follow an exponential pattern: base * multiplier^(attempt-1).
        """

        call_count = 0

        def mock_send(payload:'bytes') -> 'AckResult':
            nonlocal call_count
            call_count += 1

            out = AckResult()

            # First three calls return AR, fourth returns AA ..
            if call_count <= 3:
                out.ack_code = 'AR'
                out.should_retry = True
                out.error_text = 'Application reject (AR)'
            else:
                out.ack_code = 'AA'
                out.is_accepted = True

            return out

        def mock_dlq(payload:'bytes', error_text:'str', retry_count:'int') -> 'None':
            pass

        recorded_delays:'list[float]' = []

        def recording_sleep(seconds:'float') -> 'None':
            recorded_delays.append(seconds)

        engine = RetryEngine(
            send_func=mock_send,
            dlq_func=mock_dlq,
            max_retries=5,
            backoff_base=1.0,
            backoff_multiplier=2.0,
            jitter_percent=0,
            sleep_func=recording_sleep,
        )

        _ = engine.send_with_retry(b'test-payload')

        # With jitter=0, delays should be exactly 1.0, 2.0, 4.0
        assert len(recorded_delays) == 3
        assert recorded_delays[0] == 1.0
        assert recorded_delays[1] == 2.0
        assert recorded_delays[2] == 4.0

# ################################################################################################################################
# ################################################################################################################################
# Group 8 - Circuit breaker in-process
# ################################################################################################################################
# ################################################################################################################################

class TestCircuitBreaker:
    """ Verifies circuit breaker state transitions using direct calls.
    No subprocess needed.
    """

# ################################################################################################################################

    def test_opens_after_threshold_exceeded(self) -> 'None':
        """ When the failure rate exceeds the threshold, the circuit must open.
        """

        breaker = CircuitBreaker(failure_threshold_percent=50, window_seconds=60)

        # Record 5 successes and 6 failures (>50% failure rate) ..
        for _ in range(5):
            breaker.record_success()

        for _ in range(6):
            breaker.record_failure()

        assert breaker.state == CircuitState.Open
        assert breaker.can_execute() is False

# ################################################################################################################################

    def test_half_open_after_reset_period(self) -> 'None':
        """ After the reset period elapses, the circuit must transition to half-open.
        """

        breaker = CircuitBreaker(
            failure_threshold_percent=50,
            window_seconds=60,
            reset_seconds=_circuit_breaker_reset_seconds,
        )

        # Open the circuit by exceeding the threshold ..
        for _ in range(3):
            breaker.record_success()

        for _ in range(4):
            breaker.record_failure()

        assert breaker.state == CircuitState.Open

        # .. sleep past the reset period ..
        time.sleep(_circuit_breaker_reset_seconds + 0.05)

        # .. can_execute should transition to half-open.
        assert breaker.can_execute() is True
        assert breaker.state == CircuitState.Half_Open

# ################################################################################################################################

    def test_success_in_half_open_closes(self) -> 'None':
        """ A success recorded in half-open state must close the circuit.
        """

        breaker = CircuitBreaker(
            failure_threshold_percent=50,
            window_seconds=60,
            reset_seconds=_circuit_breaker_reset_seconds,
        )

        # Open the circuit ..
        for _ in range(3):
            breaker.record_success()

        for _ in range(4):
            breaker.record_failure()

        assert breaker.state == CircuitState.Open

        # .. sleep past the reset period to reach half-open ..
        time.sleep(_circuit_breaker_reset_seconds + 0.05)
        _ = breaker.can_execute()

        assert breaker.state == CircuitState.Half_Open

        # .. record a success to close the circuit.
        breaker.record_success()
        assert breaker.state == CircuitState.Closed

# ################################################################################################################################

    def test_failure_in_half_open_reopens(self) -> 'None':
        """ A failure recorded in half-open state must reopen the circuit.
        """

        breaker = CircuitBreaker(
            failure_threshold_percent=50,
            window_seconds=60,
            reset_seconds=_circuit_breaker_reset_seconds,
        )

        # Open the circuit ..
        for _ in range(3):
            breaker.record_success()

        for _ in range(4):
            breaker.record_failure()

        assert breaker.state == CircuitState.Open

        # .. sleep past the reset period to reach half-open ..
        time.sleep(_circuit_breaker_reset_seconds + 0.05)
        _ = breaker.can_execute()

        assert breaker.state == CircuitState.Half_Open

        # .. record a failure to reopen the circuit.
        breaker.record_failure()
        assert breaker.state == CircuitState.Open

# ################################################################################################################################
# ################################################################################################################################

def _noop_sleep(seconds:'float') -> 'None':
    """ A no-op sleep replacement for tests that do not need real delays.
    """
    pass

# ################################################################################################################################
# ################################################################################################################################

def _read_one_framed_response(raw_socket:'socket.socket') -> 'bytes':
    """ Reads from a raw socket until one complete MLLP frame is received.
    """
    decoder = FrameDecoder(start_sequence, end_sequence, _max_message_size)

    while True:
        chunk = raw_socket.recv(_recv_buffer_size)

        if not chunk:
            raise ConnectionError('Socket closed before receiving a complete frame')

        decoder.feed(chunk)
        message = decoder.next_message()

        if message is not None:

            out = message
            break

    return out # pyright: ignore[reportPossiblyUnbound]

# ################################################################################################################################

def _read_two_framed_responses(raw_socket:'socket.socket') -> 'tuple[bytes, bytes]':
    """ Reads from a raw socket until two complete MLLP frames are received.
    Uses a single decoder so bytes from both frames are not lost across calls.
    """
    decoder = FrameDecoder(start_sequence, end_sequence, _max_message_size)

    collected:'list[bytes]' = []

    while len(collected) < 2:
        chunk = raw_socket.recv(_recv_buffer_size)

        if not chunk:
            raise ConnectionError('Socket closed before receiving two complete frames')

        decoder.feed(chunk)

        # Extract all complete messages from the current buffer state ..
        while len(collected) < 2:
            message = decoder.next_message()

            if message is None:
                break

            collected.append(message)

    out = (collected[0], collected[1])
    return out

# ################################################################################################################################
# ################################################################################################################################
