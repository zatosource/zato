# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from traceback import format_exc

# Zato
from zato.common.api import AS2, CHANNEL, URL_TYPE
from zato.common.as2.config import build_partnerships
from zato.common.as2.outbound import describe_send_result, new_send_report
from zato.common.as2.reconcile import MDNReconciler
from zato.common.as2.resubmit import find_connection_name, load_event, reprocess, resend
from zato.common.as4.resubmit import describe_send_result as as4_describe_send_result, \
    find_connection_name as as4_find_connection_name, load_event as as4_load_event, \
    new_send_report as as4_new_send_report, reprocess as as4_reprocess, resend as as4_resend
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.resubmit import resend_hop
from zato.common.destination.audit import get_hop_entry
from zato.common.hl7.resubmit import reprocess as hl7_reprocess, resend as hl7_resend
from zato.common.json_internal import dumps
from zato.server.connection.as4 import AS4ChannelRuntime
from zato.server.destination.channel import new_channel_item, run_for_channel
from zato.server.destination.dispatch import send as dispatch_send
from zato.server.destination.hook import narrow_to
from zato.server.service import Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.outbound import SendResult
    from zato.common.as4.ebms import UserMessageDetails
    from zato.common.as4.outbound import SendResult as AS4SendResult
    from zato.common.as4.resend import ResendCandidate
    from zato.common.typing_ import any_, anylist, callable_, dictlist, stranydict, strlist, strnone
    from zato.common.util.xml_.mime_ import part_list
    any_ = any_
    anylist = anylist
    AS4SendResult = AS4SendResult
    callable_ = callable_
    part_list = part_list
    ResendCandidate = ResendCandidate
    SendResult = SendResult
    stranydict = stranydict
    strnone = strnone
    UserMessageDetails = UserMessageDetails

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

            # The payload is the bytes of a single document, or the list of payload items
            # a multi-attachment delivery consists of - the connection takes either.
            def send(payload:'any_', filename:'strnone') -> 'SendResult':
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
            'message_count': 0,
            'error': '',
        }

        # The routing targets a reprocessed message can land on.
        def invoke_service(service_name:'str', message:'stranydict') -> 'None':
            _ = self.server.invoke(service_name, message)

        def publish(topic_name:'str', message:'stranydict') -> 'None':
            _ = self.server.pubsub_backend.publish(topic_name, message, cid=self.cid, correl_id=self.cid)

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

            # A multi-attachment delivery routes one message per document, so the operator
            # sees how many actually went out rather than assuming it was one.
            report['message_count'] = len(result.messages)

        except Exception:
            report['error'] = format_exc()

        report['action'] = _action_reprocess
        report['cid'] = self.cid

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################
# ################################################################################################################################

class ResendAS4Message(AdminService):
    """ Sends the payloads stored with an outbound AS4 audit event through the partner's outgoing
    connection again, as a message of its own with a new eb:MessageId - an operator action, distinct
    from the repeat delivery that reuses the eb:MessageId of the attempt it repeats when a receipt
    is overdue. The new attempt lands as its own audit event linked to the original one
    by the correlation id.
    """
    name = 'zato.audit-log.as4.resend'
    input = Int('event_id')
    output = 'response_data'

    def handle(self) -> 'None':

        event_id = self.request.input.event_id

        # A failed resend comes back as a report too, never as a bare exception,
        # so the caller always sees the same shape with the details inside.
        try:
            event = as4_load_event(event_id)

            # The two eb:PartyId values of the original exchange name the connection
            # the payloads go back out through.
            from_party, to_party = event.object_name.split(':', 1)

            configs:'dictlist' = []
            for config in self._get_outgoing_configs():
                configs.append(config)

            connection_name = as4_find_connection_name(configs, from_party, to_party)

            # Deliver through the real pipeline - the connection's own recording is not used here
            # because the resend records the attempt itself, which is how it links it to the original.
            invoker = self.as4[connection_name]

            def send(candidate:'ResendCandidate') -> 'AS4SendResult':
                out = invoker.resubmit(candidate)
                return out

            audit_log = AuditLog(self.server.name)

            result = as4_resend(event, send, audit_log, self.cid)
            report = as4_describe_send_result(result)

        except Exception:
            report = as4_new_send_report()
            report['error'] = format_exc()

        report['action'] = _action_resend
        report['cid'] = self.cid

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################

    def _get_outgoing_configs(self) -> 'dictlist':
        """ Returns the configuration of every outgoing AS4 connection - what the pair of a stored
        message is matched against.
        """

        # Our response to produce
        out:'dictlist' = []

        config_store = self.server.config_manager.config_store.out_as4

        for name in list(config_store):
            item = config_store[name]

            # The store also holds entries that are not connections of their own.
            if isinstance(item, str):
                continue

            out.append(item.config)

        return out

# ################################################################################################################################
# ################################################################################################################################

class ReprocessAS4Message(AdminService):
    """ Routes the payloads stored with an inbound AS4 audit event to the channel's target again -
    for when the system behind the channel was down and the documents that were already received
    are to flow once more. The new attempt lands as its own audit event linked to the original one
    by the correlation id.
    """
    name = 'zato.audit-log.as4.reprocess'
    input = Int('event_id')
    output = 'response_data'

    def handle(self) -> 'None':

        event_id = self.request.input.event_id

        # A failed reprocess comes back as a report too, never as a bare exception,
        # so the caller always sees the same shape with the details inside.
        report:'stranydict' = {
            'is_ok': False,
            'target_kind': '',
            'target_name': '',
            'message_count': 0,
            'error': '',
        }

        try:
            event = as4_load_event(event_id)

            # The channel the message arrived on is what routes it again, to the target
            # a live delivery goes to.
            runtime = self._get_channel_runtime(event.object_name)

            def route(user_message:'UserMessageDetails', payloads:'part_list') -> 'anylist':
                out = runtime.route_again(self.cid, user_message, payloads)
                return out

            audit_log = AuditLog(self.server.name)

            result = as4_reprocess(event, route, audit_log, self.cid)

            target_kind, target_name = runtime.get_target()

            report['is_ok'] = True
            report['target_kind'] = target_kind
            report['target_name'] = target_name

            # A delivery of several payloads routes one message per payload, so the operator sees
            # how many actually went out rather than assuming it was one.
            report['message_count'] = len(result.messages)

        except Exception:
            report['error'] = format_exc()

        report['action'] = _action_reprocess
        report['cid'] = self.cid

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################

    def _get_channel_runtime(self, pair:'str') -> 'AS4ChannelRuntime':
        """ Returns the runtime of the AS4 channel whose two eb:PartyId values form the given pair.
        The runtime is the one live deliveries use, built on first use the way they build it.
        """
        url_data = self.server.config_manager.request_dispatcher.url_data

        for channel_item in url_data.channel_data:

            if channel_item['transport'] != URL_TYPE.AS4:
                continue

            from_party = channel_item['as4_from_party']
            to_party = channel_item['as4_to_party']

            if f'{from_party}:{to_party}' != pair:
                continue

            runtime = channel_item.get('as4_runtime')

            if runtime is None:
                runtime = AS4ChannelRuntime(self.server, channel_item)
                channel_item['as4_runtime'] = runtime

            out = runtime
            break

        else:
            raise Exception(f'No AS4 channel matches the pair `{pair}`')

        return out

# ################################################################################################################################
# ################################################################################################################################

class ResendHL7Message(AdminService):
    """ Sends the payload stored with an outbound HL7 audit event through the same MLLP
    outgoing connection again - for when the receiving system was down and the messages
    are to flow once more. An edited payload may be supplied in place of the stored one.
    The new attempt lands as its own audit event linked to the original
    by the correlation id, with its acknowledgment recorded alongside.
    """
    name = 'zato.audit-log.hl7.resend'
    input = Int('event_id'), '-payload'
    output = 'response_data'

    def handle(self) -> 'None':

        event_id = self.request.input.event_id

        # An edited payload replaces the stored one - the empty string means none was given
        edited_payload = self.request.input.payload
        if edited_payload == '':
            edited_payload = None

        # A failed resend comes back as a report too, never as a bare exception,
        # so the caller always sees the same shape with the details inside.
        report:'stranydict' = {
            'is_ok': False,
            'event_id': None,
            'control_id': '',
            'ack_status': '',
            'ack_outcome': '',
            'error': '',
        }

        try:
            event = load_event(event_id)

            # The original event names the connection the payload goes back through -
            # the connection's own recording is off because the resend records the events
            # itself, linking them to the original by the correlation id.
            invoker = self.mllp[event.object_name]

            def send(payload:'str') -> 'strnone':
                ack_result = invoker.send(payload, needs_audit=False)
                return ack_result.ack_text # type: ignore[union-attr]

            audit_log = AuditLog(self.server.name)
            result = hl7_resend(event, send, audit_log, self.cid, payload=edited_payload)

            report['is_ok'] = True
            report['event_id'] = result.event_id
            report['control_id'] = result.control_id
            report['ack_status'] = result.ack_status
            report['ack_outcome'] = result.ack_outcome

        except Exception:
            report['error'] = format_exc()

        report['action'] = _action_resend
        report['cid'] = self.cid

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################
# ################################################################################################################################

class ReprocessHL7Message(AdminService):
    """ Re-routes the payload stored with an inbound HL7 audit event through the channel it arrived
    on - for when the recipient system was down and the already-received messages are to flow
    through again. The channel's service runs the way a live delivery would run it and the channel's
    destinations receive what it produced, a channel with no service of its own sending the message
    on as it stands. Naming destinations sends the message to those alone, for catching one receiver
    up without the others being sent it twice. An edited payload may be supplied in place of the
    stored one. The new attempt lands as its own audit event linked to the original
    by the correlation id.
    """
    name = 'zato.audit-log.hl7.reprocess'
    input = Int('event_id'), '-payload', '-destinations'
    output = 'response_data'

    def handle(self) -> 'None':

        event_id = self.request.input.event_id

        # An edited payload replaces the stored one - the empty string means none was given
        edited_payload = self.request.input.payload
        if edited_payload == '':
            edited_payload = None

        # The input arrives as None when the caller names no destinations at all
        destinations = self.request.input.destinations
        if destinations is None:
            destinations = ''

        destination_names = _get_destination_names(destinations)

        # A failed reprocess comes back as a report too, never as a bare exception,
        # so the caller always sees the same shape with the details inside.
        report:'stranydict' = {
            'is_ok': False,
            'event_id': None,
            'control_id': '',
            'service_name': '',
            'destinations': [],
            'error': '',
        }

        try:
            event = load_event(event_id)

            # The original event names the channel it arrived on, and that channel says everything
            # about how the message flows through a second time
            config = _find_channel_config(self.server.config_manager.channel_hl7_mllp, event.object_name)
            channel_item = new_channel_item(config)

            # The message reaches the destinations named and no others
            if destination_names:
                channel_item = narrow_to(channel_item, destination_names)

            def invoke_service(service_name:'str', payload:'str') -> 'None':

                # A channel with a service of its own fans out at the end of that service's
                # pipeline, so the channel rides along with the invocation to be read there ..
                if service_name:
                    _ = self.server.invoke(service_name, payload,
                        channel=CHANNEL.HL7_MLLP, zato_ctx={'zato.channel_item': channel_item})

                # .. and one without a service delivers the message as it stands, the same as
                # it does when a message arrives on it live.
                else:
                    _ = run_for_channel(self.server, channel_item, payload)

            audit_log = AuditLog(self.server.name)
            result = hl7_reprocess(event, config['service'], invoke_service, audit_log, self.cid,
                payload=edited_payload, destination_names=destination_names)

            report['is_ok'] = True
            report['event_id'] = result.event_id
            report['control_id'] = result.control_id
            report['service_name'] = result.service_name
            report['destinations'] = result.destination_names

        except Exception:
            report['error'] = format_exc()

        report['action'] = _action_reprocess
        report['cid'] = self.cid

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################
# ################################################################################################################################

def _find_channel_config(channel_configs:'stranydict', channel_name:'str') -> 'stranydict':
    """ Returns what one HL7 MLLP channel is configured as.
    """
    for config in channel_configs.values():
        if config['name'] == channel_name:
            out = config
            break
    else:
        raise Exception(f'No HL7 MLLP channel matches the name `{channel_name}`')

    return out

# ################################################################################################################################

def _get_destination_names(destinations:'str') -> 'strlist':
    """ Returns the destinations one reprocess was aimed at, out of the comma-separated list
    it names them in - naming none of them aims the reprocess at all of them.
    """
    out:'strlist' = []

    for name in destinations.split(','):
        if name := name.strip():
            out.append(name)

    return out

# ################################################################################################################################
# ################################################################################################################################

class ResendHop(AdminService):
    """ Repeats a single recorded delivery to one destination - the exact payload stored
    with an outgoing event goes through the same connection again, without re-running
    the service that produced it and without involving any other destination.
    The attempt lands as its own audit event linked to the original by the correlation id.
    """
    name = 'zato.audit-log.resend-hop'
    input = Int('event_id')
    output = 'response_data'

    def handle(self) -> 'None':

        event_id = self.request.input.event_id

        # A failed resend comes back as a report too, never as a bare exception,
        # so the caller always sees the same shape with the details inside.
        report:'stranydict' = {
            'is_ok': False,
            'event_id': None,
            'error': '',
        }

        try:
            event = load_event(event_id)

            send = self._build_send(event)

            audit_log = AuditLog(self.server.name)
            result = resend_hop(event, send, audit_log, self.cid)

            report['is_ok'] = True
            report['event_id'] = result.event_id

        except Exception:
            report['error'] = format_exc()

        report['cid'] = self.cid

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################

    def _build_send(self, event:'any_') -> 'callable_':
        """ Returns a callable repeating one recorded delivery. The row says which destination
        it went to and what its own type needed, so the repeat goes out through the very adapter
        the delivery went out through - with the connection's own recording off, because the
        per-hop resend records the attempt itself.
        """
        entry = get_hop_entry(event.source, event.object_name, event.details)

        def send(payload:'str') -> 'any_':
            out = dispatch_send(self, entry, payload)
            return out

        return send

# ################################################################################################################################
# ################################################################################################################################
