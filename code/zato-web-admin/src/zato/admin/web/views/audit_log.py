# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging

# SQLAlchemy
from sqlalchemy import func, or_, select

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.audit_log.api import event_table, get_audit_engine
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

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
_row_columns = ('id', 'cid', 'source', 'event_type', 'event_time_iso', 'msg_id', 'endpoint', 'outcome', 'size', 'data')

# The free-text search covers these columns
_search_columns = ('data', 'msg_id', 'correl_id', 'endpoint')

# Per-source page titles - more sources will follow, e.g. REST outgoing connections
_source_title = {
    'pubsub': 'Pub/sub audit log',
    'rest-channel': 'REST channel audit log',
    'soap-channel': 'SOAP channel audit log',
    'rest-outgoing': 'Outgoing REST audit log',
    'soap-outgoing': 'Outgoing SOAP audit log',
    'email-imap': 'IMAP audit log',
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

# Per-source table columns
_source_columns = {
    'pubsub': _pubsub_columns,
    'rest-channel': _rest_channel_columns,
    'soap-channel': _soap_channel_columns,
    'rest-outgoing': _rest_outgoing_columns,
    'soap-outgoing': _soap_outgoing_columns,
    'email-imap': _email_imap_columns,
}

# ################################################################################################################################
# ################################################################################################################################

def _escape_like(query:'str') -> 'str':
    """ Escapes LIKE wildcards in a user query so they match literally.
    """
    out = query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    return out

# ################################################################################################################################

def _build_where(source:'str', object_name:'str', query:'str') -> 'anylist':
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

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def object_index(req:'any_') -> 'TemplateResponse':
    """ The audit log page for one object of one source, e.g. a pub/sub topic.
    """
    source = req.GET['source']
    object_name = req.GET['object_name']

    # The frontend renders the table headers and cells based on this source's columns
    columns = _source_columns[source]
    columns_json = json.dumps(columns)

    return TemplateResponse(req, 'zato/audit_log.html', {
        'cluster_id': default_cluster_id,
        'source': source,
        'object_name': object_name,
        'audit_log_title': _source_title[source],
        'section_title': object_name,
        'poll_url': _poll_url,
        'columns': columns,
        'columns_json': columns_json,
        'zato_clusters': True,
        'zato_template_name': 'zato/audit_log.html',
    })

# ################################################################################################################################

@method_allowed('POST')
def poll(req:'any_') -> 'HttpResponse':
    """ Returns one page of audit events as JSON, in the shape the detail-kit pagination expects.
    """
    body = json.loads(req.body)

    source = body['source']
    object_name = body['object_name']
    query = body['query']

    page = body['page']
    page_size = body['page_size']

    if page < _default_page:
        page = _default_page

    where_conditions = _build_where(source, object_name, query)

    rows:'anylist' = []

    # The same select column order as in _row_columns
    select_columns:'anylist' = []

    for column_name in _row_columns:
        column = event_table.c[column_name]
        select_columns.append(column)

    # Build both queries upfront ..
    count_query = select(func.count()).select_from(event_table).where(*where_conditions)

    offset = (page - 1) * page_size
    page_query = select(*select_columns).where(*where_conditions).order_by(event_table.c.id.desc()). \
        limit(page_size).offset(offset)

    # .. and run them against the shared audit log database.
    engine = get_audit_engine()

    with engine.connect() as connection:

        total = connection.execute(count_query).scalar()

        for db_row in connection.execute(page_query):
            row = dict(zip(_row_columns, db_row))

            # Only a preview of the payload goes into the table.
            data = row['data']
            row['data'] = data[:_data_preview_len]

            rows.append(row)

    response_json = json.dumps({'rows': rows, 'total': total, 'page': page})
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')
    return out

# ################################################################################################################################

@method_allowed('POST')
def details(req:'any_') -> 'HttpResponse':
    """ Returns the complete payload of one audit event, without any truncation.
    """
    body = json.loads(req.body)
    event_id = body['id']

    data = ''

    # Read the full payload of this one event from the shared audit log database.
    details_query = select(event_table.c.data).where(event_table.c.id == event_id)
    engine = get_audit_engine()

    with engine.connect() as connection:

        row = connection.execute(details_query).fetchone()
        if row:
            data = row[0]

    response_json = json.dumps({'data': data})
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')
    return out

# ################################################################################################################################
# ################################################################################################################################
