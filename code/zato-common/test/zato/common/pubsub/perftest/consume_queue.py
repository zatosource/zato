#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import argparse
import logging
import sys
from json import loads
from traceback import format_exc

# Kombu
from kombu import Connection, Queue
from kombu.exceptions import OperationalError

# Zato
from zato.common.pubsub.util import get_broker_config

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s'
)

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class QueueConsumer:
    """ Consumes all messages from a specified AMQP queue using Kombu.
    """

    def __init__(self, queue_name: 'str') -> 'None':
        self.queue_name = queue_name
        self.message_count = 0
        self.connection = None
        self.should_stop = False

    def setup(self) -> 'None':
        """ Set up connection and queue.
        """
        logger.info('Setting up queue consumer for queue: %s', self.queue_name)

        # Get broker configuration
        broker_config = get_broker_config()

        # Log connection details
        connection_url = broker_config.to_url()
        logger.info('Broker config - address: %s', broker_config.address)
        logger.info('Broker config - username: %s', broker_config.username)
        logger.info('Broker config - password: %s', broker_config.password)
        logger.info('Broker config - vhost: %s', broker_config.vhost)
        logger.info('Broker config - protocol: %s', broker_config.protocol)
        logger.info('Connection URL: %s', connection_url)

        # Create connection with explicit parameters
        self.connection = Connection(
            hostname=broker_config.address.split(':')[0],
            port=int(broker_config.address.split(':')[1]),
            userid=broker_config.username,
            password=broker_config.password,
            virtual_host=broker_config.vhost,
            transport='pyamqp'
        )

        logger.info('Connection setup complete')

    def _on_message(self, body: 'any_', message: 'any_') -> 'None':
        """ Callback invoked when a message is received.
        """
        try:
            self.message_count += 1

            # Parse message body if it's JSON
            if isinstance(body, str):
                try:
                    parsed_body = loads(body)
                    logger.debug('Message %d: %s', self.message_count, parsed_body)
                except Exception:
                    logger.debug('Message %d (raw): %s', self.message_count, body)
            else:
                logger.debug('Message %d: %s', self.message_count, body)

            # Log message properties if available
            if hasattr(message, 'properties') and message.properties:
                properties = {}
                for prop in ['correlation_id', 'message_id', 'timestamp']:
                    if hasattr(message.properties, prop):
                        value = getattr(message.properties, prop)
                        if value:
                            properties[prop] = value
                if properties:
                    logger.debug('Message %d properties: %s', self.message_count, properties)

            # Log progress every 100 messages
            if self.message_count % 100 == 0:
                logger.info('Consumed %d message(s) so far', self.message_count)

            # Acknowledge the message
            message.ack()

        except Exception as e:
            logger.error('Error processing message %d: %s', self.message_count, e)
            logger.error('Exception details: %s', format_exc())
            # Still acknowledge to avoid redelivery
            message.ack()

    def start_consuming(self) -> 'None':
        """ Start consuming messages from the queue.
        """
        logger.info('Starting to consume messages from queue: %s', self.queue_name)

        try:
            with self.connection:
                # Create queue object - don't declare, just consume from existing queue
                queue = Queue(self.queue_name, no_declare=True)

                # Create consumer
                with self.connection.Consumer(queue, callbacks=[self._on_message]) as consumer:
                    logger.info('Consumer started, waiting for messages...')

                    # Keep consuming until interrupted
                    consecutive_timeouts = 0
                    max_consecutive_timeouts = 2

                    while not self.should_stop:
                        try:
                            self.connection.drain_events(timeout=1)
                            consecutive_timeouts = 0
                        except KeyboardInterrupt:
                            logger.info('Received interrupt signal, stopping consumer')
                            self.should_stop = True
                            break
                        except Exception as e:
                            if 'timed out' in str(e).lower():
                                consecutive_timeouts += 1
                                if consecutive_timeouts >= max_consecutive_timeouts:
                                    logger.info('No messages received for %d seconds, stopping consumer', max_consecutive_timeouts)
                                    self.should_stop = True
                                    break
                            else:
                                logger.debug('Drain events exception: %s', e)

        except OperationalError as e:
            logger.error('Connection error: %s', e)
        except Exception as e:
            logger.error('Error during message consumption: %s', e)
            logger.error('Exception details: %s', format_exc())
        finally:
            logger.info('=== CONSUMPTION SUMMARY ===')
            logger.info('Total messages consumed: %d', self.message_count)
            logger.info('Queue: %s', self.queue_name)

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':
    """ Main entry point.
    """
    parser = argparse.ArgumentParser(description='Consume all messages from a specified AMQP queue')
    parser.add_argument('queue_name', help='Name of the queue to consume from')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug('Debug logging enabled')

    logger.info('Starting queue consumer for queue: %s', args.queue_name)

    try:
        # Create and set up consumer
        consumer = QueueConsumer(args.queue_name)
        consumer.setup()

        # Start consuming
        consumer.start_consuming()

    except KeyboardInterrupt:
        logger.info('Interrupted by user')
    except Exception as e:
        logger.error('Fatal error: %s', e)
        logger.error('Exception details: %s', format_exc())
        sys.exit(1)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
