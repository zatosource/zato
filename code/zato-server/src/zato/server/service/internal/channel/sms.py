# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The two services of an SMS channel - the one invoked by a provider's callback through the internal webhook channel
# and the one invoked by the scheduler for a channel in polling mode. Both read the provider class through
# the channel's outgoing connection.

# stdlib
from contextlib import closing
from logging import getLogger
from time import monotonic

# Zato
from zato.common.api import GENERIC, SMS
from zato.common.audit_log.common import AuditBody, AuditEvent, AuditOutcome, AuditSource
from zato.common.broker_message import GENERIC as BROKER_GENERIC
from zato.common.exception import Forbidden, NotFound
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.sms.config import is_polling
from zato.server.connection.sms.base import CallbackRejected, Ctx_Content_Type, Ctx_Headers, Ctx_Query
from zato.server.connection.sms.channel import get_webhook_url, handle_events
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.sms.model import SMSEvent
    from zato.common.typing_ import anydict, stranydict
    from zato.server.connection.sms.base import Provider
    from zato.server.generic.api.outconn_sms import OutconnSMSWrapper

    SMSEventList = list[SMSEvent]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The path parameter of the internal webhook channel
_path_param_channel_name = 'channel_name'

# The WSGI key of the request content type
_wsgi_content_type = 'CONTENT_TYPE'

# The keys a config edit message has beyond the config itself
_msg_action = 'action'
_msg_old_name = 'old_name'

# The config keys that are never part of a config edit message
_msg_skip_keys = ('conn',)

# The maximum number of rounds of one poll while the provider reports further pages
_max_poll_rounds = 100

# ################################################################################################################################
# ################################################################################################################################

def _get_channel(service:'Service', channel_name:'str') -> 'Bunch':
    """ The SMS channel of that name in this server's configuration.
    """
    channels = service.server.config_manager.channel_sms

    if channel_name not in channels:
        raise NotFound(service.cid, f'No such SMS channel `{channel_name}`')

    out = channels[channel_name]
    return out

# ################################################################################################################################

def _get_outconn(service:'Service', channel:'Bunch') -> 'OutconnSMSWrapper':
    """ The wrapper of an SMS channel's outgoing connection.
    """
    outconn_name = channel[SMS.Field_Outconn_Name]
    outconns = service.server.config_manager.outconn_sms

    if outconn_name not in outconns:
        raise NotFound(service.cid, f'SMS channel `{channel["name"]}` points to a missing outgoing connection `{outconn_name}`')

    out = outconns[outconn_name].conn
    return out

# ################################################################################################################################

def _audit_batch(
    service:'Service',
    event_type:'str',
    channel:'Bunch',
    provider:'Provider',
    events:'SMSEventList',
    new_count:'int',
    start:'float',
    outcome:'str',
    status:'str',
    body:'str',
    ) -> 'None':
    """ Records one callback or one poll as a single audit entry that contains the whole batch.
    """
    audit_log = service.server.service_audit_log

    if not audit_log:
        return

    duration_ms = int((monotonic() - start) * 1000)

    attrs = {
        'events': len(events),
        'new_events': new_count,
        SMS.Field_Receive_Mode: channel[SMS.Field_Receive_Mode],
        SMS.Field_Service: channel[SMS.Field_Service],
    }

    _ = audit_log.insert(
        AuditSource.SMS_Channel,
        event_type,
        channel['name'],
        cid=service.cid,
        endpoint=provider.name,
        size=len(body),
        outcome=outcome,
        status=status,
        duration_ms=duration_ms,
        attrs=attrs,
        bodies={AuditBody.Request: body},
    )

# ################################################################################################################################
# ################################################################################################################################

class Receive(Service):
    """ Receives one provider callback for one SMS channel - verifies it, reads its events, delivers each new event
    to the channel's service or queue and responds in the provider's format.
    """
    name = SMS.Webhook_Service

    def handle(self) -> 'None':

        start = monotonic()
        channel_name = self.request.http.params[_path_param_channel_name]
        channel = _get_channel(self, channel_name)

        # A polling channel has no webhook path
        if is_polling(channel):
            raise NotFound(self.cid, f'SMS channel `{channel_name}` is in polling mode')

        outconn = _get_outconn(self, channel)
        provider = outconn.provider

        raw_body = self.request.raw
        if isinstance(raw_body, str):
            raw_body = raw_body.encode('utf8')
        if raw_body is None:
            raw_body = b''

        content_type = self.request_ctx.get(_wsgi_content_type)
        if content_type is None:
            content_type = ''

        request_ctx = {
            Ctx_Headers: dict(self.request.http.headers),
            Ctx_Query: dict(self.request.http.GET),
            Ctx_Content_Type: content_type,
        }

        # The provider signs over the channel's webhook URL
        url = get_webhook_url(channel_name)

        try:
            provider.verify_callback(request_ctx, raw_body, url)
        except CallbackRejected as e:
            body_text = raw_body.decode('utf8', 'replace')
            _audit_batch(self, AuditEvent.Received, channel, provider, [], 0, start, AuditOutcome.Error, str(e), body_text)
            raise Forbidden(self.cid, str(e))

        events = provider.read_callback(request_ctx, raw_body)
        body_text = raw_body.decode('utf8', 'replace')

        # With use_queue disabled, an exception from the channel's service fails the callback and the provider resends it
        try:
            new_count = handle_events(self.server, self.cid, channel, provider.name, events)
        except Exception as e:
            _audit_batch(self, AuditEvent.Received, channel, provider, events, 0, start, AuditOutcome.Error, str(e),
                body_text)
            raise

        _audit_batch(self, AuditEvent.Received, channel, provider, events, new_count, start, AuditOutcome.OK, '', body_text)

        status_code, response_content_type, response_body = provider.callback_response()

        self.response.status_code = status_code
        self.response.content_type = response_content_type
        self.response.payload = response_body
        self.response.headers[SMS.Header_Callback_CID] = self.cid

# ################################################################################################################################
# ################################################################################################################################

class Poll(Service):
    """ Runs one poll of one SMS channel on behalf of the scheduler. Each page the provider returns is read, its new events
    are delivered and the poll state is saved before the next page is read, so that a poll that fails before completion
    neither loses events nor delivers an event twice.
    """
    name = SMS.Scheduler.Dispatch_Service

    def handle(self) -> 'None':

        start = monotonic()

        # The scheduler job's extra data has the channel's name
        context = self.request.payload
        channel_name = context[SMS.Scheduler.Extra_Conn_Name]

        channel = _get_channel(self, channel_name)

        # A channel in webhook mode is not polled
        if not is_polling(channel):
            logger.info('SMS channel `%s` is in webhook mode, skipping poll', channel_name)
            return

        outconn = _get_outconn(self, channel)
        provider = outconn.provider

        state = self._load_state(channel)
        events:'SMSEventList' = []
        new_count = 0

        try:
            state, new_count = self._poll(outconn, provider, channel, state, events)
        except Exception as e:
            _audit_batch(self, AuditEvent.Received, channel, provider, events, new_count, start, AuditOutcome.Error, str(e),
                dumps(state))
            raise

        _audit_batch(self, AuditEvent.Received, channel, provider, events, new_count, start, AuditOutcome.OK, '', dumps(state))

        logger.info('SMS channel `%s` polled %s event(s), %s new', channel_name, len(events), new_count)

# ################################################################################################################################

    def _poll(self, outconn:'OutconnSMSWrapper', provider:'Provider', channel:'Bunch', state:'stranydict',
        events:'SMSEventList') -> 'tuple[stranydict, int]':
        """ Runs every request of a poll and further rounds while the provider reports more pages.
        The events of each page are delivered and the state is saved before the next page is requested.
        """
        new_count = 0

        for _ in range(_max_poll_rounds):

            requests = provider.build_poll_requests(state)

            for request in requests:
                response = outconn.request(request.method, request.url, request.headers, request.params)
                page_events, state = provider.read_poll_response(request, response, state)
                events.extend(page_events)

                new_count += handle_events(self.server, self.cid, channel, provider.name, page_events)

                # Every event of this page is stored or delivered, and the state of the next page is saved
                self._save_state(channel, state)

            if not provider.has_more_pages(state):
                break

        out = (state, new_count)
        return out

# ################################################################################################################################

    def _load_state(self, channel:'Bunch') -> 'stranydict':
        """ The state recorded by the previous poll, an empty dict for a channel that has not polled.
        """
        poll_state = channel[SMS.Field_Poll_State]

        if not poll_state:
            return {}

        out = loads(poll_state)
        return out

# ################################################################################################################################

    def _save_state(self, channel:'Bunch', state:'stranydict') -> 'None':
        """ Writes the poll state to the channel's row and publishes it to every server through a config edit message.
        """
        poll_state = dumps(state)
        channel_id = channel['id']

        with closing(self.odb.session()) as session:
            conn = session.query(ModelGenericConn).filter(ModelGenericConn.id == channel_id).one()

            opaque = loads(conn.opaque1) if conn.opaque1 else {}
            opaque[SMS.Field_Poll_State] = poll_state
            conn.opaque1 = dumps(opaque)

            session.add(conn)
            session.commit()

        msg = self._build_edit_message(channel, poll_state)
        self.config_dispatcher.publish(msg)

# ################################################################################################################################

    def _build_edit_message(self, channel:'Bunch', poll_state:'str') -> 'anydict':
        """ A config edit message with the channel's configuration and the new poll state.
        """
        out = {}

        for key, value in channel.items():
            if key in _msg_skip_keys:
                continue
            out[key] = value

        out[SMS.Field_Poll_State] = poll_state
        out[_msg_action] = BROKER_GENERIC.CONNECTION_EDIT.value
        out[_msg_old_name] = channel['name']
        out['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_SMS

        return out

# ################################################################################################################################
# ################################################################################################################################
