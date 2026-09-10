# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from datetime import datetime, timezone

# SQLAlchemy
from sqlalchemy import func, select

# Django
from django.http import HttpResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.admin.web.views.audit_log.columns import _data_preview_length, _default_page, _flow_columns, _row_columns, \
    _status_outstanding
from zato.admin.web.views.audit_log.query import _hydrate_rows, _normalize_row
from zato.admin.web.views.audit_log.trace import attach_trace_lines
from zato.common.audit_log.api import event_table, get_audit_engine, AuditSource
from zato.common.audit_log.flow import get_flow_ids, resolve_seed
from zato.common.audit_log.search import build_search_conditions

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

def _read_rows_by_id(connection:'any_', select_columns:'anylist', event_ids:'anylist') -> 'anylist':
    """ The rows with the given ids, normalized but not hydrated.
    """
    out:'anylist' = []

    is_wanted = event_table.c.id.in_(event_ids)

    query = select(*select_columns)
    query = query.where(is_wanted)

    result = connection.execute(query)

    for db_row in result:
        row_values = zip(_row_columns, db_row)
        row:'anydict' = dict(row_values)
        _normalize_row(row)
        out.append(row)

    return out

# ################################################################################################################################

@method_allowed('POST')
def poll(req:'any_') -> 'HttpResponse':
    """ Returns one page of audit events as JSON, in the shape the detail-kit pagination expects.
    """
    body = json.loads(req.body)

    sources = body['sources']
    sources_excluded = body['sources_excluded']
    object_names = body['object_names']
    object_names_excluded = body['object_names_excluded']
    outcomes = body['outcomes']
    query = body['query']
    status = body['status']
    time_from = body['time_from']
    time_to = body['time_to']
    event_types = body['event_types']
    statuses_excluded = body['statuses_excluded']

    # The rows the client keeps watching - the running ones and the selected one - read again alongside the page.
    watched_ids = body['watched_ids']

    page = body['page']
    page_size = body['page_size']

    if page < _default_page:
        page = _default_page

    where_conditions = build_search_conditions(
        sources, object_names, outcomes, query, status, time_from, time_to, event_types,
        sources_excluded=sources_excluded, object_names_excluded=object_names_excluded,
        statuses_excluded=statuses_excluded)

    rows:'anylist' = []
    updated:'anylist' = []

    # The same select column order as in _row_columns
    select_columns:'anylist' = []

    for column_name in _row_columns:
        column = event_table.c[column_name]
        select_columns.append(column)

    # Outstanding items are shown oldest first - the longest-waiting exchange is the most
    # urgent one - while the regular view shows the newest events first. It is the time an
    # event happened that orders them, not the order they were written in, so that a page
    # and the window it is read through agree on what newest means. Two events of the same
    # moment are told apart by their ids.
    if status == _status_outstanding:
        order_by = [event_table.c.event_time_iso.asc(), event_table.c.id.asc()]
    else:
        order_by = [event_table.c.event_time_iso.desc(), event_table.c.id.desc()]

    # Build both queries upfront ..
    event_count = func.count()

    count_query = select(event_count)
    count_query = count_query.select_from(event_table)
    count_query = count_query.where(*where_conditions)

    offset = (page - 1) * page_size

    page_query = select(*select_columns)
    page_query = page_query.where(*where_conditions)
    page_query = page_query.order_by(*order_by)
    page_query = page_query.limit(page_size)
    page_query = page_query.offset(offset)

    # .. and run them against the shared audit log database.
    engine = get_audit_engine()

    with engine.connect() as connection:

        count_result = connection.execute(count_query)
        total = count_result.scalar()

        page_result = connection.execute(page_query)

        for db_row in page_result:
            row_values = zip(_row_columns, db_row)
            row:'anydict' = dict(row_values)

            # A column the database has no value for is an empty one to the frontend ..
            _normalize_row(row)

            # .. an MCP row additionally says what response shaping did, read out of
            # the full data document before it is cut down to a preview ..
            data = row['data']

            if row['source'] == AuditSource.MCP:
                if data:
                    attach_trace_lines(row, data)

            rows.append(row)

        # Everything else the frontend reads off a row - this source's own extra columns, its
        # attrs, a preview of a payload kept elsewhere, the lineage, the message bodies there
        # are to read and the resubmitted marker - is merged in here, a query per set of rows
        # rather than one per row. The rows still carry their full data documents because
        # the per-source enrichment reads columns out of them, e.g. an AS4 conversation id.
        _hydrate_rows(connection, rows)

        # The watched rows the page no longer holds are read on their own.
        page_ids = set()

        for row in rows:
            page_ids.add(row['id'])

        wanted_ids:'anylist' = []

        for watched_id in watched_ids:
            if watched_id not in page_ids:
                wanted_ids.append(watched_id)

        if wanted_ids:
            updated = _read_rows_by_id(connection, select_columns, wanted_ids)
            _hydrate_rows(connection, updated)

        # Only a preview of each payload goes into the table.
        for row in rows:
            row['data'] = row['data'][:_data_preview_length]

        for row in updated:
            row['data'] = row['data'][:_data_preview_length]

    response_json = json.dumps({'rows': rows, 'total': total, 'page': page, 'updated': updated})
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')

    return out

# ################################################################################################################################

# The activity strip never answers with more buckets than this, nor with fewer,
# whatever width the screen reports
_strip_max_buckets = 80
_strip_min_buckets = 16

# Events all within one short burst still spread over at least this much - an hour -
# so one busy minute does not fill the whole strip
_strip_min_span_ms = 60 * 60 * 1000

# ################################################################################################################################

def _strip_edge_iso(epoch_ms:'float') -> 'str':
    """ An epoch-ms moment as an ISO string of the very format the event times are stored in,
    so a bucket's edges can serve as time filters over them.
    """
    moment = datetime.fromtimestamp(epoch_ms / 1000, timezone.utc)

    out = moment.isoformat()

    return out

# ################################################################################################################################

@method_allowed('POST')
def strip(req:'any_') -> 'HttpResponse':
    """ Returns the matching events cut into time buckets with per-outcome counts, for the
    activity strip over the listing - the same filter keys the poll reads, without paging.
    """
    body = json.loads(req.body)

    sources = body['sources']
    sources_excluded = body['sources_excluded']
    object_names = body['object_names']
    object_names_excluded = body['object_names_excluded']
    outcomes = body['outcomes']
    query = body['query']
    status = body['status']
    time_from = body['time_from']
    time_to = body['time_to']
    event_types = body['event_types']
    statuses_excluded = body['statuses_excluded']

    # How many buckets the screen has room for, kept within what the strip may answer with
    bucket_count = body['bucket_count']

    if bucket_count > _strip_max_buckets:
        bucket_count = _strip_max_buckets

    if bucket_count < _strip_min_buckets:
        bucket_count = _strip_min_buckets

    where_conditions = build_search_conditions(
        sources, object_names, outcomes, query, status, time_from, time_to, event_types,
        sources_excluded=sources_excluded, object_names_excluded=object_names_excluded,
        statuses_excluded=statuses_excluded)

    events_query = select(event_table.c.event_time_iso, event_table.c.outcome)
    events_query = events_query.where(*where_conditions)

    engine = get_audit_engine()

    # Each matching event as its moment in epoch ms and its outcome
    events:'anylist' = []

    with engine.connect() as connection:
        result = connection.execute(events_query)

        for event_time_iso, outcome in result:
            moment = datetime.fromisoformat(event_time_iso)
            event_ms = moment.timestamp() * 1000

            events.append((event_ms, outcome))

    # With nothing matching there is nothing to draw and the frontend says so in words
    if not events:
        response_json = json.dumps({'buckets': []})
        response_bytes = response_json.encode('utf-8')

        out = HttpResponse(response_bytes, content_type='application/json')

        return out

    # The window is what the events cover ..
    times:'anylist' = []

    for event_ms, _ in events:
        times.append(event_ms)

    min_ms = min(times)
    max_ms = max(times)

    # .. stretched to the least window when they all sit within one short burst ..
    span_ms = max_ms - min_ms

    if span_ms < _strip_min_span_ms:
        min_ms = max_ms - _strip_min_span_ms
        span_ms = _strip_min_span_ms

    # .. and it is cut into as many equal buckets as were asked for.
    bucket_ms = span_ms / bucket_count

    buckets:'anylist' = []

    for bucket_index in range(bucket_count):
        start_ms = min_ms + bucket_index * bucket_ms
        end_ms = min_ms + (bucket_index + 1) * bucket_ms

        buckets.append({
            'start_iso': _strip_edge_iso(start_ms),
            'end_iso': _strip_edge_iso(end_ms),
            'counts': {},
        })

    # Each event counts into the bucket its moment falls in, under its own outcome
    for event_ms, outcome in events:
        offset_ms = event_ms - min_ms
        target = int(offset_ms // bucket_ms)

        # The window's very last moment belongs to the last bucket rather than one past it
        if target >= bucket_count:
            target = bucket_count - 1

        counts = buckets[target]['counts']

        if outcome not in counts:
            counts[outcome] = 0

        counts[outcome] += 1

    response_json = json.dumps({'buckets': buckets})
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')

    return out

# ################################################################################################################################

def _read_flow_rows(connection:'any_', seed_id:'int') -> 'anylist':
    """ One event's whole flow as the frontend reads it - every event related to the seed,
    the newest first the way the event list reads, each one saying why it is in the flow
    and which event it was found through. Shared by the flow view and the journey one.
    """
    rows:'anylist' = []

    # A line of the flow reads what a list row reads and two things more
    select_columns:'anylist' = []

    for column_name in _flow_columns:
        column = event_table.c[column_name]
        select_columns.append(column)

    # A flow reads the way the list does, newest first, and two events of one moment are told
    # apart by where they stand among the others of their correlation id - a request and the
    # response to it are written down within the same millisecond often enough for that to matter.
    order_by = [
        event_table.c.event_time_iso.desc(),
        event_table.c.cid_sequence.desc(),
        event_table.c.id.desc(),
    ]

    # Which events are in the flow and why each of them is comes first ..
    flow_ids = get_flow_ids(connection, seed_id)
    relation_by_id = flow_ids.relation_by_id
    via_by_id = flow_ids.via_by_id

    # .. then they are read in the order they are to be shown in ..
    flow_query = select(*select_columns)
    flow_query = flow_query.where(event_table.c.id.in_(list(relation_by_id)))
    flow_query = flow_query.order_by(*order_by)

    flow_result = connection.execute(flow_query)

    for db_row in flow_result:
        row_values = zip(_flow_columns, db_row)

        # A line of a flow carries two keys no column of the event table has
        row:'anydict' = dict(row_values)

        _normalize_row(row)

        # An MCP line says what response shaping did, read out of the full document
        data = row['data']

        if row['source'] == AuditSource.MCP:
            if data:
                attach_trace_lines(row, data)

        # The relation and the seed marker are separate fields.
        row['relation'] = relation_by_id[row['id']]
        row['is_seed'] = row['id'] == seed_id

        # Which event this one was found through, zero when its relation is a shared one
        # that names no event in particular
        if row['id'] in via_by_id:
            row['via_id'] = via_by_id[row['id']]
        else:
            row['via_id'] = 0

        rows.append(row)

    # .. and brought up to the shape a list row arrives in, per source, because a flow
    # is not all one source. The enrichment reads the full documents, so they are cut down
    # to a preview only afterwards - the whole of a payload is fetched by the line that is opened.
    _hydrate_rows(connection, rows)

    for row in rows:
        row['data'] = row['data'][:_data_preview_length]

    return rows

# ################################################################################################################################

@method_allowed('POST')
def flow(req:'any_') -> 'HttpResponse':
    """ Returns one event's whole flow as JSON - every event related to it, the newest first
    the way the event list reads, each one saying why it is in the flow. A flow crosses
    sources, because one correlation id spans a channel and everything it fanned its
    message out to.
    """
    body = json.loads(req.body)
    seed_id = body['id']

    engine = get_audit_engine()

    with engine.connect() as connection:
        rows = _read_flow_rows(connection, seed_id)

    response_json = json.dumps({'rows': rows, 'seed_id': seed_id})
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')

    return out

# ################################################################################################################################

@method_allowed('POST')
def journey(req:'any_') -> 'HttpResponse':
    """ Returns the whole journey of whatever one search term names - the term is resolved
    to a seed event (an event id, a cid or a control id, the newest matching event winning)
    and the seed's flow comes back the same shape the flow view sends, along with what the
    term turned out to name. A term that names nothing comes back with no rows and an empty
    resolved_by, which is how the message flow page knows to say so.
    """
    body = json.loads(req.body)
    term = body['term'].strip()

    rows:'anylist' = []

    engine = get_audit_engine()

    with engine.connect() as connection:

        resolved = resolve_seed(connection, term)

        if resolved.seed_id:
            rows = _read_flow_rows(connection, resolved.seed_id)

    response_json = json.dumps({
        'rows': rows,
        'seed_id': resolved.seed_id,
        'resolved_by': resolved.resolved_by,
    })
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')

    return out

# ################################################################################################################################
# ################################################################################################################################
