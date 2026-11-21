# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queues in front of outgoing connections. A process that the arbiter bound to the region of its server keeps
# the publish lock and the name mark of each queue in that region, which the worker and the config process share.

# stdlib
import logging
from contextlib import contextmanager
from threading import RLock
from time import monotonic

# gevent
from gevent import sleep

# Zato
from zato.common.api import PubSub
from zato.common.broker_message import Server as BrokerMessageServer
from zato.common.pubsub.dlq import get_dlq_sub_key, get_dlq_topic_name, is_dlq_sub_key
from zato.common.pubsub.outgoing import audit_disabled_conn_types, find_outgoing_conn, get_outgoing_sub_config, \
    get_outgoing_sub_key, get_outgoing_topic_name, locate_outgoing_conn, parse_outgoing_sub_key
from zato.common.worker_slot import is_config_owner, is_config_process
from zato.server.base.config_manager.common import ConfigManagerImpl
from zato.server.control.hub import ModuleCtx as HubCtx
from zato.server.outgoing_region import get_outgoing_binding, pause_outgoing_delivery, resume_outgoing_delivery, \
    SharedNameMark, SharedPublishLock

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.ext.bunch import Bunch
    from zato.common.typing_ import any_, anydict, anytuple, callable_

    Bunch = Bunch

    publish_lock = RLock | SharedPublishLock

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# How long the worker waits for the change that renamed or deleted a connection to reach its configuration,
# and how often it checks, in seconds
_name_wait_timeout = HubCtx.Query_Timeout
_name_wait_interval = 0.01

# ################################################################################################################################
# ################################################################################################################################

class OutgoingNameMark:
    """ The name marks of a server of one process, whose configuration holds the current name of each connection.
    """

    def set_name(self, sub_key:'str', conn_name:'str') -> 'None':
        pass

    def clear(self, sub_key:'str') -> 'None':
        pass

    def is_current(self, sub_key:'str', conn_name:'str') -> 'bool':
        return True

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

def changes_shared_queues() -> 'bool':
    """ Whether a change of configuration in this process changes the queues of outgoing connections in the pub/sub
    database, which the config process and the process that no arbiter started do, while the worker applies the change
    that the config process relayed to its own state alone.
    """
    out = is_config_owner()
    return out

# ################################################################################################################################
# ################################################################################################################################

class OutgoingQueues(ConfigManagerImpl):
    """ The outgoing-queue side of a config manager.
    """

    _push_subs: 'anydict'

    _outgoing_sub_key_cache: 'set[str]'
    _outgoing_sub_key_lock: 'RLock'
    _outgoing_conn_locks: 'dict[str, publish_lock]'
    outgoing_queue_depth: 'OutgoingQueueDepth'
    outgoing_name_mark: 'OutgoingNameMark | SharedNameMark'

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

        # A process that the arbiter started shares the name marks with the other process of its server
        if binding := get_outgoing_binding():
            self.outgoing_name_mark = SharedNameMark(binding)
        else:
            self.outgoing_name_mark = OutgoingNameMark()

        self.init_outgoing_dlqs()

# ################################################################################################################################

    def get_outgoing_publish_lock(self, conn_type:'str', conn_id:'int') -> 'publish_lock':
        """ The lock under which publications to one outgoing connection take turns with its renames and deletes,
        in both processes of the server.
        """
        sub_key = get_outgoing_sub_key(conn_type, conn_id)

        with self._outgoing_sub_key_lock:
            lock = self._outgoing_conn_locks.get(sub_key)
            if not lock:
                if binding := get_outgoing_binding():
                    lock = SharedPublishLock(binding, sub_key)
                else:
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
    def hold_outgoing_queue(self, conn_type:'str', conn_id:'int', resumes_on_success:'bool'=True) -> 'any_':
        """ Holds one connection's queue still for as long as the block runs - nothing is published to it and its delivery
        stops between two rounds, so no message is in flight while the block changes the connection or the messages of its
        queue. A round in flight would otherwise resolve the connection's topics from a configuration the block is replacing,
        or go on with a message the block discarded or replaced. The delivery stops in the worker,
        whichever process holds the queue. Without resumes_on_success, a block that completes leaves the delivery stopped,
        and only a block that raises starts it again.
        """
        sub_key = get_outgoing_sub_key(conn_type, conn_id)
        delivery = self.server.pubsub_push_delivery

        with self.get_outgoing_publish_lock(conn_type, conn_id):

            # A connection that never had a queue has no delivery to stop
            has_queue = sub_key in self._outgoing_sub_key_cache

            if has_queue:
                pause_outgoing_delivery(delivery, sub_key)

            is_completed = False

            try:
                yield
                is_completed = True
            finally:

                # A queue the block deleted has nothing to start again ..
                is_still_there = sub_key in self._outgoing_sub_key_cache

                # .. and one whose delivery the caller starts again later stays stopped, unless the block raised.
                needs_resume = resumes_on_success or not is_completed

                if has_queue and is_still_there and needs_resume:
                    resume_outgoing_delivery(delivery, sub_key)

# ################################################################################################################################

    @contextmanager
    def pause_outgoing_queue_locally(self, conn_type:'str', conn_id:'int') -> 'any_':
        """ Stops the delivery of one connection's queue in the worker while the worker applies a change that the config
        process relayed, and starts it again afterwards, unless the change deleted the queue.
        """
        sub_key = get_outgoing_sub_key(conn_type, conn_id)
        delivery = self.server.pubsub_push_delivery

        # A queue without a delivery greenlet has nothing to stop or to start ..
        delivery.pause_sub_key(sub_key)

        try:
            yield
        finally:

            # .. and a queue that the change deleted has nothing to start again.
            if sub_key in self._outgoing_sub_key_cache:
                delivery.resume_sub_key(sub_key)

# ################################################################################################################################

    def hold_outgoing_queue_for_change(self, conn_type:'str', conn_id:'int') -> 'any_':
        """ Holds one connection's queue through hold_outgoing_queue while a change of configuration renames or deletes it
        in the process that changes the shared queues. The config process leaves the delivery of the queue in the worker
        stopped, and the worker starts it again once it applied the relayed change, so that no round runs under
        the configuration that the change replaces. The worker that applies the relayed change takes no publish lock,
        because it applies the change on the control channel through which it confirms a pause, and stops only
        a delivery of its own.
        """
        if is_config_process():
            out = self.hold_outgoing_queue(conn_type, conn_id, resumes_on_success=False)

        elif changes_shared_queues():
            out = self.hold_outgoing_queue(conn_type, conn_id)

        else:
            out = self.pause_outgoing_queue_locally(conn_type, conn_id)

        return out

# ################################################################################################################################

    def _wait_for_current_outgoing_name(self, conn_type:'str', conn_id:'int', sub_key:'str') -> 'None':
        """ Waits until the configuration of this process holds the name of one outgoing connection that the config process
        gave it last. The change that renames a connection reaches the worker after the config process released
        the publish lock of the queue, and a publication under the previous name would go to a topic that no queue reads.
        """
        deadline = monotonic() + _name_wait_timeout

        while True:

            # A connection that no longer exists in this process raises here ..
            conn_name, _ = locate_outgoing_conn(self.server, conn_type, conn_id)

            # .. one under the name that the config process gave it is ready for the publication ..
            if self.outgoing_name_mark.is_current(sub_key, conn_name):
                return

            # .. and one whose change did not arrive in time is refused.
            if monotonic() > deadline:
                message = f'Outgoing {conn_type} connection `{conn_name}` (id `{conn_id}`) was renamed'
                message += f' and the change did not reach this process within {_name_wait_timeout}s'
                raise Exception(message)

            sleep(_name_wait_interval)

# ################################################################################################################################

    def ensure_outgoing_subscription(self, conn_type:'str', conn_id:'int') -> 'anytuple':
        """ Makes sure that one outgoing connection has a topic and a queue, returning the topic's name and the connection's
        current name.
        """
        sub_key = get_outgoing_sub_key(conn_type, conn_id)

        # The name of the connection is the one that the config process gave it last ..
        self._wait_for_current_outgoing_name(conn_type, conn_id, sub_key)

        # .. and the topic is that name's.
        with self._outgoing_sub_key_lock:

            conn_name, _ = locate_outgoing_conn(self.server, conn_type, conn_id)
            topic_name = get_outgoing_topic_name(conn_type, conn_name)

            self._set_outgoing_topic_audit_flag(conn_type, topic_name)

            if sub_key not in self._outgoing_sub_key_cache:

                self.server.pubsub_backend.subscribe(sub_key, topic_name)
                self._add_outgoing_queue(sub_key, topic_name)

                logger.info('Created outgoing connection queue `%s` for topic `%s`', sub_key, topic_name)

                # The worker delivers the messages of the queue, and each process of the server lists, renames
                # and deletes the queue, so each of them adds it as well
                self.server.config_dispatcher.relay_only({
                    'action': BrokerMessageServer.Outgoing_Queue_Created.value,
                    'sub_key': sub_key,
                    'topic_name': topic_name,
                })

        return topic_name, conn_name

# ################################################################################################################################

    def _add_outgoing_queue(self, sub_key:'str', topic_name:'str') -> 'None':
        """ Adds the queue of an outgoing connection to this process, whose delivery starts if this process is the worker.
        """
        sub_config = get_outgoing_sub_config(sub_key, topic_name)
        self._push_subs[sub_key] = [sub_config]

        self.server.pubsub_push_delivery.start_sub_key(sub_key)

        self._outgoing_sub_key_cache.add(sub_key)

# ################################################################################################################################

    def on_config_event_Server_Outgoing_Queue_Created(self, msg:'Bunch') -> 'None':
        """ Adds the queue that another process of the server created on the first publication to its connection.
        """
        with self._outgoing_sub_key_lock:
            if msg.sub_key not in self._outgoing_sub_key_cache:
                self._add_outgoing_queue(msg.sub_key, msg.topic_name)

# ################################################################################################################################

    def rename_outgoing_subscription(self, conn_type:'str', conn_id:'int', old_name:'str', new_name:'str') -> 'None':
        """ Moves the topic of one outgoing connection to the connection's new name. The caller holds the queue
        through hold_outgoing_queue, so nothing is published to the topic and no round is in flight while it moves.
        """
        sub_key = get_outgoing_sub_key(conn_type, conn_id)

        # The worker that has not applied the rename yet publishes only once it has, including the first publication
        # that creates the queue ..
        if changes_shared_queues():
            self.outgoing_name_mark.set_name(sub_key, new_name)

        # .. and a connection that was never published to has no topic to move.
        if sub_key not in self._outgoing_sub_key_cache:
            return

        old_topic_name = get_outgoing_topic_name(conn_type, old_name)
        new_topic_name = get_outgoing_topic_name(conn_type, new_name)

        # The topic and its DLQ move in the pub/sub database once, and each process then reads the queue under the new name
        if changes_shared_queues():

            self.server.pubsub_backend.rename_topic(old_topic_name, new_topic_name)

            self.server.pubsub_backend.delete_topic_audit_flag(old_topic_name)
            self._set_outgoing_topic_audit_flag(conn_type, new_topic_name)

            logger.info('Moved outgoing connection queue `%s` from topic `%s` to `%s`',
                sub_key, old_topic_name, new_topic_name)

            self.rename_outgoing_dlq(conn_type, conn_id, old_name, new_name)

        sub_config = get_outgoing_sub_config(sub_key, new_topic_name)
        self._push_subs[sub_key] = [sub_config]

# ################################################################################################################################

    def delete_outgoing_subscription(self, conn_type:'str', conn_id:'int', conn_name:'str') -> 'None':
        """ Removes the queue of a deleted outgoing connection along with whatever it still held.
        """
        sub_key = get_outgoing_sub_key(conn_type, conn_id)

        # The queue is held first, so no round of its delivery moves a message to the DLQ while the DLQ goes away
        with self.hold_outgoing_queue_for_change(conn_type, conn_id):

            # A connection created later under the same id starts without a mark ..
            if changes_shared_queues():
                self.outgoing_name_mark.clear(sub_key)

            # .. and the DLQ goes first, while its queue's lock still exists.
            self.delete_outgoing_dlq(conn_type, conn_id, conn_name)

            if sub_key not in self._outgoing_sub_key_cache:
                return

            self.server.pubsub_push_delivery.stop_sub_key(sub_key)

            # The topic and its messages leave the pub/sub database once, and each process then drops the queue
            if changes_shared_queues():

                topic_name = get_outgoing_topic_name(conn_type, conn_name)
                dropped_count = self.server.pubsub_backend.get_total_count(sub_key, topic_name, 'pending')

                self.server.pubsub_backend.delete_topic(topic_name)
                self.server.pubsub_backend.delete_topic_audit_flag(topic_name)

                logger.info('Deleted outgoing connection queue `%s` for topic `%s`, messages dropped:%d',
                    sub_key, topic_name, dropped_count)

            del self._push_subs[sub_key]
            self._outgoing_sub_key_cache.remove(sub_key)

        # The lock is dropped once it is no longer held, and a process that never published to the connection has none
        with self._outgoing_sub_key_lock:
            if sub_key in self._outgoing_conn_locks:
                del self._outgoing_conn_locks[sub_key]

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

            # A rename a crash interrupted is finished here, the DLQ's as well, which is renamed after the queue
            for subscribed_topic in self.server.pubsub_backend.get_subscribed_topics(sub_key):
                if subscribed_topic != topic_name:
                    logger.info('Finishing the move of outgoing topic `%s` to `%s`', subscribed_topic, topic_name)
                    self.server.pubsub_backend.rename_topic(subscribed_topic, topic_name)

            dlq_sub_key = get_dlq_sub_key(conn_type, conn_id)
            dlq_topic_name = get_dlq_topic_name(conn_type, conn_name)

            for subscribed_topic in self.server.pubsub_backend.get_subscribed_topics(dlq_sub_key):
                if subscribed_topic != dlq_topic_name:
                    logger.info('Finishing the move of outgoing DLQ topic `%s` to `%s`', subscribed_topic, dlq_topic_name)
                    self.server.pubsub_backend.rename_topic(subscribed_topic, dlq_topic_name)

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
