# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Bunch
from bunch import bunchify

# Kombu
from kombu.entity import PERSISTENT_DELIVERY_MODE

# Zato
from zato.server.connection.amqp_ import get_connection_class, Producer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

class BrokerClient:

    def __init__(self, *, server:'ParallelServer | None'   = None) -> 'None':

        broker_protocol = os.environ['Zato_Broker_Protocol']
        broker_address  = os.environ['Zato_Broker_Address']
        broker_vhost    = os.environ['Zato_Broker_Virtual_Host']
        broker_username = os.environ['Zato_Broker_Username']
        broker_password = os.environ['Zato_Broker_Password']

        if ':' in broker_address:
            host, port = broker_address.split(':')
            port = int(port)
        else:
            host = broker_address
            port = 5672  # Default AMQP port

        conn_url = f'{broker_protocol}://{broker_username}:{broker_password}@{host}:{port}/{broker_vhost}'

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
            'vhost': broker_vhost,
            'username': broker_username,
            'password': broker_password,
            'pool_size': 10,
            'get_conn_class_func': get_conn_class_func
        })

        self.producer = Producer(producer_config)

# ################################################################################################################################

    def publish(self, msg:'anydict', *ignored_args:'any_', **kwargs:'any_') -> 'any_':

        with self.producer.acquire() as client:

            client.publish(
                str(msg),
                exchange='components',
                routing_key='server',
                content_type='text/plain',
                delivery_mode=PERSISTENT_DELIVERY_MODE
            )

    invoke_async = publish

# ################################################################################################################################
# ################################################################################################################################
