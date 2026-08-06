# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Access to patient data is itself an audited operation - reading a message body writes
# one content-viewed row saying who read what, downloading an attachment writes one too,
# and both name the source and object the viewed event belongs to.

# stdlib
import os
from contextlib import contextmanager
from json import dumps

# Django
from django.http import QueryDict

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.admin.web.views.audit_log import attachment_download, details
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine, AuditEvent, AuditLog, \
    AuditOutcome, AuditSource, ModuleCtx as AuditLogCtx
from zato.common.audit_log.attachment import build_attachment, list_attachments
from zato.common.ext.bunch import Bunch

# Test support
from live_sql.env import database_env

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anydict

    envgen = Iterator[int]

# ################################################################################################################################
# ################################################################################################################################

# The server and connection the viewed event is written under
_server_name = 'test-access-logging-server'
_conn_name = 'test.access.logging'

# Who is logged into the dashboard in these tests
_username = 'dashboard.reader'

# The file the viewed event carries
_pdf_name = 'referral.pdf'
_pdf_type = 'application/pdf'
_pdf_content = b'%PDF-1.4 referral'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def _event_to_view(tmp_path:'any_') -> 'envgen':
    """ Points the audit log at a throwaway SQLite database holding one event with a body
    and an attachment and hands the event's id to the block.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    details_config = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env(_env_prefix, details_config):

        audit_log = AuditLog(_server_name)

        envelopes = [build_attachment(_pdf_name, _pdf_type, _pdf_content)]

        event_id = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Message_Sent, _conn_name,
            cid='cid-access-logging-1', outcome=AuditOutcome.OK, data='The message body somebody reads',
            attachments=envelopes)

        yield event_id

# ################################################################################################################################

def _get_view_events() -> 'any_':
    """ The content-viewed rows the access log holds, with their attributes, oldest first.
    """
    engine = get_audit_engine()

    events_query = select(event_table.c.id, event_table.c.source, event_table.c.event_type, event_table.c.object_name)
    events_query = events_query.where(event_table.c.event_type == AuditEvent.Content_Viewed)
    events_query = events_query.order_by(event_table.c.id)

    out = []

    with engine.connect() as connection:

        for row in connection.execute(events_query):

            attrs_query = select(event_attr_table.c.name, event_attr_table.c.value)
            attrs_query = attrs_query.where(event_attr_table.c.event_id == row[0])

            attrs:'anydict' = {}

            for attr_row in connection.execute(attrs_query):
                attrs[attr_row[0]] = attr_row[1]

            out.append({
                'id': row[0],
                'source': row[1],
                'event_type': row[2],
                'object_name': row[3],
                'attrs': attrs,
            })

    return out

# ################################################################################################################################

def _new_details_request(event_id:'int') -> 'Bunch':
    """ Builds the request the details view is called with - the JSON the detail pane posts.
    """
    out = Bunch()

    out.method = 'POST'
    out.body = dumps({'id': event_id, 'kind': '', 'preview': False}).encode('utf-8')

    out.user = Bunch()
    out.user.username = _username

    return out

# ################################################################################################################################

def _new_download_request(attachment_id:'int') -> 'Bunch':
    """ Builds the request the download view is called with - the id in the query string.
    """
    query = QueryDict('', mutable=True)
    query['id'] = f'{attachment_id}'

    out = Bunch()

    out.method = 'GET'
    out.GET = query

    out.user = Bunch()
    out.user.username = _username

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_body_read_writes_one_content_viewed_row_with_the_actor(tmp_path:'os.PathLike') -> 'None':
    """ Opening a message body is recorded - who, which event, and whose channel it was.
    """
    with _event_to_view(tmp_path) as event_id:

        response = details(_new_details_request(event_id))
        assert response.status_code == 200

        view_events = _get_view_events()
        assert len(view_events) == 1

        view_event = view_events[0]

        assert view_event['source'] == AuditSource.Config
        assert view_event['attrs']['actor'] == _username
        assert view_event['attrs']['viewed_event_id'] == f'{event_id}'
        assert view_event['attrs']['viewed_source'] == AuditSource.Email_SMTP
        assert view_event['attrs']['viewed_object_name'] == _conn_name

# ################################################################################################################################

def test_an_attachment_download_writes_one_content_viewed_row_too(tmp_path:'os.PathLike') -> 'None':
    """ Downloading a file is recorded against the event the file arrived with.
    """
    with _event_to_view(tmp_path) as event_id:

        engine = get_audit_engine()
        items = list_attachments(engine, event_id)

        response = attachment_download(_new_download_request(items[0]['id']))
        assert response.status_code == 200

        view_events = _get_view_events()
        assert len(view_events) == 1

        view_event = view_events[0]

        assert view_event['attrs']['actor'] == _username
        assert view_event['attrs']['viewed_event_id'] == f'{event_id}'
        assert view_event['attrs']['viewed_source'] == AuditSource.Email_SMTP
        assert view_event['attrs']['viewed_object_name'] == _conn_name

# ################################################################################################################################

def test_a_missing_attachment_writes_nothing(tmp_path:'os.PathLike') -> 'None':
    """ A download that found nothing showed nothing, so there is nothing to record.
    """
    with _event_to_view(tmp_path):

        response = attachment_download(_new_download_request(987654321))
        assert response.status_code == 404

        assert _get_view_events() == []

# ################################################################################################################################
# ################################################################################################################################
