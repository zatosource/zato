# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic
from traceback import format_exc

# Zato
from zato.common.api import CHANNEL
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.common import AuditEvent, AuditOutcome
from zato.common.audit_log.file_transfer import load_transfer_content, record_schedule_event
from zato.common.audit_log.resubmit import get_stored_payload, load_event, require_resendable_request, resend_hop, \
    run_once, Action_Reprocess, Action_Resend, DuplicateResubmitException, ResubmitException
from zato.common.destination.audit import get_hop_entry
from zato.common.file_transfer.api import Default_Encoding
from zato.common.hl7.mllp.preprocess import build_channel_tolerance_config
from zato.common.hl7.resubmit import reprocess as hl7_reprocess, resend as hl7_resend
from zato.common.json_internal import dumps
from zato.common.model.file_transfer_ import FileTransferItem
from zato.common.pubsub.outgoing import SendResult as QueueSendResult
from zato.common.util.api import asbool
from zato.hl7v2 import parse_hl7
from zato.server.destination.channel import new_channel_item, run_for_channel
from zato.server.destination.dispatch import send as dispatch_send, is_own_recorded_call, send_recorded
from zato.server.destination.hook import narrow_to
from zato.server.service import Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.destination.model import HopSendResult
    from zato.common.typing_ import any_, callable_, stranydict, strlist, strnone
    any_ = any_
    callable_ = callable_
    HopSendResult = HopSendResult
    stranydict = stranydict
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# What the resubmit reports call each of the two directions.
_action_resend    = 'resend'
_action_reprocess = 'reprocess'

# Milliseconds per second.
_ms_per_second = 1000

# ################################################################################################################################
# ################################################################################################################################

def _elapsed_ms(start:'float') -> 'int':
    elapsed = monotonic() - start
    out = int(elapsed * _ms_per_second)
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
            'is_duplicate': False,
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
                result = invoker.send(payload, needs_audit=False)

                # With the queue switch on the acknowledgment, if there was one, rides on the result
                if isinstance(result, QueueSendResult):
                    result = result.response

                if result is None:
                    return None

                out = result.ack_text
                return out

            audit_log = AuditLog(self.server.name)

            def resubmit_one() -> 'any_':
                out = hl7_resend(event, send, audit_log, self.cid, payload=edited_payload)
                return out

            # The key covers the payload that actually goes out.
            if edited_payload is None:
                key_payload = get_stored_payload(event)
            else:
                key_payload = edited_payload

            result = run_once(Action_Resend, event_id, key_payload, self.cid, '', resubmit_one)

            report['is_ok'] = True
            report['event_id'] = result.event_id
            report['control_id'] = result.control_id
            report['ack_status'] = result.ack_status
            report['ack_outcome'] = result.ack_outcome

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
            'is_duplicate': False,
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

                # Everything runs under the reprocess's own cid, the same as a live delivery runs under
                # the cid the message arrived under, so the new row and every delivery it fanned out to
                # read as one trail.

                # A channel with a service of its own fans out at the end of that service's
                # pipeline, so the channel rides along with the invocation to be read there ..
                if service_name:

                    # A live delivery gives the service a parsed message when the channel
                    # parses on input, so a reprocess gives it the same shape, parsed under the
                    # channel's own tolerance toggles - without re-validating, because the
                    # message was already accepted once.
                    if asbool(config['should_parse_on_input']):
                        tolerance_config = build_channel_tolerance_config(config)
                        service_payload = parse_hl7(payload, validate=False, tolerance=tolerance_config)
                    else:
                        service_payload = payload

                    _ = self.server.invoke(service_name, service_payload, cid=self.cid,
                        channel=CHANNEL.HL7_MLLP, zato_ctx={'zato.channel_item': channel_item})

                # .. and one without a service delivers the message as it stands, the same as
                # it does when a message arrives on it live.
                else:
                    _ = run_for_channel(self.server, channel_item, payload, cid=self.cid)

            audit_log = AuditLog(self.server.name)

            def resubmit_one() -> 'any_':
                out = hl7_reprocess(event, config['service'], invoke_service, audit_log, self.cid,
                    payload=edited_payload, destination_names=destination_names)
                return out

            # The key covers the payload that actually goes through.
            if edited_payload is None:
                key_payload = get_stored_payload(event)
            else:
                key_payload = edited_payload

            # Which destinations the message reaches is part of what the key covers, catching one
            # receiver up and then another being two operations rather than one repeated.
            key_destinations = ','.join(destination_names)
            key_material = f'{key_payload}:{key_destinations}'

            result = run_once(Action_Reprocess, event_id, key_material, self.cid, '', resubmit_one)

            report['is_ok'] = True
            report['event_id'] = result.event_id
            report['control_id'] = result.control_id
            report['service_name'] = result.service_name
            report['destinations'] = result.destination_names

        except DuplicateResubmitException as e:
            report['is_duplicate'] = True
            report['error'] = str(e)

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

class ReprocessFileTransfer(AdminService):
    """ Runs a stored file transfer through the schedule's target service again - for when
    the service or the system behind it was down and an already-taken file needs to be
    processed once more. The bytes come from the read event, which stored them when
    the connection keeps file contents. The new attempt is recorded as its own audit event
    linked to the original one by the correlation id.
    """
    name = 'zato.audit-log.file-transfer-reprocess'
    input = Int('event_id'), '-actor'
    output = 'response_data'

    def handle(self) -> 'None':

        event_id = self.request.input.event_id

        # The actor is optional.
        actor = self.request.input.actor
        if actor is None:
            actor = ''

        # A failed reprocess comes back as a report too, never as a bare exception,
        # so the caller always sees the same shape with the details inside.
        report:'stranydict' = {
            'is_ok': False,
            'is_duplicate': False,
            'event_id': None,
            'error': '',
        }

        try:
            event = load_event(event_id)

            # Only what a schedule handed to its target service can be run through it again
            if event.event_type not in (AuditEvent.Delivered, AuditEvent.Delivery_Failed):
                error_message = f'Only `{AuditEvent.Delivered}` and `{AuditEvent.Delivery_Failed}` events ' + \
                    f'can be reprocessed, not `{event.event_type}`'
                raise ResubmitException(error_message)

            # The event's own data says which schedule took the file, which service received it
            # and what the file was - the bytes come from the read event sharing the same cid.
            details = event.details

            schedule_name = details['schedule']
            service_name = details['service']
            file_name = details['file_name']
            full_path = details['remote_path']
            conn_type = details['conn_type']
            last_modified = details['last_modified']

            data = load_transfer_content(event.cid)

            # Events recorded before schedules had an encoding were all read as UTF-8.
            if 'encoding' in details:
                encoding = details['encoding']
            else:
                encoding = Default_Encoding

            # The directory is the part of the path the file's own name leaves out
            directory = full_path.rsplit('/', 1)[0]

            audit_log = AuditLog(self.server.name)

            # The new event carries the same details a live run's event carries,
            # so a reprocess of this new attempt has everything it needs too.
            event_extra = {
                'conn_type': conn_type,
                'last_modified': last_modified,
                'encoding': encoding,
            }

            # The actor is a searchable attribute.
            attrs_extra:'stranydict' = {}
            if actor:
                attrs_extra['actor'] = actor

            def resubmit_one() -> 'int':

                # The file is handed to the target service again under this cid,
                # a failed attempt being recorded too, and its spool file is deleted once the service returns.
                item = FileTransferItem.from_bytes(conn_type, event.object_name, schedule_name, directory, file_name,
                    full_path, last_modified, data, encoding)

                service_start = monotonic()

                try:
                    _ = self.server.invoke(service_name, item, cid=self.cid)
                except Exception:
                    error = format_exc()
                    service_ms = _elapsed_ms(service_start)
                    event_extra['service_ms'] = service_ms
                    _ = record_schedule_event(audit_log, event.object_name, AuditEvent.Delivery_Failed, full_path,
                        cid=self.cid, correl_id=event.cid, schedule=schedule_name, outcome=AuditOutcome.Error,
                        file_name=file_name, service=service_name, size=len(data), error=error,
                        duration_ms=service_ms, extra=event_extra, attrs_extra=attrs_extra, parents=[event.id])
                    raise
                finally:
                    item.close()

                service_ms = _elapsed_ms(service_start)
                event_extra['service_ms'] = service_ms

                out = record_schedule_event(audit_log, event.object_name, AuditEvent.Delivered, full_path,
                    cid=self.cid, correl_id=event.cid, schedule=schedule_name, outcome=AuditOutcome.OK,
                    file_name=file_name, service=service_name, size=len(data), duration_ms=service_ms,
                    extra=event_extra, attrs_extra=attrs_extra, parents=[event.id])

                return out

            # The key covers the bytes of the file.
            key_payload = data.decode('utf-8', errors='replace')

            new_event_id = run_once(Action_Reprocess, event_id, key_payload, self.cid, actor, resubmit_one)

            report['is_ok'] = True
            report['event_id'] = new_event_id

        except DuplicateResubmitException as e:
            report['is_duplicate'] = True
            report['error'] = str(e)

        except Exception:
            report['error'] = format_exc()

        report['action'] = _action_reprocess
        report['cid'] = self.cid

        self.response.payload.response_data = dumps(report)

# ################################################################################################################################
# ################################################################################################################################

class ResendHop(AdminService):
    """ Repeats a single recorded delivery to one destination - the exact payload stored
    with an outgoing event goes through the same connection again, without re-running
    the service that produced it and without involving any other destination.
    The attempt lands as its own audit event linked to the original by the correlation id.
    """
    name = 'zato.audit-log.resend-hop'
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
            'error': '',
        }

        try:
            event = load_event(event_id)

            send = self._build_send(event)

            audit_log = AuditLog(self.server.name)

            def resubmit_one() -> 'any_':
                out = resend_hop(event, send, audit_log, self.cid, actor)
                return out

            payload = get_stored_payload(event)
            result = run_once(Action_Resend, event_id, payload, self.cid, actor, resubmit_one)

            report['is_ok'] = True
            report['event_id'] = result.event_id

        except DuplicateResubmitException as e:
            report['is_duplicate'] = True
            report['error'] = str(e)

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
        details = event.details

        # A row a channel's fan-out engine wrote names the destination it went to, and a row an
        # outgoing connection wrote for a call a service made itself does not. The second kind
        # carries the whole call and is repeated as that call, the first kind through the
        # destination it was declared as.
        if is_own_recorded_call(event.source, details):
            require_resendable_request(event)

            def send(payload:'str') -> 'HopSendResult':
                out = send_recorded(self, event.source, event.object_name, details, payload, self.cid)
                return out

            return send

        entry = get_hop_entry(event.source, event.object_name, details)

        def send(payload:'str') -> 'HopSendResult':
            out = dispatch_send(self, entry, payload, self.cid)
            return out

        return send

# ################################################################################################################################
# ################################################################################################################################
