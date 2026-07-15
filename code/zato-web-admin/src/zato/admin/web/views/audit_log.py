# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
from dataclasses import dataclass

# SQLAlchemy
from sqlalchemy import and_, func, or_, select

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import invoke_action_handler, method_allowed
from zato.common.as2.mdn import describe_disposition
from zato.common.audit_log.api import AuditEvent, event_table, get_audit_engine
from zato.common.audit_log.query import outstanding_conditions
from zato.common.defaults import default_cluster_id
from zato.x12.render import render_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_poll_url = '/zato/audit-log/poll/'

_default_page = 1
_default_page_size = 25

# How many characters of the payload are shown in the table
_data_preview_len = 200

# The columns returned to the frontend, in the order they appear in the select below
_row_columns = ('id', 'cid', 'source', 'event_type', 'object_name', 'event_time_iso', 'msg_id', 'endpoint', 'ext_client_id',
    'outcome', 'size', 'data')

# The free-text search covers these columns
_search_columns = ('data', 'msg_id', 'correl_id', 'endpoint')

# The status query parameter value narrowing the page down to open exchanges
_status_outstanding = 'outstanding'

# Per-source page titles - more sources will follow, e.g. REST outgoing connections
_source_title = {
    'pubsub': 'Pub/sub audit log',
    'rest-channel': 'REST channel audit log',
    'soap-channel': 'SOAP channel audit log',
    'rest-outgoing': 'Outgoing REST audit log',
    'soap-outgoing': 'Outgoing SOAP audit log',
    'email-imap': 'IMAP audit log',
    'as2': 'AS2 audit log',
    'x12': 'X12 audit log',
    'mcp': 'MCP audit log',
}

# Each column tells the frontend which row key to read, what header label to show
# and how to render the cell - the types are implemented in audit_log.js
_pubsub_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'msg_id', 'label': 'Message id', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Endpoint', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_rest_channel_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Endpoint', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_soap_channel_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Endpoint', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_rest_outgoing_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Endpoint', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_soap_outgoing_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Endpoint', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_email_imap_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Folder', 'type': 'text'},
    {'key': 'msg_id', 'label': 'Message id', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_as2_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'object_name', 'label': 'Partner', 'type': 'text'},
    {'key': 'msg_id', 'label': 'Message id', 'type': 'text'},
    {'key': 'disposition', 'label': 'Disposition', 'type': 'text'},
    {'key': 'mic', 'label': 'MIC', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
    {'key': 'action', 'label': 'Actions', 'type': 'action'},
]

_x12_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'object_name', 'label': 'Partner', 'type': 'text'},
    {'key': 'msg_id', 'label': 'Control number', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

_mcp_columns = [
    {'key': 'event_time_iso', 'label': 'Time', 'type': 'time'},
    {'key': 'cid', 'label': 'CID', 'type': 'cid'},
    {'key': 'event_type', 'label': 'Event', 'type': 'text'},
    {'key': 'endpoint', 'label': 'Tool', 'type': 'text'},
    {'key': 'ext_client_id', 'label': 'Caller', 'type': 'text'},
    {'key': 'outcome', 'label': 'Outcome', 'type': 'text'},
    {'key': 'size', 'label': 'Size', 'type': 'size'},
    {'key': 'data', 'label': 'Data preview', 'type': 'data'},
]

# Per-source table columns
_source_columns = {
    'pubsub': _pubsub_columns,
    'rest-channel': _rest_channel_columns,
    'soap-channel': _soap_channel_columns,
    'rest-outgoing': _rest_outgoing_columns,
    'soap-outgoing': _soap_outgoing_columns,
    'email-imap': _email_imap_columns,
    'as2': _as2_columns,
    'x12': _x12_columns,
    'mcp': _mcp_columns,
}

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OutstandingFilter:
    """ The outstanding filter of one source - the event that opens an exchange, the acknowledgment
    that closes it, and whether the close matches on the partner pair too. AS2 MDNs answer
    the Message-ID alone while X12 acknowledgments echo both the pair and the control number.
    """
    open_event: str = ''
    close_event: str = ''
    needs_object_name_match: bool = False

# ################################################################################################################################

def _new_outstanding_filter(open_event:'str', close_event:'str', needs_object_name_match:'bool') -> 'OutstandingFilter':
    out = OutstandingFilter()
    out.open_event = open_event
    out.close_event = close_event
    out.needs_object_name_match = needs_object_name_match

    return out

# ################################################################################################################################

# The sources whose pages carry the outstanding filter pill
_source_outstanding = {
    'as2': _new_outstanding_filter(AuditEvent.Message_Sent, AuditEvent.MDN_Received, False),
    'x12': _new_outstanding_filter(AuditEvent.Interchange_Sent, AuditEvent.Ack_Received, True),
}

# ################################################################################################################################
# ################################################################################################################################

# Per-source resubmit actions - each source declares which of its events are resubmittable,
# how the row action is labelled and which service performs it.
_as2_resubmit = {
    AuditEvent.Message_Sent:     {'label': 'Resend',    'service': 'zato.audit-log.as2.resend'},
    AuditEvent.Message_Received: {'label': 'Reprocess', 'service': 'zato.audit-log.as2.reprocess'},
}

# The sources whose pages carry resubmit actions
_source_resubmit = {
    'as2': _as2_resubmit,
}

# ################################################################################################################################
# ################################################################################################################################

def _enrich_as2_row(row:'anydict') -> 'None':
    """ Extracts the disposition and MIC of an AS2 event out of its JSON data,
    so they render as columns of their own.
    """
    row['disposition'] = ''
    row['mic'] = ''

    data = row['data']
    if not data:
        return

    # A payload that is not JSON, e.g. a raw MIME body, has nothing to extract.
    try:
        details = json.loads(data)
    except ValueError:
        return

    # A message-sent event carries the MIC computed at send time,
    # an mdn-received event carries what the receipt itself reported.
    if mic := details.get('mic'):
        row['mic'] = mic

    if disposition := details.get('disposition'):
        row['disposition'] = describe_disposition(disposition, details['modifier_kind'], details['modifier'])

# ################################################################################################################################

# Per-source row enrichment - a source with columns extracted out of the event data registers itself here
_source_row_enrich = {
    'as2': _enrich_as2_row,
}

# ################################################################################################################################
# ################################################################################################################################

def _escape_like(query:'str') -> 'str':
    """ Escapes LIKE wildcards in a user query so they match literally.
    """
    out = query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    return out

# ################################################################################################################################

def _build_where(source:'str', object_name:'str', query:'str', status:'str') -> 'anylist':
    """ Builds the WHERE conditions for the poll query.
    """

    # Our response to produce
    out:'anylist' = []

    out.append(event_table.c.source == source)
    out.append(event_table.c.object_name == object_name)

    # The free-text search covers several columns, matching wildcards literally
    if query:
        escaped = _escape_like(query)
        like_value = f'%{escaped}%'

        like_parts:'anylist' = []

        for column_name in _search_columns:
            column = event_table.c[column_name]
            like_parts.append(column.like(like_value, escape='\\'))

        out.append(or_(*like_parts))

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

def _get_resubmit_labels(source:'str') -> 'anydict':
    """ Returns the per-event-type labels of this source's resubmit actions,
    which is what tells the frontend which rows get an action link at all.
    """

    # Our response to produce
    out:'anydict' = {}

    if actions := _source_resubmit.get(source):
        for event_type, action in actions.items():
            out[event_type] = action['label']

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

    statement = select(event_table.c.correl_id).where(and_(
        event_table.c.source == source,
        event_table.c.correl_id.in_(cids),
    ))

    resubmitted = set()
    result = connection.execute(statement)

    for db_row in result:
        resubmitted.add(db_row[0])

    for row in rows:
        if row['cid'] in resubmitted:
            row['is_resubmitted'] = True

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

    # The frontend renders the table headers and cells based on this source's columns
    columns = _source_columns[source]
    columns_json = json.dumps(columns)

    # The per-event-type resubmit labels of this source, empty for sources without resubmit
    resubmit_labels = _get_resubmit_labels(source)
    resubmit_labels_json = json.dumps(resubmit_labels)

    return_data = {
        'cluster_id': default_cluster_id,
        'source': source,
        'object_name': object_name,
        'audit_log_title': _source_title[source],
        'section_title': object_name,
        'poll_url': _poll_url,
        'columns': columns,
        'columns_json': columns_json,
        'status': status,
        'has_outstanding_filter': source in _source_outstanding,
        'resubmit_labels_json': resubmit_labels_json,
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

    page = body['page']
    page_size = body['page_size']

    if page < _default_page:
        page = _default_page

    where_conditions = _build_where(source, object_name, query, status)

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
    count_query = select(func.count())
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
            row = dict(zip(_row_columns, db_row))

            # Sources with extra columns extract them out of the full payload first ..
            if enrich := _source_row_enrich.get(source):
                enrich(row)

            # .. and only a preview of the payload goes into the table.
            data = row['data']
            row['data'] = data[:_data_preview_len]

            rows.append(row)

        # Rows already resubmitted get their marker, on sources with resubmit actions.
        if source in _source_resubmit:
            _mark_resubmitted(connection, source, rows)

    response_json = json.dumps({'rows': rows, 'total': total, 'page': page})
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')

    return out

# ################################################################################################################################

@method_allowed('POST')
def details(req:'any_') -> 'HttpResponse':
    """ Returns the complete payload of one audit event, without any truncation,
    along with the human-readable rendering of the EDI document the payload carries,
    if it carries one at all.
    """
    body = json.loads(req.body)
    event_id = body['id']

    data = ''

    # Read the full payload of this one event from the shared audit log database.
    details_query = select(event_table.c.data).where(event_table.c.id == event_id)
    engine = get_audit_engine()

    with engine.connect() as connection:

        result = connection.execute(details_query)
        row = result.fetchone()

        if row:
            data = row[0]

    # A payload that embeds an EDI document additionally renders as its parsed view.
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
