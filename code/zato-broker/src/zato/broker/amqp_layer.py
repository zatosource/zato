# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Kombu
from kombu.connection import Connection as KombuConnection
from kombu.entity import Exchange, Queue

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.util import get_broker_config
from zato.common.util.api import new_cid_broker_client

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.common import BrokerConfig
    from zato.common.typing_ import strdictnone

# ################################################################################################################################
# ################################################################################################################################

class BrokerConnection(KombuConnection):

    def ensure_connection(self, *args, **kwargs):
        kwargs['timeout'] = None
        _ = self._ensure_connection(*args, **kwargs)
        return self

# ################################################################################################################################
# ################################################################################################################################

class AMQP:

    def get_connection(self, broker_config:'BrokerConfig | None'=None, needs_ensure:'bool'=True) -> 'BrokerConnection':
        """ Returns a new AMQP connection object using broker configuration parameters.
        """
        # Get broker configuration
        broker_config = get_broker_config()

        # Split host and port from address
        host, port = broker_config.address.split(':')
        port = int(port)

        # Create and return a new connection
        conn = BrokerConnection(
            hostname=host,
            port=port,
            userid=broker_config.username,
            password=broker_config.password,
            virtual_host=broker_config.vhost,
            transport=broker_config.protocol,
        )

        # Make sure we are connected
        _ = conn.ensure_connection(timeout=1)

        return conn

# ################################################################################################################################

    def create_bindings(
        self,
        cid: 'str',
        sub_key: 'str',
        exchange_name: 'str',
        queue_name: 'str',
        routing_key: 'str',
        conn: 'BrokerConnection | None'=None,
        queue_arguments: 'strdictnone'=None,
    ) -> 'None':

        # Make sure we have a cid
        cid = cid or new_cid_broker_client()

        # Get broker connection from input or build a new one
        if conn:
            should_close = False
        else:
            conn = self.get_connection()
            should_close = True

        # Customize the queue per our needs ..
        queue_arguments = queue_arguments or {}
        queue_arguments.update({
            'x-queue-type': 'quorum',
            'x-delivery-limit': PubSub.Max_Repeats
        })

        # Create exchange and queue objects
        exchange = Exchange(exchange_name, type='topic', durable=True)
        queue = Queue(name=queue_name, exchange=exchange, routing_key=routing_key, durable=True, queue_arguments=queue_arguments)

        # Bind the queue to the exchange with the topic name as the routing key
        logger = getLogger('zato')
        logger.debug(f'[{cid}] [{sub_key}] Configuring bindings for exchange={exchange.name} -> queue={queue_name} (topic={routing_key})')

        _ = queue.maybe_bind(conn)
        _ = queue.declare()
        _ = queue.bind_to(
            exchange=exchange, # type: ignore
            routing_key=routing_key
        )

        # Close the connection if it was opened by us
        if should_close:
            conn.close()

# ################################################################################################################################
# ################################################################################################################################
