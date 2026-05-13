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

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server

    def publish(
        self,
        topic_name:'str',
        data:'any_',
        *,
        priority:'int'=_default_priority,
        expiration:'int'=_default_expiration,
        correl_id:'strnone'=None,
        in_reply_to:'strnone'=None,
        ext_client_id:'strnone'=None,
        publisher:'strnone'=None,
        pub_time:'strnone'=None,
    ) -> 'PublishResult':

        out = self.server.pubsub_redis.publish(
            topic_name,
            data,
            priority=priority,
            expiration=expiration,
            correl_id=correl_id,
            in_reply_to=in_reply_to,
            ext_client_id=ext_client_id,
            publisher=publisher,
            pub_time=pub_time,
        )

        return out

    def get_messages(
        self,
        sub_key:'str',
        max_messages:'int'=_default_max_messages,
        max_len:'int'=_default_max_len,
    ) -> 'anylist':

        out = self.server.pubsub_redis.fetch_messages(sub_key, max_messages=max_messages, max_len=max_len)
        return out

    def subscribe(self, topic_name:'str', sub_key:'str') -> 'None':
        self.server.pubsub_redis.subscribe(sub_key, topic_name)

    def unsubscribe(self, topic_name:'str', sub_key:'str') -> 'None':
        self.server.pubsub_redis.unsubscribe(sub_key, topic_name)

# ################################################################################################################################
# ################################################################################################################################
