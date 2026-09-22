# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queues in front of outgoing connections.

# stdlib
import logging
from contextlib import contextmanager
from threading import RLock

# Zato
from zato.common.api import PubSub
from zato.common.pubsub.dlq import is_dlq_sub_key
from zato.common.pubsub.outgoing import audit_disabled_conn_types, find_outgoing_conn, get_outgoing_sub_config, \
    get_outgoing_sub_key, get_outgoing_topic_name, locate_outgoing_conn, parse_outgoing_sub_key
from zato.server.base.config_manager.common import ConfigManagerImpl

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anytuple, callable_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingQueueDepth:
    """ How many messages wait in the queue of each outgoing connection, by sub key.
    """

    def __init__(self) -> 'None':
        self._counts:'anydict' = {}

# ################################################################################################################################

    def get(self, sub_key:'str') -> 'int':
        """ How many messages wait in one queue.
        """
        out = self._counts.get(sub_key, 0)
        return out

# ################################################################################################################################

    def raise_(self, sub_key:'str') -> 'None':
        """ One more message waits in this queue.
        """
        self._counts[sub_key] = self.get(sub_key) + 1

# ################################################################################################################################

    def lower(self, sub_key:'str', count:'int') -> 'None':
        """ That many messages left this queue.
        """
        self._counts[sub_key] = self.get(sub_key) - count

# ################################################################################################################################

    def set_counts(self, counts:'anydict') -> 'None':
        """ Sets the counts read from the database at startup.
        """
        self._counts.update(counts)

# ################################################################################################################################
# ################################################################################################################################

class OutgoingQueues(ConfigManagerImpl):
    """ The outgoing-queue side of a config manager.
    """

    _push_subs: 'anydict'

    _outgoing_sub_key_cache: 'set[str]'
    _outgoing_sub_key_lock: 'RLock'
    _outgoing_conn_locks: 'dict[str, RLock]'
    outgoing_queue_depth: 'OutgoingQueueDepth'

    init_outgoing_dlqs: 'callable_'
    rename_outgoing_dlq: 'callable_'
    delete_outgoing_dlq: 'callable_'
    restore_outgoing_dlqs: 'callable_'

    def init_outgoing_queues(self) -> 'None':
        """ Sets up what the queues of outgoing connections are tracked with.
        """

        # Sub keys of the connections that already have a queue
        self._outgoing_sub_key_cache = set()

        # Serializes the setup of those queues
        self._outgoing_sub_key_lock = RLock()

        # One lock per connection, under which publications take turns with renames and deletes
        self._outgoing_conn_locks = {}

        self.outgoing_queue_depth = OutgoingQueueDepth()

        self.init_outgoing_dlqs()

# ################################################################################################################################

    def get_outgoing_publish_lock(self, conn_type:'str', conn_id:'int') -> 'RLock':
        """ The lock under which publications to one outgoing connection take turns with its renames and deletes.
        """
        sub_key = get_outgoing_sub_key(conn_type, conn_id)

        with self._outgoing_sub_key_lock:
            lock = self._outgoing_conn_locks.get(sub_key)
            if not lock:
                lock = RLock()
                self._outgoing_conn_locks[sub_key] = lock

        return lock

# ################################################################################################################################

    def _set_outgoing_topic_audit_flag(self, conn_type:'str', topic_name:'str') -> 'None':
        """ Turns the pub/sub audit log of one outgoing topic off when its connection type says so.
        """
        if conn_type in audit_disabled_conn_types:
            self.server.pubsub_backend.set_topic_audit_flag(topic_name, False)

# ################################################################################################################################

    @contextmanager
    def hold_outgoing_queue(self, conn_type:'str', conn_id:'int') -> 'any_':
        """ Holds one connection's queue still for as long as the block runs - nothing is published to it and its delivery
        stops between two rounds, so no message is in flight while the block changes the connection or the messages of its
        queue. A round in flight would otherwise resolve the connection's topics from a configuration the block is replacing,
        or go on with a message the block discarded or replaced.
        """
        sub_key = get_outgoing_sub_key(conn_type, conn_id)
        delivery = self.server.pubsub_push_delivery

        with self.get_outgoing_publish_lock(conn_type, conn_id):

            # A connection that never had a queue has no delivery to stop
            has_queue = sub_key in self._outgoing_sub_key_cache

            if has_queue:
                delivery.pause_sub_key(sub_key)

            try:
                yield
            finally:

                # A queue the block deleted has nothing to start again
                is_still_there = sub_key in self._outgoing_sub_key_cache

                if has_queue and is_still_there:
                    delivery.resume_sub_key(sub_key)

# ################################################################################################################################

    def ensure_outgoing_subscription(self, conn_type:'str', conn_id:'int') -> 'anytuple':
        """ Makes sure that one outgoing connection has a topic and a queue, returning the topic's name and the connection's
        current name.
        """
        sub_key = get_outgoing_sub_key(conn_type, conn_id)

        with self._outgoing_sub_key_lock:

            conn_name, _ = locate_outgoing_conn(self.server, conn_type, conn_id)
            topic_name = get_outgoing_topic_name(conn_type, conn_name)

            self._set_outgoing_topic_audit_flag(conn_type, topic_name)

            if sub_key not in self._outgoing_sub_key_cache:

                self.server.pubsub_backend.subscribe(sub_key, topic_name)

                sub_config = get_outgoing_sub_config(sub_key, topic_name)
                self._push_subs[sub_key] = [sub_config]

                self.server.pubsub_push_delivery.start_sub_key(sub_key)

                self._outgoing_sub_key_cache.add(sub_key)

                logger.info('Created outgoing connection queue `%s` for topic `%s`', sub_key, topic_name)

        return topic_name, conn_name

# ################################################################################################################################

    def rename_outgoing_subscription(self, conn_type:'str', conn_id:'int', old_name:'str', new_name:'str') -> 'None':
        """ Moves the topic of one outgoing connection to the connection's new name. The caller holds the queue
        through hold_outgoing_queue, so nothing is published to the topic and no round is in flight while it moves.
        """
        sub_key = get_outgoing_sub_key(conn_type, conn_id)

        if sub_key not in self._outgoing_sub_key_cache:
            return

        old_topic_name = get_outgoing_topic_name(conn_type, old_name)
        new_topic_name = get_outgoing_topic_name(conn_type, new_name)

        self.server.pubsub_backend.rename_topic(old_topic_name, new_topic_name)

        self.server.pubsub_backend.delete_topic_audit_flag(old_topic_name)
        self._set_outgoing_topic_audit_flag(conn_type, new_topic_name)

        sub_config = get_outgoing_sub_config(sub_key, new_topic_name)
        self._push_subs[sub_key] = [sub_config]

        logger.info('Moved outgoing connection queue `%s` from topic `%s` to `%s`',
            sub_key, old_topic_name, new_topic_name)

        self.rename_outgoing_dlq(conn_type, conn_id, old_name, new_name)

# ################################################################################################################################

    def delete_outgoing_subscription(self, conn_type:'str', conn_id:'int', conn_name:'str') -> 'None':
        """ Removes the queue of a deleted outgoing connection along with whatever it still held.
        """
        sub_key = get_outgoing_sub_key(conn_type, conn_id)

        # The queue is held first, so no round of its delivery moves a message to the DLQ while the DLQ goes away
        with self.hold_outgoing_queue(conn_type, conn_id):

            # The DLQ goes first, while its queue's lock still exists
            self.delete_outgoing_dlq(conn_type, conn_id, conn_name)

            if sub_key not in self._outgoing_sub_key_cache:
                return

            topic_name = get_outgoing_topic_name(conn_type, conn_name)

            self.server.pubsub_push_delivery.stop_sub_key(sub_key)

            dropped_count = self.server.pubsub_backend.get_total_count(sub_key, topic_name, 'pending')

            self.server.pubsub_backend.delete_topic(topic_name)
            self.server.pubsub_backend.delete_topic_audit_flag(topic_name)

            del self._push_subs[sub_key]
            self._outgoing_sub_key_cache.remove(sub_key)

        # The lock is dropped once it is no longer held
        with self._outgoing_sub_key_lock:
            del self._outgoing_conn_locks[sub_key]

        logger.info('Deleted outgoing connection queue `%s` for topic `%s`, messages dropped:%d',
            sub_key, topic_name, dropped_count)

# ################################################################################################################################

    def restore_outgoing_subscriptions(self) -> 'None':
        """ Brings back the queues of outgoing connections at startup, their greenlets are started by the caller.
        """
        sub_key_list = self.server.pubsub_backend.get_sub_keys_by_prefix(PubSub.Outgoing.Sub_Key_Prefix)
        restored_count = 0

        # The DLQs share the prefix and are brought back on their own
        self.restore_outgoing_dlqs(sub_key_list)

        for sub_key in sub_key_list:

            if is_dlq_sub_key(sub_key):
                continue

            conn_type, conn_id = parse_outgoing_sub_key(sub_key)

            found = find_outgoing_conn(self.server, conn_type, conn_id)

            if not found:
                logger.info('Skipping outgoing connection queue `%s`, there is no connection with that id', sub_key)
                continue

            conn_name, _ = found
            topic_name = get_outgoing_topic_name(conn_type, conn_name)

            # A rename a crash interrupted is finished here
            for subscribed_topic in self.server.pubsub_backend.get_subscribed_topics(sub_key):
                if subscribed_topic != topic_name:
                    logger.info('Finishing the move of outgoing topic `%s` to `%s`', subscribed_topic, topic_name)
                    self.server.pubsub_backend.rename_topic(subscribed_topic, topic_name)

            self._set_outgoing_topic_audit_flag(conn_type, topic_name)

            sub_config = get_outgoing_sub_config(sub_key, topic_name)
            self._push_subs[sub_key] = [sub_config]
            self._outgoing_sub_key_cache.add(sub_key)

            restored_count += 1

        # The depths are read before the first send is made
        pending_counts = self.server.pubsub_backend.get_pending_counts_by_prefix(PubSub.Outgoing.Sub_Key_Prefix)

        # A send does not wait behind what a DLQ holds
        for sub_key in list(pending_counts):
            if is_dlq_sub_key(sub_key):
                del pending_counts[sub_key]

        self.outgoing_queue_depth.set_counts(pending_counts)

        suffix = 'queue' if restored_count == 1 else 'queues'

        logger.info('Restored %d outgoing connection %s, messages waiting: %s', restored_count, suffix, pending_counts)

# ################################################################################################################################
# ################################################################################################################################
