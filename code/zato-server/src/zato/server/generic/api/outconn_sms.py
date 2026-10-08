# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing SMS connection - one HTTP session to one provider, with the provider's own request and response
# shapes confined to its provider class, and the connection's retry policy, queue and DLQ around every send.

# stdlib
from logging import getLogger
from time import monotonic

# requests
from requests import Session
from requests.adapters import HTTPAdapter

# Zato
from zato.common.api import HTTP_SOAP, SMS
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.common import AuditClassification, derive_http_classification, Export_Payload_Flag
from zato.common.json_internal import dumps
from zato.common.pubsub.delivery import deliver_with_policy
from zato.common.pubsub.outgoing import Attempts_None, Key_Data, OutgoingPublisher, OutgoingType, SendRejected
from zato.common.sms.config import is_polling
from zato.common.util.api import asbool, new_cid_server
from zato.common.util.delivery_config import Delivery_Field_Defaults
from zato.common.util.retry import RetryPolicy
from zato.server.connection.sms.base import Method_GET, ProviderError
from zato.server.connection.sms.channel import get_webhook_url
from zato.server.connection.sms.registry import get_provider

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.ext.bunch import Bunch
    from zato.common.pubsub.sql.backend import PublishResult
    from zato.common.sms.model import SendResult
    from zato.common.typing_ import any_, anydict, anylist, stranydict, strnone
    from zato.server.base.parallel import ParallelServer
    from zato.server.connection.sms.base import Provider

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_retry = HTTP_SOAP.Retry
_use_queue_field = HTTP_SOAP.Queue.Field_Use_Queue

# Whether a connection writes a sent and a received audit event per attempt, unless its configuration says otherwise
_audit_log_field = 'is_audit_log_active'
_audit_log_default = True

# The keys of a queued message's request
Key_To = 'to'
Key_Body = 'body'
Key_Sender = 'sender'

# The prefixes of the URL schemes a host may use
_url_scheme_prefixes = ('http://', 'https://')

# ################################################################################################################################
# ################################################################################################################################

# Defaults for fields the create path did not supply
outconn_config_defaults:'anydict' = {
    SMS.Field_Provider: SMS.Provider.Twilio,
    SMS.Field_Host: '',
    SMS.Field_Username: '',
    SMS.Field_Sender: '',
    SMS.Field_Signature_Secret: '',
    SMS.Field_Channel_Name: '',
    SMS.Field_Pool_Size: SMS.Default_Pool_Size,
    SMS.Field_Timeout: SMS.Default_Timeout,
    _retry.Field_Max_Retries: _retry.Default_Max_Retries,
    _retry.Field_Sleep_Time: _retry.Default_Sleep_Time,
    _retry.Field_Backoff_Threshold: _retry.Default_Backoff_Threshold,
    _retry.Field_Backoff_Multiplier: _retry.Default_Backoff_Multiplier,
}
outconn_config_defaults.update(Delivery_Field_Defaults)

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_int_config_keys = (
    SMS.Field_Pool_Size,
    SMS.Field_Timeout,
    _retry.Field_Max_Retries,
    _retry.Field_Sleep_Time,
    _retry.Field_Backoff_Threshold,
    _retry.Field_Backoff_Multiplier,
    HTTP_SOAP.DLQ.Field_Retries,
    HTTP_SOAP.DLQ.Field_Retry_Interval,
)

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_bool_config_keys = (
    _use_queue_field,
    HTTP_SOAP.DLQ.Field_Use_DLQ,
    HTTP_SOAP.DLQ.Field_Keep_Header,
)

# ################################################################################################################################
# ################################################################################################################################

def build_send_request(to:'str', body:'str', sender:'str') -> 'stranydict':
    """ The request part of a queued SMS message's envelope - the body under the common data key for the delivery page.
    """
    out = {
        Key_To: to,
        Key_Body: body,
        Key_Sender: sender,
        Key_Data: body,
    }

    return out

# ################################################################################################################################

def is_permanent_rejection(response:'Response') -> 'bool':
    """ Whether the status a provider turned a send down with says the message itself is wrong.
    """
    classification = derive_http_classification(response.status_code)
    out = classification == AuditClassification.Permanent
    return out

# ################################################################################################################################
# ################################################################################################################################

class OutconnSMSWrapper:
    """ An outgoing SMS connection, sending through one provider's REST API.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        self.config = config
        self.server = server

        # Whether a send that did not go through waits in the connection's queue
        self.use_queue = self.config[_use_queue_field]

        # How a direct send that could not be delivered is tried again
        self.retry_policy = RetryPolicy.from_config(config, _retry)

        # How long one request to the provider may take, in seconds
        self.timeout = config[SMS.Field_Timeout]

        # A connection whose audit log is on writes a sent and a received event per attempt
        if asbool(config.get(_audit_log_field, _audit_log_default)):
            self.audit_log:'AuditLog | None' = AuditLog(server.name)
        else:
            self.audit_log = None

        # The payloads leave with the audit export only if the connection says so
        self.is_export_payload_active = asbool(config.get(Export_Payload_Flag, False))

        # The publisher is keyed by the connection's id, a rename leaves it alone.
        self.publisher = OutgoingPublisher(server, OutgoingType.SMS, self.config.id)

        self.provider:'Provider' = get_provider(config)
        self.session = self._new_session(config[SMS.Field_Pool_Size])

        logger.info('Outgoing SMS connection `%s` registered (%s)', config.name, self.provider.name)

# ################################################################################################################################

    def __repr__(self) -> 'str':
        return f'OutconnSMSWrapper({self.config.name} at {hex(id(self))})'

# ################################################################################################################################

    def _new_session(self, pool_size:'int') -> 'Session':
        out = Session()
        adapter = HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size)

        for prefix in _url_scheme_prefixes:
            out.mount(prefix, adapter)

        return out

# ################################################################################################################################

    def delete(self) -> 'None':
        self.session.close()

# ################################################################################################################################

    def build_wrapper(self) -> 'None':
        pass

# ################################################################################################################################

    def get_callback_url(self) -> 'strnone':
        """ The webhook URL of the SMS channel the connection names, if it names one that receives by webhook.
        """
        channel_name = self.config.get(SMS.Field_Channel_Name)

        if not channel_name:
            return None

        channels = self.server.config_manager.channel_sms

        if channel_name not in channels:
            return None

        channel_config = channels[channel_name]

        if is_polling(channel_config):
            return None

        out = get_webhook_url(channel_name)
        return out

# ################################################################################################################################

    def request(self, method:'str', url:'str', headers:'anydict', data:'any_') -> 'Response':
        """ One HTTP request to the provider - a GET sends its data as the query string, a POST as the body.
        """
        if method == Method_GET:
            out = self.session.get(url, headers=headers, params=data, timeout=self.timeout)
        else:
            out = self.session.post(url, headers=headers, data=data, timeout=self.timeout)

        return out

# ################################################################################################################################

    def ping(self) -> 'None':
        """ Performs the cheapest authenticated read the provider offers, raising unless it succeeds.
        """
        method, url, headers, data = self.provider.build_ping_request()
        response = self.request(method, url, headers, data)

        if not response.ok:
            raise Exception(f'SMS ping of `{self.config.name}` failed with HTTP {response.status_code}: {response.text}')

# ################################################################################################################################

    def _audit(self, cid:'str', event_type:'str', outcome:'str', data:'str', endpoint:'str', started:'float'=0.0) -> 'None':
        """ Writes one audit event of an attempt, under the cid of the service that sent the message.
        """
        if not self.audit_log:
            return

        if started:
            duration_ms = int((monotonic() - started) * 1000)
        else:
            duration_ms = 0

        _ = self.audit_log.insert(
            AuditSource.SMS_Outgoing,
            event_type,
            self.config.name,
            cid=cid,
            endpoint=endpoint,
            size=len(data),
            outcome=outcome,
            duration_ms=duration_ms,
            data=data,
            is_export_payload_active=self.is_export_payload_active,
        )

# ################################################################################################################################

    def send_once(self, request:'stranydict', cid:'str'='') -> 'SendResult':
        """ Makes one attempt to send one message, raising SendRejected when the provider turned it down.
        Each attempt writes a sent event and a received one, the latter with what the provider answered
        or how the attempt failed.
        """
        to = request[Key_To]
        body = request[Key_Body]
        sender = request[Key_Sender]

        if not cid:
            cid = new_cid_server()

        callback_url = self.get_callback_url()
        method, url, headers, data = self.provider.build_send_request(to, body, sender, callback_url)

        started = monotonic()
        self._audit(cid, AuditEvent.Request_Sent, AuditOutcome.OK, body, to)

        # The request itself may fail before the provider answers, e.g. on a timeout ..
        try:
            response = self.request(method, url, headers, data)
        except Exception as e:
            self._audit(cid, AuditEvent.Response_Received, AuditOutcome.Error, str(e), to, started)
            raise

        # .. and the provider may turn the message down, which the queue tells apart from a failed request.
        try:
            out = self.provider.read_send_response(response)
        except ProviderError as e:
            self._audit(cid, AuditEvent.Response_Received, AuditOutcome.Error, str(e), to, started)
            raise SendRejected(str(e), response, is_permanent=is_permanent_rejection(response))

        self._audit(cid, AuditEvent.Response_Received, AuditOutcome.OK, dumps(out.raw), to, started)

        return out

# ################################################################################################################################

    def send_from_queue(self, cid:'str', request:'stranydict') -> 'SendResult':
        """ Makes one attempt to deliver a message the queue holds.
        """
        out = self.send_once(request, cid)
        return out

# ################################################################################################################################

    def send(self, to:'str', body:'str', *, from_:'str'='', cid:'str'='') -> 'any_':
        """ Sends one message - directly under the connection's retry policy, or through the connection's queue when
        the queue switch is on, returning the queue's own result then.
        """
        if not from_:
            from_ = self.config[SMS.Field_Sender]

        request = build_send_request(to, body, from_)

        if not cid:
            cid = new_cid_server()

        if self.use_queue:

            def attempt() -> 'SendResult':
                out = self.send_once(request, cid)
                return out

            out = self.publisher.send_or_queue(cid, request, attempt)
            return out

        # The outcome of the attempt that went through.
        outcome:'anylist' = []

        def attempt_with_outcome() -> 'None':
            outcome.append(self.send_once(request, cid))

        deliver_with_policy(self.retry_policy, Attempts_None, cid, self.config.name, attempt_with_outcome)

        out = outcome[0]
        return out

# ################################################################################################################################

    def publish(self, to:'str', body:'str', *, from_:'str'='', **kwargs:'any_') -> 'PublishResult':
        """ Queues one message for delivery to this connection, returning as soon as it is stored.
        """
        if not from_:
            from_ = self.config[SMS.Field_Sender]

        request = build_send_request(to, body, from_)

        out = self.publisher.publish_request('', Attempts_None, request, **kwargs)
        return out

# ################################################################################################################################
# ################################################################################################################################
