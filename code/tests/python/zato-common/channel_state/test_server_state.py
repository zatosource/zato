# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The MLLP server's live-state instrumentation driven in-process - messages are handed
# straight to the message handler over a fake socket, so no transport runs and the tests
# stay offline.

# Zato
from zato.common.hl7.mllp.router import HL7MessageRouter
from zato.common.hl7.mllp.server import ConnectionContext, HL7MLLPServer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# Standard MLLP framing bytes
_start_sequence = b'\x0b'
_end_sequence   = b'\x1c\x0d'

# The peer the fake connection pretends to be
_peer_address = ('127.0.0.1', 12345)

# A well-formed admission
_adt_a01 = (
    b'MSH|^~\\&|HIS|GENERAL_HOSPITAL|LAB_SYSTEM|CENTRAL_LAB|20260115103000||ADT^A01^ADT_A01|MSG000001|P|2.9\r'
    b'EVN|A01|20260115103000\r'
    b'PID|1||445566^^^GENERAL_HOSPITAL^MR||SMITH^JOHN^A||19850315|M\r'
    b'PV1|1|I|ICU^101^A\r'
)

# ################################################################################################################################
# ################################################################################################################################

class _FakeSocket:
    """ A stand-in for the peer's socket, remembering what the server sent back.
    """
    def __init__(self) -> 'None':
        self.sent:'anylist' = []

    def sendall(self, data:'bytes') -> 'None':
        self.sent.append(data)

# ################################################################################################################################

def _new_server(callback:'any_', **overrides:'any_') -> 'HL7MLLPServer':
    """ Builds a server whose default route leads to the given callback -
    never started, so no transport runs.
    """
    router = HL7MessageRouter()
    router.add_route(channel_name='test', service_name='test', callback=callback, is_default=True)

    out = HL7MLLPServer('127.0.0.1:0', router, _start_sequence, _end_sequence, **overrides)
    return out

# ################################################################################################################################

def _deliver(server:'HL7MLLPServer', message:'bytes', control_id:'str'='') -> '_FakeSocket':
    """ Hands one message to the server's message handler over a fake socket.
    """
    if control_id:
        message = message.replace(b'MSG000001', control_id.encode('utf8'))

    fake_socket = _FakeSocket()
    context = ConnectionContext(_peer_address)

    server._handle_message(fake_socket, message, context)

    return fake_socket

# ################################################################################################################################
# ################################################################################################################################

class TestServerState:

    def test_a_processed_message_counts_as_received_and_acked(self) -> 'None':

        def callback(data:'any_') -> 'None':
            pass

        server = _new_server(callback)
        fake_socket = _deliver(server, _adt_a01)

        # The message was acknowledged positively over the wire ..
        assert len(fake_socket.sent) == 1
        assert b'MSA|AA' in fake_socket.sent[0]

        # .. and the live state saw both the arrival and the acknowledgment.
        assert server.state.received == 1
        assert server.state.acked == 1
        assert server.state.nacked == 0
        assert server.state.nack_streak == 0
        assert server.state.last_message_time is not None

# ################################################################################################################################

    def test_a_failing_service_counts_as_nacked(self) -> 'None':

        def callback(data:'any_') -> 'None':
            raise ValueError('The service failed')

        server = _new_server(callback)
        fake_socket = _deliver(server, _adt_a01)

        # The sender got a negative acknowledgment ..
        assert b'MSA|AE' in fake_socket.sent[0]

        # .. and the live state counts it toward the streak and the error rate.
        assert server.state.received == 1
        assert server.state.acked == 0
        assert server.state.nacked == 1
        assert server.state.nack_streak == 1
        assert server.state.get_error_rate() == 1.0

# ################################################################################################################################

    def test_a_recovery_ends_the_streak(self) -> 'None':

        outcomes = [ValueError('down'), ValueError('still down'), None]

        def callback(data:'any_') -> 'None':
            outcome = outcomes.pop(0)
            if outcome is not None:
                raise outcome

        server = _new_server(callback)

        _ = _deliver(server, _adt_a01, control_id='MSG000010')
        _ = _deliver(server, _adt_a01, control_id='MSG000011')

        assert server.state.nack_streak == 2

        _ = _deliver(server, _adt_a01, control_id='MSG000012')

        assert server.state.nack_streak == 0
        assert server.state.acked == 1
        assert server.state.nacked == 2

# ################################################################################################################################

    def test_a_duplicate_is_acknowledged_and_counted(self) -> 'None':

        invocations:'anylist' = []

        def callback(data:'any_') -> 'None':
            invocations.append(data)

        server = _new_server(callback, dedup_ttl_value=5, dedup_ttl_unit='minutes')

        _ = _deliver(server, _adt_a01)
        fake_socket = _deliver(server, _adt_a01)

        # The duplicate was acknowledged positively without reaching the service ..
        assert b'MSA|AA' in fake_socket.sent[0]
        assert len(invocations) == 1

        # .. and the live state counts it as one more received and acked message.
        assert server.state.received == 2
        assert server.state.acked == 2

# ################################################################################################################################

    def test_the_state_carries_the_channel_metrics(self) -> 'None':

        def callback(data:'any_') -> 'None':
            pass

        server = _new_server(callback)
        _ = _deliver(server, _adt_a01)

        metrics = server.state.get_metrics()

        # The listener never started, so the metrics say disconnected -
        # while the message counters reflect what flowed through.
        assert metrics.is_connected is False
        assert metrics.error_rate == 0.0
        assert metrics.nack_streak == 0

# ################################################################################################################################
# ################################################################################################################################
