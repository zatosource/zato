# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# PyZMQ
import zmq.green as zmq

# Zato
from zato.common import ZMQ
from zato.server.connection.connector import Connector

# ################################################################################################################################

class BaseZMQSimple(Connector):
    """ Base class for ZeroMQ connections, both channels and outgoing ones, other than Majordomo (MDP).
    """
    def _start(self):
        self.log_details = '{} {}'.format(self.config.socket_type, self.config.address)
        self.ctx = zmq.Context()
        self.impl = self.ctx.socket(getattr(zmq, self.config.socket_type))
        self.conn = self

        if self.config.socket_type == ZMQ.SUB and self.config.sub_key:
            self.impl.setsockopt(zmq.SUBSCRIBE, self.config.sub_key)

        # Whether to bind or connect?
        socket_method = getattr(self.impl, self.config.socket_method)
        socket_method(self.config.address)

    def _send(self, msg, *args, **kwargs):
        self.impl.send(msg, *args, **kwargs)

    def _stop(self):
        self.impl.close(50) # TODO: Should be configurable

# ################################################################################################################################
