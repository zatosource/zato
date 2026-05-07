# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.hl7.mllp.server import HL7MLLPServer
from zato.common.util.api import hex_sequence_to_bytes, spawn_greenlet
from zato.server.connection.wrapper import Wrapper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ChannelHL7MLLPWrapper(Wrapper):
    """ Represents an HL7 MLLP channel.
    """
    needs_self_client = False
    wrapper_type = 'HL7 MLLP channel'
    build_if_not_active = True

    def __init__(self, *args:'object', **kwargs:'object') -> 'None':
        super().__init__(*args, **kwargs)
        self._impl:'HL7MLLPServer | None' = None

# ################################################################################################################################

    def _init_impl(self) -> 'None':

        with self.update_lock:

            start_sequence = hex_sequence_to_bytes(self.config.start_seq)
            end_sequence   = hex_sequence_to_bytes(self.config.end_seq)

            # Convert recv_timeout from milliseconds to seconds
            receive_timeout = self.config.recv_timeout / 1000.0

            self._impl = HL7MLLPServer(
                self.config.address,
                self.server.invoke, # pyright: ignore[reportOptionalMemberAccess]
                start_sequence,
                end_sequence,
                receive_timeout=receive_timeout,
                max_message_size=int(self.config.max_msg_size),
                read_buffer_size=int(self.config.read_buffer_size),
                should_log_messages=self.config.should_log_messages,
            )

            spawn_greenlet(self._impl.start)

            self.is_connected = True

# ################################################################################################################################

    def _delete(self) -> 'None':
        if self._impl:
            self._impl.stop()

# ################################################################################################################################

    def _ping(self) -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################
