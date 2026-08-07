# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Reading one page of events out of the audit log database - what the filters narrow it down to and
what a page of rows is enriched with before it reaches the browser.
"""

# SQLAlchemy
from sqlalchemy import and_, func, or_, select

# Zato
from zato.admin.web.views.audit_log.columns import _data_preview_len, _row_numeric_columns, _search_columns, \
    _source_attr_columns, _source_body_preview, _status_outstanding
from zato.admin.web.views.audit_log.sources import _source_outstanding, _source_resubmit, _source_row_enrich
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, event_table
from zato.common.audit_log.query import outstanding_conditions

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

def _escape_like(query:'str') -> 'str':
    """ Escapes LIKE wildcards in a user query so they match literally.
    """
    out = query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    return out

# ################################################################################################################################

def _build_where(
    sources:'anylist',
    object_names:'anylist',
    outcomes:'anylist',
    query:'str',
    status:'str',
    time_from:'str' = '',
    time_to:'str' = '',
    event_types:'anylist' = [],
    ) -> 'anylist':
    """ Builds the WHERE conditions for the poll query. A per-source page names its one
    source, the all-events page names whichever ones its reader picked - none at all
    reads everything. The same goes for the objects - any number can be picked at once.
    """

    # Our response to produce
    out:'anylist' = []

    # No sources is the whole log - every source, every object - and no
    # object names reads the whole of whatever sources are given
    if sources:
        out.append(event_table.c.source.in_(sources))

    if object_names:
        out.append(event_table.c.object_name.in_(object_names))

    # The outcome legend switches outcomes off - naming some means show these alone,
    # naming none means the legend stands whole and filters nothing
    if outcomes:
        out.append(event_table.c.outcome.in_(outcomes))

    # An event word clicked on the page filters the log down to events of that kind alone -
    # none picked reads every kind, the same way the sources do
    if event_types:
        out.append(event_table.c.event_type.in_(event_types))

    # The page can be scoped down to a time window, e.g. one clicked on an analytics chart -
    # event times are ISO timestamps, so string prefixes compare correctly.
    if time_from:
        out.append(event_table.c.event_time_iso >= time_from)

    if time_to:
        out.append(event_table.c.event_time_iso < time_to)

    # The free-text search covers several columns, matching wildcards literally
    if query:
        escaped = _escape_like(query)
        pattern = f'%{escaped}%'

        like_parts:'anylist' = []

        for column_name in _search_columns:
            column = event_table.c[column_name]
            is_like_pattern = column.like(pattern, escape='\\')

            like_parts.append(is_like_pattern)

        # Sources with attr columns also search through them, with the attr-to-cid shape -
        # the cids of the events whose attr matches, then every event on those cids,
        # so a search by an MRN returns the whole trace the MRN appears in. With several
        # sources picked, their attrs are searched together.
        attr_names:'anylist' = []

        for source in sources:
            if source_attr_names := _source_attr_columns.get(source):
                attr_names.extend(source_attr_names)

        if attr_names:

            is_wanted_attr = event_attr_table.c.name.in_(attr_names)
            is_matching_attr = event_attr_table.c.value.like(pattern, escape='\\')

            attr_event_ids = select(event_attr_table.c.event_id)
            attr_event_ids = attr_event_ids.where(is_wanted_attr)
            attr_event_ids = attr_event_ids.where(is_matching_attr)

            is_matching_event = event_table.c.id.in_(attr_event_ids)
            matching_cids = select(event_table.c.cid).where(is_matching_event)

            is_matching_cid = event_table.c.cid.in_(matching_cids)
            like_parts.append(is_matching_cid)

        any_like_part = or_(*like_parts)
        out.append(any_like_part)

    # The outstanding filter narrows the page down to the open exchanges of one source -
    # the sent messages or interchanges whose acknowledgment has not arrived. What counts
    # as open is each source's own affair, so the filter takes one source alone, which is
    # what a per-source page sends.
    if status == _status_outstanding and len(sources) == 1:
        one_source = sources[0]

        if outstanding := _source_outstanding.get(one_source):
            conditions = outstanding_conditions(
                one_source,
                outstanding.open_event,
                outstanding.close_event,
                outstanding.needs_object_name_match,
            )
            out.extend(conditions)

    return out

# ################################################################################################################################

def _normalize_row(row:'anydict') -> 'None':
    """ Turns the NULLs of one row's text columns into empty strings, so that every cell
    the frontend reads is a value of the type its column says it is.
    """
    for key, value in row.items():

        # Numbers are left alone - a missing duration is not a duration of zero,
        # and the frontend says so rather than showing one.
        if key in _row_numeric_columns:
            continue

        if value is None:
            row[key] = ''

# ################################################################################################################################

def _group_by_source(rows:'anylist') -> 'anydict':
    """ Sorts a set of rows into one list per source. A page of a listing is all one source while
    a message's flow crosses them - a channel fanning a message out to its destinations is one
    correlation id spanning several - and what a source declares about its own events is asked
    of that source's rows alone.
    """
    out:'anydict' = {}

    for row in rows:
        source = row['source']

        if source not in out:
            out[source] = []

        out[source].append(row)

    return out

# ################################################################################################################################

def _hydrate_rows(connection:'any_', rows:'anylist') -> 'None':
    """ Brings a set of rows read straight out of the event table up to the shape the frontend reads,
    whatever sources they came from - the same shape a page of a listing arrives in, so one row
    renderer serves both.
    """
    rows_by_source = _group_by_source(rows)

    for source, source_rows in rows_by_source.items():

        # A column extracted out of the payload is extracted by the source that put it there ..
        if enrich := _source_row_enrich.get(source):
            for row in source_rows:
                enrich(row)

        # .. an attr column is read out of the attr table, one query per source ..
        _attach_attr_columns(connection, source, source_rows)

        # .. a payload kept outside the event row is previewed the same way ..
        _attach_body_previews(connection, source, source_rows)

        # .. and a row can only carry the resubmitted marker on a source that has resubmits at all.
        if source in _source_resubmit:
            _mark_resubmitted(connection, source, source_rows)
        else:
            for row in source_rows:
                row['is_resubmitted'] = False

    # Lineage and message bodies are keyed on the event id alone, so they answer for every
    # row at once no matter which source wrote it.
    _attach_lineage(connection, rows)
    _attach_body_kinds(connection, rows)

# ################################################################################################################################

def _attach_lineage(connection:'any_', rows:'anylist') -> 'None':
    """ Merges the lineage of the page rows in - what each event came out of and what came out of it.
    One event may have several parents because aggregation makes one message out of many, and several
    children because a message may be resubmitted more than once.
    """
    row_by_event_id:'anydict' = {}

    for row in rows:
        row['parents'] = []
        row['children'] = []

        row_by_event_id[row['id']] = row

    if not row_by_event_id:
        return

    is_child_here = event_link_table.c.child_event_id.in_(row_by_event_id)
    is_parent_here = event_link_table.c.parent_event_id.in_(row_by_event_id)

    statement = select(
        event_link_table.c.child_event_id,
        event_link_table.c.parent_event_id,
        event_link_table.c.link_type,
    )
    statement = statement.where(or_(is_child_here, is_parent_here))

    result = connection.execute(statement)

    for child_event_id, parent_event_id, link_type in result:

        # A link is seen from both ends when both of its events are on the page,
        # and from one end only when the other event is on a page of its own.
        if child_row := row_by_event_id.get(child_event_id):
            child_row['parents'].append({'id': parent_event_id, 'link_type': link_type})

        if parent_row := row_by_event_id.get(parent_event_id):
            parent_row['children'].append({'id': child_event_id, 'link_type': link_type})

# ################################################################################################################################

def _attach_body_kinds(connection:'any_', rows:'anylist') -> 'None':
    """ Says which message bodies each row of the page has - what was sent, what came back and what
    the other side said when it failed - so a row can offer them without asking for them first.
    """
    row_by_event_id:'anydict' = {}

    for row in rows:
        row['body_kinds'] = []

        row_by_event_id[row['id']] = row

    if not row_by_event_id:
        return

    is_wanted_event = event_body_table.c.event_id.in_(row_by_event_id)

    statement = select(event_body_table.c.event_id, event_body_table.c.kind)
    statement = statement.where(is_wanted_event)
    statement = statement.order_by(event_body_table.c.id)

    result = connection.execute(statement)

    for event_id, kind in result:
        row = row_by_event_id[event_id]

        # One event stores one body of each kind, yet a retried delivery may have stored
        # its own, so the kind is named once no matter how many rows carry it.
        if kind not in row['body_kinds']:
            row['body_kinds'].append(kind)

# ################################################################################################################################

def _mark_resubmitted(connection:'any_', source:'str', rows:'anylist') -> 'None':
    """ Flags the rows whose event was already resubmitted - a resubmit lands as a new event
    whose correlation id is the CID of the original one.
    """
    cids:'anylist' = []

    for row in rows:
        row['is_resubmitted'] = False

        if row['cid']:
            cids.append(row['cid'])

    if not cids:
        return

    is_resubmit_of_row = event_table.c.correl_id.in_(cids)

    conditions = and_(
        event_table.c.source == source,
        is_resubmit_of_row,
    )

    statement = select(event_table.c.correl_id).where(conditions)

    resubmitted = set()
    result = connection.execute(statement)

    for db_row in result:
        resubmitted.add(db_row[0])

    for row in rows:
        if row['cid'] in resubmitted:
            row['is_resubmitted'] = True

# ################################################################################################################################

def _attach_attr_columns(connection:'any_', source:'str', rows:'anylist') -> 'None':
    """ Merges this source's attr columns into the page rows - one query
    for the whole page, empty strings where an event has no such attr.
    """
    if not (attr_names := _source_attr_columns.get(source)):
        return

    row_by_event_id:'anydict' = {}

    for row in rows:
        for attr_name in attr_names:
            row[attr_name] = ''

        row_by_event_id[row['id']] = row

    if not row_by_event_id:
        return

    is_wanted_event = event_attr_table.c.event_id.in_(row_by_event_id)
    is_wanted_attr = event_attr_table.c.name.in_(attr_names)

    statement = select(event_attr_table.c.event_id, event_attr_table.c.name, event_attr_table.c.value)
    statement = statement.where(is_wanted_event)
    statement = statement.where(is_wanted_attr)

    result = connection.execute(statement)

    for event_id, name, value in result:
        row = row_by_event_id[event_id]
        row[name] = value

# ################################################################################################################################

def _attach_body_previews(connection:'any_', source:'str', rows:'anylist') -> 'None':
    """ Fills the data previews of a source whose payloads live in the body table -
    one query for the whole page, truncated in the database already.
    """
    if source not in _source_body_preview:
        return

    row_by_event_id:'anydict' = {}

    for row in rows:
        if not row['data']:
            row_by_event_id[row['id']] = row

    if not row_by_event_id:
        return

    data_preview = func.substr(event_body_table.c.data, 1, _data_preview_len)
    is_wanted_event = event_body_table.c.event_id.in_(row_by_event_id)

    statement = select(event_body_table.c.event_id, data_preview)
    statement = statement.where(is_wanted_event)
    statement = statement.order_by(event_body_table.c.id)

    result = connection.execute(statement)

    # An event with both a request and a response body previews the earlier one
    for event_id, preview in result:
        row = row_by_event_id[event_id]
        if not row['data']:
            row['data'] = preview

# ################################################################################################################################
# ################################################################################################################################
