# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The resubmit service of service invocations - one recorded request is handed to its service again.

# stdlib
from traceback import format_exc

# Zato
from zato.common.audit_log.common import AuditEvent
from zato.common.audit_log.resubmit import get_stored_payload, load_event, require_event_type, run_once, \
    Action_Reprocess, DuplicateResubmitException
from zato.common.audit_log.service import Resubmit_Of_Cid_Key, Resubmit_Of_Event_Id_Key
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

class ReprocessServiceRequest(AdminService):
    """ Invokes the service recorded by a service-request audit event with the very request body
    the event stored. The service's own request and response events are the new attempt, linked
    to the original by the correlation id and the parent link.
    """
    name = 'zato.audit-log.service.reprocess'
    input = Int('event_id'), '-actor'
    output = 'response_data'

    def handle(self) -> 'None':

        event_id = self.request.input.event_id

        # Who asked for the run - the empty string means the caller did not say.
        actor = self.request.input.actor

        # A failed run comes back as a report too, never as a bare exception,
        # so the caller always sees the same shape with the details inside.
        report:'stranydict' = {
            'is_ok': False,
            'is_duplicate': False,
            'event_id': None,
            'service_name': '',
            'error': '',
        }

        try:
            event = load_event(event_id)
            require_event_type(event, AuditEvent.Service_Request, 'run again')

            service_name = event.object_name
            payload = get_stored_payload(event)

            # The audit hook reads these two keys to link what it records to the event repeated here.
            request_ctx = {
                Resubmit_Of_Event_Id_Key: event.id,
                Resubmit_Of_Cid_Key: event.cid,
            }

            def resubmit_one() -> 'any_':
                out = self.server.invoke(service_name, payload, cid=self.cid, request_ctx=request_ctx)
                return out

            # The key covers the body the service is given.
            _ = run_once(Action_Reprocess, event_id, payload, self.cid, actor, resubmit_one)

            report['is_ok'] = True
            report['service_name'] = service_name

        except DuplicateResubmitException as e:
            report['is_duplicate'] = True
            report['error'] = str(e)

        except Exception:
            report['error'] = format_exc()

        report['action'] = Action_Reprocess
        report['cid'] = self.cid

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################
# ################################################################################################################################
