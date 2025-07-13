# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass
from logging import getLogger

# Bunch
from bunch import bunchify

# Kombu
from kombu.connection import Connection as KombuAMQPConnection

# Zato
from zato.common.api import AMQP
from zato.common.pubsub.util import get_broker_config
from zato.server.connection.amqp_ import Consumer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ConsumerConfig:
    name: 'str'
    is_internal: 'bool'
    queue_name: 'str'
    prefetch_count: 'int'
    consumer_tag_prefix: 'str'
    on_msg_callback: 'callable_'

# ################################################################################################################################
# ################################################################################################################################

def start_consumer(consumer_config:'ConsumerConfig') -> 'None':

    # For later use
    visibility = 'internal' if consumer_config.is_internal else 'public'

    # Get broker configuration from the utility function
    broker_config = get_broker_config()

    conn_url = f'{broker_config.protocol}://{broker_config.username}:{broker_config.password}@{broker_config.address}/{broker_config.vhost}'
    conn_url_no_password = f'{broker_config.protocol}://{broker_config.username}:********@{broker_config.address}/{broker_config.vhost}'

    broker_config = bunchify({
        'name': consumer_config.name,
        'queue': consumer_config.queue_name,
        'consumer_tag_prefix': consumer_config.consumer_tag_prefix,
        'ack_mode': AMQP.ACK_MODE.ACK.id,
        'prefetch_count': consumer_config.prefetch_count,
        'conn_url': conn_url,
        'conn_class': KombuAMQPConnection,
        'is_active': True
    })

    consumer = Consumer(broker_config, consumer_config.on_msg_callback)

    logger.info(f'Starting {visibility} consumer for queue={consumer_config.queue_name} -> {conn_url_no_password}')

    try:
        consumer.start()
    except KeyboardInterrupt:
        consumer.stop()
        logger.info(f'Stopped {visibility} consumer for queue={consumer_config.queue_name} -> {conn_url_no_password}')

# ################################################################################################################################
# ################################################################################################################################

def start_internal_consumer(on_msg_callback:'callable_') -> 'None':

    name = 'zato.server'
    is_internal = True
    queue_name = 'server'
    prefetch_count = 1
    consumer_tag_prefix = 'zato-server'

    config = ConsumerConfig()
    config.name = name
    config.is_internal = is_internal
    config.queue_name = queue_name
    config.prefetch_count = prefetch_count
    config.consumer_tag_prefix = consumer_tag_prefix
    config.on_msg_callback = on_msg_callback

    start_consumer(config)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    def process_message(body:'any_', msg:'any_', name:'str', config:'dict') -> 'None':

        # Print what we received ..
        print(msg)

        # .. and acknowledge the message so we can read more of them.
        msg.ack()

    start_internal_consumer(process_message)

# ################################################################################################################################
# ################################################################################################################################
