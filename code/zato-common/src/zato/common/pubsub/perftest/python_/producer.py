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
        max_topics:'int'=3,
        burst_multiplier:'int'=10,
        burst_duration:'int'=10,
        burst_interval:'int'=60
    ) -> 'None':

        super().__init__(progress_tracker, producer_id, reqs_per_second, max_topics)
        self.reqs_per_producer = reqs_per_producer
        self.burst_multiplier = burst_multiplier
        self.burst_duration = burst_duration
        self.burst_interval = burst_interval

    def _get_config(self) -> 'anydict':
        """ Get configuration from environment variables.
        """
        config = super()._get_config()
        config['reqs_per_producer'] = self.reqs_per_producer
        config['burst_multiplier'] = self.burst_multiplier
        config['burst_duration'] = self.burst_duration
        config['burst_interval'] = self.burst_interval
        return config

# ################################################################################################################################

    def _create_payload(self, topic_name:'str') -> 'anydict':
        """ Create message payload for publishing.
        """
        return {
            'data': {
                'message': {'msg':'Test message from Python client' * 250},
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
        burst_multiplier = config['burst_multiplier']
        burst_duration = config['burst_duration']
        burst_interval = config['burst_interval']

        normal_interval = 1.0 / reqs_per_second
        burst_interval_time = 1.0 / (reqs_per_second * burst_multiplier)

        start_time = utcnow()
        last_burst_time = start_time
        message_count = 0
        current_burst_status = False

        for _ in range(reqs_per_producer):
            for topic_num in range(1, max_topics_range):
                message_count += 1
                current_time = utcnow()

                # Check if we should start a burst
                time_since_last_burst = (current_time - last_burst_time).total_seconds()
                time_since_start = (current_time - start_time).total_seconds()

                is_burst_time = time_since_last_burst >= burst_interval
                is_in_burst = is_burst_time and (time_since_start % burst_interval) < burst_duration

                if is_burst_time and not is_in_burst:
                    last_burst_time = current_time
                    is_in_burst = True

                # Track burst status for timing only
                current_burst_status = is_in_burst

                request_start = utcnow()

                topic_name = f'demo.{topic_num}'
                url = f'{config["base_url"]}/pubsub/topic/{topic_name}'
                payload = self._create_payload(topic_name)

                self._publish_message(url, payload, headers, auth)

                request_end = utcnow()
                request_duration = (request_end - request_start).total_seconds()

                # Use appropriate interval based on burst mode
                target_interval = burst_interval_time if is_in_burst else normal_interval
                sleep_time = target_interval - request_duration

                if sleep_time > 0:
                    sleep(sleep_time)

# ################################################################################################################################
# ################################################################################################################################
