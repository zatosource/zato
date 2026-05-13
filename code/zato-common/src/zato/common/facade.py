# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.pubsub.redis_backend import PublishResult
    from zato.common.typing_ import any_, anydict, anydictnone
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class SecurityFacade:

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server

    def get_bearer_token_by_name(self, key:'str') -> 'anydict':
        item:'anydictnone' = self.server.config_manager.request_dispatcher.url_data.oauth_config.get(key)
        if item:
            return item['config']
        else:
            raise KeyError(f'Security definition not found by key (1) -> {key}')

    def get_bearer_token_by_id(self, id:'int') -> 'anydict':

        for value in self.server.config_manager.request_dispatcher.url_data.oauth_config.values():
            if value['config']['id'] == id:
                return value['config']
        else:
            raise KeyError(f'Security definition not found ID -> {id}')

# ################################################################################################################################
# ################################################################################################################################

class PubSubFacade:

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server

    def publish(self, topic_name:'str', data:'any_', **kwargs:'any_') -> 'PublishResult':
        return self.server.pubsub_redis.publish(
            topic_name,
            data,
            priority=kwargs.get('priority', 5),
            expiration=kwargs.get('expiration', 31536000),
            correl_id=kwargs.get('correl_id') or kwargs.get('cid'),
            in_reply_to=kwargs.get('in_reply_to'),
            ext_client_id=kwargs.get('ext_client_id'),
            publisher=kwargs.get('publisher'),
            pub_time=kwargs.get('pub_time'),
        )

    def get_messages(self, sub_key:'str', max_messages:'int'=50, max_len:'int'=5_000_000) -> 'list':
        return self.server.pubsub_redis.fetch_messages(sub_key, max_messages=max_messages, max_len=max_len)

    def subscribe(self, topic_name:'str', sub_key:'str') -> 'None':
        self.server.pubsub_redis.subscribe(sub_key, topic_name)

    def unsubscribe(self, topic_name:'str', sub_key:'str') -> 'None':
        self.server.pubsub_redis.unsubscribe(sub_key, topic_name)

# ################################################################################################################################
# ################################################################################################################################
