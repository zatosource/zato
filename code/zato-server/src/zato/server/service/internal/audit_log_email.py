# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The resubmit services of the e-mail connections.

# stdlib
from traceback import format_exc

# Zato
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.resubmit import load_event, run_once, Action_Resend, DuplicateResubmitException
from zato.common.email.resubmit import resend as smtp_resend
from zato.common.json_internal import dumps
from zato.server.service import Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# What the resubmit reports call this direction.
_action_resend = 'resend'

# ################################################################################################################################
# ################################################################################################################################

class ResendSMTPMessage(AdminService):
    """ Sends the e-mail stored with an outgoing SMTP audit event through the same connection
    again - for when the server was down or refused it and the message is to go out once more.
    The message is rebuilt as it was recorded, attachments included, and the new attempt lands
    as its own audit event linked to the original by the correlation id.
    """
    name = 'zato.audit-log.smtp.resend'
    input = Int('event_id'), '-actor'
    output = 'response_data'

    def handle(self) -> 'None':

        event_id = self.request.input.event_id

        # Who asked for the resend - the empty string means the caller did not say
        actor = self.request.input.actor
        if actor is None:
            actor = ''

        # A failed resend comes back as a report too, never as a bare exception,
        # so the caller always sees the same shape with the details inside.
        report:'stranydict' = {
            'is_ok': False,
            'is_duplicate': False,
            'event_id': None,
            'attachment_count': 0,
            'error': '',
        }

        try:
            event = load_event(event_id)

            # The original event names the connection the message goes back through - the
            # connection's own recording is off because the resend records the attempt itself,
            # which is how it links it to the original.
            connection = self.email.smtp[event.object_name].conn

            def send(msg:'any_') -> 'bool':
                out = connection.send(msg, cid=self.cid, needs_audit=False)
                return out

            audit_log = AuditLog(self.server.name)

            def resubmit_one() -> 'any_':
                out = smtp_resend(event, send, audit_log, self.cid)
                return out

            # The key covers the body of the e-mail.
            key_payload = event.details['body']

            result = run_once(Action_Resend, event_id, key_payload, self.cid, actor, resubmit_one)

            report['is_ok'] = True
            report['event_id'] = result.event_id
            report['attachment_count'] = result.attachment_count

        except DuplicateResubmitException as e:
            report['is_duplicate'] = True
            report['error'] = str(e)

        except Exception:
            report['error'] = format_exc()

        report['action'] = _action_resend
        report['cid'] = self.cid

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################
# ################################################################################################################################
