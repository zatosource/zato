# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc

# Zato
from zato.common.api import FileTransfer
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.common import AuditEvent, AuditOutcome
from zato.common.audit_log.file_transfer import record_schedule_event
from zato.common.audit_log.resubmit import load_event, ResubmitException
from zato.common.json_internal import dumps
from zato.server.service import Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The action name in the response.
_action_retry = 'retry'

# ################################################################################################################################
# ################################################################################################################################

class RetryFileTransfer(AdminService):
    """ Moves a quarantined file back to its schedule's directory and records the move as a File_Retried event.
    """
    name = 'zato.audit-log.file-transfer-retry'
    input = Int('event_id'), '-actor'
    output = 'response_data'

    def handle(self) -> 'None':

        event_id = self.request.input.event_id

        # The actor is optional.
        actor = self.request.input.actor
        if actor is None:
            actor = ''

        # Our response to produce, a failed retry has the same shape.
        out:'stranydict' = {
            'is_ok': False,
            'event_id': None,
            'error': '',
        }

        try:
            event = load_event(event_id)

            # Only a quarantined file can be retried.
            if event.event_type != AuditEvent.File_Quarantined:
                msg = f'Only `{AuditEvent.File_Quarantined}` events can be retried, not `{event.event_type}`'
                raise ResubmitException(msg)

            details = event.details

            schedule_name   = details['schedule']
            file_name       = details['file_name']
            full_path       = details['remote_path']
            quarantine_path = details['quarantine_path']
            conn_type       = details['conn_type']
            conn_name       = event.object_name

            # The connection is reached through the facade of its type.
            facade_attr = FileTransfer.Facade_Attr[conn_type]
            facade = getattr(self, facade_attr)
            conn = facade[conn_name]
            conn.cid = self.cid

            audit_log = AuditLog(self.server.name)

            attrs_extra:'stranydict' = {}
            if actor:
                attrs_extra['actor'] = actor

            extra = {
                'conn_type': conn_type,
                'from_path': quarantine_path,
                'retry_reset': True,
            }

            # A failed move is recorded before it is raised.
            try:
                _ = conn.move(quarantine_path, full_path)
            except Exception:
                error = format_exc()
                _ = record_schedule_event(audit_log, conn_name, AuditEvent.File_Retried, full_path,
                    cid=self.cid, correl_id=event.cid, schedule=schedule_name, outcome=AuditOutcome.Error,
                    file_name=file_name, error=error, extra=extra, attrs_extra=attrs_extra, parents=[event.id])
                raise

            new_event_id = record_schedule_event(audit_log, conn_name, AuditEvent.File_Retried, full_path,
                cid=self.cid, correl_id=event.cid, schedule=schedule_name, outcome=AuditOutcome.OK,
                file_name=file_name, extra=extra, attrs_extra=attrs_extra, parents=[event.id])

            out['is_ok'] = True
            out['event_id'] = new_event_id

        except Exception:
            out['error'] = format_exc()

        out['action'] = _action_retry
        out['cid'] = self.cid

        self.response.payload.response_data = dumps(out)

# ################################################################################################################################
# ################################################################################################################################
