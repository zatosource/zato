# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An alert e-mail names a connection and nothing else, so a Microsoft 365 connection
# must serve the same interface the generic SMTP one serves - the message goes out
# through the Graph mailbox, the audit log receives the same message-sent events
# and the store hands out the kind of connection the server type names.

# stdlib
import os
from base64 import b64decode
from contextlib import contextmanager
from json import loads

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.api import EMAIL, SMTPMessage
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource, \
     ModuleCtx as AuditLogCtx
from zato.common.audit_log.attachment import get_attachment, list_attachments
from zato.common.ext.bunch import Bunch
from zato.server.connection.email import Microsoft365SMTPConnection, SMTPConnection, SMTPConnStore

# Test support
from chat_simulators import find_free_port
from live_sql.env import database_env
from teams_simulator import start_teams_server, TeamsGraphTestHandler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anylist

    envgen = Iterator[None]

# ################################################################################################################################
# ################################################################################################################################

# The server the audit events are written under
Server_Name = 'test-microsoft-365-smtp-server'

# The name the connection under test goes by
Connection_Name = 'test.microsoft.365.smtp'

# The mailbox the messages go out through
Mailbox_Address = 'alerts@example.com'

# The credentials the simulated Graph accepts
Tenant_ID = 'tenant-id-microsoft-365-smtp'
Client_ID = 'client-id-microsoft-365-smtp'
Client_Secret = 'secret-microsoft-365-smtp'

# The message every test sends
_subject = 'Discharge summary'
_to = 'first@example.com'
_body = 'The summary the recipient receives'

# The file that travels with it when a test attaches one
_pdf_name = 'summary.pdf'
_pdf_content = b'%PDF-1.4 summary'

# The cid a caller hands the send
_cid = 'cid-microsoft-365-smtp-1'

# The prefix all the audit log database environment variables share
_env_prefix = 'Zato_Audit_Log_DB_'

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def audit_env(tmp_path:'any_') -> 'envgen':
    """ Points the audit log at a throwaway SQLite database for the duration of a test.
    """
    db_path = os.path.join(str(tmp_path), 'audit.db')

    details = {
        'type': AuditLogCtx.Type_SQLite,
        'name': db_path,
    }

    with database_env(_env_prefix, details):
        yield

# ################################################################################################################################

@pytest.fixture()
def graph_server() -> 'any_':
    """ The simulated Graph the connection under test sends through, over TLS.
    """
    port = find_free_port()
    server = start_teams_server(port, Tenant_ID, Client_ID, Client_Secret, teams=[])

    yield f'https://127.0.0.1:{port}'

    server.shutdown()

# ################################################################################################################################

def new_connection(
    address:'str',
    *,
    secret:'str' = Client_Secret,
    is_audit_log_active:'bool' = True,
    ) -> 'Microsoft365SMTPConnection':
    """ Builds the connection under test, pointed at the simulated Graph.
    """
    config = Bunch()

    config.name = Connection_Name
    config.username = Mailbox_Address
    config.tenant_id = Tenant_ID
    config.client_id = Client_ID
    config.password = secret
    config.address = address
    config.auth_server_url = address
    config.verify_tls = False
    config.is_audit_log_active = is_audit_log_active

    audit_log = AuditLog(Server_Name)

    out = Microsoft365SMTPConnection(config, config, audit_log)
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

def test_a_send_reaches_the_mailbox_with_recipient_subject_and_body(
    tmp_path:'os.PathLike',
    graph_server:'str',
    ) -> 'None':
    """ What a send was given is what arrives at the Graph - the mailbox it goes out
    through, the recipient, the subject and the plain-text body.
    """
    with audit_env(tmp_path):

        conn = new_connection(graph_server)

        msg = SMTPMessage(to=_to, subject=_subject, body=_body)
        result = conn.send(msg, cid=_cid)

        assert result is True

        # One message reached the simulator, through the configured mailbox
        assert len(TeamsGraphTestHandler.sent_mail) == 1

        sent = TeamsGraphTestHandler.sent_mail[0]
        assert sent['mailbox'] == Mailbox_Address

        message = sent['payload']['message']

        assert message['subject'] == _subject
        assert message['body']['content'] == _body
        assert message['body']['contentType'] == 'Text'

        recipients = message['toRecipients']
        assert len(recipients) == 1
        assert recipients[0]['emailAddress']['address'] == _to

# ################################################################################################################################

def test_a_successful_send_writes_one_message_sent_event(
    tmp_path:'os.PathLike',
    graph_server:'str',
    ) -> 'None':
    """ A send that went through leaves the same message-sent row the generic
    SMTP connection leaves.
    """
    with audit_env(tmp_path):

        conn = new_connection(graph_server)

        msg = SMTPMessage(to=_to, subject=_subject, body=_body)
        _ = conn.send(msg, cid=_cid)

        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['source'] == AuditSource.Email_SMTP
        assert event['event_type'] == AuditEvent.Message_Sent
        assert event['object_name'] == Connection_Name
        assert event['outcome'] == AuditOutcome.OK
        assert event['cid'] == _cid
        assert event['endpoint'] == _to
        assert event['server_name'] == Server_Name

        # The data is the summary of what was sent
        summary = loads(event['data'])

        assert summary['subject'] == _subject
        assert summary['to'] == _to
        assert summary['body'] == _body

# ################################################################################################################################

def test_an_html_message_keeps_its_html_body(
    tmp_path:'os.PathLike',
    graph_server:'str',
    ) -> 'None':
    """ A message built as HTML arrives at the Graph with an HTML body.
    """
    with audit_env(tmp_path):

        conn = new_connection(graph_server)

        html_body = '<p>The summary the recipient receives</p>'

        msg = SMTPMessage(to=_to, subject=_subject, body=html_body, is_html=True)
        result = conn.send(msg, cid=_cid)

        assert result is True

        sent = TeamsGraphTestHandler.sent_mail[0]
        message = sent['payload']['message']

        assert message['body']['content'] == html_body
        assert message['body']['contentType'] == 'HTML'

# ################################################################################################################################

def test_attachments_travel_inside_the_message_and_into_the_audit_log(
    tmp_path:'os.PathLike',
    graph_server:'str',
    ) -> 'None':
    """ An attachment goes out inside the Graph message itself and its bytes,
    as they went out, are what the audit log keeps.
    """
    with audit_env(tmp_path):

        conn = new_connection(graph_server)

        msg = SMTPMessage(to=_to, subject=_subject, body=_body)
        msg.attach(_pdf_name, _pdf_content)

        result = conn.send(msg, cid=_cid)
        assert result is True

        # The attachment arrived at the simulator, base64-encoded inside the message
        sent = TeamsGraphTestHandler.sent_mail[0]
        message = sent['payload']['message']

        attachments = message['attachments']
        assert len(attachments) == 1

        assert attachments[0]['name'] == _pdf_name
        assert b64decode(attachments[0]['contentBytes']) == _pdf_content

        # The audit log keeps the same bytes
        engine = get_audit_engine()
        event = _get_events()[0]

        items = list_attachments(engine, event['id'])
        assert len(items) == 1
        assert items[0]['filename'] == _pdf_name

        stored = get_attachment(engine, items[0]['id'])
        assert stored['content'] == _pdf_content

# ################################################################################################################################

def test_rejected_credentials_write_the_error_and_the_send_returns_false(
    tmp_path:'os.PathLike',
    graph_server:'str',
    ) -> 'None':
    """ A send the Graph's own token server refused is recorded with what stopped it,
    before the caller learns that nothing was sent.
    """
    with audit_env(tmp_path):

        conn = new_connection(graph_server, secret='secret-that-does-not-match')

        msg = SMTPMessage(to=_to, subject=_subject, body=_body)
        result = conn.send(msg, cid=_cid)

        assert result is False
        assert TeamsGraphTestHandler.sent_mail == []

        events = _get_events()
        assert len(events) == 1

        event = events[0]

        assert event['event_type'] == AuditEvent.Message_Sent
        assert event['outcome'] == AuditOutcome.Error

# ################################################################################################################################

def test_the_flag_turned_off_writes_nothing(
    tmp_path:'os.PathLike',
    graph_server:'str',
    ) -> 'None':
    """ A connection whose audit log is off sends and leaves no trace.
    """
    with audit_env(tmp_path):

        conn = new_connection(graph_server, is_audit_log_active=False)

        msg = SMTPMessage(to=_to, subject=_subject, body=_body)
        result = conn.send(msg, cid=_cid)

        assert result is True
        assert _get_events() == []

# ################################################################################################################################

def test_the_store_builds_the_kind_the_server_type_names() -> 'None':
    """ The store reads the server type and hands out the matching kind of connection,
    with connections that predate the type treated as generic ones.
    """
    store = SMTPConnStore(Server_Name)

    # A Microsoft 365 connection needs no SMTP details of its own
    ms365_config = Bunch()
    ms365_config.name = Connection_Name
    ms365_config.username = Mailbox_Address
    ms365_config.tenant_id = Tenant_ID
    ms365_config.client_id = Client_ID
    ms365_config.password = Client_Secret
    ms365_config.server_type = EMAIL.SMTP.ServerType.Microsoft365
    ms365_config.is_audit_log_active = True

    ms365_conn = store.create_impl(ms365_config, ms365_config)
    assert isinstance(ms365_conn, Microsoft365SMTPConnection)

    # A generic connection speaks the SMTP protocol itself
    generic_config = Bunch()
    generic_config.name = 'test.generic.smtp'
    generic_config.host = 'smtp.example.com'
    generic_config.port = 587
    generic_config.mode = EMAIL.SMTP.MODE.STARTTLS
    generic_config.is_debug = False
    generic_config.timeout = 10
    generic_config.needs_tls_verify = True
    generic_config.ca_certs_path = ''
    generic_config.helo_hostname = ''
    generic_config.from_address = ''
    generic_config.username = ''
    generic_config.password = ''
    generic_config.server_type = EMAIL.SMTP.ServerType.Generic
    generic_config.is_audit_log_active = True

    generic_conn = store.create_impl(generic_config, generic_config)
    assert isinstance(generic_conn, SMTPConnection)

    # A connection created before the server type existed is a generic one
    older_config = Bunch()
    older_config.name = 'test.older.smtp'
    older_config.host = 'smtp.example.com'
    older_config.port = 587
    older_config.mode = EMAIL.SMTP.MODE.STARTTLS
    older_config.is_debug = False
    older_config.timeout = 10
    older_config.needs_tls_verify = True
    older_config.ca_certs_path = ''
    older_config.helo_hostname = ''
    older_config.from_address = ''
    older_config.username = ''
    older_config.password = ''
    older_config.is_audit_log_active = True

    older_conn = store.create_impl(older_config, older_config)
    assert isinstance(older_conn, SMTPConnection)

# ################################################################################################################################
# ################################################################################################################################
