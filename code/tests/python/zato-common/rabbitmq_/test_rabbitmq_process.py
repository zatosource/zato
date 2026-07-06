# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import socket
import unittest

# Zato
from zato.common.test.rabbitmq_ import declare_and_bind, drain_queue, get_queue_depth, publish_to_exchange, RabbitMQProcess

# ################################################################################################################################
# ################################################################################################################################

def _is_port_open(port:'int') -> 'bool':
    """ Returns True if something accepts TCP connections on the port.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.settimeout(1)
        result = tcp_socket.connect_ex(('127.0.0.1', port))

        out = result == 0
        return out

# ################################################################################################################################
# ################################################################################################################################

class TestRabbitMQProcessLifecycle(unittest.TestCase):
    """ Item 12 - start a broker, publish and consume through the helpers, stop, assert cleanup.
    """

    def test_basic_lifecycle(self) -> 'None':

        broker = RabbitMQProcess()
        broker.start()

        try:
            # The AMQP port accepts connections ..
            self.assertTrue(_is_port_open(broker.amqp_port))

            # .. declare an exchange, a queue and a binding ..
            declare_and_bind(broker.amqp_url, 'test.exchange', 'test.queue', 'test.key')

            # .. publish one message through the helpers ..
            publish_to_exchange(broker.amqp_url, 'test.exchange', 'test.key', 'lifecycle-message-1')

            # .. and consume it back.
            messages = drain_queue(broker.amqp_url, 'test.queue', timeout=3)

            self.assertEqual(messages, ['lifecycle-message-1'])

            # The queue is empty after the drain acked everything
            depth = get_queue_depth(broker.amqp_url, 'test.queue')
            self.assertEqual(depth, 0)

        finally:
            broker.stop()

        # The process is gone ..
        self.assertFalse(_is_port_open(broker.amqp_port))

        # .. and the base directory was removed.
        self.assertFalse(os.path.exists(broker.base_directory))

# ################################################################################################################################
# ################################################################################################################################

class TestRabbitMQProcessParallel(unittest.TestCase):
    """ Item 13 - two parallel brokers do not clash.
    """

    def test_two_brokers_in_parallel(self) -> 'None':

        broker1 = RabbitMQProcess()
        broker2 = RabbitMQProcess()

        broker1.start()
        broker2.start()

        try:
            # Distinct ports, nodenames and directories ..
            self.assertNotEqual(broker1.amqp_port, broker2.amqp_port)
            self.assertNotEqual(broker1.dist_port, broker2.dist_port)
            self.assertNotEqual(broker1.nodename, broker2.nodename)
            self.assertNotEqual(broker1.base_directory, broker2.base_directory)

            # .. both accept connections ..
            self.assertTrue(_is_port_open(broker1.amqp_port))
            self.assertTrue(_is_port_open(broker2.amqp_port))

            # .. set up the same exchange and queue names on both brokers ..
            declare_and_bind(broker1.amqp_url, 'parallel.exchange', 'parallel.queue', 'parallel.key')
            declare_and_bind(broker2.amqp_url, 'parallel.exchange', 'parallel.queue', 'parallel.key')

            # .. publish a different message to each ..
            publish_to_exchange(broker1.amqp_url, 'parallel.exchange', 'parallel.key', 'for-broker-1')
            publish_to_exchange(broker2.amqp_url, 'parallel.exchange', 'parallel.key', 'for-broker-2')

            # .. and confirm there is no crosstalk.
            messages1 = drain_queue(broker1.amqp_url, 'parallel.queue', timeout=3)
            messages2 = drain_queue(broker2.amqp_url, 'parallel.queue', timeout=3)

            self.assertEqual(messages1, ['for-broker-1'])
            self.assertEqual(messages2, ['for-broker-2'])

        finally:
            broker1.stop()
            broker2.stop()

        # Both are gone along with their directories
        self.assertFalse(_is_port_open(broker1.amqp_port))
        self.assertFalse(_is_port_open(broker2.amqp_port))
        self.assertFalse(os.path.exists(broker1.base_directory))
        self.assertFalse(os.path.exists(broker2.base_directory))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()
