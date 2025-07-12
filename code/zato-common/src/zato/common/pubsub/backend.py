# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from json import dumps
from logging import getLogger
from uuid import uuid4

# Zato
from zato.common.typing_ import strnone
from zato.common.util.api import utcnow

from zato.common.api import PubSub
from zato.common.util.api import new_cid, new_sub_key
from zato.common.pubsub.models import PubMessage, PubResponse, StatusResponse
from zato.common.pubsub.models import Subscription, Topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.broker.client import BrokerClient
    from zato.common.typing_ import dict_, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_prefix = PubSub.Prefix

# ################################################################################################################################
# ################################################################################################################################

subs_by_username = 'dict_[str, Subscription]' # username -> Subscription
topic_subs = 'dict_[str, subs_by_username]'   # topic_name -> {username -> Subscription}

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:
    Exchange_Name = 'pubsubapi'

# ################################################################################################################################
# ################################################################################################################################

def generate_msg_id() -> 'str':
    """ Generate a unique message ID with prefix.
    """
    return f'{_prefix.Msg_ID}{uuid4().hex}'

# ################################################################################################################################
# ################################################################################################################################

class Backend:
    """ Backend implementation of pub/sub, irrespective of the actual REST server.
    """
    topics: 'dict_[str, Topic]'
    subs_by_topic: 'topic_subs'

    def __init__(self, broker_client:'BrokerClient') -> 'None':
        self.broker_client = broker_client
        self.topics = {}
        self.subs_by_topic = {}

# ################################################################################################################################

    def create_topic(self, cid:'str', source:'str', topic_name:'str') -> 'None':

        topic = Topic()
        topic.name = topic_name

        self.topics[topic_name] = topic
        self.subs_by_topic[topic_name] = {}

        logger.info(f'[{cid}] Created new topic: {topic_name} ({source}')

# ################################################################################################################################

    def publish_impl(
        self,
        topic_name:'str',
        msg:'PubMessage',
        username:'str',
        ext_client_id:'strnone'=None
        ) -> 'PubResponse':
        """ Publish a message to a topic using the broker client.
        """
        cid = new_cid()
        logger.info(f'[{cid}] Publishing message to topic {topic_name} from {username}')

        # Create topic if it doesn't exist
        if topic_name not in self.topics:
            self.create_topic(cid, 'publish', topic_name)

        # Generate message ID and calculate size
        msg_id = generate_msg_id()
        data_str = dumps(msg.data) if not isinstance(msg.data, str) else msg.data
        size = len(data_str.encode('utf-8'))

        # Set timestamps
        now = utcnow()
        pub_time_iso = now.isoformat()
        expiration_time = now + timedelta(seconds=msg.expiration)
        expiration_time_iso = expiration_time.isoformat()

        # Create message object
        message = {
            'data': msg.data,
            'topic_name': topic_name,
            'msg_id': msg_id,
            'correl_id': msg.correl_id,
            'in_reply_to': msg.in_reply_to,
            'priority': msg.priority,
            'ext_client_id': msg.ext_client_id,
            'pub_time_iso': pub_time_iso,
            'recv_time_iso': pub_time_iso,  # Same as pub_time for direct API calls
            'expiration': msg.expiration,
            'expiration_time_iso': expiration_time_iso,
            'size': size,
            'delivery_count': 0,
            'publisher': username,
        }

        self.broker_client.publish(message, exchange=ModuleCtx.Exchange_Name, routing_key=topic_name)

        ext_client_part = f' -> {ext_client_id}' if ext_client_id else ''
        logger.info(f'[{cid}] Published message to topic {topic_name} ({username}{ext_client_part})')

        # Return success response
        response = PubResponse()
        response.is_ok = True
        response.msg_id = msg_id
        response.cid = cid

        return response

# ################################################################################################################################

    def subscribe_impl(
        self,
        topic_name:'str',
        username:'str'
        ) -> 'StatusResponse':
        """ Subscribe to a topic.
        """
        cid = new_cid()
        logger.info(f'[{cid}] Subscribing {username} to topic {topic_name}')

        # Create topic if it doesn't exist
        if topic_name not in self.topics:
            self.create_topic(cid, 'subscribe', topic_name)

        # Check if already subscribed
        if topic_name in self.subs_by_topic and username in self.subs_by_topic[topic_name]:
            logger.info(f'[{cid}] Endpoint {username} already subscribed to {topic_name}')
            response = StatusResponse()
            response.is_ok = True
            return response

        # Create subscription
        sub_key = new_sub_key()
        sub = Subscription()
        sub.topic_name = topic_name
        sub.username = username
        sub.sub_key = sub_key

        # Store subscription
        if topic_name not in self.subs_by_topic:
            self.subs_by_topic[topic_name] = {}

        subs_by_username = self.subs_by_topic[topic_name]
        subs_by_username[username] = sub

        # Register subscription with broker client
        self.broker_client.subscribe(topic_name, username, sub_key) # type: ignore
        logger.info(f'[{cid}] Successfully subscribed {username} to {topic_name} with key {sub_key}')

        response = StatusResponse()
        response.is_ok = True

        return response

# ################################################################################################################################

    def unsubscribe_impl(
        self,
        topic_name:'str',
        username:'str'
        ) -> 'StatusResponse':
        """ Unsubscribe from a topic.
        """
        cid = new_cid()
        logger.info(f'[{cid}] Unsubscribing {username} from topic {topic_name}')

        # Check if subscription exists
        if topic_name in self.subs_by_topic and username in self.subs_by_topic[topic_name]:

            # Local aliases
            subs_by_username = self.subs_by_topic[topic_name]
            sub:'Subscription' = subs_by_username[username]

            # Get subscription key before removing it
            sub_key = sub.sub_key

            # Remove the subscription from our metadata
            _ = subs_by_username.pop(username)

            # Unregister subscription with broker client
            self.broker_client.unsubscribe(topic_name, username, sub_key) # type: ignore

            logger.info(f'[{cid}] Successfully unsubscribed {username} from {topic_name}')
        else:
            logger.info(f'[{cid}] No subscription found for {username} to {topic_name}')

        response = StatusResponse()
        response.is_ok = True

        return response

# ################################################################################################################################
# ################################################################################################################################
