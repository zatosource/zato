# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import socket
from threading import Thread
from time import monotonic, sleep

# pytest
import pytest

# Zato
from zato.common.ext.bunch import Bunch
from zato.common.hl7.exception import HL7Exception
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.util.tcp import get_free_port
from zato.server.generic.api.outconn_hl7_mllp import _HL7MLLPConnection

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

_Host = '127.0.0.1'

_Start_Sequence = b'\x0b'
_End_Sequence   = b'\x1c\x0d'

# How long the listener waits for the client's frame before concluding that none is coming
_Listener_Read_Timeout = 5.0

# How long a send waits for its acknowledgment, in seconds and in the milliseconds a connection's config has
_Receive_Timeout = 0.3
_Receive_Timeout_Ms = 300

# What share of the receive timeout passes between two pieces of an acknowledgment that arrives in pieces -
# each gap is inside the timeout and the three of them together are outside it
_Piece_Gap_Share = 0.8
_Piece_Count = 3

# A message with every MSH field through MSH-12, and the same message cut after MSH-9, so that it has no MSH-10
_Message_With_Control_Id = 'MSH|^~\\&|SEND|FAC|RECV|FAC|20260101000000||ADT^A01|CTRL-0001|P|2.5\rPID|1||10001^^^MRN||Smith^John'
_Message_Without_Control_Id = 'MSH|^~\\&|SEND|FAC|RECV|FAC|20260101000000||ADT^A01\rPID|1||10001^^^MRN||Smith^John'

# A message in ISO-8859-1, which MSH-18 says, with a byte in PID-5 that is not UTF-8
_Message_In_Latin_1 = 'MSH|^~\\&|SEND|FAC|RECV|FAC|20260101000000||ADT^A01|CTRL-0002|P|2.5|||||8859/1\rPID|1||10002^^^MRN||Dubé^Rémi'

# ################################################################################################################################
# ################################################################################################################################

def _build_ack(frame:'bytes', ack_code:'str') -> 'bytes':
    """ Builds the acknowledgment a receiving system answers one frame with, echoing MSH-10 in MSA-2 - an empty
    MSA-2 for a message that has no MSH-10.
    """
    payload = frame[len(_Start_Sequence):-len(_End_Sequence)]
    msh_line = payload.split(b'\r', 1)[0].decode('ascii', errors='replace')
    fields = msh_line.split('|')

    field_count = len(fields)
    has_control_id = field_count > 9

    if has_control_id:
        control_id = fields[9]
    else:
        control_id = ''

    ack = f'MSH|^~\\&|RECV|FAC|SEND|FAC|20260101000001||ACK|ACK-0001|P|2.5\rMSA|{ack_code}|{control_id}'

    out = _Start_Sequence + ack.encode('utf-8') + _End_Sequence
    return out

# ################################################################################################################################

class _ReceivingSystem:
    """ A listener that accepts one connection, records the frame it received and answers it the way the test says.
    """

    def __init__(self, answer:'callable_') -> 'None':
        self.port = get_free_port()
        self.frame = b''
        self._answer = answer

        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((_Host, self.port))
        self._server.listen(1)
        self._server.settimeout(_Listener_Read_Timeout)

        self._thread = Thread(target=self._serve, daemon=True)
        self._thread.start()

# ################################################################################################################################

    def _serve(self) -> 'None':

        conn, _ = self._server.accept()
        conn.settimeout(_Listener_Read_Timeout)

        try:
            # The frame is complete once its end sequence has arrived ..
            while _End_Sequence not in self.frame:
                chunk = conn.recv(4096)

                if not chunk:
                    break

                self.frame += chunk

            # .. and the answer is whatever the test chose.
            self._answer(conn, self.frame)

        finally:
            conn.close()

# ################################################################################################################################

    def close(self) -> 'None':
        self._thread.join(_Listener_Read_Timeout)
        self._server.close()

# ################################################################################################################################
# ################################################################################################################################

def _answer_aa_in_pieces(conn:'socket.socket', frame:'bytes') -> 'None':
    """ Sends an AA in pieces, each inside the receive timeout and all of them together outside it.
    """
    ack = _build_ack(frame, 'AA')
    piece_size = len(ack) // _Piece_Count
    gap = _Receive_Timeout * _Piece_Gap_Share

    for index in range(_Piece_Count):
        start = index * piece_size

        if index == _Piece_Count - 1:
            piece = ack[start:]
        else:
            piece = ack[start:start + piece_size]

        conn.sendall(piece)
        sleep(gap)

# ################################################################################################################################

def _answer_ae(conn:'socket.socket', frame:'bytes') -> 'None':
    ack = _build_ack(frame, 'AE')
    conn.sendall(ack)

# ################################################################################################################################

def _answer_aa(conn:'socket.socket', frame:'bytes') -> 'None':
    ack = _build_ack(frame, 'AA')
    conn.sendall(ack)

# ################################################################################################################################
# ################################################################################################################################

def _build_client(port:'int') -> 'HL7MLLPClient':
    out = HL7MLLPClient(_Host, port, _Start_Sequence, _End_Sequence, receive_timeout=_Receive_Timeout)
    return out

# ################################################################################################################################

def _build_connection(port:'int') -> '_HL7MLLPConnection':
    config = Bunch()
    config.name = 'test-mllp-client-send'
    config.address = f'{_Host}:{port}'
    config.start_seq = '0b'
    config.end_seq = '1c 0d'
    config.recv_timeout = _Receive_Timeout_Ms
    config.max_msg_size = 2_000_000
    config.read_buffer_size = 4096
    config.should_log_messages = False
    config.tls_ca_path = ''
    config.tls_cert_path = ''
    config.tls_key_path = ''

    out = _HL7MLLPConnection(config)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestClientSend:
    """ One send through the client Zato's outgoing MLLP connections use - how long the acknowledgment is waited
    for, what the result says of the acknowledgment and what the wire carries.
    """

    def test_an_acknowledgment_arriving_in_pieces_is_held_to_one_deadline(self) -> 'None':
        """ The receive timeout is for the whole acknowledgment - one that arrives in pieces, each inside the
        timeout and all of them together outside it, is a timed out send.
        """
        receiving_system = _ReceivingSystem(_answer_aa_in_pieces)

        try:
            client = _build_client(receiving_system.port)
            data = _Message_With_Control_Id.encode('utf-8')

            started = monotonic()

            with pytest.raises(HL7Exception) as raised:
                _ = client.send(data, 'CTRL-0001')

            elapsed = monotonic() - started

        finally:
            receiving_system.close()

        assert 'Timed out waiting for ACK response' in str(raised.value)

        # The send gave up once the timeout had passed rather than once the last piece had arrived
        assert elapsed < _Receive_Timeout * _Piece_Count * _Piece_Gap_Share

# ################################################################################################################################

    def test_a_message_without_a_control_id_is_answered_with_the_code_the_receiving_system_gave(self) -> 'None':
        """ A message with no MSH-10 is held to the acknowledgment that came back like any other - an AE is an AE.
        """
        receiving_system = _ReceivingSystem(_answer_ae)

        try:
            client = _build_client(receiving_system.port)
            data = _Message_Without_Control_Id.encode('utf-8')

            result = client.send(data, '')

        finally:
            receiving_system.close()

        assert result.ack_code == 'AE'
        assert not result.is_accepted
        assert not result.should_retry
        assert 'MSA|AE|' in result.ack_text

# ################################################################################################################################

    def test_a_message_without_a_control_id_is_accepted_by_an_aa_with_an_empty_msa_2(self) -> 'None':
        """ The acknowledgment of a message with no MSH-10 names no control id either, and it is an acceptance.
        """
        receiving_system = _ReceivingSystem(_answer_aa)

        try:
            client = _build_client(receiving_system.port)
            data = _Message_Without_Control_Id.encode('utf-8')

            result = client.send(data, '')

        finally:
            receiving_system.close()

        assert result.ack_code == 'AA'
        assert result.is_accepted

# ################################################################################################################################

    def test_bytes_outside_utf8_reach_the_wire_as_given(self) -> 'None':
        """ A message given as bytes travels as those bytes, whatever encoding they are in.
        """
        receiving_system = _ReceivingSystem(_answer_aa)

        try:
            connection = _build_connection(receiving_system.port)
            given = _Message_In_Latin_1.encode('iso-8859-1')

            result = connection.invoke(given, needs_audit=False)

        finally:
            receiving_system.close()

        assert result.is_accepted

        on_wire = receiving_system.frame[len(_Start_Sequence):-len(_End_Sequence)]
        assert on_wire == given

# ################################################################################################################################
# ################################################################################################################################
