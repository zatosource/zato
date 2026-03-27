# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import BAD_REQUEST, OK, UNAUTHORIZED
from logging import getLogger

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.util import validate_topic_name
from zato.server.service import Int, Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_min_priority = PubSub.Message.Priority_Min
_max_priority = PubSub.Message.Priority_Max
_default_priority = PubSub.Message.Priority_Default
_default_expiration = PubSub.Message.Default_Expiration
_max_messages_default = 50
_max_len_default = 5_000_000

# ################################################################################################################################
# ################################################################################################################################

class Publish(Service):
    """ Publish a message to a topic.
    """
    name = 'pubsub.rest.publish'

    class SimpleIO:
        input_required = 'topic_name', 'data'
        input_optional = Int('priority'), Int('expiration'), 'correl_id', 'in_reply_to', 'ext_client_id', 'pub_time'
        output_optional = 'msg_id', 'is_ok', 'cid', 'status', 'details'

# ################################################################################################################################

    def handle(self) -> 'None':

        # Local aliases
        cid = self.cid
        input = self.request.input

        # Get authenticated username
        username = self.channel.security.username

        if not username:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = UNAUTHORIZED
            self.response.payload.details = 'Authentication required'
            return

        # Get topic name
        topic_name = input.topic_name

        # Validate topic name
        try:
            validate_topic_name(topic_name)
        except Exception as e:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = BAD_REQUEST
            self.response.payload.details = str(e)
            return

        # Check permissions
        permission_result = self.server.pubsub_pattern_matcher.evaluate(username, topic_name, 'publish')

        if not permission_result.is_ok:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = UNAUTHORIZED
            self.response.payload.details = 'Permission denied'
            return

        # Get message data
        data = input.data

        if data is None:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = BAD_REQUEST
            self.response.payload.details = "Invalid input: 'data' element missing"
            return

        # Get optional parameters
        priority = input.priority if input.priority is not None else _default_priority
        expiration = input.expiration if input.expiration is not None else _default_expiration
        correl_id = input.correl_id or cid
        in_reply_to = input.in_reply_to or ''
        ext_client_id = input.ext_client_id or ''

        # Validate priority
        if priority < _min_priority or priority > _max_priority:
            priority = _default_priority

        # Validate expiration
        expiration = round(expiration)
        if expiration < 1:
            expiration = 1

        # Publish to Redis
        msg_id = self.server.pubsub_redis.publish(
            topic_name,
            data,
            priority=priority,
            expiration=expiration,
            correl_id=correl_id,
            in_reply_to=in_reply_to,
            ext_client_id=ext_client_id,
            publisher=username,
        )

        # Build response
        self.response.payload.is_ok = True
        self.response.payload.cid = cid
        self.response.payload.msg_id = msg_id

# ################################################################################################################################
# ################################################################################################################################

class GetMessages(Service):
    """ Retrieve messages for the authenticated user.
    """
    name = 'pubsub.rest.get-messages'

    class SimpleIO:
        input_optional = Int('max_messages'), Int('max_len')
        output_optional = 'messages', Int('message_count'), 'is_ok', 'cid', 'status', 'details'

# ################################################################################################################################

    def handle(self) -> 'None':

        # Local aliases
        cid = self.cid
        input = self.request.input

        # Get authenticated username
        username = self.channel.security.username

        if not username:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = UNAUTHORIZED
            self.response.payload.details = 'Authentication required'
            return

        # Get sub_key for this user
        sub_key = self._get_sub_key_for_user(username)

        if not sub_key:
            self.response.payload.is_ok = True
            self.response.payload.cid = cid
            self.response.payload.messages = []
            self.response.payload.message_count = 0
            return

        # Get optional parameters
        max_messages = input.max_messages if input.max_messages is not None else _max_messages_default
        max_len = input.max_len if input.max_len is not None else _max_len_default

        # Fetch messages from Redis
        messages = self.server.pubsub_redis.fetch_messages(
            sub_key,
            max_messages=max_messages,
            max_len=max_len
        )

        # Build response
        self.response.payload.is_ok = True
        self.response.payload.cid = cid
        self.response.payload.messages = messages
        self.response.payload.message_count = len(messages)

# ################################################################################################################################

    def _get_sub_key_for_user(self, username:'str') -> 'str':
        """ Get the subscription key for a user.
        """
        # Look up in the subscriptions store
        return self.server.pubsub_subscriptions.get_sub_key_by_username(username)

# ################################################################################################################################
# ################################################################################################################################

class Subscribe(Service):
    """ Subscribe to a topic.
    """
    name = 'pubsub.rest.subscribe'

    class SimpleIO:
        input_required = 'topic_name'
        output_optional = 'is_ok', 'cid', 'status', 'details', 'sub_key'

# ################################################################################################################################

    def handle(self) -> 'None':

        # Local aliases
        cid = self.cid
        input = self.request.input

        # Get authenticated username
        username = self.channel.security.username

        if not username:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = UNAUTHORIZED
            self.response.payload.details = 'Authentication required'
            return

        # Get topic name
        topic_name = input.topic_name

        # Validate topic name
        try:
            validate_topic_name(topic_name)
        except Exception as e:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = BAD_REQUEST
            self.response.payload.details = str(e)
            return

        # Check permissions
        permission_result = self.server.pubsub_pattern_matcher.evaluate(username, topic_name, 'subscribe')

        if not permission_result.is_ok:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = UNAUTHORIZED
            self.response.payload.details = 'Permission denied'
            return

        # Get or create sub_key for this user
        sub_key = self.server.pubsub_subscriptions.get_or_create_sub_key(username)

        # Subscribe in Redis
        self.server.pubsub_redis.subscribe(sub_key, topic_name)

        # Persist subscription in ODB
        self._persist_subscription(username, topic_name, sub_key)

        # Build response
        self.response.payload.is_ok = True
        self.response.payload.cid = cid
        self.response.payload.sub_key = sub_key

# ################################################################################################################################

    def _persist_subscription(self, username:'str', topic_name:'str', sub_key:'str') -> 'None':
        """ Persist subscription to ODB.
        """
        request = {
            'sub_key': sub_key,
            'topic_name_list': [topic_name],
            'sec_name': self._get_sec_name(username),
            'is_delivery_active': True,
            'is_pub_active': True,
            'delivery_type': PubSub.Delivery_Type.Pull,
        }
        _ = self.invoke('zato.pubsub.subscription.subscribe', request)

# ################################################################################################################################

    def _get_sec_name(self, username:'str') -> 'str':
        """ Get security definition name for username.
        """
        return self.server.pubsub_subscriptions.get_sec_name_by_username(username)

# ################################################################################################################################
# ################################################################################################################################

class Unsubscribe(Service):
    """ Unsubscribe from a topic.
    """
    name = 'pubsub.rest.unsubscribe'

    class SimpleIO:
        input_required = 'topic_name'
        output_optional = 'is_ok', 'cid', 'status', 'details'

# ################################################################################################################################

    def handle(self) -> 'None':

        # Local aliases
        cid = self.cid
        input = self.request.input

        # Get authenticated username
        username = self.channel.security.username

        if not username:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = UNAUTHORIZED
            self.response.payload.details = 'Authentication required'
            return

        # Get topic name
        topic_name = input.topic_name

        # Validate topic name
        try:
            validate_topic_name(topic_name)
        except Exception as e:
            self.response.payload.is_ok = False
            self.response.payload.cid = cid
            self.response.payload.status = BAD_REQUEST
            self.response.payload.details = str(e)
            return

        # Get sub_key for this user
        sub_key = self.server.pubsub_subscriptions.get_sub_key_by_username(username)

        if not sub_key:
            # User has no subscriptions, return success (idempotent)
            self.response.payload.is_ok = True
            self.response.payload.cid = cid
            return

        # Unsubscribe in Redis
        self.server.pubsub_redis.unsubscribe(sub_key, topic_name)

        # Remove subscription from ODB
        self._remove_subscription(username, topic_name)

        # Build response
        self.response.payload.is_ok = True
        self.response.payload.cid = cid

# ################################################################################################################################

    def _remove_subscription(self, username:'str', topic_name:'str') -> 'None':
        """ Remove subscription from ODB.
        """
        request = {
            'sec_name': self._get_sec_name(username),
            'username': username,
            'topic_name_list': [topic_name],
        }
        _ = self.invoke('zato.pubsub.subscription.unsubscribe', request)

# ################################################################################################################################

    def _get_sec_name(self, username:'str') -> 'str':
        """ Get security definition name for username.
        """
        return self.server.pubsub_subscriptions.get_sec_name_by_username(username)

# ################################################################################################################################
# ################################################################################################################################
