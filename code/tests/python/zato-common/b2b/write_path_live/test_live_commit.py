# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import time
from datetime import timedelta
from signal import SIGKILL
from threading import Thread

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import inspect, select

# Zato
from live_db import count_rows, Line_Claimed, Line_Committing, Line_Ready, new_audit_log, new_event, start_child, \
    Type_MySQL, Type_PostgreSQL, Type_SQLite, wait_for_line
from zato.common.audit_log.api import AuditEvent, event_body_table, event_table
from zato.common.audit_log.attachment import build_attachment
from zato.common.audit_log.common import B2BAttr
from zato.common.b2b.common.clock import ManualClock
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.commit_sql import ClaimWrite, EventWrite, StatusWrite
from zato.common.b2b.common.schema import b2b_event_table, message_table, open_table, OpenKind
from zato.common.b2b.common.send_log import SendLog
from zato.common.b2b.common.store import MessageStore
from zato.common.b2b.ebms2.common import SyncReplyMode
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import deliver, new_exchange, send, use_store
from zato.common.test.b2b_write_path import CommitGate, CommitRefused, FailingCommit, FakeMonotonic, new_identity, \
    new_sent_message, new_stored_message, Server, Source, Start_Time, StatementRecorder, Wire_Body

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from live_db import LiveDB
    from zato.common.b2b.common.commit_ticket import CommitTicket
    from zato.common.b2b.ebms2.inbound import InboundResult
    from zato.common.test.b2b_cpa import AgreementSettings
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import anylist, strlist
    AgreementSettings = AgreementSettings
    anylist = anylist
    CommitTicket = CommitTicket
    InboundResult = InboundResult
    LiveDB = LiveDB
    strlist = strlist
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# How long a test waits for a thread or a commit, in seconds.
_wait_seconds = 30

# How long a test confirms that a caller is still waiting, in seconds.
_still_waiting_seconds = 0.2

# A row limit that no transaction of a test reaches.
_max_rows = 1_000_000

# How many events the parent and the child of the identifier test commit.
_parent_events = 1000
_child_batches = 40
_child_batch_size = 50

# How many identities two processes claim at the same time, and how far ahead their common start is, in seconds.
_shared_claims = 200
_shared_start_delay = 5

# The transaction at the row limit - events, each with its attributes and its attachment.
_full_events = 250
_full_attachment_size = 200 * 1024

# The B2B tables the audit log database holds.
_b2b_tables = ('b2b_message', 'b2b_sequence', 'b2b_held_message', 'b2b_open')

# The tables each database selects from to learn the identifiers of the rows a transaction wrote.
_identifier_selects = {
    Type_SQLite: ['event'],
    Type_MySQL: ['b2b_message', 'event'],
    Type_PostgreSQL: [],
}

# The statement that inserts the rows whose identifiers are not read back, for each database.
_bulk_insert_verbs = {
    Type_SQLite: 'INSERT',
    Type_MySQL: 'INSERT',
    Type_PostgreSQL: 'COPY',
}

# ################################################################################################################################
# ################################################################################################################################

def _settings(parties:'TestParties') -> 'AgreementSettings':
    out = new_settings(parties, Start_Time)
    out.business_channel.sync_reply_mode = SyncReplyMode.MSH_Signals_Only

    return out

# ################################################################################################################################

def _claim(message_id:'str') -> 'ClaimWrite':
    out = ClaimWrite()
    out.identity = new_identity(message_id)
    out.message = new_stored_message()

    return out

# ################################################################################################################################

def _status(message_id:'str') -> 'StatusWrite':
    out = StatusWrite()
    out.identity = new_identity(message_id)
    out.status = 'Processed'

    return out

# ################################################################################################################################

def _opening(event:'EventWrite') -> 'EventWrite':
    event.opens.append(OpenKind.Exchange)
    return event

# ################################################################################################################################

def _closing(event:'EventWrite') -> 'EventWrite':
    event.closes.append(OpenKind.Exchange)
    return event

# ################################################################################################################################

def _inline_writer(database:'LiveDB') -> 'GroupCommitWriter':
    """ A writer with no thread, whose pending writes are committed when the test says so.
    """
    out = GroupCommitWriter(database.engine, interval_ms=0, max_rows=_max_rows, is_started=False)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCommitBeforeConfirmation:
    """ No acknowledgment and no delivery precede the commit that records them.
    """

    def test_receive(self, database:'LiveDB', writer:'GroupCommitWriter', parties:'TestParties') -> 'None':
        exchange = new_exchange(parties, _settings(parties))
        use_store(exchange.receiver, MessageStore(writer))
        outbound = send(exchange)

        gate = CommitGate(database.engine)
        results:'list[InboundResult]' = []

        def receive() -> 'None':
            result = deliver(exchange, outbound)
            results.append(result)

        thread = Thread(target=receive)
        thread.start()

        assert gate.wait_for_commit(_wait_seconds)
        thread.join(_still_waiting_seconds)

        assert thread.is_alive()
        assert results == []

        gate.open()
        thread.join(_wait_seconds)

        assert results[0].outcome.delivered
        assert b'Acknowledgment' in results[0].response.body

        gate.stop()

    def test_send(self, database:'LiveDB', writer:'GroupCommitWriter') -> 'None':
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer)

        gate = CommitGate(database.engine)
        posts:'list[bytes]' = []

        def post() -> 'None':
            send_log.record_first_attempt(new_sent_message('message-1'))
            body = send_log.wire_body('message-1')
            posts.append(body)

        thread = Thread(target=post)
        thread.start()

        assert gate.wait_for_commit(_wait_seconds)
        thread.join(_still_waiting_seconds)

        assert thread.is_alive()
        assert posts == []
        assert not send_log.is_open('message-1')

        gate.open()
        thread.join(_wait_seconds)

        assert posts == [Wire_Body]

        gate.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestDuplicateClaims:
    """ Two copies of one message produce one claim and one delivery.
    """

    def test_one_transaction(self, database:'LiveDB') -> 'None':
        writer = _inline_writer(database)

        first = writer.enqueue(_claim('message-1'), 1)
        second = writer.enqueue(_claim('message-1'), 1)

        assert writer.commit_due()

        assert first.wait() is True
        assert second.wait() is False
        assert count_rows(database.engine, message_table) == 1

    def test_two_transactions(self, database:'LiveDB', writer:'GroupCommitWriter') -> 'None':
        store = MessageStore(writer)

        assert store.claim(new_identity('message-1'), new_stored_message())
        assert not store.claim(new_identity('message-1'), new_stored_message())

    def test_one_delivery(self, database:'LiveDB', writer:'GroupCommitWriter', parties:'TestParties') -> 'None':
        exchange = new_exchange(parties, _settings(parties))
        use_store(exchange.receiver, MessageStore(writer))
        outbound = send(exchange)

        first = deliver(exchange, outbound)
        second = deliver(exchange, outbound)

        assert first.outcome.delivered
        assert second.outcome.duplicate
        assert not second.outcome.delivered

# ################################################################################################################################
# ################################################################################################################################

class TestStatementCounts:
    """ A transaction holds one statement per table, the selects of the identifiers included, and one commit.
    """

    def test_counts(self, database:'LiveDB') -> 'None':
        clock = FakeMonotonic()
        writer = GroupCommitWriter(database.engine, interval_ms=100, max_rows=_max_rows, clock=clock, is_started=False)
        audit_log = new_audit_log()

        for idx in range(3):
            _ = writer.enqueue(_claim(f'message-{idx}'), 1)
            _ = writer.enqueue(_opening(new_event(audit_log, f'message-{idx}')), 4)

        clock.advance(1)
        assert writer.commit_due()

        recorder = StatementRecorder(database.engine)

        for idx in range(3, 6):
            _ = writer.enqueue(_claim(f'message-{idx}'), 1)

        for idx in range(3):
            _ = writer.enqueue(_status(f'message-{idx}'), 1)
            _ = writer.enqueue(_closing(new_event(audit_log, f'message-{idx}')), 4)
            _ = writer.enqueue(_opening(new_event(audit_log, f'message-{idx}')), 4)

        clock.advance(1)
        assert writer.commit_due()

        bulk_verb = _bulk_insert_verbs[database.name]

        assert recorder.writes() == [
            'INSERT b2b_message',
            'UPDATE b2b_message',
            'INSERT event',
            f'{bulk_verb} b2b_event',
            f'{bulk_verb} event_body',
            'DELETE b2b_open',
            f'{bulk_verb} b2b_open',
        ]

        selected:'strlist' = []

        for statement in recorder.selects():
            selected.append(statement.table)

        assert selected == _identifier_selects[database.name]
        assert recorder.commits == 1

        recorder.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestOneTransaction:
    """ The B2B tables are in the audit log database, and one transaction holds the claims and the events.
    """

    def test_tables(self, database:'LiveDB', writer:'GroupCommitWriter') -> 'None':
        table_names = inspect(database.engine).get_table_names()

        for table_name in _b2b_tables:
            assert table_name in table_names

        assert 'event' in table_names

    def test_rollback(self, database:'LiveDB') -> 'None':
        writer = _inline_writer(database)
        audit_log = new_audit_log()
        failing = FailingCommit(database.engine)

        claim = writer.enqueue(_claim('message-1'), 1)
        event = writer.enqueue(_opening(new_event(audit_log, 'message-1')), 4)

        assert writer.commit_due()

        for ticket in (claim, event):
            with pytest.raises(CommitRefused):
                _ = ticket.wait()

        failing.stop()

        engine = database.engine

        assert count_rows(engine, message_table) == 0
        assert count_rows(engine, event_table) == 0
        assert count_rows(engine, b2b_event_table) == 0
        assert count_rows(engine, event_body_table) == 0
        assert count_rows(engine, open_table) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestEventIdentifiers:
    """ Each attribute and body is stored against its own event while another process commits into the same tables.
    """

    def test_identifiers(self, database:'LiveDB') -> 'None':
        child = start_child(database, 'write', str(_child_batches), str(_child_batch_size))
        wait_for_line(child, Line_Ready)

        writer = _inline_writer(database)
        audit_log = new_audit_log()

        tickets:'list[CommitTicket]' = []

        for idx in range(_parent_events):
            ticket = writer.enqueue(new_event(audit_log, f'parent-{idx}'), 3)
            tickets.append(ticket)

        assert writer.commit_due()

        _, stderr = child.communicate(timeout=_wait_seconds * 10)
        assert child.returncode == 0, stderr

        engine = database.engine
        message_ids:'dict[int, str]' = {}

        with engine.connect() as connection:

            for event_id, message_id in connection.execute(select(event_table.c.id, event_table.c.msg_id)):
                message_ids[event_id] = message_id

            attrs = connection.execute(select(b2b_event_table.c.event_id, b2b_event_table.c.service)).all()
            bodies = connection.execute(select(event_body_table.c.event_id, event_body_table.c.data)).all()

        child_events = _child_batches * _child_batch_size
        all_events = _parent_events + child_events

        assert len(message_ids) == all_events
        assert len(attrs) == all_events
        assert len(bodies) == all_events

        for idx, ticket in enumerate(tickets):
            event_id = ticket.wait()
            assert message_ids[event_id] == f'parent-{idx}'

        for event_id, value in attrs:
            assert value == message_ids[event_id]

        for event_id, data in bodies:
            assert data == message_ids[event_id]

# ################################################################################################################################
# ################################################################################################################################

class TestClaimsFromTwoProcesses:
    """ Two processes claim the same messages at the same time, and each message is claimed once.
    """

    def test_claims(self, database:'LiveDB') -> 'None':
        start_at = time.time() + _shared_start_delay

        first = start_child(database, 'claim', str(start_at), str(_shared_claims))
        second = start_child(database, 'claim', str(start_at), str(_shared_claims))

        claimed:'list[set[str]]' = []

        for child in (first, second):
            stdout, stderr = child.communicate(timeout=_wait_seconds * 10)
            assert child.returncode == 0, stderr

            lines = stdout.strip().splitlines()
            report = json.loads(lines[-1])
            claimed.append(set(report['claimed']))

        first_claimed, second_claimed = claimed

        expected:'set[str]' = set()

        for idx in range(_shared_claims):
            expected.add(f'shared-{idx}')

        assert not first_claimed & second_claimed
        assert first_claimed | second_claimed == expected
        assert count_rows(database.engine, message_table) == _shared_claims

# ################################################################################################################################
# ################################################################################################################################

class TestFullTransaction:
    """ A transaction at the row limit, with the largest bodies, commits on each database.
    """

    def test_full(self, database:'LiveDB') -> 'None':
        writer = _inline_writer(database)
        audit_log = new_audit_log()

        content = os.urandom(_full_attachment_size)
        attachment = build_attachment('document.bin', 'application/octet-stream', content)

        row_count = 0

        for idx in range(_full_events):
            write = EventWrite()
            write.pending = audit_log.new_pending_event(Source, AuditEvent.Message_Sent, 'b2b-agreement',
                msg_id=f'message-{idx}', data='{}', attrs={B2BAttr.Attempt: idx, B2BAttr.Action: f'value-{idx}'},
                attachments=[attachment])

            row_count += write.row_count
            _ = writer.enqueue(write, write.row_count)

        assert row_count == 1000
        assert writer.commit_due()

        engine = database.engine

        assert count_rows(engine, event_table) == _full_events
        assert count_rows(engine, b2b_event_table) == _full_events
        assert count_rows(engine, event_body_table) == _full_events

# ################################################################################################################################
# ################################################################################################################################

class TestProcessStopped:
    """ A process stopped before the commit of a claim leaves none, and one stopped after it leaves the claim.
    """

    def _resend(self, database:'LiveDB', message_id:'str') -> 'tuple[bool, bool]':
        """ Claims a message as the partner resends it, twice, and says whether each copy was claimed.
        """
        writer = GroupCommitWriter(database.engine, interval_ms=10)
        store = MessageStore(writer)
        received_at = Start_Time + timedelta(seconds=10)

        first = store.claim(new_identity(message_id), new_stored_message(received_at))
        second = store.claim(new_identity(message_id), new_stored_message(received_at))

        writer.stop()

        return first, second

    def test_before_commit(self, database:'LiveDB') -> 'None':
        child = start_child(database, 'kill-before', 'message-1')
        wait_for_line(child, Line_Committing)

        child.send_signal(SIGKILL)
        _ = child.wait(_wait_seconds)

        assert count_rows(database.engine, message_table) == 0

        # The resend is delivered once.
        assert self._resend(database, 'message-1') == (True, False)

    def test_after_commit(self, database:'LiveDB') -> 'None':
        child = start_child(database, 'kill-after', 'message-1')
        wait_for_line(child, Line_Claimed)

        child.send_signal(SIGKILL)
        _ = child.wait(_wait_seconds)

        assert count_rows(database.engine, message_table) == 1

        # The resend is a duplicate.
        assert self._resend(database, 'message-1') == (False, False)

# ################################################################################################################################
# ################################################################################################################################
