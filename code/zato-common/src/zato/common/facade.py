# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.api import PubSub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.redis_backend import PublishResult
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, strnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_default_priority = PubSub.Message.Priority_Default
_default_expiration = PubSub.Message.Default_Expiration
_default_max_messages = PubSub.Message.Default_Max_Messages
_default_max_len = PubSub.Message.Default_Max_Len

_service_topic_prefix = 'zato.s.to.'
_service_sub_key_prefix = 'zato.service.'

# ################################################################################################################################

def _service_name_to_topic(service_name:'str') -> 'str':
    out = _service_topic_prefix + service_name
    return out

# ################################################################################################################################
# ################################################################################################################################

class SecurityFacade:

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server

    def get_bearer_token_by_name(self, key:'str') -> 'anydict':
        item:'anydictnone' = self.server.config_manager.request_dispatcher.url_data.oauth_config.get(key)
        if item:
            out = item['config']
            return out
        else:
            raise KeyError(f'Security definition not found by key (1) -> {key}')

    def get_bearer_token_by_id(self, id:'int') -> 'anydict':

        for value in self.server.config_manager.request_dispatcher.url_data.oauth_config.values():
            if value['config']['id'] == id:
                out = value['config']
                return out
        else:
            raise KeyError(f'Security definition not found ID -> {id}')

# ################################################################################################################################
# ################################################################################################################################

class PubSubFacade:

    def __init__(self, server:'ParallelServer', service_name:'str') -> 'None':
        self.server = server
        self.service_name = service_name

# ################################################################################################################################

    def publish(
        self,
        topic_name:'str',
        data:'any_',
        *,
        priority:'int'=_default_priority,
        expiration:'int'=_default_expiration,
        cid:'strnone'=None,
        in_reply_to:'strnone'=None,
        ext_client_id:'strnone'=None,
        pub_time:'strnone'=None,
    ) -> 'PublishResult':

        is_service = topic_name in self.server.service_store.name_to_impl_name

        # Check if the topic_name is actually a known service name ..
        if is_service:
            topic_name = self._ensure_service_topic(topic_name)

        # .. now, publish the message to the topic ..
        out = self.server.pubsub_redis.publish(
            topic_name,
            data,
            priority=priority,
            expiration=expiration,
            correl_id=cid,
            in_reply_to=in_reply_to,
            ext_client_id=ext_client_id,
            publisher=self.service_name,
            pub_time=pub_time,
        )

        return out

# ################################################################################################################################

    def _ensure_service_topic(self, service_name:'str') -> 'str':

        # Build the topic name for this service ..
        computed_topic = _service_name_to_topic(service_name)

        # .. acquire the lock to prevent races during setup ..
        with self.server._service_topic_lock:

            # .. if already set up, there is nothing to do ..
            if service_name not in self.server._service_topic_cache:

                # .. build the subscription key ..
                sub_key = _service_sub_key_prefix + service_name

                # .. create the topic stream and consumer group in Redis ..
                self.server.pubsub_redis.subscribe(sub_key, computed_topic)

                # .. register push config so the delivery greenlet picks it up ..
                sub_config = {
                    'sub_key': sub_key,
                    'topic_name': computed_topic,
                    'push_type': PubSub.Push_Type.Service,
                    'push_service_name': service_name,
                    'rest_push_endpoint_id': None,
                }

                if sub_key not in self.server._push_subs:
                    self.server._push_subs[sub_key] = []

                self.server._push_subs[sub_key].append(sub_config)

                # .. start a delivery greenlet for this sub_key ..
                self.server.pubsub_push_delivery.start_sub_key(sub_key)

                # .. mark as set up ..
                self.server._service_topic_cache.add(service_name)

                # .. and log it.
                logger.info('Auto-created service topic `%s` for service `%s`', computed_topic, service_name)

        return computed_topic

# ################################################################################################################################

    def get_messages(
        self,
        sub_key:'str',
        max_messages:'int'=_default_max_messages,
        max_len:'int'=_default_max_len,
    ) -> 'anylist':

        out = self.server.pubsub_redis.fetch_messages(sub_key, max_messages=max_messages, max_len=max_len)
        return out

# ################################################################################################################################

    def subscribe(self, topic_name:'str', sub_key:'str') -> 'None':
        self.server.pubsub_redis.subscribe(sub_key, topic_name)

# ################################################################################################################################

    def unsubscribe(self, topic_name:'str', sub_key:'str') -> 'None':
        self.server.pubsub_redis.unsubscribe(sub_key, topic_name)

# ################################################################################################################################
# ################################################################################################################################
