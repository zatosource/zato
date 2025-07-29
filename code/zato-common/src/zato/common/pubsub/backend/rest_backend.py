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
    from zato.common.pubsub.server import PubSubRESTServer
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

        logger.warning('222 on_broker_msg_SECURITY_BASIC_AUTH_CREATE')

        # Local aliases
        cid = msg['cid']
        sec_name = msg['sec_name']
        password = msg['password']

        # Create the user now
        self.rest_server.create_user(cid, sec_name, password)

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

            # .. and actually do it ..
            self.rest_server.change_username(cid, old_username, new_username)

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

        # Update the password in the users dictionary
        if username in self.rest_server.users:
            self.rest_server.users[username] = new_password
            logger.info(f'[{cid}] Updated password for user `{username}`')
        else:
            logger.info(f'[{cid}] User not found for password change: `{username}`')

        logger.info('HTTP Basic Auth password changed -> msg: %s', replace_secrets(msg))

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

        # Parse patterns
        patterns = [elem.strip() for elem in pattern.splitlines() if elem.strip()]

        # Create permission list
        permissions = [{'pattern': elem, 'access_type': access_type} for elem in patterns]

        # Update permissions for all existing users
        for username in self.rest_server.users:
            self.pattern_matcher.set_permissions(username, permissions)
            logger.info(f'[{cid}] Set {len(permissions)} permissions for {username}')

        logger.info('PubSub permission edited -> msg: %s', msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_PERMISSION_DELETE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']

        # Remove permissions for all existing users
        for username in self.rest_server.users:
            self.pattern_matcher.remove_client(username)
            logger.info(f'[{cid}] Removed all permissions for {username}')

        logger.info('PubSub permission deleted -> msg: %s', msg)

# ################################################################################################################################
# ################################################################################################################################
