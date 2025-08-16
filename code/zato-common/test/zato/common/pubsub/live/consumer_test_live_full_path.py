# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import sys
from logging import basicConfig, getLogger, INFO
from time import sleep

# kombu
from kombu import Connection, Consumer, Queue
from kombu.exceptions import ConnectionError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kombu.message import Message

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def setup_logging() -> 'None':
    """ Set up basic logging configuration.
    """
    basicConfig(
        level=INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

# ################################################################################################################################

def get_broker_connection() -> 'Connection':
    """ Get connection to default RabbitMQ broker.
    """
    connection_url = 'amqp://guest:guest@localhost:5672/zato.internal'
    return Connection(connection_url)

# ################################################################################################################################

def process_message(body:'str', message:'Message') -> 'None':
    """ Process received message and print to screen.
    """
    logger.info(f'Received message: {body}')
    print(f'Message: {body}')
    message.ack()

# ################################################################################################################################

def consume_from_queue() -> 'None':
    """ Connect to broker and consume messages from Q1 queue.
    """

    setup_logging()
    logger.info('Starting consumer for queue Q1')

    connection = get_broker_connection()
    queue = Queue('Q1', durable=True, queue_arguments={'x-queue-type': 'quorum'})

    try:
        with connection:
            logger.info('Connected to broker')

            with Consumer(connection, [queue], callbacks=[process_message]):
                logger.info('Consumer started, waiting for messages...')
                print('Consumer started, waiting for messages from Q1...')

                while True:
                    try:
                        connection.drain_events(timeout=1.0)
                    except Exception as e:
                        logger.debug(f'Drain events timeout or error: {e}')
                        sleep(0.1)

    except ConnectionError as e:
        logger.error(f'Connection error: {e}')
        print(f'Connection error: {e}')
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info('Consumer stopped by user')
        print('Consumer stopped')
        sys.exit(0)
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        print(f'Unexpected error: {e}')
        sys.exit(1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    consume_from_queue()

# ################################################################################################################################
# ################################################################################################################################
