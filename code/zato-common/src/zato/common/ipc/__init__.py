# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from gevent import monkey
monkey.patch_all()

# stdlib
import logging
import os
from tempfile import gettempdir

# ZeroMQ
import zmq.green as zmq

# Zato
from zato.common.util import make_repr

# ################################################################################################################################

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ################################################################################################################################

class IPCBase(object):
    """ Base class for core IPC objects.
    """
    socket_method = None
    socket_type = None

    def __init__(self, address, pid):
        self.address = self.get_address(address)
        self.pid = pid
        self.ctx = zmq.Context()
        self.set_up_socket()
        self.keep_running = True
        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.info('Connected %s/%s to %s', self.socket_type, self.socket_method, self.address)

# ################################################################################################################################

    def set_up_socket(self):
        self.socket = self.ctx.socket(self.socket_type)
        self.socket.setsockopt(zmq.LINGER, 0)
        getattr(self.socket, self.socket_method)(self.address)

# ################################################################################################################################

    def get_address(self, address):
        return 'ipc://{}'.format(os.path.join(gettempdir(), 'zato-ipc-{}'.format(address)))

# ################################################################################################################################

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

    def close(self):
        self.keep_running = False
        self.socket.close()
        self.ctx.term()

# ################################################################################################################################
