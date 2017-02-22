# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Kombu
from kombu import Connection, pools
from kombu.transport.pyamqp import Connection as PyAMQPConnection, Transport

# Zato
from zato.common import SECRET_SHADOW, version
from zato.common.util import get_component_name
from zato.server.connection.connector import Connector

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class ConnectorAMQP(Connector):
    """ An AMQP connector under which channels or outgoing connections run.
    """
    start_in_greenlet = True

    def _start(self):

        # Subclasses below are needed so as to be able to return per-greenlet/thread/process/definition information
        # in zato.* properties and, except for zato.version, this information is not available on module level.

        class _PyAMQPConnection(PyAMQPConnection):
            def __init__(_py_amqp_self, *args, **kwargs):
                super(_PyAMQPConnection, _py_amqp_self).__init__(client_properties={
                    'zato.component':get_component_name('amqp'),
                    'zato.version':version,
                    'zato.definition.name':self.config.name,
                }, *args, **kwargs)

        class _AMQPTransport(Transport):
            Connection = _PyAMQPConnection

        class _AMQPConnection(Connection):
            def get_transport_cls(self):
                return _AMQPTransport

        self.conn = _AMQPConnection(self._get_conn_string())
        self.conn.connect()
        self.is_connected = self.conn.connected

        # Create a custom pool of producers with up to amqp.pool_size objects (as defined in server.conf)
        if self.is_connected:
            self._create_producers()

    def _create_producers(self):
        self._amqp_connections = pools.Connections(limit=self.config.pool_size)
        self._amqp_producers = pools.Producers(limit=self._amqp_connections.limit)

    def _stop(self):
        self.conn.release()

    def _get_conn_string(self, needs_password=True):
        return 'amqp://{}:{}@{}:{}{}'.format(self.config.username, self.config.password if needs_password else SECRET_SHADOW,
            self.config.host, self.config.port, self.config.vhost)

    def get_log_details(self):
        return self._get_conn_string(False)

    def invoke(self, msg, exchange='/', routing_key=None, properties=None, headers=None):
        with self._amqp_producers[self.conn].acquire(block=True) as producer:
            producer.publish(msg, routing_key, exchange=exchange)

# ################################################################################################################################
