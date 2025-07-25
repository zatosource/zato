# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from json import dumps
from logging import getLogger
from traceback import format_exc
from uuid import uuid4

# gevent
from gevent.lock import RLock

# Zato
from zato.broker.message_handler import handle_broker_msg
from zato.common.api import PubSub
from zato.common.pubsub.models import PubMessage, PubResponse, StatusResponse, Subscription, Topic
from zato.common.util.api import new_sub_key, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kombu.transport.pyamqp import Message as KombuMessage
    from zato.broker.client import BrokerClient
    from zato.common.typing_ import any_, anydictnone, dict_, strdict, strlist, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_prefix = PubSub.Prefix

# ################################################################################################################################
# ################################################################################################################################

subs_by_sec_name = 'dict_[str, Subscription]' # sec_name -> Subscription
topic_subs = 'dict_[str, subs_by_sec_name]'   # topic_name -> {sec_name -> Subscription}

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
    """ Backend implementation of pub/sub, irrespective of the actual server using it (REST pub/sub vs. Parallel).
    """
    topics: 'dict_[str, Topic]' # Maps topic_name to a Topic object
    subs_by_topic: 'topic_subs'

    def __init__(self,broker_client:'BrokerClient') -> 'None':

        self.broker_client = broker_client
        self.topics = {}
        self.subs_by_topic = {}
        self._main_lock = RLock()

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid:'str' = msg['cid']
        sub_key:'str' = msg['sub_key']
        sec_name:'str' = msg['sec_name']
        topic_name_list:'strlist' = msg['topic_name_list']

        # Process each topic in the list
        for topic_name in topic_name_list:
            _ = self.register_subscription(cid, topic_name, sec_name, sub_key)

        # Log all subscribed topics
        topic_name_list_human = ', '.join(topic_name_list)
        log_msg = f'[{cid}] Successfully subscribed {sec_name} to topics: {topic_name_list_human} with key {sub_key}'
        logger.info(log_msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_DELETE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid:'str' = msg['cid']
        topic_name:'str' = msg['topic_name']

        logger.info(f'[{cid}] Deleting topic {topic_name}')

        # Check if topic exists
        if topic_name not in self.topics:
            logger.warning(f'[{cid}] Topic {topic_name} not found, cannot delete')
            return

        # Get all subscriptions to this topic
        subs_by_sec_name = self.subs_by_topic.get(topic_name, {})

        # If there are any subscriptions, we need to unsubscribe them
        if subs_by_sec_name:
            logger.info(f'[{cid}] Unsubscribing {len(subs_by_sec_name)} users from topic {topic_name}')

            # Create a copy to avoid modification during iteration
            sec_names = list(subs_by_sec_name.keys())

            # Unsubscribe each user
            for sec_name in sec_names:
                _ = self.unregister_subscription(cid, topic_name, sec_name)

        # Remove the topic from our mappings
        _ = self.topics.pop(topic_name)
        _ = self.subs_by_topic.pop(topic_name, None)

        logger.info(f'[{cid}] Successfully deleted topic {topic_name}')

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']
        sub_key = msg['sub_key']
        sec_name = msg['sec_name']

        logger.info(f'[{cid}] Processing delete for sub_key={sub_key}, sec_name={sec_name}')

        # Find all topics this user is subscribed to with this sub_key
        topics_to_unsubscribe = []
        for topic_name, subscriptions_by_sec_name in self.subs_by_topic.items():
            if sec_name in subscriptions_by_sec_name:
                subscription = subscriptions_by_sec_name[sec_name]
                if subscription.sub_key == sub_key:
                    topics_to_unsubscribe.append(topic_name)

        # If we didn't find any matching subscriptions
        if not topics_to_unsubscribe:
            logger.info(f'[{cid}] No subscriptions found for {sec_name} with key {sub_key}')
            return

        # Unsubscribe from each topic
        for topic_name in topics_to_unsubscribe:
            _ = self.unregister_subscription(cid, topic_name, sec_name, sub_key=sub_key)

# ################################################################################################################################

    def _on_internal_message_callback(self, body:'strdict', msg:'KombuMessage', name:'str', config:'strdict') -> 'None':

        # Invoke the callback for this message ..
        try:
            _ = handle_broker_msg(body, self)
        except Exception:
            logger.warning('Exception when calling handle_broker_msg: %s', format_exc())
        finally:
            # .. these are configuration messages so we always need to acknowledge them.
            msg.ack()

# ################################################################################################################################

    def invoke_service_with_pubsub(
        self,
        service:'str',
        request:'anydictnone'=None,
        timeout:'int'=20,
        needs_root_elem:'bool'=False,
    ) -> 'any_':
        response = self.broker_client.invoke_sync(service, request, timeout, needs_root_elem)
        return response

# ################################################################################################################################

    def create_topic(self, cid:'str', source:'str', topic_name:'str') -> 'None':

        topic = Topic()
        topic.name = topic_name

        self.topics[topic_name] = topic
        self.subs_by_topic[topic_name] = {}

        logger.info(f'[{cid}] Created new topic: {topic_name} ({source})')

# ################################################################################################################################

    def publish_impl(
        self,
        cid: 'str',
        topic_name:'str',
        msg:'PubMessage',
        sec_name:'str',
        ext_client_id:'strnone'=None
        ) -> 'PubResponse':
        """ Publish a message to a topic using the broker client.
        """
        logger.info(f'[{cid}] Publishing message to topic {topic_name} from {sec_name}')

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
            'publisher': sec_name,
        }

        self.broker_client.publish(message, exchange=ModuleCtx.Exchange_Name, routing_key=topic_name)

        ext_client_part = f' -> {ext_client_id}' if ext_client_id else ''
        logger.info(f'[{cid}] Published message to topic {topic_name} (sec_name={sec_name} -> {ext_client_part})')

        # Return success response
        response = PubResponse()
        response.is_ok = True
        response.msg_id = msg_id
        response.cid = cid

        return response

# ################################################################################################################################

    def register_subscription(
        self,
        cid: 'str',
        topic_name: 'str',
        sec_name: 'str',
        sub_key: 'str'='',
        ) -> 'StatusResponse':
        """ Subscribe to a topic.
        """

        # This is optional and will be empty if it's an external subscription (e.g. via REST)
        sub_key = sub_key or new_sub_key(sec_name)

        logger.info(f'[{cid}] Subscribing {sec_name} to topic {topic_name} (sk={sub_key})')

        # Create topic if it doesn't exist ..
        with self._main_lock:
            if topic_name not in self.topics:
                self.create_topic(cid, 'subscribe', topic_name)

        # .. create a new subscription ..
        sub = Subscription()
        sub.topic_name = topic_name
        sub.sec_name = sec_name
        sub.sub_key = sub_key
        sub.creation_time = utcnow()

        # .. get or create a dict with subscriptions for users ..
        subs_by_sec_name = self.subs_by_topic.setdefault(topic_name, {})

        # .. now add it for that user ..
        subs_by_sec_name[sec_name] = sub

        # .. build our response ..
        response = StatusResponse()
        response.is_ok = True

        # .. and return it to our caller.
        return response

# ################################################################################################################################

    def unregister_subscription(
        self,
        cid: 'str',
        topic_name:'str',
        username:'str',
        *,
        sub_key:'strnone'=None,
        ) -> 'StatusResponse':

        # Log what we're doing
        logger.info(f'[{cid}] Unsubscribing {username} from topic {topic_name}')

        logger.info(f'[{cid}] Successfully unsubscribed {username} from {topic_name}')

        response = StatusResponse()
        response.is_ok = True

        return response

# ################################################################################################################################
# ################################################################################################################################
