# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Searching the audit log - the WHERE conditions every reader builds on and the query
# functions that return pages of events, shared by the Dashboard and by services.

# SQLAlchemy
from sqlalchemy import func, or_, select, union

# Zato
from zato.common.audit_log.common import event_attr_table, event_table, source_attr_names, Status_Outstanding
from zato.common.audit_log.query import outstanding_conditions, source_outstanding
from zato.common.audit_log.search_index import narrow_attr_search, narrow_event_search, search_columns
from zato.common.db_env.common import Type_PostgreSQL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from sqlalchemy import Table
    from sqlalchemy.engine import Engine
    from zato.common.audit_log.query import OutstandingFilter
    from zato.common.typing_ import anylist, dictlist, strdatetimedict, strorlist

    # Dummy assignments to satisfy type checkers
    anylist = anylist
    datetime = datetime
    dictlist = dictlist
    strdatetimedict = strdatetimedict
    strorlist = strorlist
    Engine = Engine
    OutstandingFilter = OutstandingFilter
    Table = Table

# ################################################################################################################################
# ################################################################################################################################

# The first page of results
Default_Page = 1

# How many events one page of results holds
Default_Page_Size = 50

# The columns a search returns for each event.
result_columns = ('id', 'cid', 'source', 'event_type', 'object_name', 'msg_id', 'correl_id',
    'ext_client_id', 'event_time', 'endpoint', 'size', 'outcome', 'classification', 'status',
    'duration_ms', 'data')

# ################################################################################################################################
# ################################################################################################################################

def _escape_like(query:'str') -> 'str':
    """ Escapes LIKE wildcards in a user query so they match literally.
    """
    out = query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    return out

# ################################################################################################################################

def as_list(value:'strorlist') -> 'anylist':
    """ Returns the value as a list - one string becomes a one-element list,
    an empty string becomes an empty list and a list is returned as given.
    """
    if isinstance(value, str):
        if value:
            out = [value]
        else:
            out = []
    else:
        out = list(value)

    return out

# ################################################################################################################################

def build_search_conditions(
    dialect_name:'str',
    sources:'anylist' = [],
    object_names:'anylist' = [],
    outcomes:'anylist' = [],
    query:'str' = '',
    status:'str' = '',
    time_from:'datetime | None' = None,
    time_to:'datetime | None' = None,
    event_types:'anylist' = [],
    sources_excluded:'anylist' = [],
    object_names_excluded:'anylist' = [],
    statuses_excluded:'anylist' = [],
    table:'Table' = event_table,
    ) -> 'anylist':
    """ Builds the WHERE conditions of one search. Every filter is optional - an empty list
    leaves its column unfiltered. Sources, object names and statuses can also be excluded,
    which returns everything except the ones named. The conditions over the key columns apply
    to the given table, which is the event table or the table of per-minute event counts,
    while the time window, the free-text query and the outstanding filter apply to the event table alone.
    """

    # Our response to produce
    out:'anylist' = []

    # An empty sources list reads every source and an empty object names list reads every object
    if sources:
        out.append(table.c.source.in_(sources))

    if object_names:
        out.append(table.c.object_name.in_(object_names))

    # Exclusions remove the named sources and objects from whatever the filters above cover ..
    if sources_excluded:
        out.append(table.c.source.notin_(sources_excluded))

    if object_names_excluded:
        out.append(table.c.object_name.notin_(object_names_excluded))

    # .. and excluded statuses leave out the rows of that status.
    if statuses_excluded:
        out.append(table.c.status.notin_(statuses_excluded))

    # Only the named outcomes are returned, none named returns all
    if outcomes:
        out.append(table.c.outcome.in_(outcomes))

    # The same for event types
    if event_types:
        out.append(table.c.event_type.in_(event_types))

    # The search can be scoped down to a time window.
    if time_from:
        out.append(event_table.c.event_time >= time_from)

    if time_to:
        out.append(event_table.c.event_time < time_to)

    # The free-text search covers several columns, matching wildcards literally
    if query:
        escaped = _escape_like(query)
        pattern = f'%{escaped}%'

        like_parts:'anylist' = []

        for column_name in search_columns:
            column = event_table.c[column_name]
            is_like_pattern = column.like(pattern, escape='\\')

            like_parts.append(is_like_pattern)

        # The native text index of the database finds the candidate rows and LIKE confirms them.
        any_column_like = or_(*like_parts)
        any_column_like = narrow_event_search(dialect_name, event_table, query, pattern, any_column_like)

        matching_parts:'anylist' = [any_column_like]

        # Sources with searchable attributes also search through them, with the attr-to-cid
        # shape - the cids of the events whose attr matches, then every event on those cids,
        # so a search by an MRN returns the whole trace the MRN appears in. With several
        # sources picked, their attrs are searched together.
        attr_names:'anylist' = []

        for source in sources:
            if source_names := source_attr_names.get(source):
                attr_names.extend(source_names)

        if attr_names:

            is_wanted_attr = event_attr_table.c.name.in_(attr_names)
            is_matching_attr = event_attr_table.c.value.like(pattern, escape='\\')
            is_matching_attr = narrow_attr_search(dialect_name, event_attr_table, query, is_matching_attr)

            attr_event_ids = select(event_attr_table.c.event_id)
            attr_event_ids = attr_event_ids.where(is_wanted_attr)
            attr_event_ids = attr_event_ids.where(is_matching_attr)

            is_matching_event = event_table.c.id.in_(attr_event_ids)
            matching_cids = select(event_table.c.cid).where(is_matching_event)

            is_matching_cid = event_table.c.cid.in_(matching_cids)
            matching_parts.append(is_matching_cid)

        # PostgreSQL reads an OR of the two parts with a scan of the whole table, so there each part
        # selects its ids through its own index and the event matches when its id is in their union.
        if len(matching_parts) > 1:
            if dialect_name == Type_PostgreSQL:
                matching_ids:'anylist' = []

                for part in matching_parts:
                    part_ids = select(event_table.c.id)
                    part_ids = part_ids.where(part)
                    matching_ids.append(part_ids)

                all_matching_ids = union(*matching_ids)
                any_matching_part = event_table.c.id.in_(all_matching_ids)

            else:
                any_matching_part = or_(*matching_parts)

        else:
            any_matching_part = any_column_like

        out.append(any_matching_part)

    # The outstanding filter narrows the search down to the open exchanges of one source -
    # the sent messages or interchanges whose acknowledgment has not arrived.
    if outstanding := get_outstanding_filter(status, sources):
        one_source = sources[0]

        # A source whose events are single rows updated in place has no exchange
        # to pair - open there means the row still carries its in-progress outcome ..
        if outstanding.open_outcome:
            out.append(event_table.c.outcome == outstanding.open_outcome)

        # .. everywhere else an open exchange is a sent message whose acknowledgment
        # has not arrived.
        else:
            conditions = outstanding_conditions(one_source)
            out.extend(conditions)

    return out

# ################################################################################################################################

def get_outstanding_filter(status:'str', sources:'anylist') -> 'OutstandingFilter | None':
    """ The outstanding filter a search applies, if any. Each source defines what counts as open,
    so the filter applies only with exactly one source that defines it.
    """
    out = None

    if status == Status_Outstanding:
        if len(sources) == 1:
            one_source = sources[0]

            if one_source in source_outstanding:
                out = source_outstanding[one_source]

    return out

# ################################################################################################################################

def search_events(
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
    page:'int' = Default_Page,
    page_size:'int' = Default_Page_Size,
    ) -> 'dictlist':
    """ Returns one page of audit events matching the filters, newest first,
    each event as a dict of the columns in result_columns. Each of source,
    object_name, outcome and event_type accepts one value or a list of values.
    """

    # Each filter accepts one value or a list of values,
    # while build_search_conditions always takes lists ..
    sources = as_list(source)
    object_names = as_list(object_name)
    outcomes = as_list(outcome)
    event_types = as_list(event_type)

    # .. so everything the filters narrow the log down to ..
    conditions = build_search_conditions(
        engine.dialect.name,
        sources=sources,
        object_names=object_names,
        outcomes=outcomes,
        query=query,
        status=status,
        time_from=time_from,
        time_to=time_to,
        event_types=event_types,
    )

    # .. read as the columns every result row carries ..
    columns:'anylist' = []

    for column_name in result_columns:
        column = event_table.c[column_name]
        columns.append(column)

    statement = select(*columns)
    statement = statement.where(*conditions)

    # .. ordered by event time, newest first, with ids breaking ties between events
    # of the same moment ..
    newest_first = event_table.c.event_time.desc()
    then_by_id = event_table.c.id.desc()
    statement = statement.order_by(newest_first, then_by_id)

    # .. and only the requested page is returned.
    offset = (page - Default_Page) * page_size
    statement = statement.offset(offset)
    statement = statement.limit(page_size)

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.mappings().all()

    out:'dictlist' = []

    for row in rows:
        out.append(dict(row))

    return out

# ################################################################################################################################

def last_seen(engine:'Engine', source:'str') -> 'strdatetimedict':
    """ Returns the newest event time of each of one source's objects - a dict mapping
    each object name to a datetime in UTC.
    """
    newest = func.max(event_table.c.event_time)

    statement = select(event_table.c.object_name, newest)
    statement = statement.where(event_table.c.source == source)
    statement = statement.group_by(event_table.c.object_name)

    with engine.connect() as connection:
        result = connection.execute(statement)
        rows = result.all()

    out:'strdatetimedict' = {}

    for object_name, newest_time in rows:
        out[object_name] = newest_time

    return out

# ################################################################################################################################
# ################################################################################################################################
