# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket

# Zato
from zato.common.hl7.mllp.codec import frame_encode

from conftest import start_sequence, end_sequence, start_server, stop_server

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

# A well-formed ADT^A01 with standard CR line endings
_standard_adt = (
    'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|QUIRK_CTRL|P|2.5\r'
    'PID|||12345^^^MRN||Doe^John||19800101|M'
)

# ################################################################################################################################
# ################################################################################################################################

class TestNormalizeLineEndings:
    """ Verifies the normalize_line_endings toggle.
    """

    def test_normalize_line_endings_on(self) -> 'None':
        """ With normalization on, a message using CRLF line endings should be accepted.
        """
        process, port = start_server(normalize_line_endings=True)

        try:
            crlf_message = _standard_adt.replace('\r', '\r\n')
            response = _send_raw_and_recv(port, crlf_message.encode('utf-8'))
            response_text = response.decode('utf-8', errors='replace')

            assert 'AA' in response_text

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_normalize_line_endings_off(self) -> 'None':
        """ With normalization off, a message with standard CR endings should still work.
        """
        process, port = start_server(normalize_line_endings=False)

        try:
            response = _send_raw_and_recv(port, _standard_adt.encode('utf-8'))

            # .. the server should still process the message (CR is the standard separator).
            assert len(response) > 0

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################

class TestForceStandardDelimiters:
    """ Verifies the force_standard_delimiters toggle.
    """

    def test_force_standard_delimiters_on(self) -> 'None':
        """ With standard delimiters forced, a message with non-standard delimiters should be corrected and accepted.
        """
        process, port = start_server(force_standard_delimiters=True)

        try:
            # Use # as the component separator instead of ^ ..
            nonstandard_message = (
                'MSH|#~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT#A01|DELIM_CTRL|P|2.5\r'
                'PID|||12345^^^MRN||Doe^John||19800101|M'
            )
            response = _send_raw_and_recv(port, nonstandard_message.encode('utf-8'))
            response_text = response.decode('utf-8', errors='replace')

            assert 'AA' in response_text

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_force_standard_delimiters_off(self) -> 'None':
        """ With standard delimiters not forced, a well-formed message should still be processed.
        """
        process, port = start_server(force_standard_delimiters=False)

        try:
            response = _send_raw_and_recv(port, _standard_adt.encode('utf-8'))

            assert len(response) > 0

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################

class TestRepairTruncatedMSH:
    """ Verifies the repair_truncated_msh toggle.
    """

    def test_repair_truncated_msh_on(self) -> 'None':
        """ With repair on, a message with a junk prefix before MSH should be recovered and accepted.
        """
        process, port = start_server(repair_truncated_msh=True)

        try:
            # Prepend junk bytes before the actual MSH ..
            junk_prefix_message = b'\x00\x00GARBAGE' + _standard_adt.encode('utf-8')
            response = _send_raw_and_recv(port, junk_prefix_message)
            response_text = response.decode('utf-8', errors='replace')

            assert 'AA' in response_text

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_repair_truncated_msh_off(self) -> 'None':
        """ With repair off, a clean message should still be processed normally.
        """
        process, port = start_server(repair_truncated_msh=False)

        try:
            response = _send_raw_and_recv(port, _standard_adt.encode('utf-8'))

            assert len(response) > 0

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################

class TestSplitConcatenatedMessages:
    """ Verifies the split_concatenated_messages toggle.
    """

    def test_split_concatenated_on(self) -> 'None':
        """ With splitting on, two concatenated messages in one frame should produce two ACKs.
        """
        process, port = start_server(split_concatenated_messages=True)

        try:
            # Two messages concatenated without MLLP framing between them ..
            message_a = (
                'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|CONCAT_A|P|2.5\r'
                'PID|||12345^^^MRN||Doe^John||19800101|M'
            )
            message_b = (
                'MSH|^~\\&|LabSys|LabFac|OrderSys|OrderFac|20230101130000||ORU^R01|CONCAT_B|P|2.5\r'
                'PID|||67890^^^MRN||Smith^Jane||19900515|F'
            )
            concatenated = message_a + message_b

            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            raw_socket.connect(('127.0.0.1', port))
            raw_socket.settimeout(_socket_timeout)

            try:
                framed = frame_encode(concatenated.encode('utf-8'), start_sequence, end_sequence)
                raw_socket.sendall(framed)

                # .. read back what we can - should contain two ACK responses ..
                import time
                time.sleep(0.5)

                response = b''
                raw_socket.settimeout(1.0)

                while True:
                    try:
                        chunk = raw_socket.recv(_recv_buffer)
                    except socket.timeout:
                        break

                    if not chunk:
                        break

                    response += chunk

                response_text = response.decode('utf-8', errors='replace')

                # .. count how many times the ACK acknowledgment code appears ..
                ack_count = response_text.count('MSA|')
                assert ack_count >= 2

            finally:
                try:
                    raw_socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                raw_socket.close()

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_split_concatenated_off(self) -> 'None':
        """ With splitting off, a single well-formed message should still be processed.
        """
        process, port = start_server(split_concatenated_messages=False)

        try:
            response = _send_raw_and_recv(port, _standard_adt.encode('utf-8'))

            assert len(response) > 0

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################

class TestUseMSH18Encoding:
    """ Verifies the use_msh18_encoding toggle.
    """

    def test_use_msh18_encoding_on(self) -> 'None':
        """ With MSH-18 encoding enabled, a message specifying UNICODE UTF-8 in MSH-18 should be accepted.
        """
        process, port = start_server(use_msh18_encoding=True)

        try:
            # MSH-18 is field index 17 (0-based from split) ..
            msh18_message = (
                'MSH|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000||ADT^A01|MSH18_CTRL|P|2.5|||AL|NE||UNICODE UTF-8\r'
                'PID|||12345^^^MRN||Doe^John||19800101|M'
            )
            response = _send_raw_and_recv(port, msh18_message.encode('utf-8'))
            response_text = response.decode('utf-8', errors='replace')

            assert 'AA' in response_text

        finally:
            stop_server(process)

# ################################################################################################################################

    def test_use_msh18_encoding_off(self) -> 'None':
        """ With MSH-18 encoding disabled, a standard message should still be processed using the default encoding.
        """
        process, port = start_server(use_msh18_encoding=False)

        try:
            response = _send_raw_and_recv(port, _standard_adt.encode('utf-8'))

            assert len(response) > 0

        finally:
            stop_server(process)

# ################################################################################################################################
# ################################################################################################################################
