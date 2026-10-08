# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The two services behind an SMS channel - the one a provider's callback reaches through the internal webhook
# channel, and the one the scheduler runs for a channel in polling mode. Both read the channel's provider class
# through its outgoing connection, so the credentials are stored once, on the outgoing side.

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

# The path parameter the internal webhook channel captures
_path_param_channel_name = 'channel_name'

# The WSGI key the content type arrives under
_wsgi_content_type = 'CONTENT_TYPE'

# The keys a config edit message has beyond the config itself
_msg_action = 'action'
_msg_old_name = 'old_name'

# The config keys that are never part of a config edit message
_msg_skip_keys = ('conn',)

# How many rounds one poll goes through at most when a provider keeps reporting further pages
_max_poll_rounds = 100

# ################################################################################################################################
# ################################################################################################################################

def _get_channel(service:'Service', channel_name:'str') -> 'Bunch':
    """ The SMS channel of that name as this server knows it.
    """
    channels = service.server.config_manager.channel_sms

    if channel_name not in channels:
        raise NotFound(service.cid, f'No such SMS channel `{channel_name}`')

    out = channels[channel_name]
    return out

# ################################################################################################################################

def _get_outconn(service:'Service', channel:'Bunch') -> 'OutconnSMSWrapper':
    """ The wrapper of the outgoing connection an SMS channel reads its provider through.
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
    """ Receives one provider callback for one SMS channel - verifies it, reads its events, passes each new one
    to the channel's service or its queue and answers in the form the provider expects.
    """
    name = SMS.Webhook_Service

    def handle(self) -> 'None':

        start = monotonic()
        channel_name = self.request.http.params[_path_param_channel_name]
        channel = _get_channel(self, channel_name)

        # A channel that polls has no webhook, so the path does not exist for it
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

        # The provider signed the URL its console was given, which is the channel's own webhook URL
        url = get_webhook_url(channel_name)

        try:
            provider.verify_callback(request_ctx, raw_body, url)
        except CallbackRejected as e:
            body_text = raw_body.decode('utf8', 'replace')
            _audit_batch(self, AuditEvent.Received, channel, provider, [], 0, start, AuditOutcome.Error, str(e), body_text)
            raise Forbidden(self.cid, str(e))

        events = provider.read_callback(request_ctx, raw_body)
        body_text = raw_body.decode('utf8', 'replace')

        # With the queue off, an exception from the channel's service fails the callback, which the provider retries
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
    """ Runs one poll of one SMS channel on behalf of the scheduler - each page the provider returns is read, its new events
    are passed on and the poll state the next request starts from is written back before the next page is read,
    so that a poll that fails midway neither loses what it has read nor hands anything over twice.
    """
    name = SMS.Scheduler.Dispatch_Service

    def handle(self) -> 'None':

        start = monotonic()

        # The scheduler job has the channel's identity in its extra data
        context = self.request.payload
        channel_name = context[SMS.Scheduler.Extra_Conn_Name]

        channel = _get_channel(self, channel_name)

        # A channel switched to webhook mode since the job ran last has nothing to poll
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
        """ Goes through every request of a poll, and through further rounds while the provider reports more pages.
        Each page's events are handed over and the state is saved before the next page is requested.
        """
        new_count = 0

        for _ in range(_max_poll_rounds):

            requests = provider.build_poll_requests(state)

            for request in requests:
                response = outconn.request(request.method, request.url, request.headers, request.params)
                page_events, state = provider.read_poll_response(request, response, state)
                events.extend(page_events)

                new_count += handle_events(self.server, self.cid, channel, provider.name, page_events)

                # Everything of this page is stored or handed over, so the state the next page starts from can be saved
                self._save_state(channel, state)

            if not provider.has_more_pages(state):
                break

        out = (state, new_count)
        return out

# ################################################################################################################################

    def _load_state(self, channel:'Bunch') -> 'stranydict':
        """ The state the previous poll left behind, an empty dict for a channel that has never polled.
        """
        poll_state = channel[SMS.Field_Poll_State]

        if not poll_state:
            return {}

        out = loads(poll_state)
        return out

# ################################################################################################################################

    def _save_state(self, channel:'Bunch', state:'stranydict') -> 'None':
        """ Writes the poll state to the channel's row and tells every server about it through a config edit message,
        so that the next poll starts from this state wherever the scheduler sends it.
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
        """ A config edit message describing the channel as it is, with the new poll state.
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
