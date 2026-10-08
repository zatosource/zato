# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Access to patient data is itself an audited operation - reading a message body writes
# one content-viewed row saying who read what, downloading an attachment writes one too,
# and both name the source and object the viewed event belongs to. A message waiting in a
# delivery queue is read the same way, its row naming the message rather than an event.

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
from zato.admin.web.views.audit_log.sources import render_view_record
from zato.admin.web.views.outgoing import delivery
from zato.common.audit_log.api import event_attr_table, event_table, get_audit_engine, AuditEvent, AuditLog, \
    AuditOutcome, AuditSource, ModuleCtx as AuditLogCtx
from zato.common.audit_log.attachment import build_attachment, list_attachments
from zato.common.ext.bunch import Bunch, bunchify
from zato.common.pubsub.outgoing import Body_Mode_HL7, Key_CID, Key_Conn_Name, Key_Data, Key_Msg_ID, Key_Request

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

# The queued message the delivery page shows, and the connection it waits in
_queue_conn_type = 'hl7-mllp'
_queue_conn_name = 'test.access.logging.orders'
_queue_cid = 'cid-access-logging-queue'
_queue_msg_id = 'zpsm-access-logging-1'
_queue_message = 'MSH|^~\\&|HIS|HOSP|LAB|LAB|20260101||ADT^A01|MSG0001|P|2.5\rPID|1||12345||DOE^JANE\r'

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

class _QueueClient:
    """ Answers the delivery page's one service call with a queued message, the way a server would.
    """
    def invoke(self, service:'str', request:'anydict') -> 'any_':
        out = bunchify({
            'ok': True,
            'details': '',
            'data': {
                'document': {
                    Key_Request: {Key_Data: _queue_message},
                    Key_CID: _queue_cid,
                    Key_Msg_ID: _queue_msg_id,
                    Key_Conn_Name: _queue_conn_name,
                },
                'body_mode': Body_Mode_HL7,
                'destination': 'lab',
                'facts': [],
                'invoker': 'orders',
                'dlq_settings': {},
            },
        })

        return out

# ################################################################################################################################

def _new_queue_request(what:'str') -> 'Bunch':
    """ Builds the request the delivery page's message and download views are called with.
    """
    query = QueryDict('', mutable=True)
    query['conn_type'] = _queue_conn_type
    query['conn_id'] = '7'
    query['kind'] = 'queue'
    query['msg_id'] = _queue_msg_id
    query['what'] = what

    out = Bunch()

    out.method = 'GET'
    out.GET = query

    out.user = Bunch()
    out.user.username = _username

    out.zato = Bunch()
    out.zato.client = _QueueClient()

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

# ################################################################################################################################

def test_a_queued_message_read_or_downloaded_writes_one_content_viewed_row_each(tmp_path:'os.PathLike') -> 'None':
    """ A message waiting in a delivery queue is patient data too - its details window and each of its
    downloads is recorded, the row naming the message and its connection rather than an audit event.
    """
    with _event_to_view(tmp_path):

        response = delivery.message(_new_queue_request(''))
        assert response.status_code == 200

        response = delivery.download(_new_queue_request(delivery.Download_Body))
        assert response.status_code == 200
        assert response.content == _queue_message.encode('utf-8')

        response = delivery.download(_new_queue_request('document'))
        assert response.status_code == 200

        view_events = _get_view_events()
        assert len(view_events) == 3

        for view_event in view_events:
            assert view_event['attrs']['actor'] == _username
            assert view_event['attrs']['viewed_source'] == _queue_conn_type
            assert view_event['attrs']['viewed_object_name'] == _queue_conn_name
            assert view_event['attrs']['viewed_msg_id'] == _queue_msg_id
            assert 'viewed_event_id' not in view_event['attrs']

        # The record reads by the message's coordinates, there being no event to resolve it against
        engine = get_audit_engine()

        data_query = select(event_table.c.data, event_table.c.event_time_iso)
        data_query = data_query.where(event_table.c.id == view_events[0]['id'])

        with engine.connect() as connection:
            data, event_time_iso = connection.execute(data_query).fetchone()

        rendered = render_view_record(engine, data, event_time_iso)

        assert f'Viewed by:  {_username}' in rendered
        assert f'Viewed:     {_queue_conn_name} ({_queue_conn_type})' in rendered
        assert f'Message:    {_queue_msg_id}' in rendered
        assert 'Screen:     Delivery queue' in rendered
