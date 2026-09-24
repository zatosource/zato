# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# SMTP resubmit semantics on top of the shared resubmit core.

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.api import SMTPMessage
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource, get_audit_engine
from zato.common.audit_log.attachment import build_attachment, get_attachment, list_attachments
from zato.common.audit_log.resubmit import register_resubmit_handler, require_event_type, ResubmitException, \
    Action_Resend
from zato.common.email.audit import Key_Charset, Key_Headers, Key_Is_HTML, Key_Is_RFC2231, Key_Recipients
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.audit_log.resubmit import StoredEvent
    from zato.common.typing_ import anylist, callable_, intnone, stranydict
    anylist = anylist
    AuditLog = AuditLog
    callable_ = callable_
    intnone = intnone
    StoredEvent = StoredEvent
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# What the status of a refused send reads as, the connection answering False rather than saying why.
_send_refused_status = 'SMTP send refused'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SMTPResendResult:
    """ What one SMTP resend did - the new event and how many attachments travelled with the message.
    """
    event_id: 'intnone' = None
    attachment_count: int = 0

# ################################################################################################################################
# ################################################################################################################################

def load_attachments(event_id:'int') -> 'anylist':
    """ The attachments of one recorded e-mail, their bytes included, in the order they were
    stored. An attachment whose bytes were left out because of the size cap stops the resend.
    """
    engine = get_audit_engine()

    # Our response to produce
    out:'anylist' = []

    for item in list_attachments(engine, event_id):

        if not item['is_content_kept']:
            filename = item['filename']
            message = (
                f'Audit event `{event_id}` stored attachment `{filename}` without its content, '
                f'so the message cannot be resubmitted')
            raise ResubmitException(message)

        attachment = get_attachment(engine, item['id'])

        out.append({
            'name': attachment['filename'],
            'content_type': attachment['content_type'],
            'contents': attachment['content'],
        })

    return out

# ################################################################################################################################

def build_attachment_envelopes(attachments:'anylist') -> 'anylist':
    """ The envelopes the new row keeps of the attachments that went back out.
    """
    out:'anylist' = []

    for item in attachments:
        out.append(build_attachment(item['name'], item['content_type'], item['contents']))

    return out

# ################################################################################################################################

def build_message(event:'StoredEvent') -> 'SMTPMessage':
    """ Rebuilds the e-mail one message-sent row recorded - the same recipients, the same body in
    the same form and the same attachments, so what goes out is what went out the first time.
    """
    details = event.details
    recipients = details[Key_Recipients]

    out = SMTPMessage(
        from_=details['from'],
        to=recipients['to'],
        subject=details['subject'],
        body=details['body'],
        attachments=load_attachments(event.id),
        cc=recipients['cc'],
        bcc=recipients['bcc'],
        is_html=details[Key_Is_HTML],
        headers=details[Key_Headers],
        charset=details[Key_Charset],
        is_rfc2231=details[Key_Is_RFC2231],
    )

    return out

# ################################################################################################################################

def resend(event:'StoredEvent', send:'callable_', audit_log:'AuditLog', cid:'str') -> 'SMTPResendResult':
    """ Sends the e-mail one message-sent row recorded through the same connection again. The new
    attempt is its own message-sent event linked to the original by the correlation id, a refusal
    recorded as one too.
    """
    require_event_type(event, AuditEvent.Message_Sent, 'resent')

    # A row written before the resend existed carries neither the recipients as they were given
    # nor what framed the body.
    for key in (Key_Recipients, Key_Headers, Key_Is_HTML, Key_Charset, Key_Is_RFC2231):
        if key not in event.details:
            message = (
                f'Audit event `{event.id}` predates stored message context, so the e-mail it '
                f'recorded cannot be rebuilt')
            raise ResubmitException(message)

    msg = build_message(event)
    data = dumps(event.details)

    # The stored document goes back as it stands, with attachments of its own.
    values:'stranydict' = {
        'cid': cid,
        'correl_id': event.cid,
        'endpoint': event.details['to'],
        'size': len(data),
        'data': data,
        'attachments': build_attachment_envelopes(msg.attachments),
        'parents': [event.id],
    }

    # Hand the message to the real connection ..
    try:
        is_sent = send(msg)

    # .. a send that raised is recorded as its own failed row before the caller learns about it.
    except Exception as e:
        _ = audit_log.insert(
            AuditSource.Email_SMTP, AuditEvent.Message_Sent, event.object_name,
            outcome=AuditOutcome.Error, status=str(e), **values)
        raise

    # A connection reports a refusal as a plain False rather than by raising.
    if not is_sent:
        _ = audit_log.insert(
            AuditSource.Email_SMTP, AuditEvent.Message_Sent, event.object_name,
            outcome=AuditOutcome.Error, status=_send_refused_status, **values)

        raise ResubmitException(f'Connection `{event.object_name}` did not send the message')

    # Our response to produce
    out = SMTPResendResult()
    out.attachment_count = len(msg.attachments)

    out.event_id = audit_log.insert(
        AuditSource.Email_SMTP, AuditEvent.Message_Sent, event.object_name,
        outcome=AuditOutcome.OK, **values)

    return out

# ################################################################################################################################
# ################################################################################################################################

# The service layer supplies the callable when it wires the real connection in.
register_resubmit_handler(AuditSource.Email_SMTP, Action_Resend, resend)

# ################################################################################################################################
# ################################################################################################################################
