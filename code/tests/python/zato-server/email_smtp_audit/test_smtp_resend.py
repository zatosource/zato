# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Sending one recorded e-mail again, rebuilt out of the row attachments and all.

# stdlib
import os

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.api import SMTPMessage
from zato.common.audit_log.api import event_table, get_audit_engine, AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.attachment import Env_Max_Attachment_Size
from zato.common.audit_log.resubmit import load_event, ResubmitException
from zato.common.email.resubmit import resend as smtp_resend

# Test support
from smtp_stub import new_smtp_connection, smtp_audit_env, Connection_Name, RaisingTransport, Server_Name, \
    TransportRecorder

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The message the tests record and then send again
_subject = 'Discharge summary'
_from = 'sender@example.com'
_to = ['first@example.com', 'second@example.com']
_cc = ['watcher@example.com']
_bcc = ['archive@example.com']
_body = '<p>The summary the recipients receive</p>'

# The file that travels with it
_pdf_name = 'summary.pdf'
_pdf_content = b'%PDF-1.4 summary'

# The cid the original send ran under, and the one the resend runs under
_original_cid = 'cid-smtp-resend-original'
_resend_cid = 'cid-smtp-resend-new'

# ################################################################################################################################
# ################################################################################################################################

def _new_message() -> 'SMTPMessage':
    """ The e-mail the original send goes out with - an HTML body, every kind of recipient
    and one attachment.
    """
    out = SMTPMessage(from_=_from, to=_to, subject=_subject, body=_body, cc=_cc, bcc=_bcc, is_html=True,
        headers={'X-Zato-Case': 'discharge'})

    out.attach(_pdf_name, _pdf_content)

    return out

# ################################################################################################################################

def _get_rows() -> 'anylist':
    """ Every message-sent row of the connection under test, oldest first.
    """
    engine = get_audit_engine()

    query = select(event_table)
    query = query.where(event_table.c.object_name == Connection_Name)
    query = query.where(event_table.c.event_type == AuditEvent.Message_Sent)
    query = query.order_by(event_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(dict(row._mapping))

    return out

# ################################################################################################################################

def _record_original() -> 'anydict':
    """ Sends one e-mail the ordinary way, so the row a resend reads back is the row a live
    send leaves behind.
    """
    TransportRecorder.sends = []

    connection = new_smtp_connection()
    assert connection.send(_new_message(), cid=_original_cid) is True

    rows = _get_rows()
    assert len(rows) == 1

    out = rows[0]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestSMTPResend:

    def test_the_same_message_goes_out_again_in_full(self, tmp_path:'any_') -> 'None':
        with smtp_audit_env(tmp_path):

            original = _record_original()

            TransportRecorder.sends = []
            connection = new_smtp_connection()

            def send(msg:'any_') -> 'bool':
                out = connection.send(msg, cid=_resend_cid, needs_audit=False)
                return out

            audit_log = AuditLog(Server_Name)
            result = smtp_resend(load_event(original['id']), send, audit_log, _resend_cid)

            assert result.attachment_count == 1

            # The transport was handed the very same e-mail.
            assert len(TransportRecorder.sends) == 1

            email, attachments, from_ = TransportRecorder.sends[0]

            assert from_ == _from
            assert email.recipients == _to
            assert email.subject == _subject
            assert email.html_body == _body
            assert email.fields['CC'] == ', '.join(_cc)
            assert email.fields['BCC'] == ', '.join(_bcc)
            assert email.fields['X-Zato-Case'] == 'discharge'

            assert len(attachments) == 1
            assert attachments[0].name == _pdf_name

# ################################################################################################################################

    def test_the_attempt_is_its_own_row_linked_to_the_one_it_repeats(self, tmp_path:'any_') -> 'None':
        with smtp_audit_env(tmp_path):

            original = _record_original()

            connection = new_smtp_connection()

            def send(msg:'any_') -> 'bool':
                out = connection.send(msg, cid=_resend_cid, needs_audit=False)
                return out

            audit_log = AuditLog(Server_Name)
            result = smtp_resend(load_event(original['id']), send, audit_log, _resend_cid)

            rows = _get_rows()

            assert len(rows) == 2

            attempt_row = rows[1]
            assert attempt_row['id'] == result.event_id
            assert attempt_row['cid'] == _resend_cid
            assert attempt_row['correl_id'] == _original_cid
            assert attempt_row['outcome'] == AuditOutcome.OK

            # The whole document goes back into the new row, so it is as repeatable as the
            # one it repeats.
            assert attempt_row['data'] == original['data']

# ################################################################################################################################

    def test_a_refused_send_is_recorded_and_reported(self, tmp_path:'any_') -> 'None':
        with smtp_audit_env(tmp_path):

            original = _record_original()

            # The transport reports a message it could not send by answering no.
            connection = new_smtp_connection(transport_class=RaisingTransport)

            def send(msg:'any_') -> 'bool':
                out = connection.send(msg, cid=_resend_cid, needs_audit=False)
                return out

            audit_log = AuditLog(Server_Name)

            with pytest.raises(ResubmitException):
                _ = smtp_resend(load_event(original['id']), send, audit_log, _resend_cid)

            rows = _get_rows()

            assert len(rows) == 2

            attempt_row = rows[1]
            assert attempt_row['outcome'] == AuditOutcome.Error
            assert attempt_row['correl_id'] == _original_cid

# ################################################################################################################################

    def test_an_attachment_over_the_cap_refuses_the_whole_resend(self, tmp_path:'any_') -> 'None':
        with smtp_audit_env(tmp_path):

            # The cap is below the attachment, so the row keeps the file's metadata alone.
            os.environ[Env_Max_Attachment_Size] = '4'

            try:
                original = _record_original()
            finally:
                del os.environ[Env_Max_Attachment_Size]

            TransportRecorder.sends = []
            connection = new_smtp_connection()

            def send(msg:'any_') -> 'bool':
                out = connection.send(msg, cid=_resend_cid, needs_audit=False)
                return out

            audit_log = AuditLog(Server_Name)

            # The refusal names the attachment it was stopped by.
            with pytest.raises(ResubmitException) as raised:
                _ = smtp_resend(load_event(original['id']), send, audit_log, _resend_cid)

            assert _pdf_name in str(raised.value)

            # Nothing was sent and nothing was recorded.
            assert TransportRecorder.sends == []
            assert len(_get_rows()) == 1

# ################################################################################################################################

    def test_a_row_from_before_the_resend_existed_is_refused_clearly(self, tmp_path:'any_') -> 'None':
        with smtp_audit_env(tmp_path):

            audit_log = AuditLog(Server_Name)

            # A row of the summary a person reads, with nothing about how the body was framed
            # or how the recipients were given.
            summary_only_id = audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Message_Sent, Connection_Name,
                cid='cid-smtp-summary-only', outcome=AuditOutcome.Error,
                data='{"subject": "Old one", "from": "a@example.com", "to": "b@example.com", "body": "text"}')

            TransportRecorder.sends = []

            def send(msg:'any_') -> 'bool':
                raise Exception('Nothing should have been sent')

            with pytest.raises(ResubmitException) as raised:
                _ = smtp_resend(load_event(summary_only_id), send, audit_log, _resend_cid)

            assert 'predates stored message context' in str(raised.value)
            assert TransportRecorder.sends == []

# ################################################################################################################################
# ################################################################################################################################

class TestPingSource:

    def test_a_ping_is_written_apart_from_the_messages(self, tmp_path:'any_') -> 'None':
        with smtp_audit_env(tmp_path):

            connection = new_smtp_connection()

            def ping(self:'any_') -> 'str':
                return 'EHLO ok'

            # The transport's ping answers nothing of interest, only that it worked.
            connection.conn_class.ping = ping

            _ = connection.ping()

            engine = get_audit_engine()

            query = select(event_table.c.source, event_table.c.event_type)
            query = query.where(event_table.c.object_name == Connection_Name)

            with engine.connect() as db_connection:
                rows = db_connection.execute(query).fetchall()

            # A ping opens a session and closes it without sending anything, so its row is
            # written under the health source rather than among the sent e-mails.
            assert len(rows) == 1

            source, event_type = rows[0]
            assert source == AuditSource.Email_SMTP_Health
            assert event_type == AuditEvent.Request_Sent

# ################################################################################################################################
# ################################################################################################################################
