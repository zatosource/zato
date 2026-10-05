# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from json import dumps, loads
from logging import getLogger
from time import monotonic

# Zato
from zato.common.api import HTTP_SOAP, KAFKA
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.audit_log.common import Export_Payload_Flag
from zato.common.pubsub.delivery import deliver_with_policy
from zato.common.pubsub.outgoing import Attempts_None, Key_Data, Key_Headers, Key_Is_Tombstone, Key_Key, Key_Partition, \
    OutgoingPublisher, OutgoingType, SendRejected
from zato.common.util.api import asbool, new_cid_server
from zato.common.util.delivery_config import Delivery_Field_Defaults
from zato.common.util.retry import RetryPolicy
from zato.server.queue_bridge.client import ModuleCtx as BridgeCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.pubsub.sql.backend import PublishResult
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, intnone, stranydict, strdict, strnone
    from zato.server.base.parallel import ParallelServer
    from zato.server.queue_bridge.client import QueueBridgeClient

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_producer = KAFKA.Producer
_retry = HTTP_SOAP.Retry
_use_queue_field = HTTP_SOAP.Queue.Field_Use_Queue

# Whether a connection writes a sent and a received audit event per attempt, unless its configuration says otherwise
_audit_log_field = 'is_audit_log_active'
_audit_log_default = True

# What the bridge's description of an error carries when the error was the client's own, e.g. a timeout, rather than
# an answer of the Kafka instances - an answer is kept with the rejection, so a caller can tell the two apart
_local_error_marker = '(Local: '

# ################################################################################################################################
# ################################################################################################################################

# Defaults for fields the create path did not supply
outconn_config_defaults:'anydict' = {
    'topic': '',
    'sasl_mechanism': '',
    'ssl': False,
    'ssl_ca_file': '',
    'ssl_cert_file': '',
    'ssl_key_file': '',
    KAFKA.Field_SSL_Key_Password: '',
    _retry.Field_Max_Retries: _retry.Default_Max_Retries,
    _retry.Field_Sleep_Time: _retry.Default_Sleep_Time,
    _retry.Field_Backoff_Threshold: _retry.Default_Backoff_Threshold,
    _retry.Field_Backoff_Multiplier: _retry.Default_Backoff_Multiplier,
}
outconn_config_defaults.update(_producer.Defaults)
outconn_config_defaults.update(Delivery_Field_Defaults)

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_int_config_keys = _producer.IntFieldList + (
    _retry.Field_Max_Retries,
    _retry.Field_Sleep_Time,
    _retry.Field_Backoff_Threshold,
    _retry.Field_Backoff_Multiplier,
    HTTP_SOAP.DLQ.Field_Retries,
    HTTP_SOAP.DLQ.Field_Retry_Interval,
)

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_bool_config_keys = (
    'ssl',
    _producer.Field_Is_Idempotent,
    _use_queue_field,
    HTTP_SOAP.DLQ.Field_Use_DLQ,
    HTTP_SOAP.DLQ.Field_Keep_Header,
)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SendOutcome:
    """ Where a message the Kafka instances acknowledged landed.
    """
    topic: 'str' = ''
    partition: 'int' = -1
    offset: 'int' = -1

# ################################################################################################################################
# ################################################################################################################################

def to_header_text(headers:'anydictnone') -> 'strdict':
    """ Headers as the text names and values the bridge takes.
    """
    out:'strdict' = {}

    if headers:
        for name, value in headers.items():
            if isinstance(value, bytes):
                value = value.decode('utf8')
            out[name] = value

    return out

# ################################################################################################################################

def build_send_request(
    data:'any_',
    *,
    key:'strnone'=None,
    headers:'anydictnone'=None,
    partition:'intnone'=None,
    is_tombstone:'bool'=False,
    ) -> 'stranydict':
    """ The request part of an outgoing Kafka message's envelope.
    """
    if isinstance(data, bytes):
        data = data.decode('utf8')
    elif not isinstance(data, str):
        data = dumps(data)

    out = {
        Key_Data: data,
        Key_Key: key,
        Key_Headers: to_header_text(headers),
        Key_Partition: partition,
        Key_Is_Tombstone: is_tombstone,
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

class OutconnKafkaWrapper:
    """ An outgoing Kafka connection, sending through the queue bridge.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        self.config = config
        self.server = server

        # Whether a send that did not go through waits in the connection's queue
        self.use_queue = self.config[_use_queue_field]

        # How a direct send that could not be delivered is tried again
        self.retry_policy = RetryPolicy.from_config(config, _retry)

        # How long the bridge waits for the Kafka instances to acknowledge one send, in seconds
        self.send_timeout = config[_producer.Field_Send_Timeout]

        # A connection whose audit log is on writes a sent and a received event per attempt
        if asbool(config.get(_audit_log_field, _audit_log_default)):
            self.audit_log:'AuditLog | None' = AuditLog(server.name)
        else:
            self.audit_log = None

        # The payloads leave with the audit export only if the connection says so
        self.is_export_payload_active = asbool(config.get(Export_Payload_Flag, False))

        # The publisher is keyed by the connection's id, a rename leaves it alone.
        self.publisher = OutgoingPublisher(server, OutgoingType.KAFKA, self.config.id)

        logger.info('Outgoing Kafka connection `%s` registered', config.name)

# ################################################################################################################################

    def __repr__(self) -> 'str':
        return f'OutconnKafkaWrapper({self.config.name} at {hex(id(self))})'

# ################################################################################################################################

    @property
    def bridge(self) -> 'QueueBridgeClient':
        return self.server._queue_bridge

# ################################################################################################################################

    def delete(self) -> 'None':
        pass

# ################################################################################################################################

    def build_wrapper(self) -> 'None':
        pass

# ################################################################################################################################

    def ping(self) -> 'None':
        """ Fetches the metadata of the connection's Kafka instances through the bridge.
        """
        reply:'anydict' = self.bridge.ping(self.config.name)
        self._check_reply(reply, 'ping')

# ################################################################################################################################

    def _check_reply(self, reply:'anydict', what:'str') -> 'None':
        """ Raises unless the bridge said the command went through.
        """
        status = reply['status']

        if status == BridgeCtx.Status_OK:
            return

        if status == BridgeCtx.Status_Error:
            error = reply['data']

            # What the Kafka instances answered, if the error is their answer and not the client's own
            if _local_error_marker in error:
                response = None
            else:
                response = error

            raise SendRejected(f'Kafka {what} through `{self.config.name}` failed: {error}', response)

        raise SendRejected(f'Kafka {what} through `{self.config.name}` timed out')

# ################################################################################################################################

    def _audit(self, cid:'str', event_type:'str', outcome:'str', data:'str', started:'float'=0.0) -> 'None':
        """ Writes one audit event of an attempt, under the cid of the service that sent the message.
        """
        if not self.audit_log:
            return

        if started:
            duration_ms = int((monotonic() - started) * 1000)
        else:
            duration_ms = 0

        _ = self.audit_log.insert(
            AuditSource.Kafka_Outgoing,
            event_type,
            self.config.name,
            cid=cid,
            endpoint=self.config.topic,
            size=len(data),
            outcome=outcome,
            duration_ms=duration_ms,
            data=data,
            is_export_payload_active=self.is_export_payload_active,
        )

# ################################################################################################################################

    def send_once(self, request:'stranydict', cid:'str'='') -> 'SendOutcome':
        """ Makes one attempt to send one message through the bridge, raising when the Kafka instances did not acknowledge it.
        Each attempt writes a sent event and a received one, the latter with what Kafka answered or how the attempt failed.
        """
        data = request[Key_Data]

        if not cid:
            cid = new_cid_server()

        started = monotonic()
        self._audit(cid, AuditEvent.Request_Sent, AuditOutcome.OK, data)

        try:
            reply:'anydict' = self.bridge.send_message(
                self.config.name,
                data.encode('utf8'),
                key=request[Key_Key],
                headers=request[Key_Headers],
                partition=request[Key_Partition],
                is_tombstone=request[Key_Is_Tombstone],
                send_timeout=self.send_timeout,
            )

            self._check_reply(reply, 'send')

        except Exception as e:
            self._audit(cid, AuditEvent.Response_Received, AuditOutcome.Error, str(e), started)
            raise

        out = SendOutcome()
        out.topic = self.config.topic

        reply_data = reply['data']

        if reply_data:
            landed = loads(reply_data)
            out.partition = landed['partition']
            out.offset = landed['offset']

        self._audit(cid, AuditEvent.Response_Received, AuditOutcome.OK, reply_data or '', started)

        return out

# ################################################################################################################################

    def send_from_queue(self, cid:'str', request:'stranydict') -> 'SendOutcome':
        """ Makes one attempt to deliver a message the queue holds.
        """
        out = self.send_once(request, cid)
        return out

# ################################################################################################################################

    def send(
        self,
        data:'any_',
        *,
        key:'strnone'=None,
        headers:'anydictnone'=None,
        partition:'intnone'=None,
        cid:'str'='',
        is_tombstone:'bool'=False,
        ) -> 'any_':
        """ Sends one message - directly under the connection's retry policy, or through the connection's queue when
        the queue switch is on, returning a SendResult then.
        """
        request = build_send_request(data, key=key, headers=headers, partition=partition, is_tombstone=is_tombstone)

        if not cid:
            cid = new_cid_server()

        if self.use_queue:

            def attempt() -> 'SendOutcome':
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

    def publish(self, data:'any_', **kwargs:'any_') -> 'PublishResult':
        """ Queues one message for delivery to this connection, returning as soon as it is stored.
        """
        request = build_send_request(
            data,
            key=kwargs.pop('key', None),
            headers=kwargs.pop('headers', None),
            partition=kwargs.pop('partition', None),
            is_tombstone=kwargs.pop('is_tombstone', False),
        )

        out = self.publisher.publish_request('', Attempts_None, request, **kwargs)
        return out

# ################################################################################################################################
# ################################################################################################################################
