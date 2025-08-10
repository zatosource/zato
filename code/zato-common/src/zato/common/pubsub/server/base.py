# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Must come first
from gevent import monkey;
_ = monkey.patch_all()

# stdlib
from logging import getLogger

from traceback import format_exc



# Zato
from zato.common.typing_ import any_, dict_

# werkzeug
from werkzeug.routing import Map, Rule

# Zato
from zato.broker.client import BrokerClient
from zato.common.api import PubSub
from zato.common.util.api import new_cid, utcnow
from zato.common.pubsub.backend.rest_backend import RESTBackend
from zato.common.pubsub.util import get_username_to_sec_name_mapping

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default_priority = PubSub.Message.Default_Priority
_default_expiration = PubSub.Message.Default_Expiration

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Exchange_Name = 'pubsubapi'

# ################################################################################################################################
# ################################################################################################################################

class UnauthorizedException(Exception):
    def __init__(self, cid:'str', *args:'any_', **kwargs:'any_') -> 'None':
        self.cid = cid
        super().__init__(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

class BadRequestException(Exception):
    def __init__(self, cid:'str', message:'str', *args:'any_', **kwargs:'any_') -> 'None':
        self.cid = cid
        self.message = message
        super().__init__(*args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################



# ################################################################################################################################
# ################################################################################################################################

class BaseServer:

    def __init__(
        self,
        host:'str',
        port:'int',
        should_init_broker_client:'bool'=True,
    ) -> 'None':
        self.host = host
        self.port = port
        self.users = {}

        # Build our broker client
        self.broker_client = BrokerClient(consumer_drain_events_timeout=0.1)
        self.broker_client.ping_connection()

        # Initialize the backend
        self.backend = RESTBackend(self, self.broker_client)

        # Do start the broker client now
        if should_init_broker_client:
            self._init_broker_client()

        # Share references for backward compatibility and simpler access
        self.topics = self.backend.topics
        self.subs_by_topic = self.backend.subs_by_topic

        # URL routing configuration
        self.url_map = Map([

            #
            # Get messages for username
            #
            Rule('/pubsub/messages/get', endpoint='on_messages_get', methods=['POST']),

            #
            # Publish to topic
            #
            Rule('/pubsub/topic/<topic_name>', endpoint='on_publish', methods=['POST']),

            #
            # Subscribe
            #
            Rule('/pubsub/subscribe/topic/<topic_name>', endpoint='on_subscribe', methods=['POST']),

            #
            # Unsubscribe
            #
            Rule('/pubsub/unsubscribe/topic/<topic_name>', endpoint='on_unsubscribe', methods=['POST']),

            #
            # Ping endpoint
            #
            Rule('/pubsub/health', endpoint='on_health_check', methods=['GET']),

            #
            # Internal details
            #
            Rule('/pubsub/admin/diagnostics', endpoint='on_admin_diagnostics', methods=['GET']),
        ])

# ################################################################################################################################

    def _init_broker_client(self):

        # Delete the queue to remove any message we don't want to read since they were published when we were not running,
        # and then create it all again so we have a fresh start ..
        self.broker_client.delete_queue('pubsub')
        self.broker_client.create_internal_queue('pubsub')

        # .. and now, start our subscriber.
        self.backend.start_internal_pubusb_subscriber()

# ################################################################################################################################

    def _load_subscriptions(self, cid:'str') -> 'None':
        """ Load subscriptions from server and set up the pub/sub structure.
        """

        # Prepare our input ..
        service = 'zato.pubsub.subscription.get-list'
        request = {
            'cluster_id': 1,
            'needs_password': True
        }

        # .. invoke the service ..
        response = self.backend.invoke_service_with_pubsub(service, request)

        # .. log what we've received ..
        len_response = len(response)
        if len_response == 1:
            logger.info('Loading 1 subscription')
        elif len_response > 0:
            logger.info(f'Loading {len_response} subscriptions')
        else:
            logger.info('No subscriptions to load')

        # Get security definitions for username lookup
        username_to_sec_name = get_username_to_sec_name_mapping(self.backend)

        # .. process each subscription ..
        for item in response:

            try:
                # .. extract what we need ..
                username = item['username']
                password = item['password']
                topic_names = item.get('topic_name_list') or []
                sub_key = item['sub_key']

                # Add user credentials
                self.create_user(cid, username, password)

                # Handle multiple topics (comma-separated)
                for topic_name in topic_names:

                    topic_name = topic_name.strip()
                    if not topic_name:
                        continue

                    logger.info(f'[{cid}] Registering subscription: `{username}` -> `{topic_name}`')

                    # Create the subscription
                    _ = self.backend.register_subscription(cid, topic_name, username, username_to_sec_name, sub_key)

            except Exception:
                logger.error(f'[{cid}] Error processing subscription {item}: {format_exc()}')

        logger.info('Finished loading subscriptions')

# ################################################################################################################################

    def create_user(self, cid:'str', username:'str', password:'str') -> 'None':
        if username not in self.users:
            logger.info(f'[{cid}] Adding user credentials for `{username}`')
            self.users[username] = password
        else:
            logger.debug(f'[{cid}] User already exists: `{username}`')

# ################################################################################################################################

    def change_username(self, cid:'str', old_username:'str', new_username:'str') -> 'None':

        if old_username not in self.users:
            logger.info(f'[{cid}] User not found: `{old_username}`')
            return

        if new_username in self.users:
            logger.info(f'[{cid}] Cannot change username, target already exists: `{new_username}`')
            return

        # Store the password
        password = self.users[old_username]

        # Create the new user entry
        self.users[new_username] = password

        # Remove the old username
        del self.users[old_username]

        logger.info(f'[{cid}] Changed username from `{old_username}` to `{new_username}`')

# ################################################################################################################################

    def setup(self) -> 'None':
        """ Set up the server, loading users, topics, and subscriptions from YAML config.
        """
        cid = new_cid()

        # For later use ..
        start = utcnow()

        # .. load all the initial subscriptions ..
        self._load_subscriptions(cid)

        # .. we're going to need it in a moment ..
        end = utcnow()

        user_count = len(self.users)
        topic_count = len(self.backend.topics)
        subscription_count = sum(len(subs) for subs in self.backend.subs_by_topic.values())

        logger.info(f'[{cid}] ✅ Setup complete in {end - start}')
        logger.info(f'[{cid}] 🠊 {user_count} {"user" if user_count == 1 else "users"}')
        logger.info(f'[{cid}] 🠊 {topic_count} {"topic" if topic_count == 1 else "topics"}')
        logger.info(f'[{cid}] 🠊 {subscription_count} {"subscription" if subscription_count == 1 else "subscriptions"}')

# ################################################################################################################################
# ################################################################################################################################
