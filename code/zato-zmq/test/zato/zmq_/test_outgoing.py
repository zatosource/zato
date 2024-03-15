# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase

# Bunch
from bunch import Bunch

# gevent
from gevent import sleep, spawn

# PyZMQ
import zmq.green as zmq

# Zato
from zato.common.api import ZMQ
from zato.common.test import get_free_tcp_port, rand_string
from zato.zmq_.outgoing import Simple as OutgoingZMQ

# ################################################################################################################################

out_client_socket_type = {
    ZMQ.PUSH: zmq.PULL,
    ZMQ.PUB: zmq.SUB
}

out_client_socket_method = {
    'bind': 'connect',
    'connect': 'bind',
}

# ################################################################################################################################

class ZMQClient:

    def __init__(self, socket_type, socket_method, port, data=None):
        self.ctx = zmq.Context()
        self.socket_type = socket_type
        self.socket = self.ctx.socket(self.socket_type)
        self.socket_method = socket_method
        getattr(self.socket, self.socket_method)('tcp://127.0.0.1:{}'.format(port))
        self.data = data

    def run(self):
        if self.socket_type == zmq.SUB:
            self.socket.setsockopt(zmq.SUBSCRIBE, '')

        while self.data is None:
            self.data = self.socket.recv_string()

# ################################################################################################################################

class TestOutgoingZMQ(TestCase):

# ################################################################################################################################

    def _get_outgoing_and_client(self, out_port, out_socket_type, out_socket_method, expected_data):

        config = Bunch()
        config.id = 1
        config.is_active = True
        config.address = 'tcp://127.0.0.1:{}'.format(out_port)
        config.socket_type = out_socket_type
        config.socket_method = out_socket_method

        outgoing = OutgoingZMQ('abc', ZMQ.OUTGOING[out_socket_type], config)
        client = ZMQClient(out_client_socket_type[out_socket_type], out_client_socket_method[out_socket_method], out_port)

        return outgoing, client

# ################################################################################################################################

    def _compare_data(self, outgoing, client, expected):

        spawn(outgoing.start)
        sleep(0.1)

        spawn(client.run)
        sleep(0.1)

        outgoing.send(expected)
        sleep(0.1)

        self.assertEqual(expected, client.data)

# ################################################################################################################################

    def test_socket_type_push_socket_method_bind(self):
        expected = 'push-bind-' + rand_string()
        outgoing, client = self._get_outgoing_and_client(get_free_tcp_port(), ZMQ.PUSH, 'bind', expected)
        self._compare_data(outgoing, client, expected)

# ################################################################################################################################

    def test_socket_type_push_socket_method_connect(self):
        expected = 'push-connect-' + rand_string()
        outgoing, client = self._get_outgoing_and_client(get_free_tcp_port(), ZMQ.PUSH, 'connect', expected)
        self._compare_data(outgoing, client, expected)

# ################################################################################################################################

    def test_socket_type_pub_socket_method_bind(self):
        expected = 'pub-bind-' + rand_string()
        outgoing, client = self._get_outgoing_and_client(get_free_tcp_port(), ZMQ.PUB, 'bind', expected)
        self._compare_data(outgoing, client, expected)

# ################################################################################################################################

    def test_socket_type_pub_socket_method_connect(self):
        expected = 'pub-connect-' + rand_string()
        outgoing, client = self._get_outgoing_and_client(get_free_tcp_port(), ZMQ.PUB, 'connect', expected)
        self._compare_data(outgoing, client, expected)

# ################################################################################################################################
