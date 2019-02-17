# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from errno import ENOTSOCK
from traceback import format_exc

# ZeroMQ
import zmq.green as zmq

# Zato
from zato.common.ipc import IPCEndpoint, Request

# This is needed so that unpickling of requests works
Request = Request

# ################################################################################################################################

class Subscriber(IPCEndpoint):
    """ Listens for incoming IPC messages and invokes callbacks for each one received.
    """
    socket_method = 'bind'
    socket_type = 'sub'

    def __init__(self, on_message_callback, *args, **kwargs):
        self.on_message_callback = on_message_callback
        super(Subscriber, self).__init__(*args, **kwargs)

    def serve_forever(self):
        self.socket.setsockopt(zmq.SUBSCRIBE, b'')

        while self.keep_running:
            try:
                self.on_message_callback(self.socket.recv_pyobj())
            except zmq.ZMQError as e:
                if e.errno == ENOTSOCK:
                    self.logger.debug('Stopping IPC socket `%s` (ENOTSOCK)', self.name)
                    self.keep_running = False
            except Exception:
                self.logger.warn('Error in IPC subscriber, e:`%s`', format_exc())

# ################################################################################################################################
