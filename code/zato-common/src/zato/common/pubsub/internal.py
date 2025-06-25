# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import getLogger

# Bunch
from bunch import bunchify

# Kombu
from kombu.connection import Connection as KombuAMQPConnection

# Zato
from zato.common.api import AMQP
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

def start_internal_consumer(on_msg_callback:'callable_') -> 'None':

    # Get broker configuration from environment variables
    broker_protocol = os.environ['Zato_Broker_Protocol']
    broker_address  = os.environ['Zato_Broker_Address']
    broker_vhost    = os.environ['Zato_Broker_Virtual_Host']
    broker_username = os.environ['Zato_Broker_Username']
    broker_password = os.environ['Zato_Broker_Password']

    queue_name = 'server'

    conn_url = f'{broker_protocol}://{broker_username}:{broker_password}@{broker_address}/{broker_vhost}'
    conn_url_no_password = f'{broker_protocol}://{broker_username}:********@{broker_address}/{broker_vhost}'

    config = bunchify({
        'name': 'zato.server',
        'queue': queue_name,
        'consumer_tag_prefix': 'zato-server',
        'ack_mode': AMQP.ACK_MODE.ACK.id,
        'prefetch_count': 5,
        'conn_url': conn_url,
        'conn_class': KombuAMQPConnection,
        'is_active': True
    })

    consumer = Consumer(config, on_msg_callback)

    logger.info(f'Starting internal pub/sub server consumer for {conn_url_no_password} (queue={queue_name})')

    try:
        consumer.start()
    except KeyboardInterrupt:
        consumer.stop()
        logger.info(f'Stopped internal pub/sub server consumer for {conn_url_no_password} (queue={queue_name})')

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
