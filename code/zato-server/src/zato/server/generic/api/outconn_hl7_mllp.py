# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from time import monotonic, sleep
from traceback import format_exc

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.audit_log.api import AuditLog
from zato.common.hl7.audit import audit_ack_received, audit_message_sent, get_wire_attrs, ACKStatus
from zato.common.hl7.mllp.ack import AckResult
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.hl7.mllp.dedup import extract_control_id
from zato.common.hl7.mllp.fields import Outgoing_Bool_Names, Outgoing_Defaults, Outgoing_Int_Names
from zato.common.hl7.mllp.tls import build_client_ssl_context
from zato.common.pubsub.outgoing import Attempts_None, Key_Data, OutgoingPublisher, OutgoingType, SendRejected
from zato.common.util.api import asbool, hex_sequence_to_bytes, new_cid_server
from zato.common.util.http_retry import get_next_sleep_time, RetryPolicy
from zato.common.util.tcp import parse_address
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.pubsub.sql.backend import PublishResult
    from zato.common.typing_ import any_, callable_, stranydict
    from zato.server.base.parallel import ParallelServer

    any_ = any_
    Bunch = Bunch
    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

# How many milliseconds one second holds - used when converting send durations
_ms_per_second = 1000

_use_queue_field = HTTP_SOAP.Queue.Field_Use_Queue

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Defaults applied by the config manager when the create path does not supply a field,
# e.g. when an outconn is created directly through zato.generic.connection.create.
outconn_config_defaults = Outgoing_Defaults

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_int_config_keys = Outgoing_Int_Names

# Config keys that must be booleans but may arrive as strings from opaque storage
outconn_bool_config_keys = Outgoing_Bool_Names

# ################################################################################################################################
# ################################################################################################################################

def get_ack_rejection(ack:'AckResult') -> 'str':
    """ Why an acknowledgment is a no - its code and the error it named. Empty for one that accepted the message,
    which is what the direct attempt and the attempts from the queue both go by.
    """
    if ack.is_accepted:
        return ''

    out = f'{ack.ack_code} {ack.error_text}'.strip()
    return out

# ################################################################################################################################

def to_message_text(data:'bytes | str | any_') -> 'str':
    """ An HL7 message as text, whether it was given as ER7 text, raw bytes or a parsed message object.
    """
    if isinstance(data, bytes):
        out = data.decode('utf-8', errors='replace')
    elif isinstance(data, str):
        out = data
    else:
        out = data.to_er7()

    return out

# ################################################################################################################################
# ################################################################################################################################

class _HL7MLLPConnection:
    """ Wraps an HL7MLLPClient instance for use with the connection pool.
    """
    def __init__(self, config:'Bunch', audit_log:'AuditLog | None' = None) -> 'None':

        # What the audit events are filed under and where they say the message went -
        # the name is only read when auditing is on, because offline tests build
        # minimal configs without one.
        self.audit_log = audit_log
        self.address = config.address

        if audit_log:
            self.name = config.name
        else:
            self.name = ''

        # How a direct send that could not be delivered is tried again
        self.retry_policy = RetryPolicy.from_config(config)

        host, port_string = parse_address(config.address)
        port = int(port_string)

        start_sequence = hex_sequence_to_bytes(config.start_seq)
        end_sequence   = hex_sequence_to_bytes(config.end_seq)

        # Config recv_timeout is in milliseconds, the client expects seconds
        receive_timeout = config.recv_timeout / _ms_per_second

        # TLS turns on when a CA bundle is configured - the client then always verifies
        # the server against it, and a cert/key pair, if also configured, enables mTLS.
        if config.tls_ca_path:
            ssl_context = build_client_ssl_context(
                ca_file=config.tls_ca_path,
                cert_file=config.tls_cert_path,
                key_file=config.tls_key_path,
            )
        else:
            ssl_context = None

        self.impl = HL7MLLPClient(
            host,
            port,
            start_sequence,
            end_sequence,
            receive_timeout=receive_timeout,
            max_message_size=config.max_msg_size,
            read_buffer_size=config.read_buffer_size,
            should_log_messages=config.should_log_messages,
            ssl_context=ssl_context,
        )

# ################################################################################################################################

    def invoke(
        self,
        data:'bytes | str | any_',
        *,
        cid:'str'='',
        needs_audit:'bool'=True,
        needs_retry:'bool'=True,
        ) -> 'AckResult':
        """ Sends data and returns an AckResult, of whatever code the receiving system answered with. The input may
        be ER7 text, raw bytes or a parsed message object, e.g. when a service forwards the parsed input its channel
        gave it. A send that no acknowledgment came back from is tried again under the connection's retry policy,
        unless the caller retries on its own, as the queue does. The audit pair is written under the caller's
        correlation id, and a resubmit turns the pair off because it records its own events.
        """

        # Everything is normalized to text first - it is what the audit trail stores
        # and what the control id is extracted from ..
        message_text = to_message_text(data)

        # .. and the wire itself carries bytes.
        data = message_text.encode('utf-8')

        # The control id correlates the ACK with the message - it also lets the client
        # validate that the ACK actually acknowledges what was sent.
        msh_line = message_text.split('\r', 1)[0]
        control_id = extract_control_id(msh_line)

        # The sent event and its acknowledgment share one correlation id, the caller's when it has one
        if self.audit_log and needs_audit:

            if not cid:
                cid = new_cid_server()

            _ = audit_message_sent(
                self.audit_log, self.name, message_text,
                cid=cid, msg_id=control_id, attrs=get_wire_attrs(msh_line), endpoint=self.address)

        send_start = monotonic()

        def send() -> 'AckResult':
            out = self.impl.send(data, control_id)
            return out

        # A send that raises means no acknowledgment ever arrived - a transient
        # failure on the audit trail, because a resend can work.
        try:
            out = self._send_with_policy(cid, send, needs_retry)
        except Exception:
            if self.audit_log and needs_audit:
                duration_ms = int((monotonic() - send_start) * _ms_per_second)
                _ = audit_ack_received(
                    self.audit_log, self.name, ACKStatus.Timeout,
                    cid=cid, msg_id=control_id, duration_ms=duration_ms)
            raise

        # The acknowledgment arrived - its code decides the outcome on its own row
        if self.audit_log and needs_audit:
            duration_ms = int((monotonic() - send_start) * _ms_per_second)
            _ = audit_ack_received(
                self.audit_log, self.name, out.ack_code,
                cid=cid, msg_id=control_id, duration_ms=duration_ms, error_text=out.error_text)

        return out

# ################################################################################################################################

    def _send_with_policy(self, cid:'str', send:'callable_', needs_retry:'bool') -> 'AckResult':
        """ Runs one send, tried again under the connection's retry policy when asked to. Only a send that no
        acknowledgment came back from is tried again - an acknowledgment of any code is the receiving system's
        answer and belongs to the caller.
        """
        if not needs_retry:
            out = send()
            return out

        policy = self.retry_policy

        attempt = 0
        total_sleep_time = 0
        current_sleep_time = policy.sleep_time

        while True:

            try:
                out = send()
                return out

            except Exception as e:

                # Both the attempt count and the total time spent sleeping are caps
                has_attempts_left = attempt < policy.max_retries
                has_time_left = total_sleep_time < policy.backoff_threshold

                if not (has_attempts_left and has_time_left):
                    raise

                attempt += 1

                logger.info('MLLP retry cid=%s, conn=%s, attempt=%s of %s, sleep=%ss, reason=%s',
                    cid, self.name, attempt, policy.max_retries, current_sleep_time, e)

                sleep(current_sleep_time)
                total_sleep_time += current_sleep_time
                current_sleep_time = get_next_sleep_time(policy, current_sleep_time, total_sleep_time)

# ################################################################################################################################
# ################################################################################################################################

class OutconnHL7MLLPWrapper(Wrapper):
    """ Wraps a queue of connections to HL7 MLLP servers.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config.auth_url = config.address
        super().__init__(config, 'HL7 MLLP', server)

        # A connection whose audit log is on writes a sent and an ACK event per message
        if asbool(self.config.is_audit_log_active):
            self.audit_log = AuditLog(server.name)
        else:
            self.audit_log = None

        # Whether a send that did not go through waits in the connection's queue
        self.use_queue = self.config[_use_queue_field]

        # What a guaranteed delivery to this connection goes through. It is built from the connection's
        # id rather than its name because that is what a rename leaves alone.
        self.publisher = OutgoingPublisher(server, OutgoingType.MLLP, self.config.id)

# ################################################################################################################################

    def add_client(self) -> 'None':
        try:
            connection = _HL7MLLPConnection(self.config, self.audit_log)
            _ = self.client.put_client(connection)
        except Exception:
            logger.warning('Error adding HL7 MLLP client (%s); e:`%s`', self.config.name, format_exc())

# ################################################################################################################################

    def delete(self, ignored_reason:'object'=None) -> 'None':
        pass

# ################################################################################################################################

    def publish(self, data:'bytes | str | any_', **kwargs:'any_') -> 'PublishResult':
        """ Queues one HL7 message for delivery to this connection, returning as soon as it is stored - no direct
        attempt is made.
        """
        request = {
            Key_Data: to_message_text(data),
        }

        out = self.publisher.publish_request('', Attempts_None, request, **kwargs)
        return out

# ################################################################################################################################

    def send_from_queue(self, cid:'str', request:'stranydict') -> 'AckResult':
        """ Makes one attempt to deliver a message the queue holds, raising when the receiving system turned it down -
        the same test the direct attempt applies, so both agree on what a failure is.
        """
        with self.client() as connection:
            ack = connection.invoke(request[Key_Data], cid=cid, needs_retry=False)

        if rejection := get_ack_rejection(ack):
            raise SendRejected(rejection, ack)

        return ack

# ################################################################################################################################
# ################################################################################################################################
