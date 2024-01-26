# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pylint: disable=unused-import, redefined-builtin, unused-variable

# stdlib
import logging

# gevent
from zato.common.typing_ import cast_
from zato.server.pubsub.model import Topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, callable_, dict_, stranydict, strintdict
    from zato.server.pubsub.core.hook import HookAPI
    from zato.server.pubsub.model import inttopicdict, sublist, topiclist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato_pubsub.ps')
logger_zato = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class TopicAPI:

    def __init__(
        self,
        *,
        hook_api, # type: HookAPI
        server_name, # type: str
        server_pid,  # type: int
        topic_meta_store_frequency, # type: int
        subscriptions_by_topic, # type: dict_[str, sublist]
        is_allowed_sub_topic_by_endpoint_id_func, # type: callable_
    ) -> 'None':

        self.hook_api = hook_api
        self.is_allowed_sub_topic_by_endpoint_id_func = is_allowed_sub_topic_by_endpoint_id_func

        self.server_name = server_name
        self.server_pid = server_pid
        self.topic_meta_store_frequency = topic_meta_store_frequency

        # Topic name -> List of Subscription objects
        self.subscriptions_by_topic = subscriptions_by_topic

        # Topic ID -> Topic object
        self.topics = cast_('inttopicdict', {})

        # Topic name -> Topic ID
        self.topic_name_to_id = {} # type: strintdict

# ################################################################################################################################

    def has_topic_by_id(self, topic_id:'int') -> 'bool':
        try:
            self.topics[topic_id]
        except KeyError:
            return False
        else:
            return True

# ################################################################################################################################

    def has_topic_by_name(self, topic_name:'str') -> 'bool':
        try:
            _ = self.get_topic_by_name(topic_name)
        except KeyError:
            return False
        else:
            return True

# ################################################################################################################################

    def get_topics(self) -> 'inttopicdict':
        return self.topics

# ################################################################################################################################

    def get_topic_by_name(self, topic_name:'str') -> 'Topic':
        topic_id = self.get_topic_id_by_name(topic_name)
        return self.topics[topic_id]

# ################################################################################################################################

    def get_topic_by_id(self, topic_id:'int') -> 'Topic':
        return self.topics[topic_id]

# ################################################################################################################################

    def get_topic_id_by_name(self, topic_name:'str') -> 'int':
        return self.topic_name_to_id[topic_name]

# ################################################################################################################################

    def create_topic_object(self, config:'stranydict') -> 'None':
        self.hook_api.set_topic_config_hook_data(config)
        config['meta_store_frequency'] = self.topic_meta_store_frequency

        topic = Topic(config, self.server_name, self.server_pid)
        self.topics[config['id']] = topic
        self.topic_name_to_id[config['name']] = config['id']

        logger.info('Created topic object `%s` (id:%s) on server `%s` (pid:%s)', topic.name, topic.id,
            topic.server_name, topic.server_pid)

# ################################################################################################################################

    def delete_topic(self, topic_id:'int', topic_name:'str') -> 'anylist':
        del self.topic_name_to_id[topic_name]
        subscriptions_by_topic = self.subscriptions_by_topic.pop(topic_name, [])
        del self.topics[topic_id]

        logger.info('Deleted topic object `%s` (%s), subs:`%s`',
            topic_name, topic_id, [elem.sub_key for elem in subscriptions_by_topic])

        return subscriptions_by_topic

# ################################################################################################################################

    def get_sub_topics_for_endpoint(self, endpoint_id:'int') -> 'topiclist':
        """ Returns all topics to which endpoint_id can subscribe.
        """
        out = [] # type: topiclist
        for topic in self.topics.values():
            if self.is_allowed_sub_topic_by_endpoint_id_func(topic.name, endpoint_id):
                out.append(topic)
        return out

# ################################################################################################################################
# ################################################################################################################################
