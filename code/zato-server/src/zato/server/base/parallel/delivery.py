# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger
from traceback import format_exc

# gevent
from gevent import joinall, sleep, spawn
from gevent.event import Event
from gevent.lock import BoundedSemaphore, RLock

# SQLAlchemy
from sqlalchemy.exc import DBAPIError

# Zato
from zato.common.api import PubSub
from zato.common.db_env.database import get_database_values
from zato.common.db_env.errors import is_transient
from zato.common.db_env.outage import SharedOutageTracker
from zato.common.pubsub.delivery_scope import new_delivery_scope
from zato.common.pubsub.sql.errors import PubSubDuplicateMsgID
from zato.common.pubsub.sql.fenced_ack import PubSubAckConflict
from zato.common.pubsub.sql.replaced import PubSubReplaced
from zato.common.worker_slot import is_config_process
from zato.server.base.parallel.delivery_batch import commit_and_claim, commit_delivery_scope, deliver_atomic_batch
from zato.server.base.parallel.delivery_fetch import Delivery_Batch_Max_Len, Delivery_Batch_Size, fetch_new, wait_push
from zato.server.base.parallel.delivery_group import GroupDelivery

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from zato.common.pubsub.sql.backend import SQLPubSubBackend
    from zato.common.typing_ import anydict, anylist, floatnone, strset
    from zato.server.base.parallel import ParallelServer

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The push deliveries of one server use at most this fraction of the connections of the pub/sub pool at a time,
# so that when a broadcast wakes up all of its push subscribers together, the remaining connections stay available
# to the publishers, whose commits are shared, and to the pulling clients.
_delivery_pool_share_numerator = 3
_delivery_pool_share_denominator = 4

# How long to wait for a subscriber's delivery greenlet to come back between two batches, which covers
# the batch it may have started just before it was asked to pause.
_pause_join_timeout = 30

# How long a delivery greenlet waits after a fetch that raised
_fetch_error_sleep = PubSub.Delivery.Fetch_Error_Sleep

_outgoing_sub_key_prefix = PubSub.Outgoing.Sub_Key_Prefix

sub_key_greenlet_dict = dict[str, 'Greenlet']
greenletlist = list['Greenlet']

# A batch of a push subscriber with the payload epoch under which its payloads were read
push_batch = tuple['anylist', int]

# ################################################################################################################################
# ################################################################################################################################

class PushDelivery(GroupDelivery):
    """ Delivers messages from the SQL pub/sub backend to target services and REST
    endpoints by maintaining one greenlet per subscriber key. All greenlets share
    one backend - a blocking fetch waits on the backend's per-subscriber event that
    publications set, so no greenlet needs a dedicated database connection.
    """

    def __init__(self, server:'ParallelServer', backend:'SQLPubSubBackend') -> 'None':
        self.server = server
        self.backend = backend
        self._stop_event = Event()
        self._greenlets:'sub_key_greenlet_dict' = {}
        self._paused:'strset' = set()
        self._lock = RLock()

        # Each read of a queue and each recorded attempt holds one of these slots while it uses a connection,
        # and no delivery holds one while it waits for a publication or sends a message to its endpoint.
        pool_size = get_database_values()['pool_size']
        slot_count = pool_size * _delivery_pool_share_numerator // _delivery_pool_share_denominator
        self._database_slots = BoundedSemaphore(slot_count)

        # An outage of the database interrupts the delivery loops of all the subscribers at once,
        # so it is logged once for all of them.
        self._outage = SharedOutageTracker('PubSub delivery')

# ################################################################################################################################

    def start_sub_key(self, sub_key:'str') -> 'None':
        """ Spawn a delivery greenlet for the given subscriber key. The config process delivers nothing.
        """
        if is_config_process():
            return

        with self._lock:
            if sub_key not in self._greenlets:
                self._greenlets[sub_key] = spawn(self._delivery_loop, sub_key)

# ################################################################################################################################

    def stop_sub_key(self, sub_key:'str') -> 'None':
        """ Kill the delivery greenlet for the given subscriber key.
        """
        with self._lock:

            # A stopped subscriber is not a paused one either, or the same key would never run again if it came back
            self._paused.discard(sub_key)

            if greenlet := self._greenlets.pop(sub_key, None):
                greenlet.kill()

# ################################################################################################################################

    def pause_sub_key(self, sub_key:'str', join_timeout:'floatnone'=None) -> 'None':
        """ Stops the delivery greenlet of one subscriber between two of its batches, rather than
        wherever it happens to be, which is what a queue being moved needs - a message whose delivery
        is cut in half is never acknowledged and goes out a second time when the queue starts again.
        A pause that the config process asked for waits for a shorter time, within the deadline of its query.
        """
        # The module's timeout is read at the time of the call, not at the time of the definition
        if join_timeout is None:
            join_timeout = _pause_join_timeout

        with self._lock:
            self._paused.add(sub_key)
            greenlet = self._greenlets.pop(sub_key, None)

        # A subscriber whose greenlet never ran has nothing to wait for
        if not greenlet:
            return

        # The loop notices the pause only once it is between batches, and a fetch of its own blocks
        # for a while, so waking that fetch up is what makes the pause take effect right away ..
        self.backend.notify_sub_keys([sub_key])

        # .. and this is where whatever is being delivered right now is waited for ..
        _ = greenlet.join(timeout=join_timeout)

        # .. while a greenlet still busy after all that time is stopped where it stands,
        # .. which is the same at-least-once trade-off that a server shutdown makes.
        if not greenlet.ready():
            logger.info('Delivery greenlet for sub_key `%s` did not pause in time, stopping it now', sub_key)
            greenlet.kill()

# ################################################################################################################################

    def resume_sub_key(self, sub_key:'str') -> 'None':
        """ Starts a paused subscriber's delivery greenlet again, under the sub key it always had.
        """
        with self._lock:
            self._paused.discard(sub_key)

        self.start_sub_key(sub_key)

# ################################################################################################################################

    def pause_all(self, join_timeout:'float') -> 'None':
        """ Pauses every subscriber of the worker at once, each between two of its batches, so that a message whose
        delivery is in progress remains in its queue for the next delivery of the key.
        """
        with self._lock:
            sub_keys = list(self._greenlets)

        pauses:'greenletlist' = []

        for sub_key in sub_keys:
            pause = spawn(self.pause_sub_key, sub_key, join_timeout)
            pauses.append(pause)

        _ = joinall(pauses)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stop all delivery greenlets on server shutdown.
        """
        self._stop_event.set()

        with self._lock:
            for greenlet in self._greenlets.values():
                greenlet.kill()
            self._greenlets.clear()

# ################################################################################################################################

    def _delivery_loop(self, sub_key:'str') -> 'None':
        """ Deliver messages for one subscriber key until stopped. A blocking fetch
        waits on the subscriber's wake-up event, so the loop sleeps while the queue
        is empty and resumes the moment a publication lands.
        """
        logger.info('PubSub delivery greenlet started for sub_key `%s`', sub_key)

        try:
            self._run_delivery_loop(sub_key)

        # Another server took over the pub/sub database, so this one delivers nothing anymore.
        except PubSubReplaced as e:
            logger.info('PubSub delivery greenlet ended for sub_key `%s`: %s', sub_key, e)
            return

        finally:
            self._outage.on_stopped(sub_key)

        logger.info('PubSub delivery greenlet stopped for sub_key `%s`', sub_key)

# ################################################################################################################################

    def _run_delivery_loop(self, sub_key:'str') -> 'None':
        """ Delivers the messages of one subscriber key until stopped.
        """
        if sub_key.startswith(_outgoing_sub_key_prefix):
            self._run_outgoing_loop(sub_key)
        else:
            self._run_push_loop(sub_key)

# ################################################################################################################################

    def _is_running(self, sub_key:'str') -> 'bool':
        """ Whether the delivery loop of a subscriber key is to continue - the server is not stopping
        and the subscriber is neither removed nor paused.
        """
        if self._stop_event.is_set():
            return False

        if sub_key not in self.server.config_manager._push_subs:
            return False

        out = sub_key not in self._paused
        return out

# ################################################################################################################################

    def _on_loop_error(self, sub_key:'str', error:'Exception') -> 'None':
        """ Records an error of one round of the delivery loop of a subscriber, in the except block that caught it.
        """
        if isinstance(error, PubSubAckConflict):
            logger.info('PubSub batch for sub_key `%s` concluded by another delivery: %s', sub_key, error)

        elif isinstance(error, PubSubDuplicateMsgID):
            logger.warning('PubSub batch for sub_key `%s` not committed, a publication was refused: %s', sub_key, error)

        elif isinstance(error, DBAPIError):
            self._on_database_error(sub_key, error)

        # .. any other error is logged with its traceback.
        else:
            logger.warning('PubSub delivery error for sub_key `%s`: %s', sub_key, format_exc())
            sleep(_fetch_error_sleep)

# ################################################################################################################################

    def _on_database_error(self, sub_key:'str', error:'DBAPIError') -> 'None':
        """ Records a database error of the delivery loop of a subscriber and pauses the loop before it runs again.
        """
        # An unavailable database or a transaction that may run again unchanged is an outage of the delivery as a whole ..
        if is_transient(error):
            self._outage.on_failure(sub_key, error)

        # .. while any other database error concerns this subscriber alone.
        else:
            logger.warning('PubSub delivery error for sub_key `%s`: %s', sub_key, format_exc())

        sleep(_fetch_error_sleep)

# ################################################################################################################################

    def _run_outgoing_loop(self, sub_key:'str') -> 'None':
        """ Drains what is pending for the queue of an outgoing connection and then delivers new messages until stopped.
        """
        # On startup, drain everything still unacknowledged for this subscriber ..
        while self._is_running(sub_key):
            try:
                read_epoch = self.backend.payload_cache.get_epoch()
                with self._database_slots:
                    pending = self.backend.fetch_pending(sub_key, max_messages=Delivery_Batch_Size)
                self._outage.on_success(sub_key)
                if not pending:
                    break
                self._deliver_outgoing_batch(pending, sub_key, read_epoch)

            except PubSubReplaced:
                raise

            except Exception as e:
                self._on_loop_error(sub_key, e)

        # .. then wait for new messages.
        while self._is_running(sub_key):
            try:
                messages, read_epoch = fetch_new(self.backend, self._database_slots, sub_key)
                self._outage.on_success(sub_key)
                if messages:
                    self._deliver_outgoing_batch(messages, sub_key, read_epoch)

            except PubSubReplaced:
                raise

            except Exception as e:
                self._on_loop_error(sub_key, e)

# ################################################################################################################################

    def _run_push_loop(self, sub_key:'str') -> 'None':
        """ Delivers the batches of a push subscriber until stopped. Each batch is claimed in the commit that
        acknowledges the batch before it, and a subscriber whose claim found nothing waits for a publication.
        A round that fails leaves its batch unacknowledged, and the next claim claims it again before any newer message.
        """
        batch:'push_batch' = ([], 0)

        while self._is_running(sub_key):
            try:
                batch = self._run_push_cycle(sub_key, batch)
                self._outage.on_success(sub_key)

            except PubSubReplaced:
                raise

            except Exception as e:
                batch = ([], 0)
                self._on_loop_error(sub_key, e)

# ################################################################################################################################

    def _run_push_cycle(self, sub_key:'str', batch:'push_batch') -> 'push_batch':
        """ Runs one round of the delivery loop of a push subscriber with the batch that the previous round left,
        and returns the batch for the next round.
        """
        messages, read_epoch = batch

        # A REST endpoint may take several messages in one request, and a batch holds at least that many ..
        push_batch_size = self._get_push_batch_size(sub_key)
        max_messages = max(Delivery_Batch_Size, push_batch_size)

        # .. a subscriber with no batch claims one, and one whose claim found nothing waits for a publication ..
        if not messages:
            out = commit_and_claim(self.backend, self._database_slots, new_delivery_scope(), sub_key,
                max_messages, Delivery_Batch_Max_Len)

            claimed, _ = out

            if not claimed:
                out = wait_push(self.backend, self.server.config_manager, self._paused, sub_key)

            return out

        # .. any other one delivers its batch, in groups or one message at a time ..
        config_by_topic = self._get_config_by_topic(sub_key)

        if push_batch_size > 1:
            scope = self._deliver_group_batch(messages, config_by_topic, sub_key, read_epoch, push_batch_size)
        else:
            scope = deliver_atomic_batch(self.backend, self._paused, self._deliver_one, messages, config_by_topic,
                sub_key, read_epoch)

        # .. and commits what it concluded together with the claim of its next batch, unless it is to stop,
        # .. in which case it commits what it concluded alone.
        if self._is_running(sub_key):
            out = commit_and_claim(self.backend, self._database_slots, scope, sub_key, max_messages,
                Delivery_Batch_Max_Len)
        else:
            commit_delivery_scope(self.backend, scope, sub_key)
            out = ([], 0)

        return out

# ################################################################################################################################

    def _get_push_batch_size(self, sub_key:'str') -> 'int':
        """ Returns how many messages one push request of a subscriber key holds, which is one for a push to a service.
        """
        sub_config = self.server.config_manager._push_subs[sub_key][0]

        if sub_config['push_type'] != PubSub.Push_Type.REST:
            return 1

        out = sub_config['push_batch_size']
        return out

# ################################################################################################################################

    def _get_config_by_topic(self, sub_key:'str') -> 'anydict':
        """ Returns the configuration of each subscription of a subscriber key, by the name of its topic.
        """
        config_list = self.server.config_manager._push_subs[sub_key]

        out:'anydict' = {}

        for config in config_list:
            out[config['topic_name']] = config

        return out

# ################################################################################################################################

    def _deliver_outgoing_batch(self, messages:'anylist', sub_key:'str', read_epoch:'int') -> 'None':
        """ Delivers a batch of the queue of an outgoing connection, retrying each message individually
        and acknowledging each message as it is concluded. An acknowledgement removes this subscriber's delivery rows only -
        a message expired or undeliverable for this subscriber stays behind for every other subscriber that needs it.
        """
        config_by_topic = self._get_config_by_topic(sub_key)

        for message in messages:

            # A queue asked to pause stops between two of its messages, and what is left of the batch
            # stays in the queue, to go out when the queue starts again.
            if sub_key in self._paused:
                break

            sub_config = config_by_topic[message['topic_name']]

            # A message that was not concluded is not acked, and nothing behind it is either ..
            if not self._deliver_one(message, sub_config, sub_key, read_epoch, None):
                break

            msg_id = message['msg_id']
            delivery_attempt = message['delivery_attempt']

            # .. and each message is acked as soon as it is concluded, counting out only what the ack removed,
            # .. so a delivery stopped in the middle of a batch leaves no concluded message behind,
            # .. and only with the attempt that this server recorded, so that a message handed out again stays.
            fully_delivered_count = self.backend.ack_delivered(sub_key, msg_id, delivery_attempt)
            self.server.config_manager.outgoing_queue_depth.lower(sub_key, fully_delivered_count)

# ################################################################################################################################
# ################################################################################################################################
