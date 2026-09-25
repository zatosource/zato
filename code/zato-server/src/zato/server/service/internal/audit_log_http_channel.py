# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The resubmit service of REST and SOAP channels - one recorded request body reaches the channel's service again.

# stdlib
from traceback import format_exc

# Zato
from zato.common.api import CHANNEL, URL_TYPE
from zato.common.audit_log.api import AuditLog
from zato.common.audit_log.common import AuditEvent, AuditOutcome
from zato.common.audit_log.resubmit import get_stored_payload, load_event, require_event_type, run_once, \
    Action_Reprocess, DuplicateResubmitException, ResubmitException
from zato.common.json_internal import dumps
from zato.server.service import Int
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.resubmit import StoredEvent
    from zato.common.typing_ import any_, intnone, stranydict
    any_ = any_
    intnone = intnone
    stranydict = stranydict
    StoredEvent = StoredEvent

# ################################################################################################################################
# ################################################################################################################################

# The transports whose channels this service serves - a REST channel and a SOAP one.
_http_transports = (URL_TYPE.PLAIN_HTTP, URL_TYPE.SOAP)

# ################################################################################################################################
# ################################################################################################################################

def find_channel_item(server:'any_', channel_name:'str') -> 'stranydict':
    """ Returns the runtime item of the REST or SOAP channel of the given name, the one live requests
    are dispatched through.
    """
    url_data = server.config_manager.request_dispatcher.url_data

    for channel_item in url_data.channel_data:

        if channel_item['transport'] not in _http_transports:
            continue

        if channel_item['name'] != channel_name:
            continue

        out = channel_item
        break

    else:
        raise ResubmitException(f'No REST or SOAP channel matches the name `{channel_name}`')

    return out

# ################################################################################################################################

def reprocess_request(
    service:'any_',
    audit_log:'AuditLog',
    event:'StoredEvent',
    channel_item:'stranydict',
    payload:'str',
    actor:'str',
    ) -> 'intnone':
    """ Hands the stored request body to the channel's service with the channel's data format
    and records the attempt as its own request-received event under the channel, linked to the
    original by the correlation id and the parent link. A run that raised is recorded as a failed one.
    """
    service_name = channel_item['service_name']
    data_format = channel_item['data_format']
    cid = service.cid

    attributes:'stranydict' = {}

    # The new event says who asked for the run.
    if actor:
        attributes['actor'] = actor

    payload_size = len(payload)

    values:'stranydict' = {
        'cid': cid,
        'correl_id': event.cid,
        'endpoint': service_name,
        'size': payload_size,
        'data': payload,
        'attrs': attributes,
        'parents': [event.id],
    }

    try:
        _ = service.server.invoke(service_name, payload, channel=CHANNEL.INVOKE, data_format=data_format, cid=cid)

    except Exception as e:
        _ = audit_log.insert(
            event.source, AuditEvent.Request_Received, event.object_name,
            outcome=AuditOutcome.Error, status=str(e), **values)
        raise

    out = audit_log.insert(
        event.source, AuditEvent.Request_Received, event.object_name,
        outcome=AuditOutcome.OK, **values)

    return out

# ################################################################################################################################
# ################################################################################################################################

class ReprocessHTTPChannelRequest(AdminService):
    """ Hands the request body recorded by a REST or SOAP channel's request-received audit event
    to the channel's service again. The new attempt lands as its own request-received event under
    the same channel, linked to the original by the correlation id and the parent link.
    """
    name = 'zato.audit-log.http-channel.reprocess'
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

            # A channel stores the request body as it arrived, not a JSON document around it.
            event = load_event(event_id, is_raw_payload=True)
            require_event_type(event, AuditEvent.Request_Received, 'run again')

            channel_item = find_channel_item(self.server, event.object_name)
            payload = get_stored_payload(event)

            audit_log = AuditLog(self.server.name)

            def resubmit_one() -> 'intnone':
                out = reprocess_request(self, audit_log, event, channel_item, payload, actor)
                return out

            # The key covers the body the service is given.
            new_event_id = run_once(Action_Reprocess, event_id, payload, self.cid, actor, resubmit_one)

            report['is_ok'] = True
            report['event_id'] = new_event_id
            report['service_name'] = channel_item['service_name']

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
