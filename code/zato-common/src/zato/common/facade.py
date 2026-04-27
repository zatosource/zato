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
    from zato.common.typing_ import any_, anydict, anydictnone, anynone
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
        item:'anydictnone' = self.server.worker_store.request_dispatcher.url_data.oauth_config.get(key)
        if item:
            return item['config']
        else:
            raise KeyError(f'Security definition not found by key (1) -> {key}')

    def get_bearer_token_by_id(self, id:'int') -> 'anydict':

        for value in self.server.worker_store.request_dispatcher.url_data.oauth_config.values():
            if value['config']['id'] == id:
                return value['config']
        else:
            raise KeyError(f'Security definition not found ID -> {id}')

# ################################################################################################################################
# ################################################################################################################################

class PubSubFacade:

    def __init__(self, server:'ParallelServer') -> 'None':
        self.server = server

    def publish(self, topic_name:'str', data:'any_', **kwargs:'any_') -> 'anydict':
        topic = self.server.pubsub_broker.get_topic_by_name(topic_name)
        if topic is None:
            topic = self.server.pubsub_broker.create_topic(topic_name)

        config = {
            'topic_id': topic['topic_id'],
            'payload': data if isinstance(data, bytes) else str(data).encode('utf-8'),
            'publisher_id': kwargs.get('publisher_id', 0),
            'priority': kwargs.get('priority', 5),
            'correl_id': kwargs.get('correl_id') or kwargs.get('cid'),
            'expiration': kwargs.get('expiration'),
            'in_reply_to': kwargs.get('in_reply_to'),
            'ext_client_id': kwargs.get('ext_client_id'),
            'pub_time': kwargs.get('pub_time'),
            'pub_msg_id': kwargs.get('pub_msg_id') or kwargs.get('msg_id'),
        }

        return self.server.pubsub_broker.publish(config)

    def get_messages(self, topic_name:'str', sub_key:'str', batch_size:'int'=100) -> 'anydict':
        topic = self.server.pubsub_broker.get_topic_by_name(topic_name)
        if topic is None:
            return {'msgs': []}

        sub_id = self.server.pubsub_broker.get_subscription_id(sub_key, topic['topic_id'])
        if sub_id is None:
            return {'msgs': []}

        window_minutes = self.server.fs_server_config.pubsub.window_minutes
        return self.server.pubsub_broker.get_messages(topic['topic_id'], sub_id, batch_size, window_minutes)

    def subscribe(self, topic_name:'str', sub_key:'str', ack_mode:'str'='client') -> 'anydict':
        topic = self.server.pubsub_broker.get_topic_by_name(topic_name)
        if topic is None:
            topic = self.server.pubsub_broker.create_topic(topic_name)

        return self.server.pubsub_broker.create_subscription(sub_key, topic['topic_id'], ack_mode)

    def unsubscribe(self, topic_name:'str', sub_key:'str') -> 'anynone':
        topic = self.server.pubsub_broker.get_topic_by_name(topic_name)
        if topic is None:
            return None

        return self.server.pubsub_broker.delete_subscription(sub_key, topic['topic_id'])

# ################################################################################################################################
# ################################################################################################################################
