# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The views the audit log page is served by - the page itself, the poll of one page of rows,
one event's whole flow, the full payload of one event, the resubmit of one event,
and the attachments of one event - their list and their download.
"""

# stdlib
import json
import logging

# SQLAlchemy
from sqlalchemy import func, select

# Django
from django.http import HttpResponse, HttpResponseNotFound
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import invoke_action_handler, method_allowed
from zato.admin.web.views.audit_log.columns import _all_sources_columns, _all_sources_section_title, _all_sources_title, \
    _data_preview_len, _default_page, _flow_columns, _get_outcomes, _poll_url, _preview_len, _row_columns, _source_columns, \
    _source_label, _source_title, _status_outstanding
from zato.admin.web.views.audit_log.query import _build_where, _hydrate_rows, _normalize_row
from zato.admin.web.views.audit_log.sources import _get_resubmit_labels, _source_outstanding, _source_parse, \
    _source_resubmit, render_view_record
from zato.common.audit_log.api import event_table, get_audit_engine, AuditLog, AuditSource
from zato.common.audit_log.attachment import get_attachment, list_attachments
from zato.common.audit_log.body import resolve_body
from zato.common.audit_log.config_audit import record_view_event
from zato.common.audit_log.flow import get_flow_ids, resolve_seed, Relation_Seed
from zato.common.defaults import default_cluster_id
from zato.x12.render import render_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# What the access log calls this application - the server name of every event it writes
_dashboard_server_name = 'dashboard'

# The screen the message bodies and attachments are read from, as the access log names it
_screen_browser = 'audit-log-browser'

# All the access events this module writes go through this one writer
_access_log = AuditLog(_dashboard_server_name)

# ################################################################################################################################

def _record_content_view(req:'any_', event_id:'int', source:'str', object_name:'str') -> 'None':
    """ Records who read the content of one event - a message body or an attachment.
    Access to patient data is itself an audited operation.
    """

    # A view record holds no patient data, so reading one is not itself a recordable
    # view - without this, browsing the access log writes views of views without end
    if source == AuditSource.Config:
        return

    _ = record_view_event(
        _access_log,
        actor=req.user.username,
        viewed_event_id=event_id,
        screen=_screen_browser,
        viewed_source=source,
        viewed_object_name=object_name,
    )

# ################################################################################################################################
# ################################################################################################################################

def _get_filter_options() -> 'anylist':
    """ What the all-events page offers its filter selects - every source there can be,
    each under its human label and with the objects its events were written against.
    """

    # Every source of the catalog is on offer whether or not it has events yet ..
    by_source:'anydict' = {}
    out:'anylist' = []

    for source, label in _source_label.items():
        entry = {'source': source, 'label': label, 'objects': []}

        by_source[source] = entry
        out.append(entry)

    # .. and the objects come from the events themselves.
    statement = select(event_table.c.source, event_table.c.object_name)
    statement = statement.distinct()
    statement = statement.order_by(event_table.c.source, event_table.c.object_name)

    engine = get_audit_engine()

    with engine.connect() as connection:
        result = connection.execute(statement)

        for source, object_name in result:

            # A source the log holds that the catalog does not know is still shown,
            # under its raw name - the log may be ahead of this application.
            if source not in by_source:
                entry = {'source': source, 'label': source, 'objects': []}

                by_source[source] = entry
                out.append(entry)

            # An event written down with no object at all adds nothing to filter by
            if object_name:
                by_source[source]['objects'].append(object_name)

    return out

# ################################################################################################################################

@method_allowed('GET')
def object_index(req:'any_') -> 'TemplateResponse':
    """ The audit log page - for one object of one source, e.g. a pub/sub topic, or, with
    no source named at all, for every event of every source in one listing.
    """
    source = req.GET.get('source', '')
    object_name = req.GET.get('object_name', '')

    # The page can open pre-filtered to the open exchanges of this source
    status = req.GET.get('status', '')

    # It can also open pre-filtered to a time window and a search query,
    # which is how the analytics screens drill down into the raw events.
    time_from = req.GET.get('time_from', '')
    time_to = req.GET.get('time_to', '')
    query = req.GET.get('query', '')

    # The listing draws each row's cells and chips out of this source's columns - the
    # all-events page reads by the columns every source shares, the source among them,
    # and it alone offers the source and object filter selects.
    if source:
        columns = _source_columns[source]
        audit_log_title = _source_title[source]
        section_title = object_name
        filter_options:'anylist' = []
    else:
        columns = _all_sources_columns
        audit_log_title = _all_sources_title
        section_title = _all_sources_section_title
        filter_options = _get_filter_options()

    columns_json = json.dumps(columns)

    # .. and offers filters for the outcomes this source's events actually report
    outcomes_json = json.dumps(list(_get_outcomes(source)))

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
        'audit_log_title': audit_log_title,
        'section_title': section_title,
        'poll_url': _poll_url,
        'columns_json': columns_json,
        'outcomes_json': outcomes_json,
        'status': status,
        'time_from': time_from,
        'time_to': time_to,
        'query': query,
        'resubmit_labels_json': resubmit_labels_json,
        'exchange_json': json.dumps(exchange),
        'filter_options_json': json.dumps(filter_options),
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

    sources = body['sources']
    object_names = body['object_names']
    outcomes = body['outcomes']
    query = body['query']
    status = body['status']
    time_from = body['time_from']
    time_to = body['time_to']

    page = body['page']
    page_size = body['page_size']

    if page < _default_page:
        page = _default_page

    where_conditions = _build_where(sources, object_names, outcomes, query, status, time_from, time_to)

    rows:'anylist' = []

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
            row = dict(row_values)

            # A column the database has no value for is an empty one to the frontend ..
            _normalize_row(row)

            # .. and only a preview of the payload goes into the table.
            data = row['data']
            row['data'] = data[:_data_preview_len]

            rows.append(row)

        # Everything else the frontend reads off a row - this source's own extra columns, its
        # attrs, a preview of a payload kept elsewhere, the lineage, the message bodies there
        # are to read and the resubmitted marker - is merged in here, a query per set of rows
        # rather than one per row.
        _hydrate_rows(connection, rows)

    response_json = json.dumps({'rows': rows, 'total': total, 'page': page})
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

        # Only a preview of the payload travels with a line - the whole of it is fetched
        # by the line that is opened, and only then.
        data = row['data']
        row['data'] = data[:_data_preview_len]

        # Why this event is in the flow, and whether it is the one the flow was read from
        relation = relation_by_id[row['id']]

        row['relation'] = relation
        row['is_seed'] = relation == Relation_Seed

        # Which event this one was found through, zero when its relation is a shared one
        # that names no event in particular
        if row['id'] in via_by_id:
            row['via_id'] = via_by_id[row['id']]
        else:
            row['via_id'] = 0

        rows.append(row)

    # .. and brought up to the shape a list row arrives in, per source, because a flow
    # is not all one source.
    _hydrate_rows(connection, rows)

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

@method_allowed('POST')
def details(req:'any_') -> 'HttpResponse':
    """ Returns the payload of one audit event, along with the human-readable rendering of the
    document it carries, if it carries one at all. A caller that only shows the top of a message -
    a line of a flow opened for a look at it - asks for a preview instead, and gets the first few
    thousand characters with no parsed view, because a fragment of a message parses into nothing.
    Either way the full length is reported, so the reader is told how much of it is on the screen.
    """
    body = json.loads(req.body)
    event_id = body['id']

    # Which of the event's message bodies is wanted - what was sent, what came back
    # or what the other side said when it failed. With none named, the newest one answers,
    # which is what the message overlay asks for.
    kind = body['kind']

    # Whether the whole message is wanted or only the top of it
    is_preview = body['preview']

    data = ''
    source = ''
    object_name = ''
    event_time_iso = ''

    # Read the full payload of this one event from the shared audit log database.
    details_query = select(
        event_table.c.source, event_table.c.object_name, event_table.c.data,
        event_table.c.event_time_iso).where(event_table.c.id == event_id)
    engine = get_audit_engine()

    with engine.connect() as connection:

        result = connection.execute(details_query)
        row = result.fetchone()

        if row:
            source = row[0]
            object_name = row[1]
            data = row[2]
            event_time_iso = row[3]

    # Whoever is reading this message is recorded - the event exists, so there is content to see
    if row:
        _record_content_view(req, event_id, source, object_name)

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

    # However much of the message is being shown, how long it is in full is what says so
    total_len = len(data)

    # A preview is the top of the message and nothing else ..
    if is_preview:
        data = data[:_preview_len]
        parsed = ''

    # .. and the whole message additionally gets its parsed view, from the source's own renderer
    # with the EDI renderer as the shared default - an empty result means no parsed tab at all.
    # A view record of the access log resolves against the database - who viewed what and when -
    # so it renders here, where the engine is at hand, rather than through _source_parse.
    else:
        if source == AuditSource.Config:
            parsed = render_view_record(engine, data, event_time_iso)
        elif renderer := _source_parse.get(source):
            parsed = renderer(data)
        else:
            parsed = render_document(data)

    response_json = json.dumps({'data': data, 'parsed': parsed, 'total_len': total_len})
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')

    return out

# ################################################################################################################################

@method_allowed('POST')
def attachments(req:'any_') -> 'HttpResponse':
    """ Returns the attachments of one audit event as JSON - the metadata of each of them,
    never the bytes, which is what the detail pane's attachment strip is drawn out of.
    """
    body = json.loads(req.body)
    event_id = body['id']

    engine = get_audit_engine()
    items = list_attachments(engine, event_id)

    response_json = json.dumps({'attachments': items})
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')

    return out

# ################################################################################################################################

@method_allowed('GET')
def attachment_download(req:'any_') -> 'HttpResponse':
    """ Streams one attachment's decoded bytes back under the filename and content type
    it was stored with, or a 404 when there is no such attachment.
    """
    # Query parameters are always strings while the body-row id column is numeric
    attachment_id = int(req.GET['id'])

    engine = get_audit_engine()
    attachment = get_attachment(engine, attachment_id)

    if attachment is None:
        out = HttpResponseNotFound('No such attachment')
        return out

    # Whoever is downloading this file is recorded, against the event the file arrived with
    owner_query = select(
        event_table.c.source, event_table.c.object_name).where(event_table.c.id == attachment['event_id'])

    with engine.connect() as connection:
        owner_row = connection.execute(owner_query).fetchone()

    source, object_name = owner_row
    _record_content_view(req, attachment['event_id'], source, object_name)

    filename = attachment['filename']

    out = HttpResponse(attachment['content'], content_type=attachment['content_type'])
    out['Content-Disposition'] = f'attachment; filename="{filename}"'

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

    # Who asked for the resubmit travels with the request, so the new event carries the actor
    out = invoke_action_handler(req, action['service'],
        extra={'event_id': event_id, 'actor': req.user.username})

    return out

# ################################################################################################################################
# ################################################################################################################################
