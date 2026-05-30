# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession

# ################################################################################################################################
# ################################################################################################################################

class TopicManager:
    """ Encapsulates topic-related lookups. Currently backed by ODB,
    to be replaced with in-memory structures in the future.
    """

    def __init__(self, session:'SASession', cluster_id:'int') -> 'None':

        # Zato
        from zato.common.odb.query.pubsub import pubsub_topic_by_name

        self._session = session
        self._cluster_id = cluster_id
        self._pubsub_topic_by_name = pubsub_topic_by_name

# ################################################################################################################################

    def is_topic_active(self, topic_name:'str') -> 'bool':
        """ Returns True if the topic exists and is active, False otherwise.
        """
        topic = self._pubsub_topic_by_name(self._session, self._cluster_id, topic_name)

        if not topic:
            return False

        out = topic.is_active
        return out

# ################################################################################################################################
# ################################################################################################################################
