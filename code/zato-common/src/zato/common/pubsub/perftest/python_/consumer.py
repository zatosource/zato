# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt
"""

# stdlib
from json import loads
from logging import getLogger

# requests
import requests

# gevent
from gevent import sleep

# Zato
from zato.common.pubsub.perftest.python_.client import Client
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist
    from zato.common.pubsub.perftest.python_.progress_tracker import ProgressTracker

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Consumer(Client):
    """ Consumer client for retrieving messages.
    """
    def __init__(self,
        progress_tracker:'ProgressTracker',
        consumer_id:'int'=0,
        pull_interval:'float'=1.0,
        max_topics:'int'=3
    ) -> 'None':

        super().__init__(progress_tracker, consumer_id, 1.0, max_topics)
        self.pull_interval = pull_interval

    def _get_config(self) -> 'anydict':
        """ Get configuration from environment variables.
        """
        config = super()._get_config()
        config['pull_interval'] = self.pull_interval
        return config

# ################################################################################################################################

    def _consume_messages(self, base_url:'str', headers:'anydict', auth:'tuple', topic_num:'int') -> 'None':
        """ Retrieve messages from a single topic.
        """
        topic_name = f'demo.{topic_num}'
        url = f'{base_url}/pubsub/messages/get'
        payload = {'topic_name': topic_name}
        response = requests.post(url, json=payload, headers=headers, auth=auth)

        success = response.status_code == 200

        self.progress_tracker.update_progress(success)

        if success:
            try:
                data = loads(response.text)
                messages = data.get('messages', [])
                if messages:
                    logger.info(f'Client {self.client_id}: Retrieved {len(messages)} messages from {topic_name}')
            except Exception as e:
                logger.error(f'Client {self.client_id}: Failed to parse response from {topic_name}: {e}')
                self.progress_tracker.update_progress(False)
        else:
            logger.error(f'Client {self.client_id}: Failed to consume from {topic_name}: {response.status_code} - {response.text}')

# ################################################################################################################################

    def start(self) -> 'None':
        """ Start the consumer.
        """
        config = self._get_config()
        auth = (config['username'], config['password'])
        headers = {'Content-Type': 'application/json'}

        pull_interval = config['pull_interval']
        base_url = config['base_url']
        max_topics = config['max_topics']
        current_topic = 1

        while True:
            start_time = utcnow()

            self._consume_messages(base_url, headers, auth, current_topic)

            current_topic += 1
            if current_topic > max_topics:
                current_topic = 1

            end_time = utcnow()
            time_diff = end_time - start_time
            elapsed_time = time_diff.total_seconds()
            sleep_time = pull_interval - elapsed_time
            if sleep_time > 0:
                sleep(sleep_time)

# ################################################################################################################################
# ################################################################################################################################
