# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt
"""

# stdlib
import os
import json
import time
from logging import getLogger
from traceback import format_exc

# requests
import requests
from requests.exceptions import ConnectionError

# gevent
from gevent import sleep

# prometheus
from prometheus_client import Counter, Histogram, push_to_gateway, CollectorRegistry

# Zato
from zato.common.pubsub.perftest.python_.client import Client
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, intnone
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
        max_messages:'int'=100,
        cpu_num:'intnone'=None,
        use_new_requests:'bool'=False
    ) -> 'None':

        super().__init__(progress_tracker, consumer_id, 1.0, 1, cpu_num, use_new_requests)
        self.pull_interval = pull_interval
        self.max_messages = max_messages

        # Prometheus metrics
        self.registry = CollectorRegistry()
        self.messages_consumed = Counter('zato_messages_consumed_total', 'Total messages consumed', ['consumer_id'], registry=self.registry)
        self.request_duration = Histogram('zato_consume_request_duration_seconds', 'Time spent on consume request', ['consumer_id'], registry=self.registry)

# ################################################################################################################################

    def _get_config(self) -> 'anydict':
        """ Get configuration from environment variables.
        """
        base_url = os.environ['Zato_Test_PubSub_OpenAPI_URL_Consumer']
        username = f'user.{self.client_id}'
        password = f'password.{self.client_id}'
        pull_interval = self.pull_interval

        return {
            'base_url': base_url,
            'username': username,
            'password': password,
            'pull_interval': pull_interval,
            'max_messages': self.max_messages,
        }

# ################################################################################################################################

    def _consume_messages(self, base_url:'str', headers:'anydict', auth:'tuple', max_messages:'int') -> 'None':
        """ Retrieve messages from user's queue.
        """
        url = f'{base_url}/pubsub/messages/get'
        payload = {'max_messages': max_messages}
        logger.debug(f'Client {self.client_id}: Attempting to consume messages')

        start_time = time.time()
        response = self.session.post(url, json=payload, headers=headers, auth=auth)
        duration = time.time() - start_time

        self.request_duration.labels(consumer_id=str(self.client_id)).observe(duration)

        success = response.status_code == 200

        if success:
            try:
                data = json.loads(response.text)
                messages = data.get('messages', [])
                message_count = len(messages)
                logger.debug(f'Client {self.client_id}: Retrieved {message_count} messages')

                self.messages_consumed.labels(consumer_id=str(self.client_id)).inc(message_count)
                self.progress_tracker.update_progress(True, message_count)

            except Exception as e:
                logger.error(f'Client {self.client_id}: Failed to parse response: {e}')
                self.progress_tracker.update_progress(False)
        else:
            logger.error(f'Client {self.client_id}: Failed to consume messages: {response.status_code} - {response.text}')
            self.progress_tracker.update_progress(False)

        push_to_gateway('server:9091', job=f'consumer_{self.client_id}', registry=self.registry)

# ################################################################################################################################

    def start(self) -> 'None':
        """ Start the consumer.
        """
        try:
            cpu_info = f' (CPU: {self.cpu_num})' if self.cpu_num is not None else ''
            logger.info(f'Client {self.client_id}: Consumer starting{cpu_info}')
            config = self._get_config()
            auth = (config['username'], config['password'])
            headers = {'Content-Type': 'application/json'}

            pull_interval = config['pull_interval']
            base_url = config['base_url']
            max_messages = config['max_messages']

            cycle_count = 0
            while True:
                cycle_count += 1
                start_time = utcnow()
                logger.debug(f'Client {self.client_id}: Starting pull cycle #{cycle_count}')

                try:
                    self._consume_messages(base_url, headers, auth, max_messages)
                except ConnectionError as e:
                    logger.error(f'Client {self.client_id}: Error in consume_messages: {e}')
                except Exception:
                    logger.error(f'Client {self.client_id}: Error in consume_messages: {format_exc()}')

                end_time = utcnow()
                time_diff = end_time - start_time
                elapsed_time = time_diff.total_seconds()
                sleep_time = pull_interval - elapsed_time
                logger.debug(f'Client {self.client_id}: Cycle #{cycle_count} took {elapsed_time:.3f}s, sleeping for {sleep_time:.2f}s')
                if sleep_time > 0:
                    sleep(sleep_time)

        except Exception:
            logger.error(f'Client {self.client_id}: Consumer crashed: {format_exc()}')
            raise

# ################################################################################################################################
# ################################################################################################################################
