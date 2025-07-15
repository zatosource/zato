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
from gevent import spawn

# Zato
from zato.broker.message_handler import handle_broker_msg
from zato.common.api import PubSub
from zato.common.broker_message import SERVICE
from zato.common.pubsub.consumer import start_internal_consumer, start_public_consumer
from zato.common.pubsub.models import PubMessage, PubResponse, StatusResponse, Subscription, Topic
from zato.common.util.api import new_sub_key, spawn_greenlet, utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from kombu.transport.pyamqp import Message as KombuMessage
    from zato.broker.client import BrokerClient
    from zato.common.typing_ import any_, anydictnone, dict_, strdict, strlist, strnone
    from zato.server.connection.amqp_ import Consumer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_prefix = PubSub.Prefix
_service_publish = SERVICE.PUBLISH.value

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
    topics: 'dict_[str, Topic]' # Maps topic_name to a Topic object
    consumers: 'dict_[str, Consumer]' # Maps sub_keys to Consumer objects
    subs_by_topic: 'topic_subs'

    def __init__(self, broker_client:'BrokerClient') -> 'None':

        self.broker_client = broker_client
        self.topics = {}
        self.consumers = {}
        self.subs_by_topic = {}

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid:'str' = msg['cid']
        sub_key:'str' = msg['sub_key']
        is_active:'bool' = msg['is_active']
        username:'str' = msg['username']
        topic_name_list:'strlist' = msg['topic_name_list']

        # Process each topic in the list
        for topic_name in topic_name_list:
            _ = self.subscribe_impl(cid, topic_name, username, sub_key, is_active)

        # Log all subscribed topics
        topic_name_list_human = ', '.join(topic_name_list)
        log_msg = f'[{cid}] Successfully subscribed {username} to topics: {topic_name_list_human} with key {sub_key}'
        logger.info(log_msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(self, msg:'strdict') -> 'None':

        # Local aliases
        cid:'str' = msg['cid']
        sub_key:'str' = msg['sub_key']
        is_active:'bool' = msg['is_active']
        topic_name_list:'strlist' = msg['topic_name_list']

        # Do we have such a consumer ..
        if consumer := self.consumers.get(sub_key):

            # .. get a queue for that consumer ..
            queue_name = consumer.config.queue

            # .. first off, update all the bindings pointing to it = update all the topics pointing to it ..
            self.broker_client.update_bindings(cid, sub_key, 'pubsubapi', queue_name, topic_name_list)

            # .. now, make sure the consumer is started or stopped, depending on what the is_active flag tells us ..

            if is_active:
                if consumer.is_stopped:
                    consumer.keep_running = True

                    # .. if its start method has been called it means it's already running in a new thread ..
                    if consumer.start_called:
                        consumer.start()

                    # .. otherwise, we start it in a new thread now ..
                    else:
                        _ = spawn_greenlet(consumer.start)
            else:
                if not consumer.is_stopped:
                    consumer.stop()

        # .. no consumer = we cannot continue.
        else:
            logger.warning(f'[{cid}] No such consumer by sub_key: {sub_key} -> {msg}')

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_EDIT(self, msg:'strdict') -> 'None':

        # Local aliases
        cid:'str' = msg['cid']
        topic_name:'str' = msg['topic_name']
        old_topic_name:'str' = msg['old_topic_name']

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
        subs_by_username = self.subs_by_topic.get(topic_name, {})

        # If there are any subscriptions, we need to unsubscribe them
        if subs_by_username:
            logger.info(f'[{cid}] Unsubscribing {len(subs_by_username)} users from topic {topic_name}')

            # Create a copy to avoid modification during iteration
            usernames = list(subs_by_username.keys())

            # Unsubscribe each user
            for username in usernames:
                _ = self.unsubscribe_impl(cid, topic_name, username)

        # Remove the topic from our mappings
        _ = self.topics.pop(topic_name)
        _ = self.subs_by_topic.pop(topic_name, None)

        # Delete all bindings for this topic from the exchange
        self.broker_client.delete_topic(cid, topic_name, ModuleCtx.Exchange_Name)

        logger.info(f'[{cid}] Successfully deleted topic {topic_name}')

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(self, msg:'strdict') -> 'None':
        """ Handle a subscription deletion message from the broker.
        Expected format: { 'action': 'action-id', 'sub_key': 'subscription-key' }
        """
        # Extract data from the message
        cid = msg['cid']
        sub_key = msg['sub_key']
        username = msg['username']

        logger.info(f'[{cid}] Processing delete for sub_key={sub_key}, username={username}')

        # Find all topics this user is subscribed to with this sub_key
        topics_to_unsubscribe = []
        for topic_name, subscriptions_by_username in self.subs_by_topic.items():
            if username in subscriptions_by_username:
                subscription = subscriptions_by_username[username]
                if subscription.sub_key == sub_key:
                    topics_to_unsubscribe.append(topic_name)

        # If we didn't find any matching subscriptions
        if not topics_to_unsubscribe:
            logger.info(f'[{cid}] No subscriptions found for {username} with key {sub_key}')
            return

        # Unsubscribe from each topic
        for topic_name in topics_to_unsubscribe:
            _ = self.unsubscribe_impl(cid, topic_name, username, sub_key=sub_key)

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

    def start_internal_subscriber(self) -> 'None':
        _ = spawn_greenlet(
            start_internal_consumer,
            'zato.pubsub',
            'pubsub',
            'zato-pubsub',
            self._on_internal_message_callback
        )

# ################################################################################################################################

    def invoke_service(
        self,
        service:'str',
        request:'anydictnone'=None,
        timeout:'int'=2,
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
        username:'str',
        ext_client_id:'strnone'=None
        ) -> 'PubResponse':
        """ Publish a message to a topic using the broker client.
        """
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
        logger.info(f'[{cid}] Published message to topic {topic_name} (user={username}{ext_client_part})')

        # Return success response
        response = PubResponse()
        response.is_ok = True
        response.msg_id = msg_id
        response.cid = cid

        return response

# ################################################################################################################################

    def subscribe_impl(
        self,
        cid: 'str',
        topic_name: 'str',
        username: 'str',
        sub_key: 'str'='',
        is_active: 'bool'=True,
        ) -> 'StatusResponse':
        """ Subscribe to a topic.
        """
        # This is optional and will be empty if it's an external subscription (e.g. via REST)
        sub_key = sub_key or new_sub_key(username)

        logger.info(f'[{cid}] Subscribing {username} to topic {topic_name} (sk={sub_key})')

        # Create topic if it doesn't exist ..
        if topic_name not in self.topics:
            self.create_topic(cid, 'subscribe', topic_name)

        # .. create a new subscription ..
        sub = Subscription()
        sub.topic_name = topic_name
        sub.username = username
        sub.sub_key = sub_key
        sub.creation_time = utcnow()

        # .. get or create a dict with subscriptions for users ..
        subs_by_username = self.subs_by_topic.setdefault(topic_name, {})

        # .. now add it for that user ..
        subs_by_username[username] = sub

        # .. create bindings for the topic ..
        self.broker_client.create_bindings(cid, sub_key, ModuleCtx.Exchange_Name, sub_key, topic_name)

        # .. create a new consumer if one doesn't exist yet ..
        if sub_key not in self.consumers:

            logger.info(f'[{cid}] Creating new consumer for sub_key={sub_key}')

            # .. start a background consumer ..
            result = spawn(start_public_consumer, cid, username, sub_key, self._on_public_message_callback, is_active)

            # .. get the actual consumer object ..
            consumer:'Consumer' = result.get()

            # .. store it for later use ..
            self.consumers[sub_key] = consumer

        # .. confirm it's started ..
        logger.info(f'[{cid}] Successfully subscribed {username} to {topic_name} with key {sub_key}')

        # .. build our response ..
        response = StatusResponse()
        response.is_ok = True

        # .. and return it to our caller.
        return response

# ################################################################################################################################

    def unsubscribe_impl(
        self,
        cid: 'str',
        topic_name:'str',
        username:'str',
        *,
        sub_key:'strnone'=None,
        ) -> 'StatusResponse':

        # Log what we're doing
        logger.info(f'[{cid}] Unsubscribing {sub_key} from topic {topic_name} ({username})')

        # Local aliases
        subs_by_username = self.subs_by_topic[topic_name]

        # Remove the subscription from our metadata ..
        sub:'Subscription' = subs_by_username.pop(username)

        # .. but use its sub_key in case we don't have it on input ..
        sub_key = sub.sub_key

        # .. remove the bindings on the broker ..
        self.broker_client.delete_bindings(
            cid,
            sub_key,
            ModuleCtx.Exchange_Name,
            sub_key,
            topic_name,
        )

        # .. get the consumer for this subscription ..
        consumer = self.consumers[sub_key]

        # .. check if there are any other bindings for this queue ..
        remaining_bindings = self.broker_client.get_bindings_by_queue(cid, sub_key, ModuleCtx.Exchange_Name)

        # .. if there are no more bindings for this queue, stop the consumer and remove it ..
        if not remaining_bindings:

            logger.info(f'[{cid}] No more bindings for {sub_key}, stopping consumer and deleting queue')

            # First stop it ..
            consumer.stop()
            _ = self.consumers.pop(sub_key)

            # .. now, delete the queue ..
            self.broker_client.delete_queue(sub_key)

        logger.info(f'[{cid}] Successfully unsubscribed {sub_key} from {topic_name} ({username})')

        response = StatusResponse()
        response.is_ok = True

        return response

# ################################################################################################################################

    def _on_public_message_callback(self, body:'any_', msg:'KombuMessage', name:'str', config:'strdict') -> 'None':

        # Local objects
        service_msg = {}

        # The name of the queue that the message was taken from is the same as the subscription key of the consumer ..
        sub_key = config.queue

        # .. enrich the message for the service ..
        body['sub_key'] = sub_key

        # .. turn that message into a form that a service can be invoked with ..
        service_msg['action'] = _service_publish
        service_msg['payload'] = body
        service_msg['cid'] = body.get('correl_id') or body.msg_id
        service_msg['service'] = 'zato.pubsub.subscription.handle-delivery'

        # .. push that message to the server ..
        self.broker_client.invoke_async(service_msg)

        # .. and acknowledge it so we can read more of them.
        msg.ack()

# ################################################################################################################################
# ################################################################################################################################
