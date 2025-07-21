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

# gevent
from gevent import sleep, spawn

# Kombu
from kombu.connection import Connection as KombuAMQPConnection

# Zato
from zato.common.api import AMQP, PubSub
from zato.common.pubsub.util import get_broker_config
from zato.server.connection.amqp_ import Consumer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, callable_, strdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ConsumerConfig:
    cid: 'str' = ''
    name: 'str'
    is_internal: 'bool'
    queue_name: 'str'
    prefetch_count: 'int'
    consumer_tag_prefix: 'str'
    on_msg_callback: 'callable_'
    wait_for_conection: 'bool'
    should_start: 'bool'
    max_repeats: 'int' = PubSub.Max_Repeats

# ################################################################################################################################
# ################################################################################################################################

def start_consumer(consumer_config:'ConsumerConfig') -> 'Consumer':

    # For later use
    visibility = 'internal' if consumer_config.is_internal else 'public'
    cid_prefix = f'[{consumer_config.cid}] ' if consumer_config.cid else ''

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
        'is_active': True,
        'queue_type': 'quorum',
        'max_repeats': consumer_config.max_repeats
    })

    consumer = Consumer(broker_config, consumer_config.on_msg_callback)

    logger.info(f'{cid_prefix}Starting {visibility} consumer for queue={consumer_config.queue_name} -> {conn_url_no_password}')

    try:

        # .. optionally, start a consumer in a new thread ..
        _ = spawn(consumer.start)

        # .. optionally, wait until it's actually connected ..
        if consumer_config.wait_for_conection:

            # .. keep running ..
            while not consumer.is_connected:

                # .. but not if the consumer has been told to stop ..
                if not consumer.keep_running:
                    break

                # .. sleep for a moment ..
                logger.debug(f'Not connected -> {consumer_config}')
                sleep(0.2)

    except KeyboardInterrupt:
        consumer.stop()
        logger.info(f'{cid_prefix}Stopped {visibility} consumer for queue={consumer_config.queue_name} -> {conn_url_no_password}')
    finally:
        logger.debug(f'Connected -> {consumer_config}')
        return consumer

# ################################################################################################################################
# ################################################################################################################################

def start_internal_consumer(
    name: 'str',
    queue_name: 'str',
    consumer_tag_prefix: 'str',
    on_msg_callback:'callable_'
) -> 'Consumer':

    is_internal = True
    prefetch_count = 1

    config = ConsumerConfig()
    config.name = name
    config.is_internal = is_internal
    config.queue_name = queue_name
    config.prefetch_count = prefetch_count
    config.consumer_tag_prefix = consumer_tag_prefix
    config.on_msg_callback = on_msg_callback
    config.wait_for_conection = False
    config.should_start = True

    consumer = start_consumer(config)
    return consumer

# ################################################################################################################################
# ################################################################################################################################

def start_public_consumer(
    cid: 'str',
    username: 'str',
    sub_key: 'str',
    on_msg_callback: 'callable_',
    should_start:'bool'=True,
) -> 'Consumer':

    name = username
    is_internal = False
    queue_name = sub_key
    prefetch_count = 1
    consumer_tag_prefix = f'{username}.{cid}'

    config = ConsumerConfig()
    config.cid = cid
    config.name = name
    config.is_internal = is_internal
    config.queue_name = queue_name
    config.prefetch_count = prefetch_count
    config.consumer_tag_prefix = consumer_tag_prefix
    config.on_msg_callback = on_msg_callback
    config.wait_for_conection = should_start
    config.should_start = should_start

    consumer = start_consumer(config)
    return consumer

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    log_format = '%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    def process_message(body:'any_', msg:'any_', name:'str', config:'strdict') -> 'None':

        # Print what we received ..
        print(msg)

        # .. and acknowledge the message so we can read more of them.
        msg.ack()

    _ = start_internal_consumer('demo-consumer', 'server', 'hello123', process_message)

# ################################################################################################################################
# ################################################################################################################################
