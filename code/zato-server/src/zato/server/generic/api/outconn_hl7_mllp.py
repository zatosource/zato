# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.api import HL7
from zato.common.hl7.mllp.client import HL7MLLPClient
from zato.common.hl7.mllp.tls import build_client_ssl_context
from zato.common.util.api import hex_sequence_to_bytes
from zato.common.util.tcp import parse_address
from zato.server.connection.queue import Wrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.server.base.parallel import ParallelServer

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
    def __init__(self, config:'object') -> 'None':

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

    def invoke(self, data:'str | bytes') -> 'object':
        """ Sends data and returns an AckResult.
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        out = self.impl.send(data)
        return out

# ################################################################################################################################
# ################################################################################################################################

class OutconnHL7MLLPWrapper(Wrapper):
    """ Wraps a queue of connections to HL7 MLLP servers.
    """
    def __init__(self, config:'Bunch', server:'ParallelServer') -> 'None':
        config.auth_url = config.address
        super().__init__(config, 'HL7 MLLP', server)

# ################################################################################################################################

    def add_client(self) -> 'None':
        try:
            connection = _HL7MLLPConnection(self.config)
            _ = self.client.put_client(connection)
        except Exception:
            logger.warning('Error adding HL7 MLLP client (%s); e:`%s`', self.config.name, format_exc())

# ################################################################################################################################

    def delete(self, ignored_reason:'object'=None) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################
