# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The channel side of SMS - what every event goes through on its way to the channel's service, whichever
# provider it came from and whether it arrived by callback or by poll. A repeated event is dropped, and the rest
# are either stored in the channel's queue or handed to the service at once.

# stdlib
from logging import getLogger
from time import monotonic, time

# Zato
from zato.common.api import DATA_FORMAT, SMS
from zato.common.audit_log.common import AuditBody, AuditEvent, AuditOutcome, AuditSource
from zato.common.json_internal import dumps
from zato.common.pubsub.outgoing import Attempts_None, InboundType, Key_Data, Key_Headers, Key_Is_Base64, Key_Service, \
    OutgoingPublisher
from zato.common.sms.config import get_webhook_path
from zato.common.util.mcp_oauth import get_server_address

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.sms.model import SMSEvent
    from zato.common.typing_ import any_, strdict, stranydict
    from zato.server.base.parallel import ParallelServer

    SMSEventList = list[SMSEvent]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The headers a channel's message travels with
Header_Channel = 'zato-sms-channel'
Header_Kind = 'zato-sms-kind'
Header_ID = 'zato-sms-id'
Header_Status = 'zato-sms-status'
Header_Provider = 'zato-sms-provider'

# The KV store key under which a channel keeps the events it has seen
_seen_key_prefix = 'zato:sms:seen:'

# What joins the parts of a seen event's member
_seen_separator = '|'

# ################################################################################################################################
# ################################################################################################################################

def get_webhook_url(channel_name:'str') -> 'str':
    """ The full URL a provider's console is pointed at for one SMS channel - the address clients reach the server at,
    which is also what the Dashboard shows on the channel's form.
    """
    server_address = get_server_address()

    out = server_address + get_webhook_path(channel_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

class SeenEvents:
    """ The last events one channel has seen, kept in the server's KV store so that every process of every server
    drops the same repeats - a provider resends callbacks and a poll revisits messages that are not final.
    """
    def __init__(self, server:'ParallelServer', channel_id:'int') -> 'None':
        self.redis = server.config_manager.cache_api.redis
        self.key = f'{_seen_key_prefix}{channel_id}'

# ################################################################################################################################

    def is_new(self, event:'SMSEvent') -> 'bool':
        """ Records one event and says whether it was seen for the first time.
        """
        member = _seen_separator.join([event.id, event.kind, event.status])

        # A member that is in the set already is not added again, which is what tells a repeat apart
        added = self.redis.zadd(self.key, {member: time()}, nx=True)
        out = bool(added)

        # The set keeps the newest entries only and lives for as long as a provider resends
        _ = self.redis.zremrangebyrank(self.key, 0, -(SMS.Seen_Events_Max + 1))
        _ = self.redis.expire(self.key, SMS.Seen_Events_Expiry_Seconds)

        return out

# ################################################################################################################################

    def forget(self, event:'SMSEvent') -> 'None':
        """ Takes one event out of the set, so that a provider's resend or the next poll hands it over again.
        """
        member = _seen_separator.join([event.id, event.kind, event.status])
        _ = self.redis.zrem(self.key, member)

# ################################################################################################################################
# ################################################################################################################################

def build_event_headers(channel_name:'str', provider_name:'str', event:'SMSEvent') -> 'strdict':
    out = {
        Header_Channel: channel_name,
        Header_Provider: provider_name,
        Header_Kind: event.kind,
        Header_ID: event.id,
        Header_Status: event.status,
    }
    return out

# ################################################################################################################################

def build_event_request(service:'str', channel_name:'str', provider_name:'str', event:'SMSEvent') -> 'stranydict':
    """ The request part of a channel message's envelope - the event as JSON under the common data key.
    """
    out = {
        Key_Service: service,
        Key_Data: dumps(event.to_dict()),
        Key_Is_Base64: False,
        Key_Headers: build_event_headers(channel_name, provider_name, event),
    }
    return out

# ################################################################################################################################

def invoke_sms_service(server:'ParallelServer', cid:'str', request:'stranydict') -> 'any_':
    """ One attempt at the service an SMS channel's event goes to, recorded in the audit log under the event's cid,
    so that a replay from the DLQ lines up with the first attempt.
    """
    service = request[Key_Service]
    data = request[Key_Data]
    headers = request[Key_Headers]

    request_ctx = {'zato.request.headers': headers}
    start = monotonic()

    try:
        out = server.invoke(service, data, data_format=DATA_FORMAT.JSON, request_ctx=request_ctx, cid=cid)
    except Exception as e:
        _audit_attempt(server, cid, request, start, AuditOutcome.Error, str(e))
        raise
    else:
        _audit_attempt(server, cid, request, start, AuditOutcome.OK, '')
        return out

# ################################################################################################################################

def _audit_attempt(
    server:'ParallelServer',
    cid:'str',
    request:'stranydict',
    start:'float',
    outcome:'str',
    status:'str',
    ) -> 'None':
    """ Records one attempt at an SMS channel's service - the channel is the object, the provider is the endpoint.
    """
    audit_log = server.service_audit_log

    if not audit_log:
        return

    headers = request[Key_Headers]
    data = request[Key_Data]
    duration_ms = int((monotonic() - start) * 1000)

    attrs = {
        Header_Kind: headers[Header_Kind],
        Header_ID: headers[Header_ID],
        Header_Status: headers[Header_Status],
        Key_Service: request[Key_Service],
    }

    _ = audit_log.insert(
        AuditSource.SMS_Channel,
        AuditEvent.Message_Received,
        headers[Header_Channel],
        cid=cid,
        endpoint=headers[Header_Provider],
        size=len(data),
        outcome=outcome,
        status=status,
        duration_ms=duration_ms,
        attrs=attrs,
        bodies={AuditBody.Request: data},
    )

# ################################################################################################################################
# ################################################################################################################################

def handle_events(server:'ParallelServer', cid:'str', channel_config:'Bunch', provider_name:'str',
    events:'SMSEventList') -> 'int':
    """ Passes every new event of a callback or a poll on to the channel's service - through the channel's queue when
    its queue switch is on, at once otherwise. Returns how many events were new. An event the service rejects
    is forgotten again, so that it is handed over once more when the provider resends it or the next poll reads it,
    the remaining events of the batch are still handed over, and the first error is raised once the batch is through.
    """
    channel_name = channel_config['name']
    channel_id = channel_config['id']
    service = channel_config[SMS.Field_Service]
    use_queue = channel_config['use_queue']

    seen = SeenEvents(server, channel_id)
    publisher = None

    if use_queue:
        publisher = OutgoingPublisher(server, InboundType.SMS, channel_id)

    out = 0
    first_error = None

    for event in events:

        if not seen.is_new(event):
            logger.info('SMS channel `%s` dropped a repeated event `%s` (%s/%s)', channel_name, event.id, event.kind,
                event.status)
            continue

        request = build_event_request(service, channel_name, provider_name, event)

        try:
            if publisher:
                _ = publisher.publish_request(cid, Attempts_None, request)
            else:
                _ = invoke_sms_service(server, cid, request)
        except Exception as e:
            seen.forget(event)
            if first_error is None:
                first_error = e
            continue

        out += 1

    if first_error is not None:
        raise first_error

    return out

# ################################################################################################################################
# ################################################################################################################################
