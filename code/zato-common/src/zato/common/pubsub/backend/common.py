# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from datetime import timedelta
from http.client import BAD_REQUEST, OK
from json import dumps
from logging import getLogger
from traceback import format_exc

# gevent
from gevent.lock import RLock

# Zato
from zato.broker.message_handler import handle_broker_msg
from zato.common.api import PubSub
from zato.common.pubsub.models import PubMessage, PubResponse, StatusResponse, Subscription, Topic
from zato.common.pubsub.util import create_subscription_bindings
from zato.common.util.api import as_bool, new_msg_id, new_sub_key, utcnow

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

_needs_details = as_bool(os.environ.get('Zato_Needs_Details', False))
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
        self._invoke_lock = RLock(enable_logging=True)

# ################################################################################################################################

    def _add_topic(self, topic_name:'str', topic:'Topic') -> 'None':
        """ Add a topic to the backend.
        """
        self.topics[topic_name] = topic

# ################################################################################################################################

    def _delete_topic(self, topic_name:'str') -> 'Topic':
        """ Delete a topic from the backend and return it.
        """
        return self.topics.pop(topic_name)

# ################################################################################################################################

    def _has_topic(self, topic_name:'str') -> 'bool':
        """ Check if a topic exists in the backend.
        """
        return topic_name in self.topics

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid:'str' = msg['cid']
        sub_key:'str' = msg['sub_key']
        sec_name:'str' = msg['sec_name']
        topic_name_list:'strlist' = msg['topic_name_list']

        # Process each topic in the list
        for topic_name in topic_name_list:
            _ = self.register_subscription(cid, topic_name, sec_name=sec_name, sub_key=sub_key)

        # Log all subscribed topics
        topic_name_list_human = ', '.join(topic_name_list)
        log_msg = f'[{cid}] Successfully subscribed {sec_name} to topics: {topic_name_list_human} with key {sub_key}'
        logger.info(log_msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid = msg['cid']
        sub_key = msg['sub_key']
        sec_name = msg['sec_name']

        logger.info(f'[{cid}] Processing delete for sub_key={sub_key}, sec_name={sec_name}')

        with self._main_lock:

            # Remove existing subscription by sub_key from all topics
            topics_to_unsubscribe = []

            for topic_name, subs_by_sec_name in self.subs_by_topic.items():
                if sec_name in subs_by_sec_name:
                    subscription = subs_by_sec_name[sec_name]
                    if subscription.sub_key == sub_key:
                        _ = subs_by_sec_name.pop(sec_name, None)
                        topics_to_unsubscribe.append(topic_name)

            # Clean up empty topic entries
            for topic_name in topics_to_unsubscribe:
                if not self.subs_by_topic[topic_name]:
                    _ = self.subs_by_topic.pop(topic_name, None)

        # If we didn't find any matching subscriptions
        if not topics_to_unsubscribe:
            logger.info(f'[{cid}] No subscriptions found for {sec_name} with key {sub_key}')
            return

        # Unsubscribe from each topic
        for topic_name in topics_to_unsubscribe:
            _ = self.unregister_subscription(cid, topic_name, sec_name=sec_name, should_notify_server=False)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_DELETE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid:'str' = msg['cid']
        topic_name:'str' = msg['topic_name']

        logger.info(f'[{cid}] Deleting topic {topic_name}')

        # Check if topic exists
        if not self._has_topic(topic_name):
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
                _ = self.unregister_subscription(cid, topic_name, sec_name=sec_name)

        # Remove the topic from our mappings
        _ = self._delete_topic(topic_name)
        _ = self.subs_by_topic.pop(topic_name, None)

        # Remove permissions for this topic from pattern matcher (if this is a REST backend)
        if hasattr(self, 'pattern_matcher') and hasattr(self, 'rest_server'):
            for username in self.rest_server.users:
                self.pattern_matcher.delete_topic(username, topic_name)

        logger.info(f'[{cid}] Successfully deleted topic {topic_name}')

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
        cid:'str'=''
    ) -> 'any_':
        if not cid:
            raise Exception()

        logger.info(f'[{cid}] INVOKE-1 {service} {request}')
        logger.info(f'[{cid}] LOCK-WAIT {service} {request}')

        with self._invoke_lock:
            logger.info(f'[{cid}] INVOKE-2 {service} {request}')
            try:
                response = self.broker_client.invoke_sync(service, request, timeout, needs_root_elem)
                logger.info(f'[{cid}] INVOKE-3 {service} {request}')
            except Exception:
                logger.error(f'[{cid}] INVOKE-ERROR {service} {request} {format_exc()}')
                raise
            else:
                logger.info(f'[{cid}] INVOKE-4 {service} {request} {response}')

        logger.info(f'[{cid}] INVOKE-5 {service} {request} {response}')
        return response

# ################################################################################################################################

    def get_sec_name_by_username(self, username:'str', username_to_sec_name:'dict') -> 'str':
        """ Get security definition name by username.
        """
        if username in username_to_sec_name:
            return username_to_sec_name[username]

        raise ValueError(f'No security definition found for username: {username}')

# ################################################################################################################################

    def create_topic(self, cid:'str', source:'str', topic_name:'str') -> 'None':

        topic = Topic()
        topic.name = topic_name

        self._add_topic(topic_name, topic)
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

        # Create topic if it doesn't exist
        if not self._has_topic(topic_name):
            self.create_topic(cid, 'publish', topic_name)

        # Generate message ID and calculate size
        msg_id = new_msg_id()
        data_str = dumps(msg.data) if not isinstance(msg.data, str) else msg.data
        size = len(data_str.encode('utf-8'))

        # Set timestamps
        now = utcnow()
        recv_time_iso = now.isoformat()
        expiration_time = now + timedelta(seconds=msg.expiration)
        expiration_time_iso = expiration_time.isoformat()

        # This is optional on input so we need to our own timestamp if not given
        pub_time_iso = msg.pub_time or recv_time_iso

        # Create message object
        message = {
            'data': msg.data,
            'topic_name': topic_name,
            'msg_id': msg_id,
            'priority': msg.priority,
            'pub_time_iso': pub_time_iso,
            'recv_time_iso': recv_time_iso,  # Same as pub_time for direct API calls
            'expiration': msg.expiration,
            'expiration_time_iso': expiration_time_iso,
            'size': size,
            'publisher': username,
        }

        if msg.ext_client_id:
            message['ext_client_id'] = msg.ext_client_id

        if msg.correl_id:
            message['correl_id'] = msg.correl_id

        if msg.in_reply_to:
            message['in_reply_to'] = msg.in_reply_to

        self.broker_client.publish(message, exchange=ModuleCtx.Exchange_Name, routing_key=topic_name)

        ext_client_part = f' -> {ext_client_id})' if ext_client_id else ')'

        if _needs_details:
            logger.info(f'[{cid}] Published message `{msg_id}` to topic `{topic_name}` (username={username}{ext_client_part}')

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
        *,
        username: 'str'='',
        sec_name: 'str'='',
        sub_key: 'str'='',
        should_create_bindings: 'bool'=True,
        should_invoke_server=False,
        ) -> 'StatusResponse':
        """ Subscribe to a topic.
        """
        # Reusable
        response = StatusResponse()

        # Get sec_name from username or use directly if it's already sec_name
        if username:
            config = self.rest_server.get_user_config(username)
            sec_name = config['sec_name']

        # Check if user is already subscribed to this topic
        with self._main_lock:
            subs_by_sec_name = self.subs_by_topic.get(topic_name, {})
            if sec_name in subs_by_sec_name:
                logger.info(f'[{cid}] User `{sec_name}` already subscribed to topic `{topic_name}` - no action needed')
                response = StatusResponse()
                response.is_ok = True
                response.status = OK
                return response

        # This is optional and will be empty if it's an external subscription (e.g. via REST)
        if not sub_key:

            if _needs_details:
                logger.info(f'Subs by topic: {self.subs_by_topic}')

            # Look for existing sub_key for this user across all topics
            for topic_subs in self.subs_by_topic.values():
                if sec_name in topic_subs:
                    sub_key = topic_subs[sec_name].sub_key
                    logger.info(f'[{cid}] Using an existing subscription for {sec_name} to topic {topic_name} (sk={sub_key})')
                    break
            else:
                # No existing sub_key found, generate new one
                sub_key = new_sub_key(sec_name)

                logger.info(f'[{cid}] New subscription for {sec_name} to topic {topic_name} (sk={sub_key})')

        # Create topic if it doesn't exist ..
        with self._main_lock:
            if not self._has_topic(topic_name):
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

            # .. create AMQP bindings for the subscription ..
            if should_create_bindings:
                create_subscription_bindings(self.broker_client, cid, sub_key, ModuleCtx.Exchange_Name, topic_name)

        # .. we go here if we need to invoke the server, and we do only if the subscription was create via the REST API,
        # .. as we don't want to invoke the server if we've just loaded the subscriptions from it ..
        if should_invoke_server:

            # .. invoke the subscription service to update the database ..
            request = {
                'sub_key': sub_key,
                'topic_name_list': [topic_name],
                'sec_name': sec_name,
                'is_active': True,
                'delivery_type': PubSub.Delivery_Type.Pull,
            }

            service_name = 'zato.pubsub.subscription.subscribe'
            service_response = self.invoke_service_with_pubsub(service_name, request, needs_root_elem=True, cid=cid)

            if error := service_response.get('error'):
                is_ok = False
                status = BAD_REQUEST
                logger.error(f'[{cid}] Failed to create subscription in server: `{error}`')
            else:
                is_ok = True
                status = OK

            # .. build our response ..
            response.is_ok = is_ok
            response.status = status

        # .. we go here if we don't invoke the server, in which case we simply indicate success ..
        else:
            response.is_ok = True

        # .. and now we can return it to our caller.
        return response

# ################################################################################################################################

    def unregister_subscription(
        self,
        cid: 'str',
        topic_name:'str',
        *,
        sec_name:'str' = '',
        username:'str' = '',
        should_notify_server:'bool'=True,
        ) -> 'StatusResponse':

        # Get sec_name from username if needed
        if username and not sec_name:
            config = self.rest_server.get_user_config(username)
            sec_name = config['sec_name']

        # Check if user is actually subscribed to this topic
        with self._main_lock:
            subs_by_sec_name = self.subs_by_topic.get(topic_name, {})
            if sec_name not in subs_by_sec_name:
                logger.info(f'[{cid}] Sec. def. `{sec_name}` not subscribed to topic `{topic_name}` - no action needed')
                response = StatusResponse()
                response.is_ok = True
                return response

        # Log what we're doing ..
        logger.info(f'[{cid}] Unsubscribing `{sec_name}` from topic `{topic_name}` should_notify_server={should_notify_server}')

        # .. this is optional because we may have been called from self.on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE ..
        # .. in which case the server has already deleted the subscription so we don't need to notify it about it ..
        if should_notify_server:

            # .. prepare the request ..
            request = {
                'sec_name': sec_name,
                'username': username,
                'topic_name_list': [topic_name],
            }

            # .. invoke our service ..
            self.invoke_service_with_pubsub('zato.pubsub.subscription.unsubscribe', request, cid=cid)

            # .. remove subscription from memory ..
            with self._main_lock:
                if topic_name in self.subs_by_topic:
                    subs_by_sec_name = self.subs_by_topic[topic_name]
                    if sec_name in subs_by_sec_name:
                        del subs_by_sec_name[sec_name]
                        if not subs_by_sec_name:
                            del self.subs_by_topic[topic_name]

        # .. log what happened ..
        logger.info(f'[{cid}] Successfully unsubscribed `{sec_name}` from `{topic_name}`')

        # .. build are OK response ..
        response = StatusResponse()
        response.is_ok = True

        # .. and return it to the caller.
        return response

# ################################################################################################################################
# ################################################################################################################################
