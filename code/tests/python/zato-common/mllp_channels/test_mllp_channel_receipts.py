# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a listener leaves behind for every frame it is handed - an acknowledgment on the wire and,
# where the channel audits, a receipt with that acknowledgment filed next to it. The listener is driven
# in-process over a fake socket, so no transport runs and the audit log is a SQLite file of the test's own.

# stdlib
import os

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog
from zato.common.audit_log.api import ModuleCtx as AuditLogCtx
from zato.common.hl7.mllp.reply import Unmatched_Object_Name
from zato.common.hl7.mllp.router import HL7MessageRouter
from zato.common.hl7.mllp.server import ConnectionContext, HL7MLLPServer
from zato.common.hl7.mllp.settings import ListenerConfig, RouteSettings
from zato.common.typing_ import cast_

from mllp_live_util import sample_adt_a01

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, dictlist
    any_ = any_
    anylist = anylist
    dictlist = dictlist

# ################################################################################################################################
# ################################################################################################################################

_channel_name = 'test-mllp-receipts'
_server_name = 'test-mllp-receipts-server'

# Who the messages are taken to be arriving from
_sender_ip   = '203.0.113.20'
_sender_port = 40100

# A batch whose header is all there is to it - not one message inside
_batch_with_no_message = b'BHS|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000\rBTS|0'

# A batch holding one admission
_batch_with_one_message = (
    b'BHS|^~\\&|SendApp|SendFac|RecvApp|RecvFac|20230101120000\r' +
    sample_adt_a01('CTRL_BATCH_001') +
    b'\rBTS|1'
)

# What the sender is told when its batch holds no message
_no_message_error_text = 'Batch contains no MSH segment'

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(autouse=True)
def audit_db_env(tmp_path:'os.PathLike') -> 'any_':
    """ Points the audit database at a SQLite file of this test's own.
    """
    database_path = os.path.join(str(tmp_path), 'audit.db')
    os.environ[AuditLogCtx.Env_Type] = AuditLogCtx.Type_SQLite
    os.environ[AuditLogCtx.Env_Name] = database_path

    yield database_path

    del os.environ[AuditLogCtx.Env_Type]
    del os.environ[AuditLogCtx.Env_Name]

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

class _RecordingCallback:
    """ Records each message it is handed, standing in for a channel's service.
    """
    def __init__(self) -> 'None':
        self.messages:'anylist' = []

    def __call__(self, message:'object', cid:'str') -> 'None':
        self.messages.append(message)

# ################################################################################################################################
# ################################################################################################################################

def _new_server(settings:'RouteSettings', *, is_audit_log_active:'bool'=True) -> 'tuple':
    """ Builds an in-process listener, never started, with one default route under the given settings
    and an audit log of its own.
    """
    callback = _RecordingCallback()

    router = HL7MessageRouter()
    router.add_route(_channel_name, callback, service_name='test.service', is_default=True, settings=settings,
        is_audit_log_active=is_audit_log_active)

    audit_log = AuditLog(_server_name)
    server = HL7MLLPServer(ListenerConfig(), router, audit_log=audit_log)

    out = (server, router, callback)
    return out

# ################################################################################################################################

def _deliver(server:'HL7MLLPServer', router:'HL7MessageRouter', message:'bytes', *, is_routed:'bool'=True) -> '_FakeSocket':
    """ Hands one frame to the server's message handler over a fake socket - under the route it matches,
    or under no route at all, which is how the listener hands over a frame nothing matched.
    """
    fake_socket = _FakeSocket()
    connection_context = ConnectionContext(_sender_ip, _sender_port, '')

    if is_routed:
        msh_line = message.split(b'\r', 1)[0].decode('ascii')
        matched_route = router.match(msh_line)
        assert matched_route is not None
        settings = matched_route.settings
    else:
        matched_route = None
        settings = RouteSettings(should_parse_on_input=False)

    active_socket = cast_('any_', fake_socket)
    server._handle_message(active_socket, message, connection_context, matched_route, settings)

    return fake_socket

# ################################################################################################################################

def _get_events(event_type:'str') -> 'dictlist':
    """ Returns every audit event of one type, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.event_type == event_type)
    query = query.order_by(event_table.c.id)

    out:'dictlist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(dict(row._mapping))

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestWhatABatchLeavesBehind:

    def test_a_batch_with_no_message_in_it_is_answered(self) -> 'None':
        """ The sender waiting on an acknowledgment is told the batch holds nothing, rather than being
        left with a connection that goes quiet - with the reason, this channel returning errors.
        """
        server, router, callback = _new_server(RouteSettings(should_parse_on_input=False, should_return_errors=True))

        fake_socket = _deliver(server, router, _batch_with_no_message)

        assert len(fake_socket.sent) == 1

        reply = fake_socket.sent[0].decode('utf-8')

        assert 'MSA|AR|' in reply
        assert _no_message_error_text in reply

        # Nothing reached the channel's service ..
        assert callback.messages == []

        # .. and the live state counts the batch as received and turned away.
        assert server.state.received == 1
        assert server.state.nacked == 1

        # The receipt and the acknowledgment are both filed under the channel.
        received = _get_events(AuditEvent.Interchange_Received)
        acks = _get_events(AuditEvent.Ack_Sent)

        assert len(received) == 1
        assert len(acks) == 1
        assert received[0]['object_name'] == _channel_name
        assert acks[0]['cid'] == received[0]['cid']

# ################################################################################################################################

    def test_a_batch_that_matched_nothing_is_recorded_under_the_reserved_name(self) -> 'None':
        """ There is no channel whose audit setting could be consulted, so a batch nothing matched
        is always audited, filed under the same reserved name a single message nothing matched is.
        """
        server, router, callback = _new_server(RouteSettings(should_parse_on_input=False))

        fake_socket = _deliver(server, router, _batch_with_one_message, is_routed=False)

        reply = fake_socket.sent[0].decode('utf-8')

        assert 'MSA|AR|' in reply
        assert callback.messages == []

        received = _get_events(AuditEvent.Interchange_Received)
        acks = _get_events(AuditEvent.Ack_Sent)

        assert len(received) == 1
        assert len(acks) == 1

        assert received[0]['object_name'] == Unmatched_Object_Name
        assert acks[0]['object_name'] == Unmatched_Object_Name
        assert acks[0]['cid'] == received[0]['cid']

        # The one message inside is its own row under the batch
        messages = _get_events(AuditEvent.Message_Received)

        assert len(messages) == 1
        assert messages[0]['object_name'] == Unmatched_Object_Name
        assert messages[0]['msg_id'] == 'CTRL_BATCH_001'

# ################################################################################################################################
# ################################################################################################################################

class TestWhatADuplicateLeavesBehind:

    def test_a_duplicate_on_an_auditing_channel_leaves_its_receipt_and_its_acknowledgment(self) -> 'None':
        """ A duplicate is acknowledged positively without reaching the service, and it was received
        all the same, so the channel keeps its receipt and its acknowledgment like any other's.
        """
        settings = RouteSettings(should_parse_on_input=False, dedup_ttl_value=60, dedup_ttl_unit='minutes')
        server, router, callback = _new_server(settings)

        message = sample_adt_a01('CTRL_DUP_RECEIPT_001')

        _ = _deliver(server, router, message)
        fake_socket = _deliver(server, router, message)

        # The second arrival was acknowledged positively and never reached the service ..
        assert 'MSA|AA|' in fake_socket.sent[0].decode('utf-8')
        assert len(callback.messages) == 1

        # .. both arrivals count on the channel's own state ..
        channel_state = server.get_channel_state(_channel_name)

        assert channel_state.received == 2
        assert channel_state.acked == 2

        # .. and both left a receipt with an acknowledgment filed next to it.
        received = _get_events(AuditEvent.Message_Received)
        acks = _get_events(AuditEvent.Ack_Sent)

        assert len(received) == 2
        assert len(acks) == 2

        for row in received:
            assert row['object_name'] == _channel_name
            assert row['msg_id'] == 'CTRL_DUP_RECEIPT_001'

        assert acks[1]['cid'] == received[1]['cid']
        assert acks[1]['cid'] != acks[0]['cid']

# ################################################################################################################################

    def test_a_duplicate_on_a_channel_that_does_not_audit_leaves_nothing(self) -> 'None':
        settings = RouteSettings(should_parse_on_input=False, dedup_ttl_value=60, dedup_ttl_unit='minutes')
        server, router, callback = _new_server(settings, is_audit_log_active=False)

        message = sample_adt_a01('CTRL_DUP_SILENT_001')

        _ = _deliver(server, router, message)
        fake_socket = _deliver(server, router, message)

        assert 'MSA|AA|' in fake_socket.sent[0].decode('utf-8')
        assert len(callback.messages) == 1

        assert _get_events(AuditEvent.Message_Received) == []
        assert _get_events(AuditEvent.Ack_Sent) == []

# ################################################################################################################################
# ################################################################################################################################

class TestWhatARefusedSenderLeavesBehind:

    def _refuse(self, server:'HL7MLLPServer', router:'HL7MessageRouter', message:'bytes') -> '_FakeSocket':
        """ Hands one message to the server as one whose sender the matched channel does not accept.
        """
        fake_socket = _FakeSocket()
        connection_context = ConnectionContext(_sender_ip, _sender_port, '')

        msh_line = message.split(b'\r', 1)[0].decode('ascii')
        matched_route = router.match(msh_line)
        assert matched_route is not None

        active_socket = cast_('any_', fake_socket)
        server._on_sender_refused(active_socket, msh_line, message, matched_route, connection_context)

        return fake_socket

# ################################################################################################################################

    def test_a_refused_sender_is_answered_counted_and_audited_on_the_channel(self) -> 'None':
        """ The refusal lands in the channel's counters and audit trail rather than nowhere - the receipt
        of the message and the acknowledgment that answered it, on one correlation id.
        """
        server, router, callback = _new_server(RouteSettings(should_parse_on_input=False, should_return_errors=True))

        fake_socket = self._refuse(server, router, sample_adt_a01('CTRL_REFUSED_001'))

        # The sender is told no, with no reason given, whatever the channel says of errors ..
        reply = fake_socket.sent[0].decode('utf-8')

        assert 'MSA|AR|CTRL_REFUSED_001' in reply
        assert 'ERR|' not in reply

        # .. nothing reached the service ..
        assert callback.messages == []

        # .. the channel counts the message as received and turned away ..
        channel_state = server.get_channel_state(_channel_name)

        assert channel_state.received == 1
        assert channel_state.nacked == 1

        # .. and the receipt and the acknowledgment are filed together under the channel.
        received = _get_events(AuditEvent.Message_Received)
        acks = _get_events(AuditEvent.Ack_Sent)

        assert len(received) == 1
        assert len(acks) == 1
        assert received[0]['object_name'] == _channel_name
        assert received[0]['msg_id'] == 'CTRL_REFUSED_001'
        assert acks[0]['object_name'] == _channel_name
        assert acks[0]['cid'] == received[0]['cid']

# ################################################################################################################################

    def test_a_refused_sender_on_a_channel_that_does_not_audit_leaves_nothing(self) -> 'None':
        server, router, callback = _new_server(RouteSettings(should_parse_on_input=False), is_audit_log_active=False)

        fake_socket = self._refuse(server, router, sample_adt_a01('CTRL_REFUSED_SILENT_001'))

        assert 'MSA|AR|' in fake_socket.sent[0].decode('utf-8')
        assert callback.messages == []

        assert _get_events(AuditEvent.Message_Received) == []
        assert _get_events(AuditEvent.Ack_Sent) == []

# ################################################################################################################################
# ################################################################################################################################
