# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The native column types and the search index every backend must agree on - timestamps given at any
# offset come back as the same moments in UTC and sort as moments, hourly periods are computed
# by the database in UTC, and the free-text search returns through the index the events with words
# that the words of a query are prefixes of.

# stdlib
from datetime import datetime, timedelta, timezone

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from common import delete_all_events
from zato.common.audit_log.api import event_attr_table, event_table, AuditEvent, AuditSource
from zato.common.db_env.database import get_database_engine
from zato.common.audit_log.payload import update_event_payload
from zato.common.audit_log.search import build_search_conditions
from zato.common.audit_log.writes import execute_audit_write, write_audit
from zato.common.test.direct_sql.seed import seed_event_row, seed_rows
from zato.common.db_env.common import hour_period

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.typing_ import any_, strlist, strset

    # Dummy assignments to satisfy type checkers
    any_ = any_
    Engine = Engine
    strlist = strlist
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

# The offsets the timestamps are given at, none of them UTC
_india_offset = timezone(timedelta(hours=5, minutes=30))
_pacific_offset = timezone(timedelta(hours=-8))

# Wall-clock order is the pacific one first, the UTC one second and the Indian one last,
# while the moments themselves run in the opposite direction for the first and the last.
_india_time = datetime(2026, 3, 1, 9, 30, 0, tzinfo=_india_offset)
_utc_time = datetime(2026, 3, 1, 4, 0, 0, 1, tzinfo=timezone.utc)
_pacific_time = datetime(2026, 3, 1, 1, 0, 0, tzinfo=_pacific_offset)

# The source the search events are written under - one that has searchable attributes
_search_source = AuditSource.MLLP_Channel

# The object all the events of this scenario belong to
_object_name = 'audit.test.storage-types'

# The searchable attribute that leads to a whole trace
_attr_name = 'mrn'
_attr_value = 'MRN-778899'

# ################################################################################################################################
# ################################################################################################################################

def _insert_event(engine:'Engine', cid:'str', event_time:'datetime', data:'str') -> 'int':
    """ Seeds one event and returns its id.
    """
    event_row = dict(
        cid=cid,
        source=_search_source,
        event_type=AuditEvent.Message_Received,
        object_name=_object_name,
        msg_id=f'msg-{cid}',
        event_time=event_time,
        data=data,
    )

    out = seed_event_row(engine, event_row)
    return out

# ################################################################################################################################

def _cids_in_time_order(engine:'Engine', *conditions:'any_') -> 'strlist':
    """ The cids of the events matching the conditions, oldest first.
    """
    is_scenario_object = event_table.c.object_name == _object_name

    query = select(event_table.c.cid)
    query = query.where(is_scenario_object, *conditions)
    query = query.order_by(event_table.c.event_time)

    with engine.connect() as connection:
        result = connection.execute(query)
        out = list(result.scalars())

    return out

# ################################################################################################################################

def _search(engine:'Engine', query:'str') -> 'strset':
    """ The cids of the events the free-text search finds.
    """
    conditions = build_search_conditions([_search_source], [_object_name], query=query)

    statement = select(event_table.c.cid).where(*conditions)

    with engine.connect() as connection:
        result = connection.execute(statement)
        out = set(result.scalars())

    return out

# ################################################################################################################################
# ################################################################################################################################

def run_timestamp_scenario() -> 'None':
    """ Timestamps given at non-UTC offsets and with zero microseconds come back as the same moments
    in UTC, sort as moments rather than as wall-clock text, and bound time windows exactly.
    """
    delete_all_events()
    engine = get_database_engine()

    _ = _insert_event(engine, 'india', _india_time, '')
    _ = _insert_event(engine, 'utc', _utc_time, '')
    _ = _insert_event(engine, 'pacific', _pacific_time, '')

    query = select(event_table.c.cid, event_table.c.event_time)
    query = query.where(event_table.c.object_name == _object_name)

    with engine.connect() as connection:
        rows = connection.execute(query).all()

    expected = {
        'india': _india_time,
        'utc': _utc_time,
        'pacific': _pacific_time,
    }

    # Each value is the moment it was written as, given in UTC ..
    for cid, event_time in rows:
        assert event_time == expected[cid]
        assert event_time.utcoffset() == timedelta(0)
        assert event_time.microsecond == expected[cid].microsecond

    # .. the order is that of the moments, 04:00:00, 04:00:00.000001 and 09:00:00 in UTC ..
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

# ################################################################################################################################

def run_hour_period_scenario() -> 'None':
    """ The database groups events into hourly periods by their moments in UTC, whatever offset they were given at.
    """
    delete_all_events()
    engine = get_database_engine()

    _ = _insert_event(engine, 'india', _india_time, '')
    _ = _insert_event(engine, 'utc', _utc_time, '')
    _ = _insert_event(engine, 'pacific', _pacific_time, '')

    period = hour_period(event_table.c.event_time)
    event_count = func.count()

    query = select(period, event_count)
    query = query.where(event_table.c.object_name == _object_name)
    query = query.group_by(period)

    with engine.connect() as connection:
        rows = connection.execute(query).all()

    periods = dict(rows)

    assert periods == {
        '2026-03-01T04': 2,
        '2026-03-01T09': 1,
    }

# ################################################################################################################################

def run_search_scenario() -> 'None':
    """ The free-text search finds through the index of the database the events with words that the words of a query
    are prefixes of, for terms in several scripts, with LIKE wildcards and quotes, and finds by LIKE the events
    for terms shorter than the words of the index.
    """
    delete_all_events()
    engine = get_database_engine()

    now = datetime.now(timezone.utc)

    _ = _insert_event(engine, 'scripts', now, 'Zamówienie 請求書 τιμολόγιο ORDER-2026-ABC')
    _ = _insert_event(engine, 'percent', now, 'progress 100% done, item value_a')
    updated_id = _insert_event(engine, 'updated', now, 'item valuexa')
    _ = _insert_event(engine, 'quoted', now, 'a quote "inner" text')
    deleted_id = _insert_event(engine, 'deleted', now, 'x y')

    # An attribute leads to every event of the trace it belongs to ..
    with_attr_id = _insert_event(engine, 'trace', now, 'MSH|^~\\&|')
    _ = _insert_event(engine, 'trace', now, 'MSA|AA|')

    attr_row = {'event_id': with_attr_id, 'name': _attr_name, 'value': _attr_value}
    seed_rows(engine, [(event_attr_table, [attr_row])])

    # .. terms long enough for every index ..
    assert _search(engine, 'ORDER-2026') == {'scripts'}
    assert _search(engine, '請求書') == {'scripts'}
    assert _search(engine, 'τιμολόγιο') == {'scripts'}
    assert _search(engine, 'Zamówienie') == {'scripts'}

    # .. LIKE wildcards are not part of a word, and each word of a query is a prefix ..
    assert _search(engine, '100%') == {'percent'}
    assert _search(engine, 'value_a') == {'percent', 'updated'}

    # .. a term with double quotes in it ..
    assert _search(engine, '"inner"') == {'quoted'}

    # .. terms shorter than the words of an index, which LIKE finds in the indexed words ..
    assert _search(engine, 'AB') == {'scripts'}
    assert _search(engine, 'x') == {'updated', 'quoted'}

    # .. and an attribute value, which returns the whole trace.
    assert _search(engine, '778899') == {'trace'}

    # The index follows updates ..
    replaced_data = 'item replaced'
    _ = write_audit(engine, update_event_payload, updated_id, {}, replaced_data)

    assert _search(engine, 'valuexa') == set()
    assert _search(engine, 'replaced') == {'updated'}

    # .. and deletes.
    delete = event_table.delete().where(event_table.c.id == deleted_id)
    _ = execute_audit_write(engine, delete)

    assert _search(engine, 'x y') == set()

# ################################################################################################################################

def run_storage_types_scenario() -> 'None':
    """ Every storage type scenario, in turn.
    """
    run_timestamp_scenario()
    run_hour_period_scenario()
    run_search_scenario()

# ################################################################################################################################
# ################################################################################################################################
