# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A direct SMTP send leaves one message-sent row describing what went out on the wire -
# summary, recipients, outcome and the attachments as they were sent - and a delivery
# through the hop machinery leaves that row and the hop's own request-sent row under
# one correlation id.

# stdlib
from json import loads

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.api import SMTPMessage
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditOutcome, AuditSource
from zato.common.audit_log.attachment import get_attachment, list_attachments
from zato.common.destination.constants import DestinationOption, DestinationType
from zato.common.destination.coordinator import deliver_hop, new_context, PlannedHop
from zato.common.destination.model import DestinationEntry
from zato.server.destination.hook import build_transports

# Test support
from smtp_stub import new_smtp_connection, smtp_audit_env, Connection_Name, RaisingTransport, Raised_Error, Server_Name

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import os
    from zato.common.typing_ import any_, anylist

    os = os

# ################################################################################################################################
# ################################################################################################################################

# The message every test sends
_subject = 'Discharge summary'
_from = 'sender@example.com'
_to = ['first@example.com', 'second@example.com']
_body = 'The summary the recipients receive'

# The two files that travel with it
_pdf_name = 'summary.pdf'
_pdf_content = b'%PDF-1.4 summary'

_txt_name = 'notes.txt'
_txt_content = b'plain notes'

# The cid a caller hands the send
_cid = 'cid-smtp-audit-1'

# ################################################################################################################################
# ################################################################################################################################

def _new_message() -> 'SMTPMessage':
    """ Builds the message the tests send - a subject, two recipients and two attachments.
    """
    out = SMTPMessage(from_=_from, to=_to, subject=_subject, body=_body)

    out.attach(_pdf_name, _pdf_content)
    out.attach(_txt_name, _txt_content)

    return out

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

def test_a_successful_send_writes_one_message_sent_event(tmp_path:'os.PathLike') -> 'None':
    """ A send that went through leaves one row - the wire truth of what left the server.
    """
    with smtp_audit_env(tmp_path):

        conn = new_smtp_connection()
        result = conn.send(_new_message(), cid=_cid)

        assert result is True

        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['source'] == AuditSource.Email_SMTP
        assert event['event_type'] == AuditEvent.Message_Sent
        assert event['object_name'] == Connection_Name
        assert event['outcome'] == AuditOutcome.OK
        assert event['cid'] == _cid
        assert event['endpoint'] == ', '.join(_to)
        assert event['server_name'] == Server_Name

        # The data is the summary of what was sent
        summary = loads(event['data'])

        assert summary['subject'] == _subject
        assert summary['from'] == _from
        assert summary['to'] == ', '.join(_to)
        assert summary['body'] == _body

# ################################################################################################################################

def test_the_sent_attachments_are_stored_as_they_went_out(tmp_path:'os.PathLike') -> 'None':
    """ Each attachment of a sent message is stored with its bytes as they left the server.
    """
    with smtp_audit_env(tmp_path):

        conn = new_smtp_connection()
        _ = conn.send(_new_message(), cid=_cid)

        engine = get_audit_engine()
        event = _get_events()[0]

        items = list_attachments(engine, event['id'])

        assert len(items) == 2

        assert items[0]['filename'] == _pdf_name
        assert items[1]['filename'] == _txt_name

        pdf_attachment = get_attachment(engine, items[0]['id'])
        assert pdf_attachment['content'] == _pdf_content

        txt_attachment = get_attachment(engine, items[1]['id'])
        assert txt_attachment['content'] == _txt_content

# ################################################################################################################################

def test_a_raising_transport_writes_the_error_and_the_send_still_returns_false(tmp_path:'os.PathLike') -> 'None':
    """ A send the server refused is recorded with what stopped it, before the caller learns
    that nothing was sent.
    """
    with smtp_audit_env(tmp_path):

        conn = new_smtp_connection(transport_class=RaisingTransport)
        result = conn.send(_new_message(), cid=_cid)

        assert result is False

        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['event_type'] == AuditEvent.Message_Sent
        assert event['outcome'] == AuditOutcome.Error
        assert Raised_Error in event['status']

# ################################################################################################################################

def test_the_flag_turned_off_writes_nothing(tmp_path:'os.PathLike') -> 'None':
    """ A connection whose audit log is off sends and leaves no trace.
    """
    with smtp_audit_env(tmp_path):

        conn = new_smtp_connection(is_audit_log_active=False)
        result = conn.send(_new_message(), cid=_cid)

        assert result is True
        assert _get_events() == []

# ################################################################################################################################

class _ConnectionsStub:
    """ Stands in for what a delivery reaches connections through - only the SMTP side
    is real, built around the recording transport.
    """

    class _Item:
        def __init__(self, conn:'any_') -> 'None':
            self.conn = conn

    class _EMail:
        def __init__(self, item:'any_') -> 'None':
            self.smtp = {Connection_Name: item}

    def __init__(self) -> 'None':
        self.rest = None
        self.mllp = None
        self.fhir = None
        self.email = self._EMail(self._Item(new_smtp_connection()))

# ################################################################################################################################

def test_a_hop_delivery_and_the_send_it_causes_share_one_cid(tmp_path:'os.PathLike') -> 'None':
    """ One delivery through the hop machinery leaves two rows - the hop's own request-sent
    row and the connection's message-sent row - and one cid ties them together.
    """
    with smtp_audit_env(tmp_path):

        connections = _ConnectionsStub()

        entry = DestinationEntry()
        entry.name = 'test.smtp.destination'
        entry.type = DestinationType.SMTP
        entry.connection = Connection_Name
        entry.options = {
            DestinationOption.To: ', '.join(_to),
            DestinationOption.Subject: _subject,
        }

        audit_log = connections.email.smtp[Connection_Name].conn.audit_log

        transports = build_transports(connections)
        context = new_context('test.smtp.channel', _cid, transports, audit_log)

        planned = PlannedHop()
        planned.entry = entry
        planned.payload = _body
        planned.sequence = 1

        result = deliver_hop(context, planned)
        assert result.is_ok is True

        events = _get_events()
        assert len(events) == 2

        # The connection's row was written first, from inside the delivery ..
        message_sent = events[0]
        assert message_sent['event_type'] == AuditEvent.Message_Sent

        # .. and the hop's own row after the delivery returned.
        request_sent = events[1]
        assert request_sent['event_type'] == AuditEvent.Request_Sent

        # Both describe one delivery, under one correlation id
        assert message_sent['cid'] == _cid
        assert request_sent['cid'] == _cid

        assert message_sent['source'] == AuditSource.Email_SMTP
        assert request_sent['source'] == AuditSource.Email_SMTP

# ################################################################################################################################
# ################################################################################################################################
