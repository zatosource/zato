# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource, event_table, get_retention_days
from zato.common.b2b.common.commit_retention import delete_old_events
from zato.common.b2b.common.outcome import FinalState
from zato.common.b2b.common.schema import held_message_table
from zato.common.b2b.ebms2.common import MessageOrderSemantics, SequenceStatus, SyncReplyMode
from zato.common.b2b.ebms2.inbound_common import pending_deliveries
from zato.common.b2b.ebms2.outbound import SendOptions
from zato.common.b2b.ebms2.sequence_gap import Default_Gap_Grace_Seconds, discard_conversation, Env_Gap_Grace_Seconds, \
    read_gaps, release_gap, report_timed_out
from zato.common.json_internal import loads
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import deliver, new_exchange, new_payload, send, Start_Time
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from pytest import MonkeyPatch
    from zato.common.b2b.common.receive_log import ReceiveLog
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import dictlist, strlist
    datetime = datetime
    dictlist = dictlist
    Exchange = Exchange
    MonkeyPatch = MonkeyPatch
    OutboundMessage = OutboundMessage
    ReceiveLog = ReceiveLog
    strlist = strlist
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

_conversation_id = 'b2b-gap-conversation'

# The retries of the sender and their interval, which the agreement of the tests declares.
_retries = 3
_retry_interval_seconds = 30

# How long a gap waits, with the default grace, from the moment its first message was held.
_gap_seconds = _retries * _retry_interval_seconds + Default_Gap_Grace_Seconds

# A grace other than the default, in seconds.
_custom_grace_seconds = 10

# How many gaps one read returns at most.
_gap_limit = 100

# How many deliveries one page of a recovery holds.
_page_size = 10

# The time between the cutoff of the retention test and each of its two held messages, in seconds,
# and how many events one retention deletes at most.
_retention_step_seconds = 1800
_event_limit = 1000

# ################################################################################################################################
# ################################################################################################################################

def _ordered(parties:'TestParties') -> 'Exchange':
    settings = new_settings(parties, Start_Time)
    settings.business_channel.sync_reply_mode = SyncReplyMode.MSH_Signals_Only
    settings.message_order = MessageOrderSemantics.Guaranteed
    settings.retries = _retries
    settings.retry_interval = f'PT{_retry_interval_seconds}S'

    out = new_exchange(parties, settings)
    return out

# ################################################################################################################################

def _numbered(exchange:'Exchange', sequence_number:'int') -> 'OutboundMessage':
    """ Returns a message of an ordered conversation with its sequence number as its payload.
    """
    options = SendOptions()
    options.conversation_id = _conversation_id
    options.sequence_number = sequence_number
    options.sequence_status = SequenceStatus.Continue

    data = f'<Order><Id>{sequence_number}</Id></Order>'.encode('ascii')
    payload = new_payload(data)

    out = send(exchange, [payload], options)
    return out

# ################################################################################################################################

def _hold(exchange:'Exchange', sequence_number:'int') -> 'OutboundMessage':
    """ Delivers a message that the receiver holds, and returns it.
    """
    out = _numbered(exchange, sequence_number)
    result = deliver(exchange, out)

    assert result.outcome.final_state == FinalState.Held

    return out

# ################################################################################################################################

def _receive_log(exchange:'Exchange') -> 'ReceiveLog':
    out = exchange.receiver.receive_log
    return out

# ################################################################################################################################

def _conversation(exchange:'Exchange') -> 'str':
    """ Returns what the receiver keeps the state of the conversation of the tests under.
    """
    gaps = read_gaps(_receive_log(exchange), _gap_limit)

    out = gaps[0].conversation
    return out

# ################################################################################################################################

def _events(exchange:'Exchange', event_type:'str') -> 'dictlist':
    """ Returns the data and the outcome of each event of the given type that the receiver recorded.
    """
    query = select(event_table.c.data, event_table.c.outcome).where(event_table.c.event_type == event_type)
    statement = query.order_by(event_table.c.id)

    out:'dictlist' = []

    with _receive_log(exchange).writer.engine.connect() as connection:
        for row in connection.execute(statement):
            out.append({'data': loads(row.data), 'outcome': row.outcome})

    return out

# ################################################################################################################################

def _message_events(exchange:'Exchange', message_id:'str') -> 'strlist':
    query = select(event_table.c.event_type).where(event_table.c.msg_id == message_id)
    statement = query.order_by(event_table.c.id)

    out:'strlist' = []

    with _receive_log(exchange).writer.engine.connect() as connection:
        for event_type in connection.execute(statement).scalars():
            out.append(event_type)

    return out

# ################################################################################################################################

def _held_count(exchange:'Exchange') -> 'int':
    query = select(held_message_table.c.id)

    with _receive_log(exchange).writer.engine.connect() as connection:
        rows = connection.execute(query).all()

    out = len(rows)
    return out

# ################################################################################################################################

def _after(seconds:'int') -> 'datetime':
    out = Start_Time + timedelta(seconds=seconds)
    return out

# ################################################################################################################################

def _payload_data(exchange:'Exchange') -> 'list[bytes]':
    """ Returns the payload of each delivery the receiver has not confirmed, in the order the deliveries began.
    """
    out:'list[bytes]' = []

    for delivery in pending_deliveries(_receive_log(exchange), _page_size):
        payload = delivery.payloads[0]
        out.append(payload.data)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestHeldEvent:
    """ Holding a message records where the sequence of its conversation stands.
    """

    def test_held_event(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        held = _hold(exchange, 2)

        assert _message_events(exchange, held.message_id) == [AuditEvent.Message_Received, AuditEvent.Message_Held]

        events = _events(exchange, AuditEvent.Message_Held)

        assert events == [{
            'data': {
                'conversation_id': _conversation_id,
                'expected_sequence_number': 0,
                'received_sequence_number': 2,
            },
            'outcome': AuditOutcome.OK,
        }]

# ################################################################################################################################
# ################################################################################################################################

class TestDeadline:
    """ A gap times out after the retries of its sender and the grace, counted from its first held message.
    """

    def test_deadline(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        _ = _hold(exchange, 1)

        # A message held later does not move the deadline.
        exchange.clock.advance(60)
        _ = _hold(exchange, 2)

        gaps = read_gaps(_receive_log(exchange), _gap_limit)

        assert len(gaps) == 1
        assert gaps[0].deadline == _after(_gap_seconds)
        assert not gaps[0].is_reported

    def test_grace_from_environment(self, parties:'TestParties', monkeypatch:'MonkeyPatch') -> 'None':
        monkeypatch.setenv(Env_Gap_Grace_Seconds, str(_custom_grace_seconds))

        exchange = _ordered(parties)

        _ = _hold(exchange, 1)

        gaps = read_gaps(_receive_log(exchange), _gap_limit)

        assert gaps[0].deadline == _after(_retries * _retry_interval_seconds + _custom_grace_seconds)

    def test_one_error_per_gap(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        _ = _hold(exchange, 1)
        _ = _hold(exchange, 3)

        receive_log = _receive_log(exchange)
        conversation = _conversation(exchange)

        # Before the deadline nothing is reported ..
        assert not report_timed_out(receive_log, conversation, _after(_gap_seconds - 1))

        # .. at the deadline the timeout is reported ..
        assert report_timed_out(receive_log, conversation, _after(_gap_seconds))

        # .. and never again for the same gap.
        assert not report_timed_out(receive_log, conversation, _after(_gap_seconds + 1))

        events = _events(exchange, AuditEvent.Sequence_Gap_Timed_Out)

        assert len(events) == 1
        assert events[0]['outcome'] == AuditOutcome.Error
        assert events[0]['data']['expected_sequence_number'] == 0
        assert events[0]['data']['first_held_sequence_number'] == 1
        assert events[0]['data']['held_count'] == 2

        gaps = read_gaps(receive_log, _gap_limit)
        assert gaps[0].is_reported

    def test_new_gap_is_reported_again(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        _ = _hold(exchange, 1)

        receive_log = _receive_log(exchange)
        conversation = _conversation(exchange)

        assert report_timed_out(receive_log, conversation, _after(_gap_seconds))

        # Message 0 closes the gap, and message 3 opens another one, whose deadline counts from its own hold.
        _ = deliver(exchange, _numbered(exchange, 0))

        exchange.clock.advance(_gap_seconds)
        _ = _hold(exchange, 3)

        assert not report_timed_out(receive_log, conversation, _after(_gap_seconds * 2 - 1))
        assert report_timed_out(receive_log, conversation, _after(_gap_seconds * 2))

        assert len(_events(exchange, AuditEvent.Sequence_Gap_Timed_Out)) == 2

# ################################################################################################################################
# ################################################################################################################################

class TestRelease:
    """ Releasing a gap delivers the held messages up to the next missing number.
    """

    def test_release(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        _ = _hold(exchange, 2)
        _ = _hold(exchange, 3)
        _ = _hold(exchange, 5)

        receive_log = _receive_log(exchange)
        conversation = _conversation(exchange)

        released = release_gap(receive_log, conversation)

        released_ids:'strlist' = []
        for message in released:
            released_ids.append(message.identity.message_id)

        assert len(released_ids) == 2
        assert _payload_data(exchange) == [b'<Order><Id>2</Id></Order>', b'<Order><Id>3</Id></Order>']

        events = _events(exchange, AuditEvent.Sequence_Gap_Released)

        assert len(events) == 1
        assert events[0]['data']['expected_sequence_number'] == 0
        assert events[0]['data']['first_held_sequence_number'] == 2
        assert events[0]['data']['held_count'] == 3

        # Message 5 waits for message 4, which the conversation expects now ..
        assert _held_count(exchange) == 1

        result = deliver(exchange, _numbered(exchange, 4))

        # .. and receiving it delivers both.
        assert len(result.deliveries) == 2
        assert _held_count(exchange) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestDiscard:
    """ Discarding a conversation deletes its held messages and starts it over.
    """

    def test_discard(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        _ = _hold(exchange, 1)
        _ = _hold(exchange, 2)

        receive_log = _receive_log(exchange)
        conversation = _conversation(exchange)

        assert discard_conversation(receive_log, conversation) == 2

        assert _held_count(exchange) == 0
        assert read_gaps(receive_log, _gap_limit) == []
        assert len(_events(exchange, AuditEvent.Conversation_Discarded)) == 1

        # The conversation starts over from zero.
        result = deliver(exchange, _numbered(exchange, 0))
        assert len(result.deliveries) == 1

# ################################################################################################################################
# ################################################################################################################################

class TestRetention:
    """ Retention deletes the held messages older than the retention of the source, with the events of their receipt.
    """

    def test_retention(self, parties:'TestParties') -> 'None':
        exchange = _ordered(parties)

        retention = timedelta(days=get_retention_days(AuditSource.EbMS2))

        old = _hold(exchange, 1)

        exchange.clock.advance(_retention_step_seconds * 2)
        recent = _hold(exchange, 2)

        receive_log = _receive_log(exchange)
        engine = receive_log.writer.engine

        # The cutoff falls between the two moments the messages were held ..
        now = _after(_retention_step_seconds) + retention
        result = receive_log.writer.run_retention(now)

        assert result.held == 1
        assert _held_count(exchange) == 1

        # .. and once the events of both are past their retention, those of the message still held are kept.
        events_now = utcnow() + retention + timedelta(days=1)

        with engine.begin() as connection:
            _ = delete_old_events(connection, AuditSource.EbMS2, events_now, _event_limit)

        assert _message_events(exchange, old.message_id) == []
        assert _message_events(exchange, recent.message_id) == [AuditEvent.Message_Received, AuditEvent.Message_Held]

# ################################################################################################################################
# ################################################################################################################################
