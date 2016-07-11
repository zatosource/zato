# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os

# gevent
from gevent import sleep, spawn, spawn_later

# ZeroMQ
import zmq.green as zmq

# Zato
from zato.common.ipc import IPCBase

# ################################################################################################################################

class Publisher(IPCBase):
    """ Sends outgoing IPC messages to any party listening for them.
    """
    socket_method = 'connect'
    socket_type = zmq.PUB

    def send(self):
        self.socket.send_pyobj('{}-{}'.format(os.getpid(), self.pid))

    def send_forever(self):
        while True:
            sleep(0.1)
            self.send()

# ################################################################################################################################

if __name__ == '__main__':

    name = 'server1-pub'
    p = Publisher(name, 1)
    p.send_forever()