# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Bunch
from bunch import bunchify

# Zato
from zato.common.api import GENERIC
from zato.common.util.api import spawn_greenlet
from zato.hl7.mllp.server import HL7MLLPServer
from zato.server.connection.wrapper import Wrapper

# ###############################################################################################################################
# ###############################################################################################################################

logger = getLogger(__name__)

# ###############################################################################################################################
# ###############################################################################################################################

_audit_log_type = GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP

# ################################################################################################################################
# ################################################################################################################################

class ChannelHL7MLLPWrapper(Wrapper):
    """ Represents an HL7 MLLP channel.
    """
    needs_self_client = False
    wrapper_type = 'HL7 MLLP channel'
    build_if_not_active = True

    def __init__(self, *args, **kwargs):
        super(ChannelHL7MLLPWrapper, self).__init__(*args, **kwargs)
        self._impl = None # type: HL7MLLPServer

# ################################################################################################################################

    def _init_impl(self):

        # Zato
        from zato.common.util.api import hex_sequence_to_bytes

        with self.update_lock:

            # Unwrap the expected bytes sequences

            config = bunchify({
                'id': self.config.id,
                'name': self.config.name,
                'address': self.config.address,
                'service_name': self.config.service,

                'max_msg_size': self.config.max_msg_size,
                'read_buffer_size': self.config.read_buffer_size,

                # Convert to seconds from milliseconds
                'recv_timeout': self.config.recv_timeout / 100.0,

                'logging_level': self.config.logging_level,
                'should_log_messages': self.config.should_log_messages,

                'start_seq': hex_sequence_to_bytes(self.config.start_seq),
                'end_seq': hex_sequence_to_bytes(self.config.end_seq),

                'is_audit_log_sent_active': self.config.get('is_audit_log_sent_active'),
                'is_audit_log_received_active': self.config.get('is_audit_log_received_active'),

            })

            # Create a server ..
            self._impl = HL7MLLPServer(config, self.server.invoke, self.server.audit_log)

            # .. start the server in a new greenlet, waiting a moment to confirm that it runs ..
            spawn_greenlet(self._impl.start)

            # .. and set up audit log.
            self.server.set_up_object_audit_log_by_config(_audit_log_type, self.config.id, self.config, False)

            # We can assume we are done building the channel now
            self.is_connected = True

# ################################################################################################################################

    def _delete(self):
        if self._impl:

            # Clear the audit log ..
            self.server.audit_log.delete_container(_audit_log_type, self.config.id)

            # .. and stop the connection.
            self._impl.stop()

# ################################################################################################################################

    def _ping(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
