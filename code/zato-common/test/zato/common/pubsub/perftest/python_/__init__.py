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
from gevent import spawn

# requests
import requests

# ################################################################################################################################
# ################################################################################################################################

log_level = logging.INFO
log_format = '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s'
logging.basicConfig(level=log_level, format=log_format)

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Invoker:
    """ Placeholder class for Invoker instances.
    """
    def __init__(self) -> 'None':
        pass

# ################################################################################################################################

    def _before_start(self) -> 'None':
        """ Called before starting the invoker.
        """
        pass

# ################################################################################################################################

    def _get_config(self) -> 'dict':
        """ Get configuration from environment variables.
        """
        return {
            'base_url': os.environ['Zato_Test_PubSub_OpenAPI_URL'],
            'username': os.environ['Zato_Test_PubSub_OpenAPI_Username'],
            'password': os.environ['Zato_Test_PubSub_OpenAPI_Password'],
            'max_topics': int(os.environ['Zato_Test_PubSub_OpenAPI_Max_Topics']),
        }

# ################################################################################################################################

    def _create_payload(self, topic_name: 'str') -> 'dict':
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

    def _publish_message(self, url: 'str', payload: 'dict', headers: 'dict', auth: 'tuple') -> 'None':
        """ Publish a single message to the broker.
        """
        response = requests.post(url, data=dumps(payload), headers=headers, auth=auth)

        topic_name = payload['data']['topic']
        if response.status_code == 200:
            logger.info(f'Published message to {topic_name}')
        else:
            logger.error(f'Failed to publish to {topic_name}: {response.status_code} - {response.text}')

# ################################################################################################################################

    def _start(self) -> 'None':
        """ Main invoker logic.
        """
        config = self._get_config()
        auth = (config['username'], config['password'])
        headers = {'Content-Type': 'application/json'}

        for topic_num in range(1, config['max_topics'] + 1):
            topic_name = f'demo.{topic_num}'
            url = f'{config["base_url"]}/pubsub/topic/{topic_name}'
            payload = self._create_payload(topic_name)

            self._publish_message(url, payload, headers, auth)

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

class InvokerManager:
    """ Creates new instances of Invoker class in greenlets.
    """

    def _start_invoker(self) -> 'any_':
        """ Creates a new Invoker instance in a greenlet.
        """
        invoker = Invoker()
        _ = spawn(invoker.start)

# ################################################################################################################################

    def run(self, num_invokers: 'int') -> 'None':
        """ Run the specified number of invokers and wait for completion.
        """
        if num_invokers == 1:
            noun = 'invoker'
        else:
            noun = 'invokers'

        logger.info(f'Starting {num_invokers} {noun}')

        greenlets = []
        for _ in range(num_invokers):
            greenlet = self._start_invoker()
            greenlets.append(greenlet)

        # Wait for all greenlets to complete
        for greenlet in greenlets:
            greenlet.join()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import argparse

    parser = argparse.ArgumentParser(description='Invoker Manager')
    _ = parser.add_argument('--num-invokers', type=int, default=1, help='Number of invokers to start')
    _ = parser.add_argument('--reqs-per-invoker', type=int, default=1, help='Number of requests each invoker should send')
    _ = parser.add_argument('--reqs-per-second', type=float, default=1.0, help='Number of requests per second each invoker should make')
    args = parser.parse_args()

    manager = InvokerManager()
    manager.run(args.num_invokers)

# ################################################################################################################################
# ################################################################################################################################
