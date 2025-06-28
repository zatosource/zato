# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps

# Bunch
from bunch import bunchify

# Kombu
from kombu.entity import PERSISTENT_DELIVERY_MODE

# Zato
from zato.common.pubsub.util import get_broker_config
from zato.server.connection.amqp_ import get_connection_class, Producer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class BrokerClient:

    def __init__(self, *, server:'ParallelServer | None'=None) -> 'None':

        broker_config = get_broker_config()
        
        host, port = broker_config.address.split(':')
        port = int(port)

        conn_url = f'{broker_config.protocol}://{broker_config.username}:{broker_config.password}@{host}:{port}/{broker_config.vhost}'

        producer_name = 'internal'

        def get_conn_class_func(suffix, is_tls):
            return get_connection_class(producer_name, suffix, is_tls)

        # Configure producer
        producer_config = bunchify({
            'name': producer_name,
            'is_active': True,
            'conn_url': conn_url,
            'frame_max': 128000,
            'heartbeat': 30,
            'host': host,
            'port': port,
            'vhost': broker_config.vhost,
            'username': broker_config.username,
            'password': broker_config.password,
            'pool_size': 10,
            'get_conn_class_func': get_conn_class_func
        })

        self.producer = Producer(producer_config)

# ################################################################################################################################

    def publish(self, msg:'anydict', *ignored_args:'any_', **kwargs:'any_') -> 'any_':

        msg = dumps(msg)

        with self.producer.acquire() as client:

            client.publish(
                msg,
                exchange='components',
                routing_key='server',
                content_type='text/plain',
                delivery_mode=PERSISTENT_DELIVERY_MODE
            )

    invoke_async = publish

# ################################################################################################################################
# ################################################################################################################################
