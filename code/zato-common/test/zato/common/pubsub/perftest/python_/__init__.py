# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt
"""

# Must come first
from gevent.monkey import patch_all
_ = patch_all()

# stdlib
import logging
import os
from json import dumps
from logging import getLogger

# gevent
from gevent import sleep, spawn

# requests
import requests

# Zato
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

log_level = logging.INFO
log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=log_level, format=log_format)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Producer:
    """ Placeholder class for Producer instances.
    """
    def __init__(self, reqs_per_producer:'int'=1, producer_id:'int'=0, reqs_per_second:'float'=1.0, max_topics:'int'=3) -> 'None':
        self.reqs_per_producer = reqs_per_producer
        self.producer_id = producer_id
        self.reqs_per_second = reqs_per_second
        self.max_topics = max_topics

# ################################################################################################################################

    def _before_start(self) -> 'None':
        """ Called before starting the invoker.
        """
        pass

# ################################################################################################################################

    def _get_config(self) -> 'anydict':
        """ Get configuration from environment variables.
        """
        base_url = os.environ['Zato_Test_PubSub_OpenAPI_URL']
        username = os.environ['Zato_Test_PubSub_OpenAPI_Username']
        password = os.environ['Zato_Test_PubSub_OpenAPI_Password']
        reqs_per_producer = self.reqs_per_producer
        reqs_per_second = self.reqs_per_second
        max_topics = self.max_topics
        
        return {
            'base_url': base_url,
            'username': username,
            'password': password,
            'max_topics': max_topics,
            'reqs_per_producer': reqs_per_producer,
            'reqs_per_second': reqs_per_second,
        }

# ################################################################################################################################

    def _create_payload(self, topic_name:'str') -> 'anydict':
        """ Create message payload for publishing.
        """
        return {
            'data': {
                'message': f'Test message from Python invoker',
                'topic': topic_name,
            },
            'priority': 5,
            'expiration': 3600,
        }

# ################################################################################################################################

    def _publish_message(self, url:'str', payload:'anydict', headers:'anydict', auth:'tuple') -> 'None':
        """ Publish a single message to the broker.
        """
        response = requests.post(url, data=dumps(payload), headers=headers, auth=auth)

        topic_name = payload['data']['topic']
        if response.status_code == 200:
            pass
        else:
            logger.error(f'Producer {self.producer_id}: Failed to publish to {topic_name}: {response.status_code} - {response.text}')

# ################################################################################################################################

    def _start(self) -> 'None':
        """ Main invoker logic.
        """
        config = self._get_config()
        auth = (config['username'], config['password'])
        headers = {'Content-Type': 'application/json'}

        reqs_per_producer = config['reqs_per_producer']
        reqs_per_second = config['reqs_per_second']
        max_topics = config['max_topics']
        max_topics_range = max_topics + 1
        
        request_interval = 1.0 / reqs_per_second
        total_messages = reqs_per_producer * max_topics
        message_count = 0

        if total_messages < 1000:
            log_interval = 10
        else:
            log_interval = 50

        for _ in range(reqs_per_producer):
            for topic_num in range(1, max_topics_range):
                message_count += 1
                start_time = utcnow()

                topic_name = f'demo.{topic_num}'
                url = f'{config["base_url"]}/pubsub/topic/{topic_name}'
                payload = self._create_payload(topic_name)

                if message_count == 1 or message_count % log_interval == 0:
                    logger.info(f'Producer {self.producer_id}: Sending message {message_count}/{total_messages} to {topic_name} ({reqs_per_second} req/s)')
                self._publish_message(url, payload, headers, auth)

                end_time = utcnow()
                time_diff = end_time - start_time
                elapsed_time = time_diff.total_seconds()
                sleep_time = request_interval - elapsed_time
                if sleep_time > 0:
                    sleep(sleep_time)

# ################################################################################################################################

    def _after_start(self) -> 'None':
        """ Called after starting the invoker.
        """
        pass

# ################################################################################################################################

    def start(self) -> 'None':
        """ Start the invoker.
        """
        self._before_start()
        self._start()
        self._after_start()

# ################################################################################################################################
# ################################################################################################################################

class ProducerManager:
    """ Creates new instances of Producer class in greenlets.
    """

    def _start_producer(self, reqs_per_producer:'int', producer_id:'int', reqs_per_second:'float', max_topics:'int') -> 'any_':
        """ Creates a new Producer instance in a greenlet.
        """
        producer = Producer(reqs_per_producer, producer_id, reqs_per_second, max_topics)
        greenlet = spawn(producer.start)
        return greenlet

# ################################################################################################################################

    def run(self, num_producers:'int', reqs_per_producer:'int'=1, reqs_per_second:'float'=1.0, max_topics:'int'=3) -> 'None':
        """ Run the specified number of producers and wait for completion.
        """
        if num_producers == 1:
            noun = 'producer'
        else:
            noun = 'producers'

        logger.info(f'Starting {num_producers} {noun}')

        greenlets = []
        for producer_id in range(1, num_producers + 1):
            greenlet = self._start_producer(reqs_per_producer, producer_id, reqs_per_second, max_topics)
            greenlets.append(greenlet)

        # Wait for all greenlets to complete
        for greenlet in greenlets:
            greenlet.join()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import argparse

    parser = argparse.ArgumentParser(description='Producer Manager')
    _ = parser.add_argument('--num-producers', type=int, default=1, help='Number of producers to start')
    _ = parser.add_argument('--reqs-per-producer', type=int, default=1, help='Number of requests each producer should send')
    _ = parser.add_argument('--reqs-per-second', type=float, default=1.0, help='Number of requests per second each producer should make')
    _ = parser.add_argument('--max-topics', type=int, default=3, help='Number of topics to publish to')
    args = parser.parse_args()

    manager = ProducerManager()
    manager.run(args.num_producers, args.reqs_per_producer, args.reqs_per_second, args.max_topics)

# ################################################################################################################################
# ################################################################################################################################
