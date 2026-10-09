# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# An outgoing SMS connection - one HTTP session to one provider. The provider class implements the provider's
# request and response formats, the wrapper applies the connection's retry policy, queue and DLQ to every send.

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

# The default of the audit log setting
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

# Defaults of fields absent from a create request
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

# Integer config keys, stored as strings in the opaque attributes
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

# Boolean config keys, stored as strings in the opaque attributes
outconn_bool_config_keys = (
    _use_queue_field,
    HTTP_SOAP.DLQ.Field_Use_DLQ,
    HTTP_SOAP.DLQ.Field_Keep_Header,
)

# ################################################################################################################################
# ################################################################################################################################

def build_send_request(to:'str', body:'str', sender:'str') -> 'stranydict':
    """ The request part of a queued SMS message's envelope - the message under the common data key.
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
    """ Whether the HTTP status of a rejected send indicates an invalid message, as opposed to a transient failure.
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

        # Whether a failed send is stored in the connection's queue
        self.use_queue = self.config[_use_queue_field]

        # The retry policy of a direct send
        self.retry_policy = RetryPolicy.from_config(config, _retry)

        # How long one request to the provider may take, in seconds
        self.timeout = config[SMS.Field_Timeout]

        # With the audit log enabled, each attempt writes a sent event and a received event
        if asbool(config.get(_audit_log_field, _audit_log_default)):
            self.audit_log:'AuditLog | None' = AuditLog(server.name)
        else:
            self.audit_log = None

        # Payloads are included in the audit export only when the setting is enabled
        self.is_export_payload_active = asbool(config.get(Export_Payload_Flag, False))

        # The publisher is keyed by the connection's ID and is unaffected by a rename.
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
        """ The webhook URL of the connection's SMS channel, or None when the connection has no channel or the channel polls.
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
        """ Performs the provider's credential verification request, raising when it fails.
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
        """ Makes one attempt to send one message, raising SendRejected when the provider rejects it.
        Each attempt writes a sent audit event and a received audit event with the provider's response or the failure.
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

        # The request fails before a response arrives, e.g. on a timeout ..
        try:
            response = self.request(method, url, headers, data)
        except Exception as e:
            self._audit(cid, AuditEvent.Response_Received, AuditOutcome.Error, str(e), to, started)
            raise

        # .. or the provider rejects the message, which the queue distinguishes from a failed request.
        try:
            out = self.provider.read_send_response(response)
        except ProviderError as e:
            self._audit(cid, AuditEvent.Response_Received, AuditOutcome.Error, str(e), to, started)
            raise SendRejected(str(e), response, is_permanent=is_permanent_rejection(response))

        self._audit(cid, AuditEvent.Response_Received, AuditOutcome.OK, dumps(out.raw), to, started)

        return out

# ################################################################################################################################

    def send_from_queue(self, cid:'str', request:'stranydict') -> 'SendResult':
        """ Makes one attempt to send a queued message.
        """
        out = self.send_once(request, cid)
        return out

# ################################################################################################################################

    def send(self, to:'str', body:'str', *, from_:'str'='', cid:'str'='') -> 'any_':
        """ Sends one message directly under the connection's retry policy, or through the connection's queue when
        use_queue is enabled, in which case the queue's result is returned.
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

        # The result of the successful attempt.
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
