# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import sqlite3

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.audit_log.api import get_audit_db_path
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
_row_columns = ('id', 'cid', 'source', 'event_type', 'event_time_iso', 'msg_id', 'endpoint', 'server_name', 'outcome',
    'size', 'data')

_select_columns = 'id, cid, source, event_type, event_time_iso, msg_id, endpoint, server_name, outcome, size, data'

# The free-text search covers these columns
_search_columns = ('data', 'msg_id', 'correl_id', 'endpoint')

# ################################################################################################################################
# ################################################################################################################################

def _open_audit_db() -> 'any_':
    """ Opens the shared audit database read-only. The server side owns all writes.
    """
    db_path = get_audit_db_path()

    # No events have been written yet if the file does not exist.
    if not os.path.exists(db_path):
        return None

    out = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    return out

# ################################################################################################################################

def _escape_like(query:'str') -> 'str':
    """ Escapes LIKE wildcards in a user query so they match literally.
    """
    out = query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    return out

# ################################################################################################################################

def _build_where(source:'str', object_name:'str', cid:'str', query:'str') -> 'tuple':
    """ Builds the WHERE clause and its parameters for the poll query. A non-empty CID means
    the cross-source page, which deliberately has no source filter - that is the cross-referencing.
    """
    where_parts:'anylist' = []
    params:'anylist' = []

    if cid:
        where_parts.append('cid = ?')
        params.append(cid)
    else:
        where_parts.append('source = ?')
        params.append(source)
        where_parts.append('object_name = ?')
        params.append(object_name)

    if query:
        escaped = _escape_like(query)
        like_value = f'%{escaped}%'

        like_parts:'anylist' = []
        for column in _search_columns:
            like_parts.append(f"{column} like ? escape '\\'")
            params.append(like_value)

        joined_likes = ' or '.join(like_parts)
        where_parts.append(f'({joined_likes})')

    out = ' and '.join(where_parts)
    return out, params

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def object_index(req:'any_') -> 'TemplateResponse':
    """ The audit log page for one object of one source, e.g. a pub/sub topic.
    """
    source = req.GET['source']
    object_name = req.GET['object_name']

    return TemplateResponse(req, 'zato/audit_log.html', {
        'cluster_id': default_cluster_id,
        'source': source,
        'object_name': object_name,
        'cid': '',
        'is_cid_page': False,
        'section_title': object_name,
        'poll_url': _poll_url,
        'zato_clusters': True,
        'zato_template_name': 'zato/audit_log.html',
    })

# ################################################################################################################################

@method_allowed('GET')
def cid_index(req:'any_', cid:'str') -> 'TemplateResponse':
    """ The cross-source audit log page for one CID, showing all events of that request.
    """
    return TemplateResponse(req, 'zato/audit_log.html', {
        'cluster_id': default_cluster_id,
        'source': '',
        'object_name': '',
        'cid': cid,
        'is_cid_page': True,
        'section_title': cid,
        'poll_url': _poll_url,
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
    cid = body['cid']
    query = body['query']

    page = body['page']
    page_size = body['page_size']

    if page < _default_page:
        page = _default_page

    where_clause, params = _build_where(source, object_name, cid, query)

    rows:'anylist' = []
    total = 0

    conn = _open_audit_db()

    # The database exists only after the first event was written.
    if conn:

        count_sql = f'select count(*) from event where {where_clause}'
        count_row = conn.execute(count_sql, params).fetchone()
        total = count_row[0]

        offset = (page - 1) * page_size
        page_sql = f'select {_select_columns} from event where {where_clause} order by id desc limit ? offset ?'
        page_params = params + [page_size, offset]

        for db_row in conn.execute(page_sql, page_params):
            row = dict(zip(_row_columns, db_row))

            # Only a preview of the payload goes into the table.
            data = row['data']
            row['data'] = data[:_data_preview_len]

            rows.append(row)

        conn.close()

    response_json = json.dumps({'rows': rows, 'total': total, 'page': page})
    response_bytes = response_json.encode('utf-8')

    out = HttpResponse(response_bytes, content_type='application/json')
    return out

# ################################################################################################################################
# ################################################################################################################################
