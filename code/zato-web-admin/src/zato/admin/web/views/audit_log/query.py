# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Reading one page of events out of the audit log database - what the filters narrow it down to and
what a page of rows is enriched with before it reaches the browser.
"""

# SQLAlchemy
from sqlalchemy import and_, func, select

# Zato
from zato.admin.web.views.audit_log.columns import _data_preview_len, _search_columns, _source_attr_columns, \
    _source_body_preview, _status_outstanding
from zato.admin.web.views.audit_log.sources import _source_outstanding, _source_resubmit
from zato.common.audit_log.api import event_attr_table, event_body_table, event_table
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
    source:'str',
    object_name:'str',
    query:'str',
    status:'str',
    time_from:'str' = '',
    time_to:'str' = '',
    ) -> 'anylist':
    """ Builds the WHERE conditions for the poll query.
    """

    # Our response to produce
    out:'anylist' = []

    out.append(event_table.c.source == source)
    out.append(event_table.c.object_name == object_name)

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
        # so a search by an MRN returns the whole trace the MRN appears in.
        if attr_names := _source_attr_columns.get(source):

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

    # The outstanding filter narrows the page down to the open exchanges of this source -
    # the sent messages or interchanges whose acknowledgment has not arrived.
    if status == _status_outstanding:
        if outstanding := _source_outstanding.get(source):
            conditions = outstanding_conditions(
                source,
                outstanding.open_event,
                outstanding.close_event,
                outstanding.needs_object_name_match,
            )
            out.extend(conditions)

    return out

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
