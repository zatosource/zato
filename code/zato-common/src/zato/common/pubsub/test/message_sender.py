# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey
_ = monkey.patch_all()

# stdlib
from datetime import datetime
from dataclasses import dataclass
from logging import getLogger
from time import sleep
import random
import uuid
from traceback import format_exc
from urllib.parse import urljoin

# Bunch
from bunch import bunchify

# gevent
import gevent
from gevent.lock import RLock
from gevent.pool import Pool

# PyYAML
from yaml import safe_load as yaml_load

# requests
import requests

# Zato
from zato.common.api import PubSub
from zato.common.util.api import get_absolute_path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strdict

# ################################################################################################################################
# ################################################################################################################################

_default_port_publish = PubSub.REST_Server.Default_Port_Publish

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ClientConfig:
    """ Client configuration parameters.
    """
    server_url:'str' = f'http://127.0.0.1:{_default_port_publish}/pubsub/topic/'
    request_timeout:'int' = 30
    retry_count:'int' = 3

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MessagingConfig:
    """ Configuration for message sending.
    """
    users_yaml_path:'str' = ''
    messages_per_topic_per_user:'int' = 10
    max_concurrent_publishers:'int' = 50
    max_send_rate:'int' = 1000
    send_interval:'float' = 0.01

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ContentConfig:
    """ Configuration for message content.
    """
    template_path:'str' = ''
    min_size:'int' = 1024
    max_size:'int' = 4096
    complexity:'str' = 'medium'  # simple, medium, complex

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SenderConfig:
    """ Overall sender configuration.
    """
    client:'ClientConfig'
    messaging:'MessagingConfig'
    content:'ContentConfig'

# ################################################################################################################################
# ################################################################################################################################

def load_config(config_file:'str') -> 'SenderConfig':
    """ Load configuration from YAML file.
    """
    try:
        with open(config_file, 'r') as f:
            config_dict = yaml_load(f)

        config_dict = bunchify(config_dict)

        # Extract configuration sections
        client_dict = config_dict.client
        messaging_dict = config_dict.messaging
        content_dict = config_dict.content

        client_config = ClientConfig()
        client_config.server_url = client_dict.server_url
        client_config.request_timeout = client_dict.request_timeout
        client_config.retry_count = client_dict.retry_count

        messaging_config = MessagingConfig()
        messaging_config.users_yaml_path = messaging_dict.users_yaml_path
        messaging_config.messages_per_topic_per_user = messaging_dict.messages_per_topic_per_user
        messaging_config.max_concurrent_publishers = messaging_dict.max_concurrent_publishers
        messaging_config.max_send_rate = messaging_dict.max_send_rate
        messaging_config.send_interval = messaging_dict.send_interval

        content_config = ContentConfig()
        content_config.template_path = content_dict.template_path
        content_config.min_size = content_dict.min_size
        content_config.max_size = content_dict.max_size
        content_config.complexity = content_dict.complexity

        sender_config = SenderConfig()
        sender_config.client = client_config
        sender_config.messaging = messaging_config
        sender_config.content = content_config

        return sender_config

    except Exception as e:
        logger.error(f'Error loading configuration from {config_file}: {e}')
        # Create default configuration with init=False
        sender_config = SenderConfig()
        sender_config.client = ClientConfig()
        sender_config.messaging = MessagingConfig()
        sender_config.content = ContentConfig()
        return sender_config

# ################################################################################################################################
# ################################################################################################################################

class UsersYAMLParser:
    """ Parser for users.yaml PubSub configuration.
    """
    data:'strdict'

    def __init__(self, users_yaml_path: str) -> None:
        self.users_yaml_path = users_yaml_path
        self._load_yaml()

    def _load_yaml(self) -> 'None':
        """ Load the YAML file from disk.
        """
        with open(self.users_yaml_path, 'r') as f:
            data = yaml_load(f)

        self.data = bunchify(data)

    def get_users(self) -> 'list[str]':
        """ Get list of all users.
        """
        return list(self.data.users)

    def get_topics(self) -> 'list[str]':
        """ Get list of all topics.
        """
        return list(self.data.topics)

    def get_user_credentials(self, username:'str') -> 'str':
        """ Get password for a user.
        """
        return self.data.users[username]

# ################################################################################################################################
# ################################################################################################################################

class MessageSender:
    """ Sends messages to the REST PubSub server.
    """
    def __init__(self, config_path:'str') -> 'None':
        """ Initialize the sender with configuration.
        """
        self.config = load_config(config_path)
        self.lock = RLock()
        self.sent_messages = 0
        self.failed_messages = 0
        self.start_time = None
        self.end_time = None
        self.publisher_stats = {}
        self.topic_stats = {}
        self.error_list = []
        self.users_parser = None
        self.session = requests.Session()

        # We need to make it absolute
        self.config.messaging.users_yaml_path = get_absolute_path(__file__, self.config.messaging.users_yaml_path)

        self.users_parser = UsersYAMLParser(self.config.messaging.users_yaml_path)

    def _generate_message_content(self, publisher:'str', topic:'str', message_index:'int') -> 'strdict':
        """ Generate message content based on configuration.
        """
        min_size = self.config.content.min_size
        max_size = self.config.content.max_size

        # Base message structure
        message = bunchify({
            'timestamp': datetime.now().isoformat(),
            'publisher_id': publisher,
            'message_index': message_index,
            'topic_name': topic,
            'message_id': f'msg-{publisher}-{topic}-{uuid.uuid4()}',
            'metadata': {
                'source':'pubsub_test_client',
                'version':'1.0'
            }
        })

        # Generate payload with lorem ipsum
        lorem_base = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec a diam lectus. Sed sit amet ipsum mauris. ' + \
                   'Maecenas congue ligula ac quam viverra nec consectetur ante hendrerit. Donec et mollis dolor. ' + \
                   'Praesent et diam eget libero egestas mattis sit amet vitae augue.'

        # Calculate needed size within min/max bounds
        desired_size = random.randint(min_size, max_size)

        # Calculate number of repetitions needed
        repetitions = (desired_size // len(lorem_base)) + 1

        # Generate the text by repeating lorem ipsum
        message.data = (lorem_base * repetitions)[:desired_size]

        return message

    def send_message(self, publisher:'str', topic:'str', content:'any_') -> 'bool':
        """ Send a single message to the PubSub server.
        """
        if self.users_parser is None:
            logger.error('Users YAML parser not initialized')
            return False

        # Get credentials for publisher
        password = self.users_parser.get_user_credentials(publisher)
        if not password:
            logger.error(f'No credentials found for publisher {publisher}')
            return False

        # Prepare the URL
        url = urljoin(self.config.client.server_url, topic)

        # Prepare the message payload
        payload = {
            'data': content,
            'ext_client_id': f'test-client-{publisher}',
            'priority': random.randint(1, 9),
            'expiration': random.randint(3600, 7200),
            'correl_id': f'corr-{uuid.uuid4()}'
        }

        # Try to send with retries
        for attempt in range(self.config.client.retry_count + 1):
            try:
                response = self.session.post(
                    url,
                    json=payload,
                    auth=(publisher, password),
                    timeout=self.config.client.request_timeout
                )

                if response.status_code == 200:
                    with self.lock:
                        self.sent_messages += 1

                        # Update publisher stats
                        if publisher not in self.publisher_stats:
                            self.publisher_stats[publisher] = bunchify({
                                'sent': 0,
                                'failed': 0,
                                'topics': {}
                            })

                        self.publisher_stats[publisher].sent += 1

                        if topic not in self.publisher_stats[publisher].topics:
                            self.publisher_stats[publisher].topics[topic] = 0
                        self.publisher_stats[publisher].topics[topic] += 1

                        # Update topic stats
                        if topic not in self.topic_stats:
                            self.topic_stats[topic] = bunchify({
                                'sent': 0,
                                'failed': 0
                            })

                        self.topic_stats[topic].sent += 1

                    return True
                else:
                    logger.warning(f'Failed to send message, status code: {response.status_code}, response: {response.text}')

                    # If this was the last attempt, record it as a failure
                    if attempt == self.config.client.retry_count:
                        self._record_failure(publisher, topic, f'HTTP error {response.status_code}: {response.text}')
                    else:
                        sleep(0.5 * (attempt + 1))  # Exponential backoff

            except Exception as e:
                logger.warning(f'Error sending message: {format_exc()}')

                # If this was the last attempt, record it as a failure
                if attempt == self.config.client.retry_count:
                    self._record_failure(publisher, topic, f'Exception: {str(e)}')
                else:
                    sleep(0.5 * (attempt + 1))  # Exponential backoff

        return False

    def _record_failure(self, publisher:'str', topic:'str', error:'str') -> 'None':
        """ Record a message sending failure.
        """
        with self.lock:
            self.failed_messages += 1

            # Update publisher stats
            if publisher not in self.publisher_stats:
                self.publisher_stats[publisher] = {'sent': 0, 'failed': 0, 'topics': {}}
            self.publisher_stats[publisher].failed += 1

            # Update topic stats
            if topic not in self.topic_stats:
                self.topic_stats[topic] = {'sent': 0, 'failed': 0}
            self.topic_stats[topic].failed += 1

            # Add to error list
            self.error_list.append({
                'publisher': publisher,
                'topic': topic,
                'error': error,
                'time': datetime.now().isoformat()
            })

    def _publisher_worker(self, publisher:'str', topic:'str', message_count:'int') -> 'None':
        """ Worker function to be run in a greenlet for each publisher-topic pair.
        """
        logger.info(f'Starting publisher worker for {publisher} -> {topic}, sending {message_count} messages')

        for idx in range(message_count):
            # Generate message content
            content = self._generate_message_content(publisher, topic, idx)

            # Send the message
            _ = self.send_message(publisher, topic, content)

            # Rate limiting
            gevent.sleep(self.config.messaging.send_interval)

    def start(self) -> 'strdict':
        """ Start sending messages based on the users.yaml configuration.
        """
        if self.users_parser is None:
            logger.error('Users YAML parser not initialized')
            return {'status':'error', 'message':'Users YAML parser not initialized'}

        self.start_time = datetime.now()
        logger.info(f'Starting message sender at {self.start_time.isoformat()}')

        # Get users and topics
        users = self.users_parser.get_users()
        topics = self.users_parser.get_topics()

        messages_per_user_topic = self.config.messaging.messages_per_topic_per_user

        # Create a pool for greenlets
        pool = Pool(self.config.messaging.max_concurrent_publishers)

        # Spawn greenlets for each publisher-topic pair
        for publisher in users:
            for topic in topics:
                _ = pool.spawn(self._publisher_worker, publisher, topic, messages_per_user_topic)

        # Wait for all greenlets to complete
        _ = pool.join()

        # Record end time
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        # Calculate rate
        rate = self.sent_messages / duration if duration > 0 else 0

        logger.info(f'Message sending complete. Sent {self.sent_messages} messages in {duration:.2f} seconds ({rate:.2f} msgs/sec)')

        # Return statistics
        return {
            'summary': {
                'total_sent': self.sent_messages,
                'failed': self.failed_messages,
                'duration_seconds': duration,
                'rate_per_second': rate,
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat()
            },
            'publishers': self.publisher_stats,
            'topics': self.topic_stats,
            'errors': self.error_list[:100]  # Limit to first 100 errors
        }

# ################################################################################################################################
# ################################################################################################################################
