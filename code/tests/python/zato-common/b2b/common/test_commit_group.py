# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import os
import subprocess
import sys
from threading import Thread

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.audit_log.api import AuditEvent, AuditLog
from zato.common.b2b.common.commit_group import Default_Commit_Interval_Ms, Default_Commit_Max_Rows, \
    Env_Commit_Interval_Ms, Env_Commit_Max_Rows, GroupCommitWriter
from zato.common.b2b.common.commit_sql import ClaimWrite, EventWrite, StatusWrite
from zato.common.b2b.common.schema import message_table, OpenKind
from zato.common.b2b.common.store import MessageStore
from zato.common.test.b2b_write_path import CommitGate, CommitRefused, FailingCommit, FakeMonotonic, new_identity, \
    new_memory_engine, new_stored_message, Server, Source, StatementRecorder

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from pytest import MonkeyPatch
    from sqlalchemy.engine import Engine
    from zato.common.b2b.common.commit_group import CommitTicket
    CommitTicket = CommitTicket
    Engine = Engine
    MonkeyPatch = MonkeyPatch

# ################################################################################################################################
# ################################################################################################################################

_interval_ms = 100
_interval_seconds = _interval_ms / 1000

# Just under the interval, in seconds.
_almost_interval = 0.099

_max_rows = 5

# How long a test waits for a caller thread to finish.
_join_seconds = 10

# The program that runs a held-back commit under gevent in a process of its own.
_gevent_program = os.path.join(os.path.dirname(__file__), 'gevent_commit.py')

# ################################################################################################################################
# ################################################################################################################################

def _claim(message_id:'str') -> 'ClaimWrite':
    out = ClaimWrite()
    out.identity = new_identity(message_id)
    out.message = new_stored_message()

    return out

# ################################################################################################################################

def _status(message_id:'str', status:'str') -> 'StatusWrite':
    out = StatusWrite()
    out.identity = new_identity(message_id)
    out.status = status

    return out

# ################################################################################################################################

def _event(audit_log:'AuditLog', message_id:'str', opens:'bool'=False, closes:'bool'=False) -> 'EventWrite':
    out = EventWrite()
    out.pending = audit_log.new_pending_event(Source, AuditEvent.Message_Sent, 'b2b-agreement', msg_id=message_id,
        data='{}', attrs={'b2b_marker': message_id}, bodies={'request': message_id})

    if closes:
        out.closes.append(OpenKind.Exchange)

    if opens:
        out.opens.append(OpenKind.Exchange)

    return out

# ################################################################################################################################

def _writer(engine:'Engine', clock:'FakeMonotonic') -> 'GroupCommitWriter':
    out = GroupCommitWriter(engine, interval_ms=_interval_ms, max_rows=_max_rows, clock=clock, is_started=False)
    return out

# ################################################################################################################################

def _count_messages(engine:'Engine') -> 'int':
    with engine.connect() as connection:
        out = connection.execute(select(func.count()).select_from(message_table)).scalar_one()

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestCommitIntervalAndRowLimit:
    """ The pending writes are committed when the interval elapses, or at once when their rows reach the limit.
    """

    def test_interval(self) -> 'None':
        clock = FakeMonotonic()
        writer = _writer(new_memory_engine(), clock)

        ticket = writer.enqueue(_claim('message-1'), 1)

        assert not writer.commit_due()

        clock.advance(_almost_interval)
        assert not writer.commit_due()
        assert not ticket.is_done

        clock.advance(_interval_seconds - _almost_interval)
        assert writer.commit_due()
        assert ticket.is_done
        assert ticket.wait() is True

    def test_row_limit(self) -> 'None':
        clock = FakeMonotonic()
        writer = _writer(new_memory_engine(), clock)

        tickets:'list[CommitTicket]' = []

        for idx in range(_max_rows - 1):
            ticket = writer.enqueue(_claim(f'message-{idx}'), 1)
            tickets.append(ticket)

        assert not writer.commit_due()

        # The last row reaches the limit, and the clock has not moved at all.
        ticket = writer.enqueue(_claim('message-last'), 1)
        tickets.append(ticket)

        assert writer.commit_due()

        for ticket in tickets:
            assert ticket.wait() is True

    def test_environment(self, monkeypatch:'MonkeyPatch') -> 'None':
        engine = new_memory_engine()

        monkeypatch.setenv(Env_Commit_Interval_Ms, '250')
        monkeypatch.setenv(Env_Commit_Max_Rows, '7')

        writer = GroupCommitWriter(engine, is_started=False)

        assert writer.interval_ms == 250
        assert writer.max_rows == 7

    def test_defaults(self, monkeypatch:'MonkeyPatch') -> 'None':
        engine = new_memory_engine()

        monkeypatch.delenv(Env_Commit_Interval_Ms, raising=False)
        monkeypatch.delenv(Env_Commit_Max_Rows, raising=False)

        writer = GroupCommitWriter(engine, is_started=False)

        assert writer.interval_ms == Default_Commit_Interval_Ms
        assert writer.max_rows == Default_Commit_Max_Rows

# ################################################################################################################################
# ################################################################################################################################

class TestCallersReleased:
    """ Each caller is released by the commit of its own transaction, and a failed commit releases all with its error.
    """

    def test_two_transactions(self) -> 'None':
        clock = FakeMonotonic()
        writer = _writer(new_memory_engine(), clock)

        first = writer.enqueue(_claim('message-1'), 1)

        clock.advance(_interval_seconds)
        second = writer.enqueue(_claim('message-2'), 1)

        assert writer.commit_due()
        assert first.is_done
        assert second.is_done

        third = writer.enqueue(_claim('message-3'), 1)
        assert not third.is_done

        clock.advance(_interval_seconds)
        assert writer.commit_due()
        assert third.is_done

    def test_caller_waits_for_its_commit(self) -> 'None':
        engine = new_memory_engine()
        writer = GroupCommitWriter(engine, interval_ms=0)
        store = MessageStore(writer)
        gate = CommitGate(engine)

        results:'list[bool]' = []

        def claim() -> 'None':
            is_claimed = store.claim(new_identity('message-1'), new_stored_message())
            results.append(is_claimed)

        thread = Thread(target=claim)
        thread.start()

        # The commit started and is held back, and the caller is still waiting for it.
        assert gate.is_waiting.wait(_join_seconds)
        thread.join(0.2)
        assert thread.is_alive()
        assert results == []

        gate.open()
        thread.join(_join_seconds)

        assert results == [True]

        gate.stop()
        writer.stop()

    def test_failed_commit(self) -> 'None':
        clock = FakeMonotonic()
        engine = new_memory_engine()
        writer = _writer(engine, clock)
        failing = FailingCommit(engine)

        tickets:'list[CommitTicket]' = []

        for idx in range(3):
            ticket = writer.enqueue(_claim(f'message-{idx}'), 1)
            tickets.append(ticket)

        clock.advance(_interval_seconds)
        assert writer.commit_due()

        for ticket in tickets:
            with pytest.raises(CommitRefused):
                _ = ticket.wait()

        failing.stop()

        # Nothing of the transaction is left behind.
        assert _count_messages(engine) == 0

# ################################################################################################################################
# ################################################################################################################################

class TestOneStatementPerTable:
    """ A transaction holds one statement for each table, in the order of the references between the tables.
    """

    def test_statements(self) -> 'None':
        clock = FakeMonotonic()
        engine = new_memory_engine()
        writer = GroupCommitWriter(engine, interval_ms=_interval_ms, max_rows=1000, clock=clock, is_started=False)
        audit_log = AuditLog(Server, flush_max_size=1)

        # The first transaction claims the messages and opens their exchanges ..
        for idx in range(3):
            _ = writer.enqueue(_claim(f'message-{idx}'), 1)
            _ = writer.enqueue(_event(audit_log, f'message-{idx}', opens=True), 4)

        clock.advance(_interval_seconds)
        assert writer.commit_due()

        recorder = StatementRecorder(engine)

        # .. and the second one holds every kind of write.
        for idx in range(3, 6):
            _ = writer.enqueue(_claim(f'message-{idx}'), 1)

        for idx in range(3):
            _ = writer.enqueue(_status(f'message-{idx}', 'Processed'), 1)
            _ = writer.enqueue(_event(audit_log, f'message-{idx}', closes=True), 4)
            _ = writer.enqueue(_event(audit_log, f'message-{idx}', opens=True), 4)

        clock.advance(_interval_seconds)
        assert writer.commit_due()

        assert recorder.writes() == [
            'INSERT b2b_message',
            'UPDATE b2b_message',
            'INSERT event',
            'INSERT event_attr',
            'INSERT event_body',
            'DELETE b2b_open',
            'INSERT b2b_open',
        ]

        # SQLite returns no ordered identifiers from a multi-row insert, so one select by the transaction returns them.
        selects = recorder.selects()

        assert len(selects) == 1
        assert selects[0].table == 'event'
        assert recorder.commits == 1

        recorder.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestTwoCopiesInOneTransaction:
    """ Two copies of one message in one transaction are resolved in memory.
    """

    def test_copies(self) -> 'None':
        clock = FakeMonotonic()
        engine = new_memory_engine()
        writer = _writer(engine, clock)
        recorder = StatementRecorder(engine)

        first = writer.enqueue(_claim('message-1'), 1)
        second = writer.enqueue(_claim('message-1'), 1)

        clock.advance(_interval_seconds)
        assert writer.commit_due()

        assert first.wait() is True
        assert second.wait() is False

        # The claim statement holds the columns of one row only.
        claim_statement = recorder.statements[0]
        column_count = len(message_table.columns) - 1

        assert claim_statement.table == 'b2b_message'
        assert claim_statement.param_count == column_count
        assert _count_messages(engine) == 1

        recorder.stop()

# ################################################################################################################################
# ################################################################################################################################

class TestOffTheEventLoop:
    """ Under gevent, a held-back commit runs in the thread pool of the hub and the event loop continues.
    """

    def test_gevent(self) -> 'None':
        result = subprocess.run([sys.executable, _gevent_program], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().splitlines()
        report = json.loads(lines[-1])

        assert report['is_claimed'] is True
        assert report['commit_thread'] != report['main_thread']
        assert report['ticks_during_commit'] >= report['min_ticks']

# ################################################################################################################################
# ################################################################################################################################
