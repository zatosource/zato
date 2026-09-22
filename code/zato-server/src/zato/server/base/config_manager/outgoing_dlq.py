# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The DLQs of outgoing connections.

# stdlib
import logging
from threading import RLock

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.dlq import get_dlq_sub_key, get_dlq_topic_name, is_dlq_sub_key, parse_dlq_sub_key
from zato.common.pubsub.outgoing import find_outgoing_conn, get_outgoing_sub_key, locate_outgoing_conn, \
    parse_outgoing_sub_key
from zato.server.base.config_manager.common import ConfigManagerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anytuple, callable_
    from zato.server.base.config_manager.outgoing_queues import OutgoingQueueDepth

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingDLQs(ConfigManagerImpl):
    """ The DLQ side of a config manager.
    """

    _outgoing_sub_key_cache: 'set[str]'
    outgoing_queue_depth: 'OutgoingQueueDepth'
    get_outgoing_publish_lock: 'callable_'

    _outgoing_dlq_cache: 'set[str]'
    _outgoing_dlq_lock: 'RLock'

    def init_outgoing_dlqs(self) -> 'None':
        """ Sets up what the DLQs of outgoing connections are tracked with.
        """

        # Sub keys of the DLQs that already exist
        self._outgoing_dlq_cache = set()

        # Serializes the setup of those DLQs
        self._outgoing_dlq_lock = RLock()

# ################################################################################################################################

    def ensure_outgoing_dlq(self, conn_type:'str', conn_id:'int') -> 'anytuple':
        """ Makes sure that one outgoing connection has a DLQ, returning the DLQ topic's name and the connection's current name.
        """
        sub_key = get_dlq_sub_key(conn_type, conn_id)

        with self._outgoing_dlq_lock:

            conn_name, _ = locate_outgoing_conn(self.server, conn_type, conn_id)
            topic_name = get_dlq_topic_name(conn_type, conn_name)

            if sub_key not in self._outgoing_dlq_cache:

                # A DLQ has a subscription and no push config, nothing is delivered out of it
                self.server.pubsub_backend.subscribe(sub_key, topic_name)
                self._outgoing_dlq_cache.add(sub_key)

                logger.info('Created outgoing connection DLQ `%s` for topic `%s`', sub_key, topic_name)

        return topic_name, conn_name

# ################################################################################################################################

    def rename_outgoing_dlq(self, conn_type:'str', conn_id:'int', old_name:'str', new_name:'str') -> 'None':
        """ Moves the DLQ topic of one outgoing connection to the connection's new name.
        """
        sub_key = get_dlq_sub_key(conn_type, conn_id)

        if sub_key not in self._outgoing_dlq_cache:
            return

        old_topic_name = get_dlq_topic_name(conn_type, old_name)
        new_topic_name = get_dlq_topic_name(conn_type, new_name)

        # The caller holds the queue, so the delivery that moves messages to the DLQ is not running now
        self.server.pubsub_backend.rename_topic(old_topic_name, new_topic_name)

        logger.info('Moved outgoing connection DLQ `%s` from topic `%s` to `%s`', sub_key, old_topic_name, new_topic_name)

# ################################################################################################################################

    def delete_outgoing_dlq(self, conn_type:'str', conn_id:'int', conn_name:'str') -> 'None':
        """ Removes the DLQ of a deleted outgoing connection along with whatever it still held.
        """
        sub_key = get_dlq_sub_key(conn_type, conn_id)

        if sub_key not in self._outgoing_dlq_cache:
            return

        topic_name = get_dlq_topic_name(conn_type, conn_name)

        with self.get_outgoing_publish_lock(conn_type, conn_id):

            dropped_count = self.server.pubsub_backend.get_total_count(sub_key, topic_name, 'pending')
            self.server.pubsub_backend.delete_topic(topic_name)
            self._outgoing_dlq_cache.remove(sub_key)

        logger.info('Deleted outgoing connection DLQ `%s` for topic `%s`, messages dropped:%d',
            sub_key, topic_name, dropped_count)

# ################################################################################################################################

    def restore_outgoing_dlqs(self, sub_key_list:'list[str]') -> 'None':
        """ Brings back the DLQs at startup, out of every outgoing sub key the database knows.
        """
        restored_count = 0

        for sub_key in sub_key_list:

            if not is_dlq_sub_key(sub_key):
                continue

            self._outgoing_dlq_cache.add(sub_key)
            restored_count += 1

        suffix = 'DLQ' if restored_count == 1 else 'DLQs'

        logger.info('Restored %d outgoing connection %s', restored_count, suffix)

# ################################################################################################################################

    def get_outgoing_dlq_sub_keys(self) -> 'list[str]':
        """ The sub key of every DLQ, sorted.
        """
        out = sorted(self._outgoing_dlq_cache)
        return out

# ################################################################################################################################

    def get_outgoing_queue_list(self) -> 'list[anydict]':
        """ One row per outgoing connection that has a queue or a DLQ, with the depth of each.
        """
        dlq_counts = self.server.pubsub_backend.get_pending_counts_by_prefix(PubSub.Outgoing.DLQ_Sub_Key_Prefix)

        conn_keys:'set[anytuple]' = set()

        for sub_key in self._outgoing_sub_key_cache:
            conn_keys.add(parse_outgoing_sub_key(sub_key))

        for sub_key in self._outgoing_dlq_cache:
            conn_keys.add(parse_dlq_sub_key(sub_key))

        out:'list[anydict]' = []

        for conn_type, conn_id in sorted(conn_keys):

            found = find_outgoing_conn(self.server, conn_type, conn_id)
            if not found:
                continue

            conn_name, _ = found

            queue_sub_key = get_outgoing_sub_key(conn_type, conn_id)
            dlq_sub_key = get_dlq_sub_key(conn_type, conn_id)

            if dlq_sub_key in dlq_counts:
                dlq_depth = dlq_counts[dlq_sub_key]
            else:
                dlq_depth = 0

            out.append({
                'conn_type': conn_type,
                'conn_id': conn_id,
                'name': conn_name,
                'queue_depth': self.outgoing_queue_depth.get(queue_sub_key),
                'dlq_depth': dlq_depth,
            })

        return out

# ################################################################################################################################
# ################################################################################################################################
