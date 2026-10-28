# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The native column types and the search indexes on each database - binary bodies at the size of the largest
# message stored and read back unchanged, timestamps given at any offset bounding windows exactly, hourly periods
# computed by the database, and the free-text search served by the index of the database.

# stdlib
from datetime import datetime, timedelta, timezone

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from live_db import Type_MySQL, Type_PostgreSQL, Type_SQLite
from zato.common.audit_log.api import event_table, AuditEvent
from zato.common.audit_log.search import build_search_conditions
from zato.common.b2b.common.clock import ManualClock
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.outcome import FinalState
from zato.common.b2b.common.send_log import SendLog
from zato.common.b2b.common.store import MessageStore
from zato.common.b2b.ebms2.common import MessageOrderSemantics, SequenceStatus
from zato.common.b2b.ebms2.inbound_common import pending_deliveries
from zato.common.b2b.ebms2.outbound import SendOptions
from zato.common.b2b.ebms2.packaging import Payload
from zato.common.db_env.common import hour_period
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import deliver, new_exchange, send, Start_Time as Exchange_Start_Time, use_store
from zato.common.test.b2b_write_path import new_sent_message, Server, Source, Start_Time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from sqlalchemy.sql import Select
    from live_db import LiveDB
    from zato.common.b2b.ebms2.outbound import OutboundMessage
    from zato.common.test.b2b_ebms2 import Exchange
    from zato.common.test.b2b_pki import TestParties
    from zato.common.typing_ import any_, strlist, strset

    any_ = any_
    Connection = Connection
    Engine = Engine
    Exchange = Exchange
    LiveDB = LiveDB
    OutboundMessage = OutboundMessage
    TestParties = TestParties
    Select = Select
    strlist = strlist
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

# The number of distinct byte values, each of which every body below holds
_byte_values = 256

# The size of the wire body, close to the largest message a B2B protocol accepts
_wire_body_size = 60 * 1024 * 1024

# The size of the held message
_held_body_size = 1024 * 1024

# The conversation the held message belongs to, and the sequence numbers of the message that releases it and its own
_conversation = 'storage-types-conversation'
_first_sequence_number = 0
_held_sequence_number = 1
_held_content_type = 'application/octet-stream'

# How many deliveries the recovery in the held message test reads
_recovery_page_size = 10

# The offsets the timestamps are given at, none of them UTC
_india_offset = timezone(timedelta(hours=5, minutes=30))
_pacific_offset = timezone(timedelta(hours=-8))

# Wall-clock order is the pacific one first, the UTC one second and the Indian one last,
# while the moments themselves run in the opposite direction for the first and the last.
_india_time = datetime(2026, 3, 1, 9, 30, 0, tzinfo=_india_offset)
_utc_time = datetime(2026, 3, 1, 4, 0, 0, 1, tzinfo=timezone.utc)
_pacific_time = datetime(2026, 3, 1, 1, 0, 0, tzinfo=_pacific_offset)

# The object all the events of these tests belong to
_object_name = 'b2b.storage-types'

# The term every database finds through its index
_indexed_term = 'ORDER-2026'

# What the plan of each database names when the index serves a search
_index_plan_markers = {
    Type_SQLite: 'VIRTUAL TABLE INDEX',
    Type_MySQL: 'fulltext',
    Type_PostgreSQL: 'idx_event_search_',
}

# ################################################################################################################################
# ################################################################################################################################

def _all_byte_values(size:'int') -> 'bytes':
    """ The given number of bytes, holding every byte value, so no value is lost or altered on the way.
    """
    values = range(_byte_values)
    pattern = bytes(values)
    repetitions = size // _byte_values

    out = pattern * repetitions
    return out

# ################################################################################################################################

def _numbered(exchange:'Exchange', sequence_number:'int', data:'bytes') -> 'OutboundMessage':
    """ Returns a message of the ordered conversation with the given sequence number and payload.
    """
    options = SendOptions()
    options.conversation_id = _conversation
    options.sequence_number = sequence_number
    options.sequence_status = SequenceStatus.Continue

    payload = Payload()
    payload.content_id = ''
    payload.content_type = _held_content_type
    payload.data = data

    out = send(exchange, [payload], options)
    return out

# ################################################################################################################################

def _insert_event(engine:'Engine', cid:'str', event_time:'datetime', data:'str') -> 'None':
    """ Inserts one event of the tests.
    """
    insert = event_table.insert().values(
        cid=cid,
        source=Source,
        event_type=AuditEvent.Message_Received,
        object_name=_object_name,
        event_time=event_time,
        data=data,
    )

    with engine.begin() as connection:
        _ = connection.execute(insert)

# ################################################################################################################################

def _insert_offset_events(engine:'Engine') -> 'None':
    """ Inserts the three events whose times are given at three different offsets.
    """
    _insert_event(engine, 'india', _india_time, '')
    _insert_event(engine, 'utc', _utc_time, '')
    _insert_event(engine, 'pacific', _pacific_time, '')

# ################################################################################################################################

def _cids_in_time_order(engine:'Engine', *conditions:'any_') -> 'strlist':
    """ The cids of the events matching the conditions, oldest first.
    """
    is_test_object = event_table.c.object_name == _object_name

    query = select(event_table.c.cid)
    query = query.where(is_test_object, *conditions)
    query = query.order_by(event_table.c.event_time)

    with engine.connect() as connection:
        result = connection.execute(query)
        out = list(result.scalars())

    return out

# ################################################################################################################################

def _search_statement(engine:'Engine', query:'str') -> 'Select':
    """ The statement the free-text search runs for the given term.
    """
    conditions = build_search_conditions(engine.dialect.name, query=query)

    out = select(event_table.c.cid).where(*conditions)
    return out

# ################################################################################################################################

def _search(engine:'Engine', query:'str') -> 'strset':
    """ The cids of the events the free-text search finds.
    """
    statement = _search_statement(engine, query)

    with engine.connect() as connection:
        result = connection.execute(statement)
        out = set(result.scalars())

    return out

# ################################################################################################################################

def _plan_lines(connection:'Connection', database_name:'str', sql:'str') -> 'strlist':
    """ Each line of the plan of a statement, as the database describes it.
    """
    out:'strlist' = []

    if database_name == Type_SQLite:
        for row in connection.exec_driver_sql('EXPLAIN QUERY PLAN ' + sql):
            out.append(row[3])

    elif database_name == Type_PostgreSQL:

        # A small table is read in full whenever that is cheaper, so the planner is made to use what indexes it can.
        _ = connection.exec_driver_sql('SET enable_seqscan = off')

        for row in connection.exec_driver_sql('EXPLAIN ' + sql):
            out.append(row[0])

    else:
        for row in connection.exec_driver_sql('EXPLAIN ' + sql).mappings():
            out.append(f'{row["table"]} {row["type"]} {row["key"]}')

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestBinaryBodies:
    """ Bodies of the size the protocols accept are stored as they are and read back byte for byte.
    """

    def test_wire_body(self, database:'LiveDB', writer:'GroupCommitWriter') -> 'None':
        send_log = SendLog(Source, Server, ManualClock(Start_Time), writer)

        message_id = 'storage-types-wire-body'
        wire_body = _all_byte_values(_wire_body_size)

        sent = new_sent_message(message_id, wire_body=wire_body)
        send_log.record_first_attempt(sent)

        # The first delivery takes the bytes held in memory ..
        assert send_log.wire_body(message_id) == wire_body

        # .. and a later one reads them from the database.
        assert send_log.wire_body(message_id) == wire_body

    def test_held_message(self, database:'LiveDB', writer:'GroupCommitWriter', parties:'TestParties') -> 'None':
        settings = new_settings(parties, Exchange_Start_Time)
        settings.message_order = MessageOrderSemantics.Guaranteed

        exchange = new_exchange(parties, settings)
        use_store(exchange.receiver, MessageStore(writer))

        held_data = _all_byte_values(_held_body_size)

        first = _numbered(exchange, _first_sequence_number, b'<Order/>')
        second = _numbered(exchange, _held_sequence_number, held_data)

        # The second message waits for the first one ..
        held_result = deliver(exchange, second)
        assert held_result.outcome.final_state == FinalState.Held

        # .. which releases it with its bytes as they arrived ..
        result = deliver(exchange, first)
        released = result.deliveries[1]

        assert released.message_id == second.message_id
        assert released.payloads[0].data == held_data

        # .. and its bytes are read again from the database by the recovery of its delivery.
        recovered = pending_deliveries(exchange.receiver.receive_log, _recovery_page_size)
        assert recovered[1].payloads[0].data == held_data

# ################################################################################################################################
# ################################################################################################################################

class TestTimestamps:
    """ Timestamps given at non-UTC offsets and with zero microseconds come back as the same moments in UTC,
    sort as moments and bound time windows exactly.
    """

    def test_round_trip(self, database:'LiveDB') -> 'None':
        engine = database.engine
        _insert_offset_events(engine)

        expected = {
            'india': _india_time,
            'utc': _utc_time,
            'pacific': _pacific_time,
        }

        query = select(event_table.c.cid, event_table.c.event_time)

        with engine.connect() as connection:
            rows = connection.execute(query).all()

        assert len(rows) == len(expected)

        for cid, event_time in rows:
            assert event_time == expected[cid]
            assert event_time.utcoffset() == timedelta(0)
            assert event_time.microsecond == expected[cid].microsecond

    def test_windows(self, database:'LiveDB') -> 'None':
        engine = database.engine
        _insert_offset_events(engine)

        # The order is that of the moments, 04:00:00, 04:00:00.000001 and 09:00:00 in UTC ..
        assert _cids_in_time_order(engine) == ['india', 'utc', 'pacific']

        # .. a window opening at a value with zero microseconds includes that value ..
        opens_at_value = event_table.c.event_time >= _india_time
        assert _cids_in_time_order(engine, opens_at_value) == ['india', 'utc', 'pacific']

        # .. a window closing one microsecond later holds that value alone ..
        closes_after_value = event_table.c.event_time < _utc_time
        assert _cids_in_time_order(engine, closes_after_value) == ['india']

        # .. and a window opening right after it leaves it out.
        opens_after_value = event_table.c.event_time > _india_time
        assert _cids_in_time_order(engine, opens_after_value) == ['utc', 'pacific']

    def test_hour_period(self, database:'LiveDB') -> 'None':
        engine = database.engine
        _insert_offset_events(engine)

        period = hour_period(event_table.c.event_time)
        event_count = func.count()

        query = select(period, event_count).group_by(period)

        with engine.connect() as connection:
            rows = connection.execute(query).all()

        periods = dict(rows)

        assert periods == {
            '2026-03-01T04': 2,
            '2026-03-01T09': 1,
        }

# ################################################################################################################################
# ################################################################################################################################

class TestSearch:
    """ The free-text search finds through the index of each database what LIKE alone would find.
    """

    def test_search(self, database:'LiveDB') -> 'None':
        engine = database.engine
        now = datetime.now(timezone.utc)

        _insert_event(engine, 'scripts', now, 'Zamówienie 請求書 τιμολόγιο ORDER-2026-ABC')
        _insert_event(engine, 'percent', now, 'progress 100% done, item value_a')
        _insert_event(engine, 'underscore', now, 'item valuexa')
        _insert_event(engine, 'short', now, 'x y')

        # Terms long enough for every index ..
        assert _search(engine, _indexed_term) == {'scripts'}
        assert _search(engine, '請求書') == {'scripts'}
        assert _search(engine, 'τιμολόγιο') == {'scripts'}

        # .. LIKE wildcards matched literally ..
        assert _search(engine, '100%') == {'percent'}
        assert _search(engine, 'value_a') == {'percent'}

        # .. and a term shorter than the tokens of any index.
        assert _search(engine, 'x') == {'underscore', 'short'}

    def test_index_serves_search(self, database:'LiveDB') -> 'None':
        engine = database.engine
        now = datetime.now(timezone.utc)

        _insert_event(engine, 'scripts', now, 'Zamówienie 請求書 τιμολόγιο ORDER-2026-ABC')

        statement = _search_statement(engine, _indexed_term)
        compiled = statement.compile(dialect=engine.dialect, compile_kwargs={'literal_binds': True})
        sql = str(compiled)

        with engine.connect() as connection:
            lines = _plan_lines(connection, database.name, sql)
            connection.rollback()

        plan = '\n'.join(lines)
        marker = _index_plan_markers[database.name]

        assert marker in plan, plan

# ################################################################################################################################
# ################################################################################################################################
