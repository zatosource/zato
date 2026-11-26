# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from contextlib import closing

# Zato
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, callable_, strbooldict

# ################################################################################################################################
# ################################################################################################################################

class TopicManager:
    """ Encapsulates topic-related lookups. The state of a topic is read from the ODB once and kept in memory,
    and the configuration events of the topic remove it from memory, so the next lookup reads it again.
    """

    def __init__(self, new_session:'callable_') -> 'None':

        # Zato
        from zato.common.odb.query.pubsub import pubsub_subscriptions_by_topic_id, pubsub_topic_by_name

        # Each lookup opens a session of its own, because lookups run concurrently and a session holds one connection
        self._new_session = new_session

        self._pubsub_topic_by_name = pubsub_topic_by_name
        self._pubsub_subscriptions_by_topic_id = pubsub_subscriptions_by_topic_id

        # Whether each topic read so far is active, by its name
        self._is_active_by_name:'strbooldict' = {}

# ################################################################################################################################

    def is_topic_active(self, topic_name:'str') -> 'bool':
        """ Returns True if the topic exists and is active, False otherwise.
        """
        # A topic read before is answered from memory ..
        if topic_name in self._is_active_by_name:
            return self._is_active_by_name[topic_name]

        with closing(self._new_session()) as session:
            topic = self._pubsub_topic_by_name(session, topic_name)

        # .. a topic that does not exist is not kept, so it is found once it is created ..
        if not topic:
            return False

        # .. and any other topic is kept until one of its configuration events arrives.
        out = cast_('bool', topic.is_active)
        self._is_active_by_name[topic_name] = out

        return out

# ################################################################################################################################

    def forget_topic(self, topic_name:'str') -> 'None':
        """ Removes the state of a topic from memory after its configuration changed.
        """
        _ = self._is_active_by_name.pop(topic_name, None)

# ################################################################################################################################

    def get_subscriptions_by_topic_id(self, topic_id:'int') -> 'anylist':
        """ Returns all subscription rows linked to a given topic.
        Must be called before the topic is deleted from the ODB.
        """
        with closing(self._new_session()) as session:
            out = self._pubsub_subscriptions_by_topic_id(session, topic_id)

        return out

# ################################################################################################################################
# ################################################################################################################################
