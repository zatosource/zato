# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc

# Zato
from zato.common.api import AS2
from zato.common.as2.config import build_partnerships
from zato.common.as2.outbound import describe_send_result, new_send_report
from zato.common.as2.reconcile import MDNReconciler
from zato.common.as2.resubmit import find_connection_name, load_event, reprocess, resend
from zato.common.audit_log.api import AuditLog
from zato.common.json_internal import dumps
from zato.server.service import Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.outbound import SendResult
    from zato.common.typing_ import dictlist, stranydict, strnone
    SendResult = SendResult
    stranydict = stranydict
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# What the resubmit reports call each of the two directions.
_action_resend    = 'resend'
_action_reprocess = 'reprocess'

# ################################################################################################################################
# ################################################################################################################################

class ResendAS2Message(AdminService):
    """ Resends the payload stored with an outbound AS2 audit event through the partner's
    outgoing connection, as a fresh message with a new Message-ID - an operator action,
    distinct from the automatic resend that reuses the original Message-ID
    when an MDN is overdue. The new attempt lands as its own audit event
    linked to the original one by the correlation id.
    """
    name = 'zato.audit-log.as2.resend'
    input = Int('event_id')
    output = 'response_data'

    def handle(self) -> 'None':

        event_id = self.request.input.event_id

        # A failed resend comes back as a report too, never as a bare exception,
        # so the caller always sees the same shape with the details inside.
        try:
            event = load_event(event_id)

            # The identities of the original exchange name the connection the payload goes back through.
            as2_from, as2_to = event.object_name.split(':', 1)

            configs:'dictlist' = []
            for config in self.server.config_manager.outconn_as2.values():
                configs.append(config)

            connection_name = find_connection_name(configs, as2_from, as2_to)

            # Deliver the payload through the real pipeline and record the new attempt -
            # the resend records the events itself so it can link them to the original
            # by the correlation id, hence the connection's own recording is turned off.
            invoker = self.as2[connection_name]
            reconciler = MDNReconciler(self.server.name)

            def send(payload:'str', filename:'strnone') -> 'SendResult':
                out = invoker.send(payload, filename, needs_audit=False)
                return out

            result = resend(event, send, reconciler, self.cid)
            report = describe_send_result(result)

        except Exception:
            report = new_send_report()
            report['error'] = format_exc()

        report['action'] = _action_resend
        report['cid'] = self.cid

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################
# ################################################################################################################################

class ReprocessAS2Message(AdminService):
    """ Re-publishes the payload stored with an inbound AS2 audit event to the partner's
    routing target - for when the recipient system was down and the already-received
    documents are to flow again. The new attempt lands as its own audit event
    linked to the original one by the correlation id.
    """
    name = 'zato.audit-log.as2.reprocess'
    input = Int('event_id')
    output = 'response_data'

    def handle(self) -> 'None':

        event_id = self.request.input.event_id

        # Our report to produce - a failed reprocess comes back as a report too,
        # never as a bare exception, so the caller always sees the same shape.
        report:'stranydict' = {
            'is_ok': False,
            'target_kind': '',
            'target_name': '',
            'error': '',
        }

        # The routing targets a reprocessed message can land on.
        def invoke_service(service_name:'str', message:'stranydict') -> 'None':
            _ = self.server.invoke(service_name, message)

        def publish(topic_name:'str', message:'stranydict') -> 'None':
            _ = self.server.pubsub_redis.publish(topic_name, message, cid=self.cid, correl_id=self.cid)

        try:
            event = load_event(event_id)

            # The partnerships carry the per-partner routing overrides.
            configs:'dictlist' = []
            for config in self.server.config_manager.outconn_as2.values():
                configs.append(config)

            partnerships = build_partnerships(configs)
            audit_log = AuditLog(self.server.name)

            result = reprocess(
                event, partnerships, invoke_service, publish, audit_log, self.cid, AS2.Default.Inbound_Topic)

            report['is_ok'] = True
            report['target_kind'] = result.target_kind
            report['target_name'] = result.target_name

        except Exception:
            report['error'] = format_exc()

        report['action'] = _action_reprocess
        report['cid'] = self.cid

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################
# ################################################################################################################################
