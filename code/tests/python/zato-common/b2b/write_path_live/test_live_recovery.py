# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from datetime import timedelta

# Zato
from live_db import count_rows, full_scans, gather_statistics, new_event
from zato.common.audit_log.api import AuditEvent, AuditLog, event_table
from zato.common.audit_log.common import get_retention_days
from zato.common.b2b.common import commit_group
from zato.common.b2b.common.business_log import BusinessLog, expired
from zato.common.b2b.common.business_state import BusinessState
from zato.common.b2b.common.clock import ManualClock
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.outcome import SignalKind
from zato.common.b2b.common.recovery import attrs_statement, body_statement, events_statement, open_statement
from zato.common.b2b.common.schema import message_table, open_table, OpenKind
from zato.common.b2b.common.send_log import SendLog
from zato.common.b2b.common.store import MessageStore
from zato.common.test.b2b_write_path import Endpoint, new_business_message, new_identity, new_sent_message, \
    new_stored_message, receipt_outcome, Server, Signal_Body, Source, Start_Time, StatementRecorder, Wire_Body
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from live_db import LiveDB
    from pytest import MonkeyPatch
    from zato.common.b2b.common.business_state import BusinessOutcome
    from zato.common.b2b.common.commit_retention import RetentionResult
    from zato.common.typing_ import strlist
    BusinessOutcome = BusinessOutcome
    datetime = datetime
    LiveDB = LiveDB
    MonkeyPatch = MonkeyPatch
    RetentionResult = RetentionResult
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# How long the writer of a test waits between two commits, in milliseconds.
_interval_ms = 10

# A row limit that no transaction of a test reaches.
_max_rows = 1_000_000

# How many expiries one check ends at most.
_expiry_limit = 100

# The messages the query plan test stores, how many of them are open, and those of another server.
_planned_messages = 1000
_planned_open = 20
_other_server_open = 480
_other_server = 'b2b-other-server'

# The event types the recovery reads.
_recovered_types = (AuditEvent.Message_Sent, AuditEvent.Message_Completed)

# The row limit of the retention test, and how many expired messages it stores.
_retention_rows = 5
_expired_messages = 12

# How long the retention test waits for retention between commits, in seconds.
_retention_wait_seconds = 30
_poll_seconds = 0.05

# ################################################################################################################################
# ################################################################################################################################

def _message_ids(outcomes:'list[BusinessOutcome]') -> 'strlist':
    out:'strlist' = []

    for outcome in outcomes:
        out.append(outcome.message_id)

    return out

# ################################################################################################################################

def _after(seconds:'int') -> 'datetime':
    out = Start_Time + timedelta(seconds=seconds)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRecovery:
    """ The open exchanges and the awaiting transactions are rebuilt and proceed as before.
    """

    def test_recover(self, database:'LiveDB', writer:'GroupCommitWriter') -> 'None':
        business_log = BusinessLog(Source, Server, writer)
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer, business_log)

        request = new_sent_message('request-1')
        business = new_business_message('request-1', receipt_seconds=30, response_seconds=60)

        send_log.record_first_attempt(request, business)
        _ = send_log.wire_body('request-1')

        notification = new_sent_message('notification-1')
        send_log.record_first_attempt(notification)
        _ = send_log.wire_body('notification-1')

        ended = new_sent_message('ended-1')
        send_log.record_first_attempt(ended)
        send_log.record_completion(ended, receipt_outcome())

        writer.stop()

        # Another process starts on the same database.
        new_writer = GroupCommitWriter(database.engine, interval_ms=_interval_ms)
        new_business_log = BusinessLog(Source, Server, new_writer)
        new_send_log = SendLog(Source, Server, ManualClock(_after(40)), new_writer, new_business_log)

        assert new_send_log.recover() == 2
        assert new_business_log.recover() == 1

        outstanding:'strlist' = []

        for sent in new_send_log.outstanding(_expiry_limit):
            outstanding.append(sent.message_id)

        assert outstanding == ['request-1', 'notification-1']

        recovered = new_send_log.get('request-1')

        assert recovered.endpoint == Endpoint
        assert recovered.policy.retries == 3
        assert recovered.retry_state.attempt_count == 1

        # A resend ..
        assert new_send_log.wire_body('request-1') == Wire_Body

        new_send_log.record_resend(recovered)
        assert recovered.retry_state.attempt_count == 2

        # .. a signal ..
        new_send_log.record_signal(recovered, {}, Signal_Body, SignalKind.Receipt, '', '')
        new_send_log.record_completion(recovered, receipt_outcome())

        assert not new_send_log.is_open('request-1')
        assert new_send_log.is_open('notification-1')

        awaiting = new_business_log.read('request-1')
        assert awaiting is not None

        new_business_log.record_reply(awaiting, BusinessState.Receipted, 'receipt-1', [])

        # .. and an expiry.
        outcomes = expired(new_business_log, _after(61), _expiry_limit)

        assert _message_ids(outcomes) == ['request-1']
        assert outcomes[0].state == BusinessState.Timed_Out

        new_writer.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestResendRead:
    """ A resend reads the bytes of the first delivery with one select.
    """

    def test_resend(self, database:'LiveDB', writer:'GroupCommitWriter') -> 'None':
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer)

        send_log.record_first_attempt(new_sent_message('message-1'))
        assert send_log.wire_body('message-1') == Wire_Body

        recorder = StatementRecorder(database.engine)

        assert send_log.wire_body('message-1') == Wire_Body

        reads = recorder.reads()

        assert len(reads) == 1
        assert reads[0].table == 'event_body'

        recorder.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestExpiryAfterRecovery:
    """ Deadlines that passed while the process was stopped expire after recovery, and later ones at their times.
    """

    def test_expiry(self, database:'LiveDB', writer:'GroupCommitWriter') -> 'None':
        business_log = BusinessLog(Source, Server, writer)

        business_log.record_sent(new_business_message('past-1', response_seconds=10))
        business_log.record_sent(new_business_message('future-1', response_seconds=1000))

        writer.stop()

        new_writer = GroupCommitWriter(database.engine, interval_ms=_interval_ms)
        new_business_log = BusinessLog(Source, Server, new_writer)

        assert new_business_log.recover() == 2

        assert _message_ids(expired(new_business_log, _after(100), _expiry_limit)) == ['past-1']
        assert _message_ids(expired(new_business_log, _after(500), _expiry_limit)) == []
        assert _message_ids(expired(new_business_log, _after(1001), _expiry_limit)) == ['future-1']

        stored = new_business_log.read('past-1')

        assert stored is not None
        assert stored.state == BusinessState.Timed_Out

        new_writer.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestRecoveryQueryPlans:
    """ The recovery queries use their indexes and read no table in full.
    """

    def test_plans(self, database:'LiveDB') -> 'None':
        writer = GroupCommitWriter(database.engine, interval_ms=0, max_rows=_max_rows, is_started=False)

        audit_log = AuditLog(Server, flush_max_size=1)
        other_audit_log = AuditLog(_other_server, flush_max_size=1)

        open_ids:'strlist' = []

        for idx in range(_planned_messages):
            message_id = f'message-{idx}'

            sent = new_event(audit_log, message_id)
            _ = writer.enqueue(sent, 3)

            if idx < _planned_open:
                sent.opens.append(OpenKind.Exchange)
                open_ids.append(message_id)
            else:
                _ = writer.enqueue(new_event(audit_log, message_id, AuditEvent.Message_Completed), 3)

        for idx in range(_other_server_open):
            other = new_event(other_audit_log, f'other-{idx}')
            other.opens.append(OpenKind.Exchange)
            _ = writer.enqueue(other, 4)

        assert writer.commit_due()

        gather_statistics(database)

        with database.engine.connect() as connection:
            event_ids = list(connection.execute(events_statement(Source, Server, open_ids, _recovered_types)).scalars())

        statements = {
            'open': open_statement(OpenKind.Exchange, Source, Server),
            'events': events_statement(Source, Server, open_ids, _recovered_types),
            'attrs': attrs_statement(event_ids),
            'body': body_statement(event_ids[0]),
        }

        scans:'dict[str, strlist]' = {}

        for name, statement in statements.items():
            scans[name] = full_scans(database, statement)

        assert len(event_ids) == _planned_open
        assert scans == {'open': [], 'events': [], 'attrs': [], 'body': []}

# ################################################################################################################################
# ################################################################################################################################

class TestRetention:
    """ Retention deletes in runs no larger than the row limit and keeps everything that is open.
    """

    def _run_until_done(self, writer:'GroupCommitWriter', now:'datetime') -> 'list[RetentionResult]':
        out:'list[RetentionResult]' = []

        while True:
            result = writer.run_retention(now)
            out.append(result)

            if not (result.messages or result.events):
                break

        return out

    def test_runs(self, database:'LiveDB') -> 'None':
        engine = database.engine

        writer = GroupCommitWriter(engine, interval_ms=_interval_ms, max_rows=_retention_rows)
        store = MessageStore(writer)

        business_log = BusinessLog(Source, Server, writer)
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer, business_log)

        for idx in range(_expired_messages):
            _ = store.claim(new_identity(f'expired-{idx}'), new_stored_message())

        _ = store.claim(new_identity('current-1'), new_stored_message(utcnow()))

        for idx in range(4):
            ended = new_sent_message(f'ended-{idx}')
            send_log.record_first_attempt(ended)
            send_log.record_completion(ended, receipt_outcome())

        send_log.record_first_attempt(new_sent_message('open-1'))
        business_log.record_sent(new_business_message('awaiting-1', response_seconds=60))

        # The events are recent, so only the expired message records go ..
        first = self._run_until_done(writer, utcnow())

        first_messages:'list[int]' = []

        for result in first:
            first_messages.append(result.messages)
            assert result.events == 0

        assert first_messages == [5, 5, 2, 0]
        assert count_rows(engine, message_table) == 1

        # .. and once the events are past their retention, everything that is not open goes too.
        retention_days = get_retention_days(Source)
        later = utcnow() + timedelta(days=retention_days + 1)

        second = self._run_until_done(writer, later)

        second_events:'list[int]' = []

        for result in second:
            second_events.append(result.events)
            assert result.events <= _retention_rows

        assert second_events == [5, 3, 0]
        assert count_rows(engine, message_table) == 0
        assert count_rows(engine, open_table) == 2

        kept:'strlist' = []

        with engine.connect() as connection:
            for row in connection.execute(event_table.select().order_by(event_table.c.id)):
                kept.append(row.msg_id)

        assert kept == ['open-1', 'awaiting-1']

        writer.stop()

    def test_between_commits(self, database:'LiveDB', monkeypatch:'MonkeyPatch') -> 'None':
        monkeypatch.setattr(commit_group, 'Retention_Interval_Seconds', 0)

        engine = database.engine
        writer = GroupCommitWriter(engine, interval_ms=_interval_ms, max_rows=_retention_rows)
        store = MessageStore(writer)

        results:'list[RetentionResult]' = []

        def run_retention(now:'datetime') -> 'RetentionResult':
            result = GroupCommitWriter.run_retention(writer, now)
            results.append(result)
            return result

        monkeypatch.setattr(writer, 'run_retention', run_retention)

        for idx in range(_expired_messages):
            _ = store.claim(new_identity(f'expired-{idx}'), new_stored_message())

        deadline = time.monotonic() + _retention_wait_seconds

        while count_rows(engine, message_table) and time.monotonic() < deadline:
            time.sleep(_poll_seconds)

        writer.stop()

        deleted = 0

        for result in results:
            assert result.messages <= _retention_rows
            deleted += result.messages

        assert count_rows(engine, message_table) == 0
        assert deleted == _expired_messages

# ################################################################################################################################
# ################################################################################################################################
