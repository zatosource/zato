# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# gevent
from gevent import sleep, spawn, spawn_later

# ZeroMQ
import zmq.green as zmq

# Zato
from zato.common.ipc import IPCBase

# ################################################################################################################################

class Subscriber(IPCBase):
    """ Listens for incoming IPC messages and invokes callbacks for each one received.
    """
    socket_method = 'bind'
    socket_type = zmq.SUB

    def serve_forever(self):
        self.socket.setsockopt(zmq.SUBSCRIBE, b'')

        while self.keep_running:
            data = self.socket.recv_pyobj()
            self.logger.warn('Got data %s in pid %s', data, self.pid)

# ################################################################################################################################

if __name__ == '__main__':

    name = 'server1-sub'

    s1 = Subscriber(name, '1')
    s2 = Subscriber(name, '2')

    spawn(s1.serve_forever)
    spawn(s2.serve_forever)

    sleep(1)

    while True:
        sleep(0.1)