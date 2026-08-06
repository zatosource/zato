# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import timedelta

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from common import delete_all_events
from zato.common.audit_log.api import event_body_table, event_table, get_audit_engine, AuditBody, AuditEvent, AuditLog, \
    AuditOutcome, AuditSource
from zato.common.audit_log.attachment import build_attachment, get_attachment, list_attachments, Env_Max_Attachment_Size
from zato.common.audit_log.body import resolve_body
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

# The server name all the test events are written under
_server_name = 'test-audit-log-server'

# The connection the test events belong to
_conn_name = 'audit.test.email'

# The two files the round trip travels with
_pdf_name = 'report.pdf'
_pdf_type = 'application/pdf'
_pdf_content = b'%PDF-1.4 test bytes'

_csv_name = 'rows.csv'
_csv_type = 'text/csv'
_csv_content = b'a,b,c\n1,2,3\n'

# The cap the oversized attachment is measured against
_small_cap = 10

# An event this old is past the default retention window
_row_expired_age_days = 40

# ################################################################################################################################
# ################################################################################################################################

def _count_attachment_rows(event_id:'int') -> 'int':
    """ How many attachment body rows one event has, straight off the table.
    """
    engine = get_audit_engine()

    count_query = select(func.count())
    count_query = count_query.select_from(event_body_table)
    count_query = count_query.where(event_body_table.c.event_id == event_id)
    count_query = count_query.where(event_body_table.c.kind == AuditBody.Attachment)

    with engine.connect() as connection:
        result = connection.execute(count_query)
        out = result.scalar()

    return out

# ################################################################################################################################

def run_attachment_scenario() -> 'None':
    """ The attachment envelope scenario every backend must pass: the round trip of several
    attachments, the size cap, the resolve_body exclusion and retention deleting attachment
    rows together with their events.
    """
    delete_all_events()

    engine = get_audit_engine()
    audit_log = AuditLog(_server_name)

    # An event carrying a message body and two attachments ..
    envelopes = [
        build_attachment(_pdf_name, _pdf_type, _pdf_content),
        build_attachment(_csv_name, _csv_type, _csv_content),
    ]

    event_id = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Message_Sent, _conn_name,
        cid='cid-attachment-1', outcome=AuditOutcome.OK, data='{"subject": "Attachment test"}',
        bodies={AuditBody.Request: 'the message body'}, attachments=envelopes)

    # .. the metadata list carries each file's name, type, size and kept-flag, and never the bytes ..
    items = list_attachments(engine, event_id)

    assert len(items) == 2

    assert items[0]['filename'] == _pdf_name
    assert items[0]['content_type'] == _pdf_type
    assert items[0]['size'] == len(_pdf_content)
    assert items[0]['is_content_kept'] is True
    assert 'content' not in items[0]

    assert items[1]['filename'] == _csv_name

    # .. the bytes come back decoded through the body-row id the metadata names ..
    pdf_attachment = get_attachment(engine, items[0]['id'])
    assert pdf_attachment['content'] == _pdf_content

    csv_attachment = get_attachment(engine, items[1]['id'])
    assert csv_attachment['content'] == _csv_content

    # .. an id nothing was stored under answers with nothing ..
    assert get_attachment(engine, 987654321) is None

    # .. and a body row of another kind is no attachment either.
    body_row_query = select(event_body_table.c.id)
    body_row_query = body_row_query.where(event_body_table.c.event_id == event_id)
    body_row_query = body_row_query.where(event_body_table.c.kind == AuditBody.Request)

    with engine.connect() as connection:
        body_row_id = connection.execute(body_row_query).scalar()

    assert get_attachment(engine, body_row_id) is None

    # The event still resolves its message body for an empty kind - the attachment rows,
    # newer than the body row, must not shadow it
    resolved = resolve_body(engine, AuditSource.Email_SMTP, event_id)
    assert resolved == 'the message body'

    # An attachment over the cap keeps its metadata and loses its bytes
    os.environ[Env_Max_Attachment_Size] = f'{_small_cap}'

    try:
        oversized = build_attachment(_pdf_name, _pdf_type, _pdf_content)
    finally:
        del os.environ[Env_Max_Attachment_Size]

    assert oversized['size'] == len(_pdf_content)
    assert oversized['is_content_kept'] is False
    assert oversized['content'] == ''

    oversized_event_id = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Message_Sent, _conn_name,
        cid='cid-attachment-2', outcome=AuditOutcome.OK, attachments=[oversized])

    oversized_items = list_attachments(engine, oversized_event_id)

    assert len(oversized_items) == 1
    assert oversized_items[0]['is_content_kept'] is False

    oversized_attachment = get_attachment(engine, oversized_items[0]['id'])
    assert oversized_attachment['content'] == b''

    # An event past the retention window takes its attachment rows with it ..
    expired_event_id = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Message_Sent, _conn_name,
        cid='cid-attachment-3', outcome=AuditOutcome.OK,
        attachments=[build_attachment(_csv_name, _csv_type, _csv_content)])

    expired_time = utcnow() - timedelta(days=_row_expired_age_days)
    expired_time_iso = expired_time.isoformat()

    backdate_event = event_table.update()
    backdate_event = backdate_event.where(event_table.c.id == expired_event_id)
    backdate_event = backdate_event.values(event_time_iso=expired_time_iso)

    backdate_bodies = event_body_table.update()
    backdate_bodies = backdate_bodies.where(event_body_table.c.event_id == expired_event_id)
    backdate_bodies = backdate_bodies.values(event_time_iso=expired_time_iso)

    with engine.begin() as connection:
        _ = connection.execute(backdate_event)
        _ = connection.execute(backdate_bodies)

    assert _count_attachment_rows(expired_event_id) == 1

    audit_log._run_retention(utcnow())

    assert _count_attachment_rows(expired_event_id) == 0

    # .. while the event within the window keeps its own.
    assert _count_attachment_rows(event_id) == 2

# ################################################################################################################################
# ################################################################################################################################
