# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The activity strip of the audit log - the events of a search cut into equal time buckets between the first
# and the last matching event, counted per outcome. Each minute of the event counts that lies within one bucket
# adds its counts to that bucket, and the minutes that a bucket edge or the edge of the time window cuts
# are counted from the events. A search with a free-text query or the outstanding filter, and buckets
# shorter than a minute, are counted from the events, grouped by the database.

# stdlib
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import BigInteger, cast, Float, func, select, union_all
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import FunctionElement

# Zato
from zato.common.audit_log.common import event_count_table, event_table
from zato.common.audit_log.listing import count_conditions, Count_Period, event_conditions, needs_event_rows, \
    split_window, time_range
from zato.common.db_env.common import Type_PostgreSQL, Type_SQLite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Connection
    from sqlalchemy.sql.compiler import SQLCompiler
    from zato.common.audit_log.listing import MinuteSplit, SearchFilters
    from zato.common.typing_ import any_, anydict, anylist

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anydict = anydict
    anylist = anylist
    datetime = datetime
    Connection = Connection
    MinuteSplit = MinuteSplit
    SearchFilters = SearchFilters
    SQLCompiler = SQLCompiler

# ################################################################################################################################
# ################################################################################################################################

# The length of a minute of the event counts in milliseconds ..
_minute_ms = Count_Period.total_seconds() * 1000

# .. and the offset from its start that lies past its last microsecond and before the next minute,
# with a margin of half a microsecond for the rounding of epoch milliseconds.
_minute_end_offset_ms = _minute_ms - 0.0005

# ################################################################################################################################
# ################################################################################################################################

class _EpochMs(FunctionElement):
    """ A moment as milliseconds since the Unix epoch, compiled to the date functions of each database.
    """
    type = Float()
    name = 'epoch_ms'
    inherit_cache = True

# ################################################################################################################################

@compiles(_EpochMs, Type_SQLite)
def compile_epoch_ms_sqlite(element:'_EpochMs', compiler:'SQLCompiler', **kwargs:'any_') -> 'str':

    # SQLite keeps the moment as text. Its whole seconds are read from the first 19 characters, without the fraction,
    # which strftime would round to milliseconds, up to the next second at the end of one, and its microseconds start
    # at the 21st character.
    column = compiler.process(element.clauses, **kwargs)
    out = "(CAST(strftime('%s', substr({0}, 1, 19)) AS INTEGER) * 1000.0 + CAST(substr({0}, 21, 6) AS INTEGER) / 1000.0)"
    out = out.format(column)

    return out

# ################################################################################################################################

@compiles(_EpochMs, Type_PostgreSQL)
def compile_epoch_ms_postgresql(element:'_EpochMs', compiler:'SQLCompiler', **kwargs:'any_') -> 'str':
    column = compiler.process(element.clauses, **kwargs)
    out = f'(EXTRACT(EPOCH FROM {column}) * 1000)'

    return out

# ################################################################################################################################

class _BucketIndex(FunctionElement):
    """ A bucket position rounded down to a whole bucket. SQLite truncates it towards zero instead, which differs
    from rounding down only below zero, and positions below zero are moved to the first bucket by the caller.
    """
    type = Float()
    name = 'bucket_index'
    inherit_cache = True

# ################################################################################################################################

@compiles(_BucketIndex, Type_SQLite)
def compile_bucket_index_sqlite(element:'_BucketIndex', compiler:'SQLCompiler', **kwargs:'any_') -> 'str':
    position = compiler.process(element.clauses, **kwargs)
    out = f'CAST({position} AS INTEGER)'

    return out

# ################################################################################################################################

@compiles(_BucketIndex, Type_PostgreSQL)
def compile_bucket_index_postgresql(element:'_BucketIndex', compiler:'SQLCompiler', **kwargs:'any_') -> 'str':
    position = compiler.process(element.clauses, **kwargs)
    out = f'floor({position})'

    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MatchWindow:
    """ The moments of the first and the last event a search matches.
    """
    first_time: 'datetime'
    last_time: 'datetime'

# ################################################################################################################################

@dataclass(init=False)
class _BucketScale:
    """ Where the buckets of the strip start and how long each one is, in epoch milliseconds, and how many there are.
    """
    start_ms: float
    bucket_ms: float
    bucket_count: int

# ################################################################################################################################
# ################################################################################################################################

def _event_time_at_end(connection:'Connection', conditions:'anylist', is_first:'bool') -> 'datetime | None':
    """ The moment of the first or the last event matching the conditions, None when there is none.
    """
    event_time = event_table.c.event_time

    if is_first:
        moment = func.min(event_time)
    else:
        moment = func.max(event_time)

    statement = select(moment)
    statement = statement.where(*conditions)

    out = connection.execute(statement).scalar_one()
    return out

# ################################################################################################################################

def _event_time_in_counts(
    connection:'Connection',
    filters:'SearchFilters',
    split:'MinuteSplit',
    is_first:'bool',
    ) -> 'datetime | None':
    """ The moment of the first or the last matching event among the whole minutes of the event counts, read
    from the events of the first or the last minute whose count is not zero, None when every count is zero.
    """
    dialect_name = connection.dialect.name
    period_start = event_count_table.c.period_start

    if is_first:
        order_by = period_start.asc()
    else:
        order_by = period_start.desc()

    # The minute comes from the event counts ..
    conditions = count_conditions(dialect_name, filters, split)
    has_events = func.sum(event_count_table.c.event_count) > 0

    statement = select(period_start)
    statement = statement.where(*conditions)
    statement = statement.group_by(period_start)
    statement = statement.having(has_events)
    statement = statement.order_by(order_by)
    statement = statement.limit(1)

    minute_start = connection.execute(statement).scalar()

    if minute_start is None:
        return None

    # .. and the moment within it from the events.
    minute_end = minute_start + Count_Period
    minute_range = time_range(minute_start, minute_end)

    minute_conditions = event_conditions(dialect_name, filters, needs_time=False)
    minute_conditions.append(minute_range)

    out = _event_time_at_end(connection, minute_conditions, is_first)
    return out

# ################################################################################################################################

def _find_end(connection:'Connection', filters:'SearchFilters', split:'MinuteSplit', is_first:'bool') -> 'datetime | None':
    """ The first or the last matching moment, read from the parts of the time window in the order
    of time - the partial minute at the start, the whole minutes and the partial minute at the end.
    """
    dialect_name = connection.dialect.name
    key_conditions = event_conditions(dialect_name, filters, needs_time=False)

    # Each part is an edge range or None, which stands for the whole minutes
    parts:'anylist' = []

    if split.lower_edge:
        parts.append(split.lower_edge)

    if split.has_whole_minutes:
        parts.append(None)

    if split.upper_edge:
        parts.append(split.upper_edge)

    # The last moment is looked for from the end of the window
    if not is_first:
        parts.reverse()

    for part in parts:

        if part is None:
            moment = _event_time_in_counts(connection, filters, split, is_first)

        else:
            start, end = part
            edge_range = time_range(start, end)

            conditions = list(key_conditions)
            conditions.append(edge_range)

            moment = _event_time_at_end(connection, conditions, is_first)

        if moment is not None:
            out = moment
            break

    else:
        out = None

    return out

# ################################################################################################################################

def get_match_window(connection:'Connection', filters:'SearchFilters') -> 'MatchWindow | None':
    """ The moments of the first and the last event a search matches, None when it matches no event.
    """
    dialect_name = connection.dialect.name

    # A search the event counts cannot answer reads both moments from the events in one statement,
    # which evaluates the free-text query once ..
    if needs_event_rows(filters):
        conditions = event_conditions(dialect_name, filters)

        event_time = event_table.c.event_time
        first_moment = func.min(event_time)
        last_moment = func.max(event_time)

        statement = select(first_moment, last_moment)
        statement = statement.where(*conditions)

        first_time, last_time = connection.execute(statement).one()

    # .. while any other one reads them from the first and last minute that holds a matching event.
    else:
        split = split_window(filters.time_from, filters.time_to)

        first_time = _find_end(connection, filters, split, True)
        last_time = _find_end(connection, filters, split, False)

    if first_time is None:
        return None

    if last_time is None:
        return None

    out = MatchWindow()
    out.first_time = first_time
    out.last_time = last_time

    return out

# ################################################################################################################################
# ################################################################################################################################

def _clamp(index:'any_', bucket_count:'int') -> 'int':
    """ The bucket an index stands for - a position before the first bucket belongs to the first one,
    and the very last moment of the window, which falls one past the last bucket, belongs to the last one.
    """
    out = int(index)

    if out < 0:
        out = 0

    if out >= bucket_count:
        out = bucket_count - 1

    return out

# ################################################################################################################################

def _bucket_position(moment_ms:'any_', scale:'_BucketScale') -> 'any_':
    """ The bucket a moment in epoch milliseconds falls in, as an SQL expression.
    """
    offset_ms = moment_ms - scale.start_ms
    position = offset_ms / scale.bucket_ms

    out = _BucketIndex(position)
    return out

# ################################################################################################################################

def _add_count(buckets:'anylist', index:'int', outcome:'str', count:'int') -> 'None':
    """ Adds a number of events of one outcome to a bucket.
    """
    counts = buckets[index]

    if outcome not in counts:
        counts[outcome] = 0

    counts[outcome] += count

# ################################################################################################################################

def _merge_ranges(ranges:'anylist') -> 'anylist':
    """ The time ranges in the order of time, with each run of ranges that adjoin one another joined into one,
    which the time index reads with one scan.
    """
    out:'anylist' = []

    for start, end in sorted(ranges):

        if out:
            last_start, last_end = out[-1]

            # This range starts where the previous one ends, so the two are one ..
            if last_end == start:
                out[-1] = (last_start, end)
                continue

        # .. while any other one starts a new run.
        out.append((start, end))

    return out

# ################################################################################################################################

def _add_event_buckets(
    connection:'Connection',
    conditions:'anylist',
    ranges:'anylist',
    scale:'_BucketScale',
    buckets:'anylist',
    ) -> 'None':
    """ Counts the events matching the conditions per bucket and outcome in one statement and adds them to the buckets.
    With time ranges given, only the events within them are counted, each range read through the time index on its own.
    """
    event_ms = _EpochMs(event_table.c.event_time)
    bucket = _bucket_position(event_ms, scale)
    bucket = bucket.label('bucket')

    # The bucket of each event is computed once, in a subquery, and the outer query groups by it ..
    positions = select(bucket, event_table.c.outcome)
    positions = positions.where(*conditions)

    # .. and a set of time ranges is a union of one such subquery per range rather than one OR of them,
    # which the databases read with a scan of everything between the first range and the last.
    if ranges:
        range_positions:'anylist' = []

        for start, end in ranges:
            in_range = positions.where(event_table.c.event_time >= start)
            in_range = in_range.where(event_table.c.event_time < end)
            range_positions.append(in_range)

        positions = union_all(*range_positions)

    positions = positions.subquery()

    event_count = func.count()

    statement = select(positions.c.bucket, positions.c.outcome, event_count)
    statement = statement.group_by(positions.c.bucket, positions.c.outcome)

    result = connection.execute(statement)

    for index, outcome, count in result:
        bucket_index = _clamp(index, scale.bucket_count)
        _add_count(buckets, bucket_index, outcome, count)

# ################################################################################################################################

def _add_count_buckets(
    connection:'Connection',
    filters:'SearchFilters',
    split:'MinuteSplit',
    scale:'_BucketScale',
    buckets:'anylist',
    ) -> 'anylist':
    """ Adds the counts of the whole minutes that lie within one bucket to the buckets, and returns the starts
    of the minutes that a bucket edge cuts, which are counted from the events.
    """
    dialect_name = connection.dialect.name
    period_start = event_count_table.c.period_start

    # The bucket of the first and of the last moment of each minute ..
    minute_start_ms = _EpochMs(period_start)
    minute_end_ms = minute_start_ms + _minute_end_offset_ms

    first_bucket = _bucket_position(minute_start_ms, scale)
    first_bucket = first_bucket.label('first_bucket')

    last_bucket = _bucket_position(minute_end_ms, scale)
    last_bucket = last_bucket.label('last_bucket')

    conditions = count_conditions(dialect_name, filters, split)

    positions = select(first_bucket, last_bucket, event_count_table.c.outcome, event_count_table.c.event_count, period_start)
    positions = positions.where(*conditions)
    positions = positions.subquery()

    # .. with the minutes of the same buckets and outcome summed, and those that hold no events left out ..
    count_sum = func.sum(positions.c.event_count)
    count_sum = cast(count_sum, BigInteger)

    has_events = func.sum(positions.c.event_count) != 0

    first_minute = func.min(positions.c.period_start)
    last_minute = func.max(positions.c.period_start)

    statement = select(positions.c.first_bucket, positions.c.last_bucket, positions.c.outcome, count_sum,
        first_minute, last_minute)
    statement = statement.group_by(positions.c.first_bucket, positions.c.last_bucket, positions.c.outcome)
    statement = statement.having(has_events)

    result = connection.execute(statement)

    # .. a minute within one bucket adds its counts to it, and one that two buckets share is counted
    # from the events, which a minute whose buckets are equal after clamping is not.
    out:'anylist' = []

    for first_index, last_index, outcome, count, first_minute_start, last_minute_start in result:

        first_index = _clamp(first_index, scale.bucket_count)
        last_index = _clamp(last_index, scale.bucket_count)

        if first_index == last_index:
            _add_count(buckets, first_index, outcome, count)

        else:
            if first_minute_start not in out:
                out.append(first_minute_start)

            if last_minute_start not in out:
                out.append(last_minute_start)

    return out

# ################################################################################################################################

def count_by_bucket(
    connection:'Connection',
    filters:'SearchFilters',
    start_ms:'float',
    bucket_ms:'float',
    bucket_count:'int',
    ) -> 'anylist':
    """ The number of matching events of each outcome in each of the buckets, as one dict per bucket,
    where each bucket is bucket_ms long and the first one starts at start_ms.
    """
    dialect_name = connection.dialect.name

    scale = _BucketScale()
    scale.start_ms = start_ms
    scale.bucket_ms = bucket_ms
    scale.bucket_count = bucket_count

    # Our response to produce
    out:'anylist' = []

    for _ in range(bucket_count):
        counts:'anydict' = {}
        out.append(counts)

    # A search the event counts cannot answer, and buckets shorter than a minute, are counted from the events ..
    if needs_event_rows(filters):
        conditions = event_conditions(dialect_name, filters)
        _add_event_buckets(connection, conditions, [], scale, out)

        return out

    if bucket_ms < _minute_ms:
        conditions = event_conditions(dialect_name, filters)
        _add_event_buckets(connection, conditions, [], scale, out)

        return out

    # .. and any other one adds up the counts of its whole minutes ..
    split = split_window(filters.time_from, filters.time_to)
    event_ranges = list(split.edges)

    if split.has_whole_minutes:
        cut_minutes = _add_count_buckets(connection, filters, split, scale, out)

        for minute_start in cut_minutes:
            minute_end = minute_start + Count_Period
            event_ranges.append((minute_start, minute_end))

    # .. with the minutes the bucket edges cut and the partial minutes at the edges of the window counted from the events.
    if event_ranges:
        conditions = event_conditions(dialect_name, filters, needs_time=False)
        event_ranges = _merge_ranges(event_ranges)

        _add_event_buckets(connection, conditions, event_ranges, scale, out)

    return out

# ################################################################################################################################
# ################################################################################################################################
