# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The processing of SMS channel events received by callback or by poll, for every provider. A repeated event
# is dropped, every other event is stored in the channel's queue or delivered to the channel's service directly.

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

# The headers of a channel's message
Header_Channel = 'zato-sms-channel'
Header_Kind = 'zato-sms-kind'
Header_ID = 'zato-sms-id'
Header_Status = 'zato-sms-status'
Header_Provider = 'zato-sms-provider'

# The KV store key of a channel's received events
_received_key_prefix = 'zato:sms:received:'

# The separator of a received event's set member
_member_separator = '|'

# ################################################################################################################################
# ################################################################################################################################

def get_webhook_url(channel_name:'str') -> 'str':
    """ The webhook URL of one SMS channel - the server's address followed by the channel's webhook path.
    The Dashboard displays the same URL on the channel's form.
    """
    server_address = get_server_address()

    out = server_address + get_webhook_path(channel_name)
    return out

# ################################################################################################################################
# ################################################################################################################################

class ReceivedEvents:
    """ The events one channel has received, kept in the server's KV store and shared by every server process.
    A provider resends callbacks and a poll reads messages that are not final more than once.
    """
    def __init__(self, server:'ParallelServer', channel_id:'int') -> 'None':
        self.redis = server.config_manager.cache_api.redis
        self.key = f'{_received_key_prefix}{channel_id}'

# ################################################################################################################################

    def add(self, event:'SMSEvent') -> 'bool':
        """ Records one event and returns whether it was received for the first time.
        """
        member = _member_separator.join([event.id, event.kind, event.status])

        # A member already in the set is not added again, which identifies a repeated event
        added = self.redis.zadd(self.key, {member: time()}, nx=True)
        out = bool(added)

        # The set holds the newest entries only and expires after the provider's resend period
        _ = self.redis.zremrangebyrank(self.key, 0, -(SMS.Received_Events_Max + 1))
        _ = self.redis.expire(self.key, SMS.Received_Events_Expiry_Seconds)

        return out

# ################################################################################################################################

    def remove(self, event:'SMSEvent') -> 'None':
        """ Removes one event from the set. The provider's resend or the next poll delivers the event again.
        """
        member = _member_separator.join([event.id, event.kind, event.status])
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
    """ One invocation of an SMS channel's service, recorded in the audit log under the event's cid.
    A replay from the DLQ is recorded under the same cid.
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
    """ Delivers every new event of a callback or a poll to the channel's service - through the channel's queue when
    use_queue is enabled, directly otherwise. Returns the number of new events. An event the service raises for is removed
    from the received set, so that the provider's resend or the next poll delivers it again. The remaining events
    of the batch are delivered and the first exception is raised after the batch.
    """
    channel_name = channel_config['name']
    channel_id = channel_config['id']
    service = channel_config[SMS.Field_Service]
    use_queue = channel_config['use_queue']

    received = ReceivedEvents(server, channel_id)
    publisher = None

    if use_queue:
        publisher = OutgoingPublisher(server, InboundType.SMS, channel_id)

    out = 0
    first_error = None

    for event in events:

        if not received.add(event):
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
            received.remove(event)
            if first_error is None:
                first_error = e
            continue

        out += 1

    if first_error is not None:
        raise first_error

    return out

# ################################################################################################################################
# ################################################################################################################################
