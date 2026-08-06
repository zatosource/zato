# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A message read out of a mailbox leaves one message-received row with its attachments
# stored as they arrived - through the generic IMAP reader and through the Microsoft 365
# one alike - and the service that receives the message afterwards still reads every
# attachment in full.

# stdlib
from json import loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.attachment import get_attachment, list_attachments
from zato.common.ext.bunch import Bunch
from zato.server.connection.email import Microsoft365IMAPConnection, _build_attachment_envelopes, \
    _get_message_summary, _insert_imap_audit_event

# Test support
from imap_stub import imap_audit_env, new_imap_connection, new_message_struct, new_native_ms365_message, \
    Attachment_Content, Attachment_Name, Attachment_Type, Body_Text, Connection_Name, Subject

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import os
    from zato.common.typing_ import anylist

    os = os

# ################################################################################################################################
# ################################################################################################################################

def _get_events() -> 'anylist':
    """ Everything the audit log holds, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.order_by(event_table.c.id)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    return out

# ################################################################################################################################
# ################################################################################################################################

def test_a_received_message_writes_one_event_with_its_attachments(tmp_path:'os.PathLike') -> 'None':
    """ Reading a mailbox records each message with the files it arrived with.
    """
    with imap_audit_env(tmp_path):

        conn = new_imap_connection(new_message_struct())
        messages = list(conn.get())

        assert len(messages) == 1

        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['source'] == AuditSource.Email_IMAP
        assert event['event_type'] == AuditEvent.Message_Received
        assert event['object_name'] == Connection_Name
        assert event['outcome'] == AuditOutcome.OK
        assert event['msg_id'] == '4211'

        # The data is the summary of what arrived
        summary = loads(event['data'])

        assert summary['subject'] == Subject
        assert summary['body'] == Body_Text

        # The attachment arrived with the event, bytes and all
        engine = get_audit_engine()
        items = list_attachments(engine, event['id'])

        assert len(items) == 1
        assert items[0]['filename'] == Attachment_Name
        assert items[0]['content_type'] == Attachment_Type

        stored = get_attachment(engine, items[0]['id'])
        assert stored['content'] == Attachment_Content

# ################################################################################################################################

def test_the_service_still_reads_the_attachment_in_full(tmp_path:'os.PathLike') -> 'None':
    """ The audit write reads the attachment's bytes without consuming the stream
    the service receives afterwards.
    """
    with imap_audit_env(tmp_path):

        conn = new_imap_connection(new_message_struct())
        _, message = list(conn.get())[0]

        service_side_content = message.data.attachments[0]['content'].read()
        assert service_side_content == Attachment_Content

# ################################################################################################################################

def test_the_flag_turned_off_writes_nothing(tmp_path:'os.PathLike') -> 'None':
    """ A connection whose audit log is off reads its mailbox and leaves no trace.
    """
    with imap_audit_env(tmp_path):

        conn = new_imap_connection(new_message_struct(), is_audit_log_active=False)
        messages = list(conn.get())

        assert len(messages) == 1
        assert _get_events() == []

# ################################################################################################################################
# ################################################################################################################################

def _new_ms365_connection() -> 'Microsoft365IMAPConnection':
    """ Builds the Microsoft 365 connection under test - only what the conversion
    and the audit write reach for, no live Graph anywhere.
    """
    config = Bunch()

    config.name = Connection_Name
    config.is_audit_log_active = True

    audit_log = AuditLog('test-ms365-audit-server')

    out = Microsoft365IMAPConnection(config, config, audit_log)
    return out

# ################################################################################################################################

def test_a_microsoft_365_message_writes_the_decoded_bytes(tmp_path:'os.PathLike') -> 'None':
    """ A native Microsoft 365 message goes through the conversion and the audit write -
    the envelope carries the decoded bytes and the service-side stream still reads in full.
    """
    with imap_audit_env(tmp_path):

        conn = _new_ms365_connection()
        native = new_native_ms365_message()

        imap_message = conn._convert_to_imap_message('msg-365-1', native)

        # The very write the reader performs for each message it hands over
        data = _get_message_summary(imap_message.data)
        attachment_envelopes = _build_attachment_envelopes(imap_message.data.attachments)

        _insert_imap_audit_event(conn.audit_log, AuditEvent.Message_Received, Connection_Name,
            cid='cid-ms365-1', msg_id='msg-365-1', folder='INBOX', outcome=AuditOutcome.OK, data=data,
            attachments=attachment_envelopes)

        events = _get_events()
        assert len(events) == 1

        event = events[0]
        assert event['cid'] == 'cid-ms365-1'

        # The envelope carries the bytes the Graph API sent base64-encoded, decoded back
        engine = get_audit_engine()
        items = list_attachments(engine, event['id'])

        assert len(items) == 1

        stored = get_attachment(engine, items[0]['id'])
        assert stored['content'] == Attachment_Content

        # The stream the service reads afterwards is still intact
        service_side_content = imap_message.data.attachments[0]['content'].read()
        assert service_side_content == Attachment_Content

# ################################################################################################################################
# ################################################################################################################################
