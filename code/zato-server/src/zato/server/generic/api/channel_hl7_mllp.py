# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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

    def __init__(self, *args, **kwargs):
        super(ChannelHL7MLLPWrapper, self).__init__(*args, **kwargs)
        self._impl = None

# ################################################################################################################################

    def _init_impl(self):

        with self.update_lock:

            config = bunchify({
                'id': self.config.id,
                'name': self.config.name,
                'address': self.config.address,

                'max_msg_size': 1_000_000,
                'read_buffer_size': 2048,
                'recv_timeout': 0.25,

                'logging_level': 'INFO',
                'should_log_messages': False,

                'start_seq': b'\x0b',
                'end_seq': b'\x1c\x0d',

                'is_audit_log_sent_active': self.config.get('is_audit_log_sent_active'),
                'is_audit_log_received_active': self.config.get('is_audit_log_received_active'),

            })

            # Create a server ..
            self._impl = HL7MLLPServer(config, self.server.audit_log)

            # .. start the server in a new greenlet, waiting a moment to confirm that it runs ..
            spawn_greenlet(self._impl.start)


            # .. and set up audit log.
            self.server.set_up_object_audit_log_by_config(
                GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP, self.config.id, self.config, False)

            # We can assume we are done building the channel now
            self.is_connected = True

# ################################################################################################################################

    def _delete(self):
        self._impl.stop()

# ################################################################################################################################

    def _ping(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
