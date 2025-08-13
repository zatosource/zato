# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.pubsub.backend.common import Backend
from zato.common.pubsub.consumer import start_internal_consumer
from zato.common.pubsub.matcher import PatternMatcher
from zato.common.util.api import replace_secrets, spawn_greenlet

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.broker.client import BrokerClient
    from zato.common.pubsub.server.rest import PubSubRESTServer
    from zato.common.typing_ import strdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class RESTBackend(Backend):
    """ The consumer backend for the pub/sub REST server.
    """

    def __init__(self, rest_server:'PubSubRESTServer', broker_client:'BrokerClient') -> 'None':

        self.rest_server = rest_server
        super().__init__(broker_client)

        self.pattern_matcher = PatternMatcher()

# ################################################################################################################################

    def start_internal_pubusb_subscriber(self) -> 'None':
        _ = spawn_greenlet(
            start_internal_consumer,
            'zato.pubsub',
            'pubsub',
            'zato-pubsub',
            self._on_internal_message_callback
        )

# ################################################################################################################################

    def _remove_subscriptions_by_username(self, username:'str') -> 'list':
        """ Remove all subscriptions for a specific username and clean up empty topics.
        Returns list of topics that had subscriptions removed.
        """
        topics_to_clean = []

        for topic_name, subs_by_sec_name in self.subs_by_topic.items():
            if username in subs_by_sec_name:
                _ = subs_by_sec_name.pop(username, None)
                topics_to_clean.append(topic_name)

        # Clean up empty topic entries
        for topic_name in topics_to_clean:
            if not self.subs_by_topic[topic_name]:
                _ = self.subs_by_topic.pop(topic_name, None)

        return topics_to_clean

# ################################################################################################################################

    def _remove_subscriptions_by_sub_key(self, sub_key:'str') -> 'list':
        """ Remove subscriptions by sub_key and clean up empty topics.
        Returns list of topics that had subscriptions removed.
        """
        topics_to_clean = []

        for topic_name, subs_by_sec_name in self.subs_by_topic.items():
            for user_sec_name, subscription in list(subs_by_sec_name.items()):
                if subscription.sub_key == sub_key:
                    _ = subs_by_sec_name.pop(user_sec_name, None)
                    topics_to_clean.append(topic_name)
                    break

        # Clean up empty topic entries
        for topic_name in topics_to_clean:
            if not self.subs_by_topic[topic_name]:
                _ = self.subs_by_topic.pop(topic_name, None)

        return topics_to_clean

# ################################################################################################################################

    def on_broker_msg_PUBSUB_RELOAD_CONFIG(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']

        logger.info(f'[{cid}] Reloading pub/sub configuration')

        with self._main_lock:

            # Clear all in-memory structures
            self.topics.clear()
            self.subs_by_topic.clear()
            self.rest_server.users.clear()
            self.pattern_matcher.clear_cache()

            # Remove all clients from pattern matcher
            for client_id in list(self.pattern_matcher._clients.keys()):
                self.pattern_matcher.remove_client(client_id)

        # Reload everything as if server was starting
        self.rest_server.setup()

        logger.info(f'[{cid}] Configuration reload completed')

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_EDIT(self, msg:'strdict') -> 'None':

        # Local aliases
        new_topic_name:'str' = msg['new_topic_name']
        old_topic_name:'str' = msg['old_topic_name']

        # Move the topic in internal mappings
        if old_topic_name in self.topics:
            topic = self.topics.pop(old_topic_name)
            self.topics[new_topic_name] = topic

        # Move all subscriptions to the new topic name
        if old_topic_name in self.subs_by_topic:
            subs = self.subs_by_topic.pop(old_topic_name)
            self.subs_by_topic[new_topic_name] = subs

            # Update each subscription to point to the new topic
            for sub in subs.values():
                sub.topic_name = new_topic_name

        # Update permissions for all users in pattern matcher
        for username in self.rest_server.users:
            self.pattern_matcher.rename_topic(username, old_topic_name, new_topic_name)

        logger.info('Topic updated -> msg: %s', msg)

# ################################################################################################################################

    def on_broker_msg_SECURITY_BASIC_AUTH_CREATE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']
        username = msg['username']
        password = msg['password']

        # Reject empty passwords
        if not password:
            logger.warning(f'[{cid}] Rejecting user creation with empty password for `{username}`')
            return

        # Create the user now
        self.rest_server.create_user(cid, username, password)

        logger.info('HTTP Basic Auth created -> msg: %s', replace_secrets(msg))

# ################################################################################################################################

    def on_broker_msg_SECURITY_BASIC_AUTH_EDIT(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']

        has_sec_name_changed = msg['has_sec_name_changed']
        has_username_changed = msg['has_username_changed']

        old_sec_name = msg['old_sec_name']
        new_sec_name = msg['new_sec_name']

        old_username = msg['old_username']
        new_username = msg['new_username']

        # We go here if the username is different ..
        if has_username_changed:

            # .. log what we're doing ..
            logger.info(f'[{cid}] Updating username from `{old_username}` to `{new_username}`')

            # .. update the username in rest_server ..
            self.rest_server.change_username(cid, old_username, new_username)

            # .. and update the client ID in pattern_matcher ..
            self.pattern_matcher.change_client_id(old_username, new_username)

        # .. we go here if the name of the security definition is different ..
        if has_sec_name_changed:

            # .. log what we're doing ..
            logger.info(f'[{cid}] Updating sec_name from {old_sec_name} to {new_sec_name}')

            # .. and actually do it ..
            for topic_name, subs_by_sec_name in self.subs_by_topic.items():

                if old_sec_name in subs_by_sec_name:

                    # .. get the subscription object ..
                    subscription = subs_by_sec_name.pop(old_sec_name)

                    # .. update the sec_name within the subscription object ..
                    subscription.sec_name = new_sec_name

                    # .. store under the new sec_name ..
                    subs_by_sec_name[new_sec_name] = subscription

                    # .. and confirm we're done.
                    log_msg = f'[{cid}] Updated subscription for topic `{topic_name}` from `{old_sec_name}` to `{new_sec_name}`'
                    logger.info(log_msg)

        logger.info('HTTP Basic Auth updated -> msg: %s', msg)

# ################################################################################################################################

    def on_broker_msg_SECURITY_BASIC_AUTH_CHANGE_PASSWORD(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']
        username = msg['username']
        new_password = msg['password']

        # Reject empty passwords
        if not new_password:
            logger.warning(f'[{cid}] Rejecting password change to empty password for `{username}`')
            return

        # Update the password in the users dictionary
        if username in self.rest_server.users:
            self.rest_server.users[username] = new_password
            logger.info(f'[{cid}] Updated password for user `{username}`')
        else:
            logger.info(f'[{cid}] User not found for password change: `{username}`')

        logger.info('HTTP Basic Auth password changed -> msg: %s', replace_secrets(msg))

# ################################################################################################################################

    def on_broker_msg_SECURITY_BASIC_AUTH_DELETE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']
        username = msg['name']

        # Remove the user
        if username in self.rest_server.users:
            del self.rest_server.users[username]
            logger.info(f'[{cid}] Deleted user `{username}`')

            # Remove all permissions for this user
            self.pattern_matcher.remove_client(username)
            logger.info(f'[{cid}] Removed all permissions for deleted user `{username}`')

            # Remove all subscriptions for this user
            topics_to_clean = self._remove_subscriptions_by_username(username)

            if topics_to_clean:
                logger.info(f'[{cid}] Removed subscriptions for deleted user `{username}` from topics: {topics_to_clean}')

        else:
            logger.warning(f'[{cid}] User not found for deletion: `{username}`')

        logger.info('HTTP Basic Auth deleted -> msg: %s', msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_PERMISSION_CREATE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']
        pattern = msg['pattern']
        access_type = msg['access_type']
        username = msg['username']

        # Parse patterns (they can be multi-line)
        patterns = [elem.strip() for elem in pattern.splitlines() if elem.strip()]

        # Create permission list
        permissions = [{'pattern': elem, 'access_type': access_type} for elem in patterns]

        if username in self.rest_server.users:
            self.pattern_matcher.add_client(username, permissions)
            logger.info(f'[{cid}] Added {len(permissions)} permissions for {username}')
        else:
            logger.info(f'[{cid}] User not found for permission creation: {username}')

        logger.info('PubSub permission created -> msg: %s', msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_PERMISSION_EDIT(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']
        pattern = msg['pattern']
        access_type = msg['access_type']
        username = msg['username']

        # Parse patterns
        patterns = [elem.strip() for elem in pattern.splitlines() if elem.strip()]

        # Create permission list
        permissions = [{'pattern': elem, 'access_type': access_type} for elem in patterns]

        if username in self.rest_server.users:
            self.pattern_matcher.set_permissions(username, permissions)
            logger.info(f'[{cid}] Set {len(permissions)} permissions for {username}')
        else:
            logger.info(f'[{cid}] User not found for permission edit: {username}')

        logger.info('PubSub permission edited -> msg: %s', msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_PERMISSION_DELETE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']
        username = msg['username']

        if username in self.rest_server.users:
            self.pattern_matcher.remove_client(username)
            logger.info(f'[{cid}] Removed all permissions for {username}')
        else:
            logger.info(f'[{cid}] User not found for permission deletion: {username}')

        logger.info('PubSub permission deleted -> msg: %s', msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']
        sub_key = msg['sub_key']
        sec_name = msg['sec_name']
        topic_name_list = msg['topic_name_list']

        with self._main_lock:
            # Remove existing subscription by sub_key from all topics
            _ = self._remove_subscriptions_by_sub_key(sub_key)

        # Add subscription to new topics
        for topic_name in topic_name_list:
            _ = self.register_subscription(cid, topic_name, sec_name, {}, sub_key)

        logger.info(f'[{cid}] Updated subscription {sub_key} for {sec_name} to topics: {topic_name_list}')

# ################################################################################################################################
# ################################################################################################################################
