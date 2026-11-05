# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Counting the events of a search. A search over the key columns alone is counted from the per-minute event counts,
# whole minutes from the counts and the partial minutes at the edges of the time window from the events themselves,
# so the result equals a count of the events. A search with a free-text query or the outstanding filter
# is counted from the events.

# stdlib
from dataclasses import dataclass
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import and_, BigInteger, cast, func, select

# Zato
from zato.common.audit_log.common import event_count_table, event_table
from zato.common.audit_log.search import as_list, build_search_conditions, get_outstanding_filter

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import any_, anylist, strorlist

    # Dummy assignments to satisfy type checkers
    any_ = any_
    anylist = anylist
    datetime = datetime
    strorlist = strorlist
    Connection = Connection
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

# The period of one row of the event counts
Count_Period = timedelta(minutes=1)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SearchFilters:
    """ The filters of one search, each list empty when its column is not filtered.
    """
    sources: 'anylist'
    object_names: 'anylist'
    outcomes: 'anylist'
    event_types: 'anylist'

    sources_excluded: 'anylist'
    object_names_excluded: 'anylist'
    statuses_excluded: 'anylist'

    query: str
    status: str

    time_from: 'datetime | None'
    time_to: 'datetime | None'

# ################################################################################################################################

def new_search_filters(
    *,
    sources:'anylist',
    object_names:'anylist',
    outcomes:'anylist',
    event_types:'anylist',
    sources_excluded:'anylist',
    object_names_excluded:'anylist',
    statuses_excluded:'anylist',
    query:'str',
    status:'str',
    time_from:'datetime | None',
    time_to:'datetime | None',
    ) -> 'SearchFilters':

    out = SearchFilters()

    out.sources = sources
    out.object_names = object_names
    out.outcomes = outcomes
    out.event_types = event_types

    out.sources_excluded = sources_excluded
    out.object_names_excluded = object_names_excluded
    out.statuses_excluded = statuses_excluded

    out.query = query
    out.status = status

    out.time_from = time_from
    out.time_to = time_to

    return out

# ################################################################################################################################

@dataclass(init=False)
class MinuteSplit:
    """ A time window split into the whole minutes the event counts answer for and the partial minutes
    at its edges, which only the events answer for. A bound of the whole minutes that is None is open.
    """
    has_whole_minutes: bool
    whole_from: 'datetime | None'
    whole_to: 'datetime | None'

    # The partial minutes before and after the whole ones, each a pair of its start and its end, exclusive,
    # or None when the window has no such partial minute ..
    lower_edge: 'tuple | None'
    upper_edge: 'tuple | None'

    # .. and both of them together.
    edges: 'anylist'

# ################################################################################################################################
# ################################################################################################################################

def needs_event_rows(filters:'SearchFilters') -> 'bool':
    """ Whether a search reads the events themselves - a free-text query and the outstanding filter
    look at more than the key columns of the event counts.
    """
    if filters.query:
        return True

    outstanding = get_outstanding_filter(filters.status, filters.sources)

    out = outstanding is not None
    return out

# ################################################################################################################################

def event_conditions(dialect_name:'str', filters:'SearchFilters', *, needs_time:'bool' = True) -> 'anylist':
    """ The conditions of a search over the event table, with or without its time window.
    """
    if needs_time:
        time_from = filters.time_from
        time_to = filters.time_to
    else:
        time_from = None
        time_to = None

    out = build_search_conditions(
        dialect_name,
        filters.sources,
        filters.object_names,
        filters.outcomes,
        filters.query,
        filters.status,
        time_from,
        time_to,
        filters.event_types,
        sources_excluded=filters.sources_excluded,
        object_names_excluded=filters.object_names_excluded,
        statuses_excluded=filters.statuses_excluded,
    )

    return out

# ################################################################################################################################

def count_conditions(dialect_name:'str', filters:'SearchFilters', split:'MinuteSplit') -> 'anylist':
    """ The conditions of a search over the event counts, limited to the whole minutes of its time window.
    """
    out = build_search_conditions(
        dialect_name,
        filters.sources,
        filters.object_names,
        filters.outcomes,
        event_types=filters.event_types,
        sources_excluded=filters.sources_excluded,
        object_names_excluded=filters.object_names_excluded,
        statuses_excluded=filters.statuses_excluded,
        table=event_count_table,
    )

    period_start = event_count_table.c.period_start

    if split.whole_from:
        out.append(period_start >= split.whole_from)

    if split.whole_to:
        out.append(period_start < split.whole_to)

    return out

# ################################################################################################################################

def floor_minute(value:'datetime') -> 'datetime':
    """ The start of the minute a moment falls in.
    """
    out = value.replace(second=0, microsecond=0)
    return out

# ################################################################################################################################

def ceil_minute(value:'datetime') -> 'datetime':
    """ The first start of a minute at or after a moment.
    """
    out = floor_minute(value)

    if out < value:
        out += Count_Period

    return out

# ################################################################################################################################

def split_window(time_from:'datetime | None', time_to:'datetime | None') -> 'MinuteSplit':
    """ Splits a time window into its whole minutes and the partial minutes at its edges.
    """
    out = MinuteSplit()
    out.has_whole_minutes = True
    out.whole_from = None
    out.whole_to = None
    out.lower_edge = None
    out.upper_edge = None
    out.edges = []

    # A bound that does not fall on the start of a minute leaves a partial minute at its edge ..
    if time_from:
        out.whole_from = ceil_minute(time_from)

        if time_from < out.whole_from:
            out.lower_edge = (time_from, out.whole_from)

    if time_to:
        out.whole_to = floor_minute(time_to)

        if out.whole_to < time_to:
            out.upper_edge = (out.whole_to, time_to)

    # .. and a window that holds no whole minute at all is read from the events as one range.
    if out.whole_from:
        if out.whole_to:
            if out.whole_from >= out.whole_to:
                out.has_whole_minutes = False
                out.whole_from = None
                out.whole_to = None
                out.lower_edge = (time_from, time_to)
                out.upper_edge = None

    if out.lower_edge:
        out.edges.append(out.lower_edge)

    if out.upper_edge:
        out.edges.append(out.upper_edge)

    return out

# ################################################################################################################################

def time_range(start:'datetime', end:'datetime') -> 'any_':
    """ The condition that an event falls between two moments, the end exclusive.
    """
    event_time = event_table.c.event_time

    is_after_start = event_time >= start
    is_before_end = event_time < end

    out = and_(is_after_start, is_before_end)
    return out

# ################################################################################################################################

def count_matching(connection:'Connection', filters:'SearchFilters') -> 'int':
    """ The number of events a search matches.
    """
    dialect_name = connection.dialect.name

    # A search the event counts cannot answer counts the events themselves ..
    if needs_event_rows(filters):
        conditions = event_conditions(dialect_name, filters)

        statement = select(func.count())
        statement = statement.select_from(event_table)
        statement = statement.where(*conditions)

        out = connection.execute(statement).scalar_one()
        return out

    # .. while any other one sums the counts of its whole minutes ..
    split = split_window(filters.time_from, filters.time_to)
    parts:'anylist' = []

    if split.has_whole_minutes:
        conditions = count_conditions(dialect_name, filters, split)

        count_sum = func.sum(event_count_table.c.event_count)
        count_sum = cast(count_sum, BigInteger)

        whole_minutes = select(count_sum)
        whole_minutes = whole_minutes.where(*conditions)
        whole_minutes = whole_minutes.scalar_subquery()

        parts.append(whole_minutes)

    # .. and counts the events of each of its partial minutes, through the time index ..
    conditions = event_conditions(dialect_name, filters, needs_time=False)

    for start, end in split.edges:
        in_edge = time_range(start, end)

        edge_events = select(func.count())
        edge_events = edge_events.select_from(event_table)
        edge_events = edge_events.where(*conditions)
        edge_events = edge_events.where(in_edge)
        edge_events = edge_events.scalar_subquery()

        parts.append(edge_events)

    # .. all in one statement.
    statement = select(*parts)
    row = connection.execute(statement).one()

    out = 0

    for value in row:

        # A sum over no rows is NULL
        if value is not None:
            out += value

    return out

# ################################################################################################################################

def count_events(
    engine:'Engine',
    *,
    source:'strorlist' = '',
    object_name:'strorlist' = '',
    outcome:'strorlist' = '',
    event_type:'strorlist' = '',
    query:'str' = '',
    status:'str' = '',
    time_from:'datetime | None' = None,
    time_to:'datetime | None' = None,
    ) -> 'int':
    """ Returns the number of audit events matching the filters that search_events accepts.
    """
    sources = as_list(source)
    object_names = as_list(object_name)
    outcomes = as_list(outcome)
    event_types = as_list(event_type)

    filters = new_search_filters(
        sources=sources,
        object_names=object_names,
        outcomes=outcomes,
        event_types=event_types,
        sources_excluded=[],
        object_names_excluded=[],
        statuses_excluded=[],
        query=query,
        status=status,
        time_from=time_from,
        time_to=time_to,
    )

    with engine.connect() as connection:
        out = count_matching(connection, filters)

    return out

# ################################################################################################################################
# ################################################################################################################################
