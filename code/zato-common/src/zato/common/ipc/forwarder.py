# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from tempfile import gettempdir

# ZeroMQ
import zmq.green as zmq

# Zato
from zato.common.ipc import IPCBase

# ################################################################################################################################

class Forwarder(IPCBase):
    """ An IPC broker forwarding requests across pub/sub processes. Required to achieve an i
    """
    def __init__(self, base_address, pid):
        self.base_address = self.get_address(base_address)
        super(Forwarder, self).__init__(base_address, pid)

    def get_address(self, address):
        return 'ipc://{}'.format(os.path.join(gettempdir(), 'zato-ipc-{}'.format(address)))

    def set_up_sockets(self):
        self.socket_for_publishers = self.ctx.socket(zmq.SUB)
        self.socket_for_publishers_address = self.base_address + '-sub'
        self.socket_for_publishers.bind(self.socket_for_publishers_address)

        self.socket_for_publishers.setsockopt(zmq.SUBSCRIBE, b'')

        self.socket_for_subscribers = self.ctx.socket(zmq.PUB)
        self.socket_for_subscribers_address = self.base_address + '-pub'
        self.socket_for_subscribers.bind(self.socket_for_subscribers_address)

        zmq.device(zmq.FORWARDER, self.socket_for_publishers, self.socket_for_subscribers)

    def log_connected(self):
        self.logger.warn('Forwarded running sub:`%s`, pub:`%s`',
            self.socket_for_publishers_address, self.socket_for_subscribers_address)

# ################################################################################################################################
