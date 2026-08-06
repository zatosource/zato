# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The detail pane's attachment strip is drawn out of one endpoint's metadata and each badge
# downloads through the other - the right names, sizes and bytes come back, under the right
# headers, and an id nothing was stored under answers with a 404.

# stdlib
import os
from contextlib import contextmanager
from json import dumps, loads

# Django
from django.http import QueryDict

# Zato
from zato.admin.web.views.audit_log import attachment_download, attachments
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource, ModuleCtx as AuditLogCtx
from zato.common.audit_log.attachment import build_attachment
from zato.common.ext.bunch import Bunch

# Test support
from live_sql.env import database_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_

    envgen = Iterator[int]

# ################################################################################################################################
# ################################################################################################################################

# The server and connection the test event is written under
_server_name = 'test-dashboard-attachments-server'
_conn_name = 'test.dashboard.attachments'

# The two files the test event carries
_pdf_name = 'discharge.pdf'
_pdf_type = 'application/pdf'
_pdf_content = b'%PDF-1.4 discharge'

_csv_name = 'codes.csv'
_csv_type = 'text/csv'
_csv_content = b'code,label\nA1,First\n'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# Who is logged into the dashboard in these tests
_username = 'dashboard.reader'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _event_with_attachments(tmp_path:'any_') -> 'envgen':
    """ Points the audit log at a throwaway SQLite database holding one event with two
    attachments and hands the event's id to the block.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env(_env_prefix, details):

        audit_log = AuditLog(_server_name)

        envelopes = [
            build_attachment(_pdf_name, _pdf_type, _pdf_content),
            build_attachment(_csv_name, _csv_type, _csv_content),
        ]

        event_id = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Message_Sent, _conn_name,
            cid='cid-dashboard-attachments-1', outcome=AuditOutcome.OK, attachments=envelopes)

        yield event_id

# ################################################################################################################################

def _new_user() -> 'Bunch':
    """ Builds what the views read off the logged-in Django user.
    """
    out = Bunch()
    out.username = _username

    return out

# ################################################################################################################################

def _new_post_request(payload:'any_') -> 'Bunch':
    """ Builds the request the metadata view is called with - the JSON the strip posts.
    """
    out = Bunch()

    out.method = 'POST'
    out.body = dumps(payload).encode('utf-8')
    out.user = _new_user()

    return out

# ################################################################################################################################

def _new_get_request(attachment_id:'any_') -> 'Bunch':
    """ Builds the request the download view is called with - the id in the query string.
    """
    query = QueryDict('', mutable=True)
    query['id'] = f'{attachment_id}'

    out = Bunch()

    out.method = 'GET'
    out.GET = query
    out.user = _new_user()

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_the_metadata_list_carries_each_file_without_its_bytes(tmp_path:'os.PathLike') -> 'None':
    """ The strip is drawn out of names, types, sizes and kept-flags - never the bytes.
    """
    with _event_with_attachments(tmp_path) as event_id:

        response = attachments(_new_post_request({'id': event_id}))
        assert response.status_code == 200

        data = loads(response.content)
        items = data['attachments']

        assert len(items) == 2

        assert items[0]['filename'] == _pdf_name
        assert items[0]['content_type'] == _pdf_type
        assert items[0]['size'] == len(_pdf_content)
        assert items[0]['is_content_kept'] is True
        assert 'content' not in items[0]

        assert items[1]['filename'] == _csv_name

# ################################################################################################################################

def test_the_download_streams_the_bytes_under_the_stored_name(tmp_path:'os.PathLike') -> 'None':
    """ A badge's click gets the very bytes that were stored, under the stored filename
    and content type.
    """
    with _event_with_attachments(tmp_path) as event_id:

        metadata_response = attachments(_new_post_request({'id': event_id}))
        items = loads(metadata_response.content)['attachments']

        response = attachment_download(_new_get_request(items[0]['id']))

        assert response.status_code == 200
        assert response.content == _pdf_content
        assert response['Content-Type'] == _pdf_type
        assert response['Content-Disposition'] == f'attachment; filename="{_pdf_name}"'

# ################################################################################################################################

def test_an_unknown_id_answers_with_a_404(tmp_path:'os.PathLike') -> 'None':
    """ An id nothing was stored under is a 404, not an empty file.
    """
    with _event_with_attachments(tmp_path):

        response = attachment_download(_new_get_request(987654321))
        assert response.status_code == 404

# ################################################################################################################################

def test_an_event_with_no_attachments_answers_with_an_empty_list(tmp_path:'os.PathLike') -> 'None':
    """ An event that carried no files draws no strip - the list is simply empty.
    """
    with _event_with_attachments(tmp_path):

        response = attachments(_new_post_request({'id': 987654321}))
        assert response.status_code == 200

        data = loads(response.content)
        assert data['attachments'] == []

# ################################################################################################################################
# ################################################################################################################################
