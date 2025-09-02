# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt
"""

# stdlib
from json import dumps
from logging import getLogger

# requests
import requests

# Zato
from zato.common.util.api import utcnow

# gevent
from gevent import sleep

# Zato
from zato.common.pubsub.perftest.python_.client import Client

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    from zato.common.pubsub.perftest.python_.progress_tracker import ProgressTracker

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Producer(Client):
    """ Producer client for publishing messages.
    """
    def __init__(self,
        progress_tracker:'ProgressTracker',
        reqs_per_producer:'int'=1,
        producer_id:'int'=0,
        reqs_per_second:'float'=1.0,
        max_topics:'int'=3
    ) -> 'None':

        super().__init__(progress_tracker, producer_id, reqs_per_second, max_topics)
        self.reqs_per_producer = reqs_per_producer

    def _get_config(self) -> 'anydict':
        """ Get configuration from environment variables.
        """
        config = super()._get_config()
        config['reqs_per_producer'] = self.reqs_per_producer
        return config

# ################################################################################################################################

    def _create_payload(self, topic_name:'str') -> 'anydict':
        """ Create message payload for publishing.
        """
        return {
            'data': {
                'message': f'Test message from Python client',
                'topic': topic_name,
            },
            'priority': 5,
            'expiration': 3600 * 1000,
        }

# ################################################################################################################################

    def _publish_message(self, url:'str', payload:'anydict', headers:'anydict', auth:'tuple') -> 'None':
        """ Publish a single message to the broker.
        """
        response = requests.post(url, data=dumps(payload), headers=headers, auth=auth)

        topic_name = payload['data']['topic']
        success = response.status_code == 200

        self.progress_tracker.update_progress(success)

        if not success:
            logger.error(f'Client {self.client_id}: Failed to publish to {topic_name}: {response.status_code} - {response.text}')

# ################################################################################################################################

    def start(self) -> 'None':
        """ Start the producer.
        """
        config = self._get_config()
        auth = (config['username'], config['password'])
        headers = {'Content-Type': 'application/json'}

        reqs_per_producer = config['reqs_per_producer']
        reqs_per_second = config['reqs_per_second']
        max_topics = config['max_topics']
        max_topics_range = max_topics + 1

        request_interval = 1.0 / reqs_per_second
        message_count = 0

        for _ in range(reqs_per_producer):
            for topic_num in range(1, max_topics_range):
                message_count += 1
                start_time = utcnow()

                topic_name = f'demo.{topic_num}'
                url = f'{config["base_url"]}/pubsub/topic/{topic_name}'
                payload = self._create_payload(topic_name)

                self._publish_message(url, payload, headers, auth)

                end_time = utcnow()
                time_diff = end_time - start_time
                elapsed_time = time_diff.total_seconds()
                sleep_time = request_interval - elapsed_time
                if sleep_time > 0:
                    sleep(sleep_time)

# ################################################################################################################################
# ################################################################################################################################
