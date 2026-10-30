# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The native column types and the search index every backend must agree on - timestamps given at any
# offset come back as the same moments in UTC and sort as moments, hourly periods are computed
# by the database in UTC, and the free-text search returns through the index what LIKE returns.

# stdlib
from datetime import datetime, timedelta, timezone

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from common import delete_all_events
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine, AuditEvent, AuditSource
from zato.common.audit_log.search import build_search_conditions
from zato.common.db_env.common import hour_period, Type_SQLite

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

# What each database adds to a statement when its own index narrows a search down
_index_markers = {
    Type_SQLite: 'event_search MATCH',
}

# ################################################################################################################################
# ################################################################################################################################

def _insert_event(engine:'Engine', cid:'str', event_time:'datetime', data:'str') -> 'int':
    """ Inserts one event and returns its id.
    """
    insert = event_table.insert().values(
        cid=cid,
        source=_search_source,
        event_type=AuditEvent.Message_Received,
        object_name=_object_name,
        msg_id=f'msg-{cid}',
        event_time=event_time,
        data=data,
    )

    with engine.begin() as connection:
        result = connection.execute(insert)
        out = result.inserted_primary_key[0]

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
    conditions = build_search_conditions(engine.dialect.name, [_search_source], [_object_name], query=query)

    statement = select(event_table.c.cid).where(*conditions)

    with engine.connect() as connection:
        result = connection.execute(statement)
        out = set(result.scalars())

    return out

# ################################################################################################################################

def _search_sql(engine:'Engine', query:'str') -> 'str':
    """ The statement a search compiles to on the given database.
    """
    conditions = build_search_conditions(engine.dialect.name, [_search_source], [_object_name], query=query)

    statement = select(event_table.c.cid).where(*conditions)
    compiled = statement.compile(dialect=engine.dialect)

    out = str(compiled)
    return out

# ################################################################################################################################
# ################################################################################################################################

def run_timestamp_scenario() -> 'None':
    """ Timestamps given at non-UTC offsets and with zero microseconds come back as the same moments
    in UTC, sort as moments rather than as wall-clock text, and bound time windows exactly.
    """
    delete_all_events()
    engine = get_audit_engine()

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
    engine = get_audit_engine()

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
    """ The free-text search finds through the index of each database what LIKE alone would find,
    for terms in several scripts, with LIKE wildcards and quotes, and for terms shorter than the index tokens.
    """
    delete_all_events()
    engine = get_audit_engine()

    now = datetime.now(timezone.utc)

    _ = _insert_event(engine, 'scripts', now, 'Zamówienie 請求書 τιμολόγιο ORDER-2026-ABC')
    _ = _insert_event(engine, 'percent', now, 'progress 100% done, item value_a')
    updated_id = _insert_event(engine, 'updated', now, 'item valuexa')
    _ = _insert_event(engine, 'quoted', now, 'a quote "inner" text')
    deleted_id = _insert_event(engine, 'deleted', now, 'x y')

    # An attribute leads to every event of the trace it belongs to ..
    with_attr_id = _insert_event(engine, 'trace', now, 'MSH|^~\\&|')
    _ = _insert_event(engine, 'trace', now, 'MSA|AA|')

    attr_insert = event_attr_table.insert().values(event_id=with_attr_id, name=_attr_name, value=_attr_value)

    with engine.begin() as connection:
        _ = connection.execute(attr_insert)

    # .. terms long enough for every index ..
    assert _search(engine, 'ORDER-2026') == {'scripts'}
    assert _search(engine, '請求書') == {'scripts'}
    assert _search(engine, 'τιμολόγιο') == {'scripts'}
    assert _search(engine, 'Zamówienie') == {'scripts'}

    # .. LIKE wildcards matched literally ..
    assert _search(engine, '100%') == {'percent'}
    assert _search(engine, 'value_a') == {'percent'}

    # .. a term with double quotes in it ..
    assert _search(engine, '"inner"') == {'quoted'}

    # .. terms shorter than the tokens of an index ..
    assert _search(engine, 'AB') == {'scripts'}
    assert _search(engine, 'x') == {'updated', 'quoted', 'deleted'}

    # .. and an attribute value, which returns the whole trace.
    assert _search(engine, '778899') == {'trace'}

    # A long term is narrowed down by the index of the database and a short one is not.
    if marker := _index_markers.get(engine.dialect.name):
        assert marker in _search_sql(engine, 'ORDER-2026')
        assert marker not in _search_sql(engine, 'x')

    # The index follows updates ..
    update = event_table.update().where(event_table.c.id == updated_id).values(data='item replaced')

    with engine.begin() as connection:
        _ = connection.execute(update)

    assert _search(engine, 'valuexa') == set()
    assert _search(engine, 'replaced') == {'updated'}

    # .. and deletes.
    delete = event_table.delete().where(event_table.c.id == deleted_id)

    with engine.begin() as connection:
        _ = connection.execute(delete)

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
