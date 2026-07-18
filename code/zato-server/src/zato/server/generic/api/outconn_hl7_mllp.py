# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from time import monotonic
from traceback import format_exc

# Zato
from zato.common.api import HL7
from zato.common.audit_log.api import AuditLog
from zato.common.hl7.audit import audit_ack_received, audit_message_sent, get_wire_attrs, ACKStatus
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.hl7.mllp.dedup import extract_control_id
from zato.common.hl7.mllp.tls import build_client_ssl_context
from zato.common.util.api import asbool, hex_sequence_to_bytes, new_cid_server
from zato.common.util.tcp import parse_address
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

# How many milliseconds one second holds - used when converting send durations
_ms_per_second = 1000

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Defaults applied by the config manager when the create path does not supply a field,
# e.g. when an outconn is created directly through zato.generic.connection.create.
outconn_config_defaults:'dict[str, object]' = {
    'start_seq': HL7.Default.start_seq,
    'end_seq': HL7.Default.end_seq,
    'recv_timeout': HL7.Default.recv_timeout,
    'max_msg_size': HL7.Default.max_msg_size,
    'read_buffer_size': HL7.Default.read_buffer_size,
    'should_log_messages': False,

    # Audit - separate from server-log verbosity, off unless turned on per connection
    'is_audit_log_active': False,

    # TLS is off by default - it turns on when a CA bundle is configured
    'tls_ca_path': '',
    'tls_cert_path': '',
    'tls_key_path': '',
}

# Config keys that must be integers but may arrive as strings from opaque storage
outconn_int_config_keys = ('recv_timeout', 'max_msg_size', 'read_buffer_size')

# ################################################################################################################################
# ################################################################################################################################

class _HL7MLLPConnection:
    """ Wraps an HL7MLLPClient instance for use with the connection pool.
    """
    def __init__(self, config:'object', audit_log:'AuditLog | None' = None) -> 'None':

        # What the audit events are filed under and where they say the message went -
        # the name is only read when auditing is on, because offline tests build
        # minimal configs without one.
        self.audit_log = audit_log
        self.address = config.address # type: ignore[union-attr]

        if audit_log:
            self.name = config.name # type: ignore[union-attr]
        else:
            self.name = ''

        host, port_string = parse_address(config.address) # type: ignore[union-attr]
        port = int(port_string)

        start_sequence = hex_sequence_to_bytes(config.start_seq) # type: ignore[union-attr]
        end_sequence   = hex_sequence_to_bytes(config.end_seq) # type: ignore[union-attr]

        # Config recv_timeout is in milliseconds, the client expects seconds
        receive_timeout = config.recv_timeout / 1000.0 # type: ignore[union-attr]

        # TLS turns on when a CA bundle is configured - the client then always verifies
        # the server against it, and a cert/key pair, if also configured, enables mTLS.
        if config.tls_ca_path: # type: ignore[union-attr]
            ssl_context = build_client_ssl_context(
                ca_file=config.tls_ca_path, # type: ignore[union-attr]
                cert_file=config.tls_cert_path, # type: ignore[union-attr]
                key_file=config.tls_key_path, # type: ignore[union-attr]
            )
        else:
            ssl_context = None

        self.impl = HL7MLLPClient(
            host,
            port,
            start_sequence,
            end_sequence,
            receive_timeout=receive_timeout,
            max_message_size=config.max_msg_size, # type: ignore[union-attr]
            read_buffer_size=config.read_buffer_size, # type: ignore[union-attr]
            should_log_messages=config.should_log_messages, # type: ignore[union-attr]
            ssl_context=ssl_context,
        )

    def invoke(self, data:'object') -> 'object':
        """ Sends data and returns an AckResult. The input may be ER7 text, raw bytes
        or a parsed message object, e.g. when a service forwards the parsed input
        its channel gave it.
        """

        # Everything is normalized to text first - it is what the audit trail stores
        # and what the control id is extracted from ..
        if isinstance(data, bytes):
            message_text = data.decode('utf-8', errors='replace')
        elif isinstance(data, str):
            message_text = data
        else:
            message_text = data.to_er7() # type: ignore[attr-defined]

        # .. and the wire itself carries bytes.
        data = message_text.encode('utf-8')

        # The control id correlates the ACK with the message - it also lets the client
        # validate that the ACK actually acknowledges what was sent.
        msh_line = message_text.split('\r', 1)[0]
        control_id = extract_control_id(msh_line)

        # The sent event and its acknowledgment share one correlation id
        if self.audit_log:
            audit_cid = new_cid_server()
            _ = audit_message_sent(
                self.audit_log, self.name, message_text,
                cid=audit_cid, msg_id=control_id, attrs=get_wire_attrs(msh_line), endpoint=self.address)
        else:
            audit_cid = ''

        send_start = monotonic()

        # A send that raises means no acknowledgment ever arrived - a transient
        # failure on the audit trail, because a resend can work.
        try:
            out = self.impl.send(data, control_id)
        except Exception:
            if self.audit_log:
                duration_ms = int((monotonic() - send_start) * _ms_per_second)
                _ = audit_ack_received(
                    self.audit_log, self.name, ACKStatus.Timeout,
                    cid=audit_cid, msg_id=control_id, duration_ms=duration_ms)
            raise

        # The acknowledgment arrived - its code decides the outcome on its own row
        if self.audit_log:
            duration_ms = int((monotonic() - send_start) * _ms_per_second)
            _ = audit_ack_received(
                self.audit_log, self.name, out.ack_code,
                cid=audit_cid, msg_id=control_id, duration_ms=duration_ms, error_text=out.error_text)

        return out

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
# ################################################################################################################################
