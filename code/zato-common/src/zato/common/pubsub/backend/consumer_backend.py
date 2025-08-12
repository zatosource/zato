# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# gevent
from gevent.lock import RLock

# Zato
from zato.common.util.api import spawn_greenlet
from zato.common.pubsub.backend.common import Backend, ModuleCtx as CommonModuleCtx
from zato.common.pubsub.consumer import start_public_consumer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.broker.client import BrokerClient
    from zato.common.typing_ import callable_, dict_, strdict, strlist
    from zato.server.connection.amqp_ import Consumer
    from zato.server.base.worker import WorkerStore

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ConsumerBackend(Backend):
    """ The consumer backend for the ParallelServer, i.e. the container for message listeners.
    """
    consumers: 'dict_[str, Consumer]' # Maps sub_keys to Consumer objects

    def __init__(self, worker_store:'WorkerStore', broker_client:'BrokerClient') -> 'None':

        self.worker_store = worker_store
        self.broker_client = broker_client
        self.consumers = {}

        # This is a dictionary per-sub_key locks used to manipulate a specific consumer
        self._sub_key_lock:'dict_[str, RLock]' = {}

        super().__init__(broker_client)

# ################################################################################################################################

    def _add_consumer(self, sub_key:'str', consumer:'Consumer') -> 'None':
        self.consumers[sub_key] = consumer

# ################################################################################################################################

    def _remove_consumer(self, sub_key:'str') -> 'None':
        _ = self.consumers.pop(sub_key)

# ################################################################################################################################

    def start_public_queue_consumer(
        self,
        cid: 'str',
        topic_name_list: 'strlist',
        sec_name: 'str',
        sub_key: 'str',
        is_active: 'bool',
        on_msg_callback:'callable_',
    ) -> 'None':

        # Get or create a per-sub_key lock
        with self._main_lock:
            if sub_key not in self._sub_key_lock:
                _lock = RLock()
                self._sub_key_lock[sub_key] = _lock
            else:
                _lock = self._sub_key_lock[sub_key]

        # .. create a new consumer if one doesn't exist yet ..
        with _lock:

            # .. update all the bindings for input topics ..
            binding_changes = self.broker_client.update_bindings(cid, sub_key, CommonModuleCtx.Exchange_Name, sub_key, topic_name_list)

            # .. now start a consumer unless we already have one ..
            if sub_key not in self.consumers:

                logger.debug(f'[{cid}] Creating a new consumer for sub_key=`{sub_key}`')

                # .. start a background consumer ..
                result = spawn_greenlet(
                    start_public_consumer,
                    cid,
                    sec_name,
                    sub_key,
                    on_msg_callback,
                    is_active
                )

                # .. get the actual consumer object ..
                consumer:'Consumer' = result.get() # type: ignore

                # .. store it for later use ..
                self._add_consumer(sub_key, consumer)

        # .. confirm it's started ..
        added = binding_changes['added']
        removed = binding_changes['removed']

        added_msg = f'[{cid}] Successfully subscribed `{sec_name}` to `{added}` with key `{sub_key}`, all topics `{topic_name_list}` (running={is_active})'
        remaining_topics = sorted(topic for topic in topic_name_list if topic not in removed)
        removed_msg = f'[{cid}] Unsubscribed `{sec_name}` from `{removed}` with key `{sub_key}`, still subscribed to `{remaining_topics}`'
        not_changed_msg = f'[{cid}] Topics for `{sub_key}` are `{topic_name_list}` (running={is_active})'

        if added or removed:
            if added:
                logger.info(added_msg)
            if removed:
                logger.info(removed_msg)
        else:
            logger.info(not_changed_msg)

# ################################################################################################################################

    def stop_public_queue_consumer(self, cid:'str', sub_key:'str') -> 'None':

        # Get the consumer for this subscription ..
        if consumer := self.consumers.get(sub_key):

            # .. first, stop it ..
            consumer.stop()
            self._remove_consumer(sub_key)

            # .. now, log success.
            logger.debug(f'[{cid}] Stopped consumer for `{sub_key}`')

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_DELETE(self, cid:'str', sub_key:'str') -> 'None':

        # Log what we're about to do
        logger.info(f'[{cid}] Deleting consumer for `{sub_key}`')

        # Get all the bindings for that consumer ..
        bindings = self.broker_client.get_bindings_by_queue(cid, sub_key, CommonModuleCtx.Exchange_Name)

        # .. extrac topic names (same as routing key) ..
        topic_names = [item['routing_key'] for item in bindings] # type: ignore
        topic_names.sort()

        logger.info(f'[{cid}] Consumer for `{sub_key}` is subscribed to {topic_names}')

        # .. go through all of them ..
        for topic_name in topic_names:

            # .. delete that binding ..
            self.broker_client.delete_bindings(
                cid,
                sub_key,
                CommonModuleCtx.Exchange_Name,
                sub_key,
                topic_name,
            )

        # .. now, stop the consumer ..
        self.stop_public_queue_consumer(cid, sub_key)

        # .. and delete its now-no-longer-in-use queue ..
        self.broker_client.delete_queue(sub_key)

        # .. and log success.
        logger.info(f'[{cid}] Deleted consumer for `{sub_key}`')

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid:'str' = msg['cid']
        sub_key:'str' = msg['sub_key']
        is_active:'bool' = msg['is_active']
        sec_name:'str' = msg['sec_name']
        topic_name_list:'strlist' = msg['topic_name_list']

        _ = self.start_public_queue_consumer(
            cid,
            topic_name_list,
            sec_name,
            sub_key,
            is_active,
            self.worker_store.on_pubsub_public_message_callback
        )

# ################################################################################################################################

    def on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT(self, msg:'strdict') -> 'None':

        # Local aliases
        cid:'str' = msg['cid']
        sub_key:'str' = msg['sub_key']
        is_active:'bool' = msg['is_active']

        topic_name_list:'strlist' = msg['topic_name_list']
        topic_name_list = sorted(topic_name_list)

        # Do we have such a consumer ..
        if consumer := self.consumers.get(sub_key):

            err_msg = f'[{cid}] Found consumer by sub_key: {sub_key} -> {topic_name_list} -> {self.consumers}'
            logger.warning(err_msg)

            # .. get a queue for that consumer ..
            queue_name = consumer.config.queue

            # .. first off, update all the bindings pointing to it = update all the topics pointing to it ..
            _ = self.broker_client.update_bindings(cid, sub_key, 'pubsubapi', queue_name, topic_name_list)

            # .. now, make sure the consumer is started or stopped, depending on what the is_active flag tells us ..

            if is_active:
                if consumer.is_stopped:

                    # .. tell it should keep running - this is used in its .start methodd ..
                    consumer.keep_running = True

                    # .. log what we're about to do ..
                    logger.info(f'[{cid}] Starting consumer for sub_key: {sub_key} -> {topic_name_list}')

                    # .. do run it ..
                    _ = spawn_greenlet(consumer.start)

            else:
                if not consumer.is_stopped:
                    logger.info(f'[{cid}] Stopping consumer for sub_key: {sub_key} -> {topic_name_list}')
                    consumer.stop()

        # .. no consumer = we cannot continue.
        else:
            err_msg = f'[{cid}] on_broker_msg_PUBSUB_SUBSCRIPTION_EDIT: No such consumer by sub_key: {sub_key} -> {topic_name_list} -> {self.consumers}'
            logger.warning(err_msg)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_EDIT(self, msg:'strdict') -> 'None':

        # Local aliases
        cid:'str' = msg['cid']
        new_topic_name:'str' = msg['new_topic_name']
        old_topic_name:'str' = msg['old_topic_name']

        # Call the broker client to rename the topic by changing all bindings
        self.broker_client.rename_topic(cid, old_topic_name, new_topic_name, CommonModuleCtx.Exchange_Name)

# ################################################################################################################################

    def on_broker_msg_PUBSUB_TOPIC_DELETE(self, msg:'strdict') -> 'None':

        # Local aliases
        cid:'str' = msg['cid']
        topic_name:'str' = msg['topic_name']

        # Delete all bindings for this topic from the exchange
        self.broker_client.delete_topic(cid, topic_name, CommonModuleCtx.Exchange_Name)

# ################################################################################################################################
