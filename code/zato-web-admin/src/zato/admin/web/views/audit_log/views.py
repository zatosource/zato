# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The four views the audit log page is served by - the page itself, the poll of one page of rows,
the full payload of one event and the resubmit of one event.
"""

# stdlib
import json
import logging

# SQLAlchemy
from sqlalchemy import func, select

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import invoke_action_handler, method_allowed
from zato.admin.web.views.audit_log.columns import _data_preview_len, _default_page, _poll_url, _row_columns, \
    _source_columns, _source_title, _status_outstanding
from zato.admin.web.views.audit_log.query import _attach_attr_columns, _attach_body_kinds, _attach_body_previews, \
    _attach_lineage, _build_where, _mark_resubmitted, _normalize_row
from zato.admin.web.views.audit_log.sources import _get_resubmit_labels, _source_outstanding, _source_parse, \
    _source_resubmit, _source_row_enrich
from zato.common.audit_log.api import event_table, get_audit_engine
from zato.common.audit_log.body import resolve_body
from zato.common.defaults import default_cluster_id
from zato.x12.render import render_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################

@method_allowed('GET')
def object_index(req:'any_') -> 'TemplateResponse':
    """ The audit log page for one object of one source, e.g. a pub/sub topic.
    """
    source = req.GET['source']
    object_name = req.GET['object_name']

    # The page can open pre-filtered to the open exchanges of this source
    status = req.GET.get('status', '')

    # It can also open pre-filtered to a time window and a search query,
    # which is how the analytics screens drill down into the raw events.
    time_from = req.GET.get('time_from', '')
    time_to = req.GET.get('time_to', '')
    query = req.GET.get('query', '')

    # The listing draws each row's cells and chips out of this source's columns
    columns_json = json.dumps(_source_columns[source])

    # The per-event-type resubmit labels of this source, empty for sources without resubmit
    resubmit_labels = _get_resubmit_labels(source)
    resubmit_labels_json = json.dumps(resubmit_labels)

    # The exchanges of this source - the event that opens one and the event that closes it -
    # which is what pairing the two halves of an exchange onto one line needs.
    exchange = {'open_event': '', 'close_event': ''}

    if outstanding := _source_outstanding.get(source):
        exchange['open_event'] = outstanding.open_event
        exchange['close_event'] = outstanding.close_event

    return_data = {
        'cluster_id': default_cluster_id,
        'source': source,
        'object_name': object_name,
        'audit_log_title': _source_title[source],
        'section_title': object_name,
        'poll_url': _poll_url,
        'columns_json': columns_json,
        'status': status,
        'time_from': time_from,
        'time_to': time_to,
        'query': query,
        'has_outstanding_filter': source in _source_outstanding,
        'resubmit_labels_json': resubmit_labels_json,
        'exchange_json': json.dumps(exchange),
        'zato_clusters': True,
        'zato_template_name': 'zato/audit_log.html',
    }

    out = TemplateResponse(req, 'zato/audit_log.html', return_data)

    return out

# ################################################################################################################################

@method_allowed('POST')
def poll(req:'any_') -> 'HttpResponse':
    """ Returns one page of audit events as JSON, in the shape the detail-kit pagination expects.
    """
    body = json.loads(req.body)

    source = body['source']
    object_name = body['object_name']
    query = body['query']
    status = body['status']
    time_from = body['time_from']
    time_to = body['time_to']

    page = body['page']
    page_size = body['page_size']

    if page < _default_page:
        page = _default_page

    where_conditions = _build_where(source, object_name, query, status, time_from, time_to)

    rows:'anylist' = []

    # The same select column order as in _row_columns
    select_columns:'anylist' = []

    for column_name in _row_columns:
        column = event_table.c[column_name]
        select_columns.append(column)

    # Outstanding items are shown oldest first - the longest-waiting exchange is the most
    # urgent one - while the regular view shows the newest events first.
    if status == _status_outstanding:
        order_by = event_table.c.id.asc()
    else:
        order_by = event_table.c.id.desc()

    # Build both queries upfront ..
    event_count = func.count()

    count_query = select(event_count)
    count_query = count_query.select_from(event_table)
    count_query = count_query.where(*where_conditions)

    offset = (page - 1) * page_size

    page_query = select(*select_columns)
    page_query = page_query.where(*where_conditions)
    page_query = page_query.order_by(order_by)
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
            row = dict(row_values)

            # A column the database has no value for is an empty one to the frontend ..
            _normalize_row(row)

            # .. sources with extra columns extract them out of the full payload next ..
            if enrich := _source_row_enrich.get(source):
                enrich(row)

            # .. and only a preview of the payload goes into the table.
            data = row['data']
            row['data'] = data[:_data_preview_len]

            rows.append(row)

        # Sources with attr columns get them merged in, one query for the page ..
        _attach_attr_columns(connection, source, rows)

        # .. sources whose payloads live in the body table get their previews the same way ..
        _attach_body_previews(connection, source, rows)

        # .. every row says what it came out of and what came out of it ..
        _attach_lineage(connection, rows)

        # .. and which of its message bodies are there to be read.
        _attach_body_kinds(connection, rows)

        # Rows already resubmitted get their marker, on sources with resubmit actions ..
        if source in _source_resubmit:
            _mark_resubmitted(connection, source, rows)

        # .. and on a source with no resubmit at all, no row of it can carry one.
        else:
            for row in rows:
                row['is_resubmitted'] = False

    response_json = json.dumps({'rows': rows, 'total': total, 'page': page})
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')

    return out

# ################################################################################################################################

@method_allowed('POST')
def details(req:'any_') -> 'HttpResponse':
    """ Returns the complete payload of one audit event, without any truncation,
    along with the human-readable rendering of the document the payload carries,
    if it carries one at all.
    """
    body = json.loads(req.body)
    event_id = body['id']

    # Which of the event's message bodies is wanted - what was sent, what came back
    # or what the other side said when it failed. With none named, the newest one answers,
    # which is what the message overlay asks for.
    kind = body['kind']

    data = ''
    source = ''

    # Read the full payload of this one event from the shared audit log database.
    details_query = select(event_table.c.source, event_table.c.data).where(event_table.c.id == event_id)
    engine = get_audit_engine()

    with engine.connect() as connection:

        result = connection.execute(details_query)
        row = result.fetchone()

        if row:
            source = row[0]
            data = row[1]

    # A named body is one the data column never holds, so it always comes out of the body store ..
    if kind:
        data = ''

    # .. and a payload stored outside the data column resolves through the body registry -
    # sources with their own body stores answer for themselves, everything else
    # reads the shared body table.
    if not data:
        resolved = resolve_body(engine, source, event_id, kind)
        if resolved is not None:
            data = resolved

    # The parsed view comes from the source's own renderer, with the EDI renderer
    # as the shared default - an empty result means no parsed tab at all.
    if renderer := _source_parse.get(source):
        parsed = renderer(data)
    else:
        parsed = render_document(data)

    response_json = json.dumps({'data': data, 'parsed': parsed})
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')

    return out

# ################################################################################################################################

@method_allowed('POST')
def resubmit(req:'any_') -> 'HttpResponse':
    """ Resubmits one audit event - a resend for outbound rows, a reprocess for inbound ones,
    performed by the service the event's source registered for that event type.
    The new attempt lands as its own event linked to the original one by CID.
    """
    # Form data is always a string while the event id column is numeric
    event_id = int(req.POST['id'])

    # Find which event this is, so the right service can perform the resubmit.
    lookup_query = select(event_table.c.source, event_table.c.event_type).where(event_table.c.id == event_id)
    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(lookup_query)
        row = result.fetchone()

    source, event_type = row

    # Each source declares which of its events are resubmittable and which service performs it.
    actions = _source_resubmit[source]
    action = actions[event_type]

    out = invoke_action_handler(req, action['service'], extra={'event_id': event_id})

    return out

# ################################################################################################################################
# ################################################################################################################################
