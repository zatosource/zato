# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# gevent
from gevent import sleep, spawn

# PyZMQ
import zmq.green as zmq

# Zato
from zato.common.test import get_free_tcp_port, rand_string

# ################################################################################################################################

class ZMQServer(object):

    def __init__(self, socket_type, socket_method, port, data=None):
        self.ctx = zmq.Context()
        self.socket_type = socket_type
        self.socket = self.ctx.socket(self.socket_type)
        self.socket_method = socket_method
        getattr(self.socket, self.socket_method)('tcp://127.0.0.1:{}'.format(port))
        self.data = data

    def run(self):
        if self.socket_type == zmq.PUSH:
            self.socket.send_string(self.data)
        else:
            while self.data is None:
                self.data = self.socket.recv_string()

# ################################################################################################################################

class TestOutgoingZMQ(TestCase):

# ################################################################################################################################

    def test_socket_type_push_socket_method_bind(self):
        server_port = get_free_tcp_port()
        data = rand_string()

        server1 = ZMQServer(zmq.PUSH, 'bind', server_port, data)
        server2 = ZMQServer(zmq.PULL, 'connect', server_port)

        spawn(server1.run)
        sleep(0.2)

        spawn(server2.run)
        sleep(0.2)

        print(333, server2.data)

# ################################################################################################################################

    def xtest_socket_type_push_socket_method_connect(self):
        self.fail()

# ################################################################################################################################

    def xtest_socket_type_pub_socket_method_bind(self):
        self.fail()

# ################################################################################################################################

    def xtest_socket_type_pub_socket_method_connect(self):
        self.fail()

# ################################################################################################################################
