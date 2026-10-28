# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import AuditEvent, event_table, ModuleCtx as AuditLogCtx
from zato.common.b2b.common.business_log import BusinessLog, expired
from zato.common.b2b.common.business_state import BusinessState
from zato.common.b2b.common.clock import ManualClock
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.outcome import FinalState, SignalKind
from zato.common.b2b.common.send_log import SendLog
from zato.common.b2b.common.store import MessageStore
from zato.common.test.b2b_write_path import FailingCommit, CommitRefused, new_business_message, new_identity, \
    new_memory_engine, new_sent_message, new_stored_message, receipt_outcome, Server, Signal_Body, Source, Start_Time, \
    StatementRecorder, Wire_Body

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pytest import MonkeyPatch
    from zato.common.typing_ import strlist
    MonkeyPatch = MonkeyPatch
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# How many expiries one check ends at most.
_expiry_limit = 100

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture
def writer(monkeypatch:'MonkeyPatch') -> 'GroupCommitWriter':
    """ A writer that commits each write as it is submitted, into an in-memory database.
    """
    monkeypatch.setenv(AuditLogCtx.Env_Enabled, 'True')

    out = GroupCommitWriter(new_memory_engine(), interval_ms=0, is_started=False)
    return out

# ################################################################################################################################

def _event_types(writer:'GroupCommitWriter', message_id:'str') -> 'strlist':
    """ Returns the type of each audit event of a message, in the order they were stored.
    """
    query = select(event_table.c.event_type).where(event_table.c.msg_id == message_id).order_by(event_table.c.id)

    with writer.engine.connect() as connection:
        out = list(connection.execute(query).scalars())

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestDuplicateClaims:
    """ Two copies of one message in two transactions produce one claim.
    """

    def test_two_transactions(self, writer:'GroupCommitWriter') -> 'None':
        store = MessageStore(writer)
        identity = new_identity('message-1')

        assert store.claim(identity, new_stored_message())
        assert not store.claim(identity, new_stored_message())

# ################################################################################################################################
# ################################################################################################################################

class TestFailedCommitOfFirstAttempt:
    """ A failed commit leaves no exchange open, so no delivery follows.
    """

    def test_first_attempt(self, writer:'GroupCommitWriter') -> 'None':
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer)
        failing = FailingCommit(writer.engine)

        with pytest.raises(CommitRefused):
            send_log.record_first_attempt(new_sent_message('message-1'))

        failing.stop()

        assert not send_log.is_open('message-1')
        assert send_log.outstanding(_expiry_limit) == []
        assert _event_types(writer, 'message-1') == []

# ################################################################################################################################
# ################################################################################################################################

class TestTwoEventsPerOutboundMessage:
    """ A business message sent, delivered and acknowledged produces two audit events.
    """

    def test_events(self, writer:'GroupCommitWriter') -> 'None':
        business_log = BusinessLog(Source, Server, writer)
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer, business_log)

        sent = new_sent_message('message-1')
        business = new_business_message('message-1', response_seconds=60)

        send_log.record_first_attempt(sent, business)
        assert send_log.wire_body('message-1') == Wire_Body

        send_log.record_signal(sent, {}, Signal_Body, SignalKind.Receipt, '', '')
        send_log.record_completion(sent, receipt_outcome())

        assert _event_types(writer, 'message-1') == [AuditEvent.Message_Sent, AuditEvent.Message_Completed]

        # The exchange ended, so the message and its bytes are read from the audit log.
        stored = send_log.get('message-1')

        assert stored.outcome.final_state == FinalState.Delivered
        assert stored.retry_state.is_answered
        assert send_log.wire_body('message-1') == Wire_Body

        # The business transaction still awaits its response.
        awaiting = business_log.read('message-1')

        assert awaiting is not None
        assert awaiting.state == BusinessState.Sent

# ################################################################################################################################
# ################################################################################################################################

class TestNoReadsInProgress:
    """ A message in progress is served from memory, and its bytes are not held after the first delivery.
    """

    def test_request_and_notification(self, writer:'GroupCommitWriter') -> 'None':
        business_log = BusinessLog(Source, Server, writer)
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer, business_log)
        recorder = StatementRecorder(writer.engine)

        # A request with its response ..
        request = new_sent_message('request-1')
        business = new_business_message('request-1', receipt_seconds=30, response_seconds=60)

        send_log.record_first_attempt(request, business)
        assert send_log.wire_body('request-1') == Wire_Body

        held = send_log.get('request-1')
        assert held.wire_body == b''

        send_log.record_signal(request, {}, Signal_Body, SignalKind.Receipt, '', '')
        send_log.record_completion(request, receipt_outcome())

        business_log.record_reply(business, BusinessState.Receipted, 'receipt-1', [])
        business_log.record_reply(business, BusinessState.Answered, 'response-1', [])

        # .. and a notification with its signal.
        notification = new_sent_message('notification-1')

        send_log.record_first_attempt(notification)
        assert send_log.wire_body('notification-1') == Wire_Body
        assert send_log.get('notification-1').wire_body == b''

        send_log.record_signal(notification, {}, Signal_Body, SignalKind.Receipt, '', '')
        send_log.record_completion(notification, receipt_outcome())

        assert recorder.reads() == []

        recorder.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestExpiryFromMemory:
    """ The deadlines held in memory expire in the order of their times, each expiry written through the writer.
    """

    def test_expiry(self, writer:'GroupCommitWriter') -> 'None':
        business_log = BusinessLog(Source, Server, writer)

        deadlines = {
            'message-a': 30,
            'message-b': 10,
            'message-c': 20,
            'message-d': 15,
        }

        messages = {}

        for message_id, seconds in deadlines.items():
            message = new_business_message(message_id, response_seconds=seconds)
            business_log.record_sent(message)
            messages[message_id] = message

        # One transaction is answered before its deadline.
        business_log.record_reply(messages['message-d'], BusinessState.Answered, 'response-d', [])

        recorder = StatementRecorder(writer.engine)

        first = expired(business_log, Start_Time + timedelta(seconds=16), _expiry_limit)
        second = expired(business_log, Start_Time + timedelta(seconds=40), _expiry_limit)
        third = expired(business_log, Start_Time + timedelta(seconds=100), _expiry_limit)

        first_ids:'strlist' = []
        second_ids:'strlist' = []

        for outcome in first:
            first_ids.append(outcome.message_id)

        for outcome in second:
            second_ids.append(outcome.message_id)

        assert first_ids == ['message-b']
        assert second_ids == ['message-c', 'message-a']
        assert third == []

        # Nothing was read, and each expiry was committed through the writer.
        assert recorder.reads() == []
        assert recorder.commits == 3

        for message_id in ('message-a', 'message-b', 'message-c'):
            assert _event_types(writer, message_id)[-1] == AuditEvent.Business_Timed_Out

            stored = business_log.read(message_id)
            assert stored is not None
            assert stored.state == BusinessState.Timed_Out

        answered = business_log.read('message-d')
        assert answered is not None
        assert answered.state == BusinessState.Answered

        recorder.stop()

# ################################################################################################################################
# ################################################################################################################################
