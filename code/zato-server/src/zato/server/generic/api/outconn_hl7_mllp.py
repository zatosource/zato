# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# Zato
from zato.common.hl7.mllp.client import HL7MLLPClient
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

class _HL7MLLPConnection:
    """ Wraps an HL7MLLPClient instance for use with the connection pool.
    """
    def __init__(self, config:'object') -> 'None':

        host, port_string = parse_address(config.address) # type: ignore[union-attr]
        port = int(port_string)

        start_sequence = hex_sequence_to_bytes(config.start_seq) # type: ignore[union-attr]
        end_sequence   = hex_sequence_to_bytes(config.end_seq) # type: ignore[union-attr]

        receive_timeout = int(config.recv_timeout) / 1000.0 # type: ignore[union-attr]

        self.impl = HL7MLLPClient(
            host,
            port,
            start_sequence,
            end_sequence,
            receive_timeout=receive_timeout,
            max_message_size=int(config.max_msg_size), # type: ignore[union-attr]
            read_buffer_size=int(config.read_buffer_size), # type: ignore[union-attr]
            should_log_messages=config.should_log_messages, # type: ignore[union-attr]
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
            self.client.put_client(connection)
        except Exception:
            logger.warning('Error adding HL7 MLLP client (%s); e:`%s`', self.config.name, format_exc())

# ################################################################################################################################

    def delete(self, ignored_reason:'object'=None) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################
