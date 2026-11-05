# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from random import Random

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, event_table, \
    get_audit_engine, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.common import event_count_table, event_dedup_table, event_open_table, Status_Outstanding
from zato.common.audit_log.event_count import compact_event_counts, count_key_columns
from zato.common.audit_log.listing import new_search_filters
from zato.common.audit_log.sqlite_writes import env_config
from zato.common.db_env import dispose_env_engine
from zato.common.db_env.engine import call_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.listing import SearchFilters
    from zato.common.typing_ import any_, anydict, anylist, anyset, anytuple, callable_, intlist, intset, stranydict

    SearchFilters = SearchFilters
    any_ = any_
    callable_ = callable_
    anydict = anydict
    anylist = anylist
    anyset = anyset
    anytuple = anytuple
    intlist = intlist
    intset = intset
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The backends every test of this directory runs against
Backend_SQLite     = 'sqlite'
Backend_PostgreSQL = 'postgresql'

# The server all the test events are written under
Server_Name = 'test-audit-log-read-server'

# The events of a test are stamped with moments between these two, at random microseconds
Base_Time = datetime(2026, 10, 29, 10, 0, 0, tzinfo=timezone.utc)
Time_Span = timedelta(hours=3)

# The connections the events belong to, and the same with None standing for an event that names none
Connection_Names = ['audit.test.read.pair-a', 'audit.test.read.pair-b', 'audit.test.read.pair-c']
Object_Names = Connection_Names + [None]

# The sources of the events, the outgoing MLLP one twice as often as each of the others ..
_sources = [AuditSource.MLLP_Outgoing, AuditSource.MLLP_Outgoing, AuditSource.MLLP_Channel, AuditSource.Scheduler]

# .. the event types of each source ..
_event_types = {
    AuditSource.MLLP_Outgoing: [AuditEvent.Message_Sent, AuditEvent.Ack_Received],
    AuditSource.MLLP_Channel:  [AuditEvent.Message_Received],
    AuditSource.Scheduler:     [AuditEvent.Job_Executed],
}

# .. and the outcomes and statuses they end with.
_outcomes = [AuditOutcome.OK, AuditOutcome.Error, AuditOutcome.Running]
_statuses = ['open', 'closed', None]

# How many message ids the events share, so that most messages meet their acknowledgments
_msg_id_count = 400

# The most rows one insert statement writes, so that preparing one statement does not block the event loop
_rows_per_statement = 500

# The triggers, tables and indexes that serve the reads, as an existing database created before them lacks them
_trigger_prefixes = ('event_count', 'event_open_mllp_outgoing')
_trigger_kinds = ('insert', 'update', 'delete')
_read_tables = ('event_count', 'event_open')
_ordered_indexes = ('idx_event_time', 'idx_event_source_time', 'idx_event_outcome_time')

# ################################################################################################################################
# ################################################################################################################################

def run_blocking(func:'callable_', *args:'any_') -> 'any_':
    """ Runs a function that makes blocking database calls, in the thread pool of the gevent hub when the database needs it,
    so that a long run of statements does not block the event loop.
    """
    engine = get_audit_engine()

    out = call_database(engine, func, *args)
    return out

# ################################################################################################################################

def delete_all_rows() -> 'None':
    """ Starts a test from empty tables because the PostgreSQL container is shared by all the tests.
    The event counts and the open exchanges are emptied last, after the triggers wrote what deleting the events changes.
    """
    engine = get_audit_engine()

    with engine.begin() as connection:
        _ = connection.execute(event_attr_table.delete())
        _ = connection.execute(event_body_table.delete())
        _ = connection.execute(event_link_table.delete())
        _ = connection.execute(event_dedup_table.delete())
        _ = connection.execute(event_table.delete())
        _ = connection.execute(event_count_table.delete())
        _ = connection.execute(event_open_table.delete())

# ################################################################################################################################

def random_time(rng:'Random') -> 'datetime':
    """ A moment within the time span of the test events.
    """
    span_microseconds = Time_Span // timedelta(microseconds=1)
    offset = rng.randrange(span_microseconds)

    out = Base_Time + timedelta(microseconds=offset)
    return out

# ################################################################################################################################

def new_event_row(
    rng:'Random',
    index:'int',
    event_time:'datetime',
    source:'str' = '',
    event_type:'str' = '',
    ) -> 'stranydict':
    """ The values of one event row, with the source and the event type chosen at random unless they are given.
    One event in ten has no message id.
    """
    if not source:
        source = rng.choice(_sources)

    if not event_type:
        event_types = _event_types[source]
        event_type = rng.choice(event_types)

    if rng.randrange(10) == 0:
        msg_id = None
    else:
        msg_number = rng.randrange(_msg_id_count)
        msg_id = f'msg.{msg_number}'

    out = {
        'cid': f'cid.read.{index}',
        'source': source,
        'event_type': event_type,
        'object_name': rng.choice(Object_Names),
        'msg_id': msg_id,
        'correl_id': '',
        'ext_client_id': '',
        'event_time': event_time,
        'server_name': Server_Name,
        'endpoint': '',
        'sub_key': '',
        'size': 10,
        'priority': 0,
        'outcome': rng.choice(_outcomes),
        'status': rng.choice(_statuses),
        'data': 'MSH|^~\\&|LAB|RIVERSIDE',
    }

    return out

# ################################################################################################################################

def new_event_rows(rng:'Random', count:'int', first_index:'int') -> 'anylist':
    """ The values of a number of event rows at random moments.
    """
    out:'anylist' = []

    for index in range(first_index, first_index + count):
        event_time = random_time(rng)
        row = new_event_row(rng, index, event_time)
        out.append(row)

    return out

# ################################################################################################################################

def insert_rows(rows:'anylist') -> 'None':
    """ Inserts event rows in one transaction, in statements of at most _rows_per_statement rows each.
    """
    engine = get_audit_engine()

    with engine.begin() as connection:
        for start in range(0, len(rows), _rows_per_statement):
            end = start + _rows_per_statement
            statement_rows = rows[start:end]

            _ = connection.execute(event_table.insert(), statement_rows)

# ################################################################################################################################

def read_event_ids() -> 'intlist':
    """ The ids of all the events, in their order.
    """
    engine = get_audit_engine()

    query = select(event_table.c.id)
    query = query.order_by(event_table.c.id)

    with engine.connect() as connection:
        result = connection.execute(query)
        ids = result.scalars()
        out = list(ids)

    return out

# ################################################################################################################################

def read_events() -> 'anylist':
    """ The columns of all the events that the event counts and the open exchanges are kept from, one dict per event.
    """
    engine = get_audit_engine()

    columns:'anylist' = [
        event_table.c.id,
        event_table.c.event_time,
        event_table.c.event_type,
        event_table.c.msg_id,
    ]

    for name in count_key_columns:
        column = event_table.c[name]
        columns.append(column)

    query = select(*columns)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query).mappings():
            values = dict(row)
            out.append(values)

    return out

# ################################################################################################################################

def _count_key(period_start:'datetime', row:'anydict') -> 'anytuple':
    """ The minute and the key columns that one row is counted under.
    """
    parts:'anylist' = [period_start]

    for name in count_key_columns:
        value = row[name]
        parts.append(value)

    out = tuple(parts)
    return out

# ################################################################################################################################

def expected_counts(events:'anylist') -> 'anydict':
    """ The number of events of each minute and key, counted from the events themselves.
    """
    out:'anydict' = {}

    for row in events:
        period_start = row['event_time'].replace(second=0, microsecond=0)
        key = _count_key(period_start, row)

        if key not in out:
            out[key] = 0

        out[key] += 1

    return out

# ################################################################################################################################

def read_count_rows() -> 'anylist':
    """ All the rows of the event counts, one dict per row.
    """
    engine = get_audit_engine()

    query = select(event_count_table)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query).mappings():
            values = dict(row)
            out.append(values)

    return out

# ################################################################################################################################

def actual_counts() -> 'anydict':
    """ The number of events of each minute and key, summed from the event counts, without the keys whose sum is zero.
    """
    sums:'anydict' = {}

    for row in read_count_rows():
        key = _count_key(row['period_start'], row)

        if key not in sums:
            sums[key] = 0

        sums[key] += row['event_count']

    out:'anydict' = {}

    for key, count in sums.items():
        if count != 0:
            out[key] = count

    return out

# ################################################################################################################################

def expected_open_ids(events:'anylist') -> 'intset':
    """ The ids of the outgoing MLLP messages that no acknowledgment of the same message id and connection answers.
    An event without a message id or a connection never answers a message.
    """
    answered:'anyset' = set()

    for row in events:

        if row['source'] != AuditSource.MLLP_Outgoing:
            continue

        if row['event_type'] != AuditEvent.Ack_Received:
            continue

        if row['msg_id'] is None:
            continue

        if row['object_name'] is None:
            continue

        answer = (row['msg_id'], row['object_name'])
        answered.add(answer)

    out:'intset' = set()

    for row in events:

        if row['source'] != AuditSource.MLLP_Outgoing:
            continue

        if row['event_type'] != AuditEvent.Message_Sent:
            continue

        exchange = (row['msg_id'], row['object_name'])

        if exchange not in answered:
            out.add(row['id'])

    return out

# ################################################################################################################################

def read_open_ids() -> 'intlist':
    """ The event ids the table of open exchanges holds, duplicates included.
    """
    engine = get_audit_engine()

    query = select(event_open_table.c.event_id)

    with engine.connect() as connection:
        result = connection.execute(query)
        ids = result.scalars()
        out = list(ids)

    return out

# ################################################################################################################################

def drop_read_schema(backend:'str') -> 'None':
    """ Turns the database into one created before the event counts and the open exchanges existed.
    """
    engine = get_audit_engine()

    with engine.begin() as connection:

        for prefix in _trigger_prefixes:
            for kind in _trigger_kinds:
                name = f'{prefix}_{kind}'

                if backend == Backend_PostgreSQL:
                    _ = connection.exec_driver_sql(f'DROP TRIGGER {name} ON event')
                    _ = connection.exec_driver_sql(f'DROP FUNCTION {name}')
                else:
                    _ = connection.exec_driver_sql(f'DROP TRIGGER {name}')

        for name in _read_tables:
            _ = connection.exec_driver_sql(f'DROP TABLE {name}')

        for name in _ordered_indexes:
            _ = connection.exec_driver_sql(f'DROP INDEX {name}')

# ################################################################################################################################

def reopen_database() -> 'None':
    """ Opens the database anew, the way a server starting up does, which creates what the schema lacks.
    """
    dispose_env_engine(env_config)
    _ = get_audit_engine()

# ################################################################################################################################

def populate(rng:'Random', event_count:'int') -> 'None':
    """ Writes events whose counts are partly compacted and partly still one row per change - inserted,
    updated in place and deleted before and after a compaction. Two thirds of the events are written
    before the compaction and one third after it.
    """
    engine = get_audit_engine()

    first_count = event_count * 2 // 3
    later_count = event_count - first_count

    # The first events are written, some of them changed and deleted ..
    rows = new_event_rows(rng, first_count, 0)
    insert_rows(rows)

    ids = read_event_ids()
    changed_ids = rng.sample(ids, first_count // 10)
    deleted_ids = rng.sample(ids, first_count // 15)

    is_changed = event_table.c.id.in_(changed_ids)
    is_deleted = event_table.c.id.in_(deleted_ids)

    update = event_table.update().where(is_changed).values(outcome=AuditOutcome.Error, status='closed')
    delete = event_table.delete().where(is_deleted)

    with engine.begin() as connection:
        _ = connection.execute(update)
        _ = connection.execute(delete)

    # .. their counts are compacted ..
    _ = compact_event_counts(engine, event_count_table, 0)

    # .. and more events are written, changed and deleted after that.
    rows = new_event_rows(rng, later_count, event_count)
    insert_rows(rows)

    ids = read_event_ids()
    changed_ids = rng.sample(ids, later_count // 7)
    deleted_ids = rng.sample(ids, later_count // 15)

    is_changed = event_table.c.id.in_(changed_ids)
    is_deleted = event_table.c.id.in_(deleted_ids)

    update = event_table.update().where(is_changed).values(source=AuditSource.MLLP_Outgoing,
        event_type=AuditEvent.Ack_Received)
    delete = event_table.delete().where(is_deleted)

    with engine.begin() as connection:
        _ = connection.execute(update)
        _ = connection.execute(delete)

# ################################################################################################################################

def _at(hours:'int', minutes:'int', seconds:'float') -> 'datetime':
    """ A moment that many hours, minutes and seconds after the start of the time span of the test events.
    """
    offset = timedelta(hours=hours, minutes=minutes, seconds=seconds)

    out = Base_Time + offset
    return out

# ################################################################################################################################

def search_windows() -> 'anylist':
    """ The time windows the searches are run with, each a pair of its start and its end, None standing for an open bound.
    """
    out:'anylist' = [

        # No window at all ..
        (None, None),

        # .. one that cuts a minute at both of its edges ..
        (_at(0, 2, 17.5), _at(2, 3, 41.25)),

        # .. one of whole minutes only ..
        (_at(0, 15, 0), _at(0, 45, 0)),

        # .. one within a single minute ..
        (_at(0, 10, 30), _at(0, 10, 45)),

        # .. one a microsecond into the minutes on either side ..
        (_at(0, 59, 59.999999), _at(1, 1, 0.000001)),

        # .. and ones open at their end or at their start.
        (_at(1, 0, 0.5), None),
        (None, _at(1, 30, 30)),
    ]

    return out

# ################################################################################################################################

def count_filter_sets() -> 'anylist':
    """ The filters the searches that the event counts answer are run with, each a dict of the ones that are set.
    """
    out:'anylist' = [
        {},
        {'sources': [AuditSource.MLLP_Outgoing]},
        {'outcomes': [AuditOutcome.Error]},
        {'object_names': [Connection_Names[0]]},
        {'sources_excluded': [AuditSource.MLLP_Channel]},
        {'statuses_excluded': ['closed']},
        {
            'sources': [AuditSource.MLLP_Outgoing],
            'event_types': [AuditEvent.Ack_Received],
            'object_names_excluded': [Connection_Names[1]],
        },
    ]

    return out

# ################################################################################################################################

def event_filter_sets() -> 'anylist':
    """ The filters the searches that only the events answer are run with - a free-text query and the outstanding filter.
    """
    out:'anylist' = [
        {'query': 'msg.1'},
        {'sources': [AuditSource.MLLP_Outgoing], 'status': Status_Outstanding},
    ]

    return out

# ################################################################################################################################

def new_filters(window:'anytuple', filter_set:'stranydict') -> 'SearchFilters':
    """ The filters of one search - a time window and the filters of one set, all the others not set.
    """
    time_from, time_to = window

    values:'stranydict' = {
        'sources': [],
        'object_names': [],
        'outcomes': [],
        'event_types': [],
        'sources_excluded': [],
        'object_names_excluded': [],
        'statuses_excluded': [],
        'query': '',
        'status': '',
    }
    values.update(filter_set)

    out = new_search_filters(time_from=time_from, time_to=time_to, **values)
    return out

# ################################################################################################################################
# ################################################################################################################################
