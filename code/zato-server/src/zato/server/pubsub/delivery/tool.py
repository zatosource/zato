# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from copy import deepcopy
from logging import getLogger
from traceback import format_exc
from typing import cast, Iterable as iterable_

# gevent
from gevent import spawn
from gevent.lock import RLock

# Zato
from zato.common.odb.api import SQLRow
from zato.common.typing_ import cast_, list_
from zato.common.util.api import grouper
from zato.common.util.time_ import utcnow_as_ms
from zato.server.pubsub.delivery.message import GDMessage, NonGDMessage
from zato.server.pubsub.delivery._sorted_list import SortedList
from zato.server.pubsub.delivery.task import DeliveryTask

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import ValuesView
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.pubsub import HandleNewMessageCtx
    from zato.common.typing_ import any_, boolnone, callable_, callnone, dict_, dictlist, intset, set_, strlist, tuple_
    from zato.server.pubsub import PubSub
    from zato.server.pubsub.delivery.message import Message

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_pubsub.task')
logger_zato = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

sqlmsglist = list_['SQLRow']
sqlmsgiter = iterable_['SQLRow']

# ################################################################################################################################
# ################################################################################################################################

class PubSubTool:
    """ A utility object for pub/sub-related tasks.
    """
    def __init__(self,
        pubsub,        # type: PubSub
        parent,        # type: any_
        endpoint_type, # type: str
        is_for_services=False,  # type: bool
        deliver_pubsub_msg=None # type: callnone
    ) -> 'None':

        self.pubsub = pubsub
        self.parent = parent # This is our parent, e.g. an individual WebSocket on whose behalf we execute
        self.endpoint_type = endpoint_type

        self.server_name = self.pubsub.server.name
        self.server_pid = self.pubsub.server.pid

        # WSX connections will have their own callback but other connections use the default one
        self.deliver_pubsub_msg = deliver_pubsub_msg or self.pubsub.deliver_pubsub_msg # type: callable_

        # A broad lock for generic pub/sub matters
        self.lock = RLock()

        # Each sub_key will get its own lock for operations related to that key only
        self.sub_key_locks = {} # type: dict_[str, RLock]

        # How many messages to send in a single delivery group,
        # may be set individually for each subscription, defaults to 1
        self.batch_size = {} # type: dict_[str, int]

        # Which sub_keys this pubsub_tool handles
        self.sub_keys = set() # type: set_[str]

        # A sorted list of message references for each sub_key
        self.delivery_lists = {} # type: dict_[str, SortedList]

        # A pub/sub delivery task for each sub_key
        self.delivery_tasks = {} # type: dict_[str, DeliveryTask]

        # Last time we tried to pull GD messages from SQL, by sub_key
        self.last_gd_run = {} # type: dict_[str, float]

        # Register with this server's pubsub
        self.register_pubsub_tool()

        # How many times self.handle_new_messages has been called
        self.msg_handler_counter = 0

        # Is this tool solely dedicated to delivery of messages to Zato services
        self.is_for_services = is_for_services

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops all delivery asks belonging to this tool.
        """
        for item in self.delivery_tasks.values():
            try:
                item.stop()
            except Exception:
                logger.info('Ignoring exception in PubSubTool.stop -> %s', format_exc())

# ################################################################################################################################

    def register_pubsub_tool(self) -> 'None':
        """ Registers ourselves with this server's pubsub to let the other control when we should shut down
        our delivery tasks for each sub_key.
        """
        self.pubsub.register_pubsub_tool(self)

# ################################################################################################################################

    def get_sub_keys(self) -> 'strlist':
        """ Returns all sub keys this task handles, as a list.
        """
        with self.lock:
            return list(self.sub_keys)

# ################################################################################################################################

    def add_sub_key_no_lock(self, sub_key:'str') -> 'None':
        """ Adds metadata about a given sub_key - must be called with self.lock held.
        """
        # Already seen it - can be ignored
        if sub_key in self.sub_keys:
            return

        self.sub_keys.add(sub_key)
        self.batch_size[sub_key] = 1

        #
        # A dictionary that maps when GD messages were last time fetched from the SQL database for each sub_key.
        # Since fetching means we are issuing a single query for multiple sub_keys at a time, we need to fetch only these
        # messages that are younger than the oldest value for all of the sub_keys whose messages will be fetched.
        #
        # Let's say we have three sub_keys: a, b, c
        #
        # time 0001: pub to a, b, c
        # time 0001: store last_gd_run = 0001 for each of a, b, c
        # ---
        # time 0002: pub to a, b
        # time 0002: store last_gd_run = 0002 for a, b
        # ---
        # time 0003: pub to b, c
        # time 0003: store last_gd_run = 0003 for b, c
        # ---
        # time 0004: pub to c
        # time 0004: store last_gd_run = 0004 for c
        #
        # We now have: {a:0002, b:0003, c:0004}
        #
        # Let's say we now receive:
        #
        # time 0005: pub to a, b, c
        #
        # Because we want to have a single SQL query for all of a, b, c instead of querying the database for each of sub_key,
        # we need to look up values stored in this dictionary for each of the sub_key and use the smallest one - in this case
        # it would be 0002 for sub_key a. Granted, we know that there won't be any keys for b in the timespan of 0002-0003
        # or for c in the duration of 0003-004, so in the case of these other keys reaching but so back in time is a bit too much
        # but this is all fine anyway because the most important part is that we can still use a single SQL query.
        #
        # Similarly, had it been a pub to b, c in time 0005 then we would be using min of b and c which is 0003.
        #
        # The reason why this is fine is that when we query the database not only do we use this last_gd_run but we also give it
        # a delivery status to return messages by (initialized only) and on top of it, we provide it a list of message IDs
        # that are currently being delivered by tasks, so in other words, the database will never give us duplicates
        # that have been already delivered or are about to be.
        #

        delivery_list = SortedList()
        delivery_lock = RLock()

        self.delivery_lists[sub_key] = delivery_list
        self.sub_key_locks[sub_key] = delivery_lock

        sub = self.pubsub.get_subscription_by_sub_key(sub_key)

        if not sub:
            all_subs = self.pubsub.get_all_subscriptions()
            msg = 'Sub key `%s` not found among `%s`'
            logger.warning(msg, sub_key, all_subs)
            logger_zato.warning(msg, sub_key, all_subs)

            # Return explicitly
            return

        else:
            self.delivery_tasks[sub_key] = DeliveryTask(
                pubsub = self.pubsub,
                sub_config = sub.config,
                sub_key = sub_key,
                delivery_lock = delivery_lock,
                delivery_list = delivery_list,
                deliver_pubsub_msg = self.deliver_pubsub_msg,
                confirm_pubsub_msg_delivered_cb = self.confirm_pubsub_msg_delivered,
                enqueue_initial_messages_func = self.enqueue_initial_messages,
                pubsub_set_to_delete = self.pubsub.set_to_delete,
                pubsub_get_before_delivery_hook = self.pubsub.get_before_delivery_hook,
                pubsub_invoke_before_delivery_hook = self.pubsub.invoke_before_delivery_hook,
            )

# ################################################################################################################################

    def add_sub_key(self, sub_key:'str') -> 'None':
        """ Same as self.add_sub_key_no_lock but holds self.lock.
        """
        with self.lock:
            self.add_sub_key_no_lock(sub_key)
            self.pubsub.set_pubsub_tool_for_sub_key(sub_key, self)

# ################################################################################################################################

    def remove_sub_key(self, sub_key:'str') -> 'None':
        with self.lock:
            try:
                self.sub_keys.remove(sub_key)
                del self.batch_size[sub_key]
                del self.sub_key_locks[sub_key]

                del self.delivery_lists[sub_key]
                self.delivery_tasks[sub_key].stop()
                del self.delivery_tasks[sub_key]

            except Exception:
                logger.info('Exception during sub_key removal `%s`, e:`%s`', sub_key, format_exc())

    delete_by_sub_key = remove_sub_key

# ################################################################################################################################

    def has_sub_key(self, sub_key:'str') -> 'bool':
        with self.lock:
            return sub_key in self.sub_keys

# ################################################################################################################################

    def remove_all_sub_keys(self) -> 'None':
        sub_keys = deepcopy(self.sub_keys)
        for sub_key in sub_keys:
            self.remove_sub_key(sub_key)

# ################################################################################################################################

    def clear_task(self, sub_key:'str') -> 'None':
        task = self.delivery_tasks[sub_key]
        task.clear()

# ################################################################################################################################

    def trigger_update_task_sub_config(self, sub_key:'str') -> 'None':
        task = self.delivery_tasks[sub_key]
        task.update_sub_config()

# ################################################################################################################################

    def _add_non_gd_messages_by_sub_key(self, sub_key:'str', messages:'dictlist') -> 'None':
        """ Low-level implementation of add_non_gd_messages_by_sub_key, must be called with a lock for input sub_key.
        """
        for msg in messages:

            # Ignore messages that are replies meant to be delievered only to sub_keys
            # other than current one. This may happen because PubSub.trigger_notify_pubsub_tasks
            # sends non-GD messages to all sub_keys subscribed to topic, no matter what deliver_to_sk
            # of a message is. This is the reason why we need to sort it out here. Eventually,
            # PubSub.trigger_notify_pubsub_tasks should be changed to notify sub_keys if deliver_to_sk
            # does not point to them.
            if msg['deliver_to_sk']:
                if sub_key not in msg['deliver_to_sk']:
                    continue

            add = cast_('callable_', self.delivery_lists[sub_key].add)
            add(NonGDMessage(sub_key, self.server_name, self.server_pid, msg))

# ################################################################################################################################

    def add_non_gd_messages_by_sub_key(self, sub_key:'str', messages:'dictlist') -> 'None':
        """ Adds to local delivery queue all non-GD messages from input.
        """
        try:
            with self.sub_key_locks[sub_key]:
                self._add_non_gd_messages_by_sub_key(sub_key, messages)
        except Exception:
            e = format_exc()
            logger.warning(e)
            logger_zato.warning(e)

# ################################################################################################################################

    def _handle_new_messages(self, ctx:'HandleNewMessageCtx', delta:'int'=60) -> 'None':
        """ A callback invoked when there is at least one new message to be handled for input sub_keys.
        If has_gd is True, it means that at least one GD message available. If non_gd_msg_list is not empty,
        it is a list of non-GD message for sub_keys.
        """
        session = None

        try:
            if ctx.has_gd:
                session = self.pubsub.server.odb.session()
            else:
                if not ctx.non_gd_msg_list:
                    # This is an unusual situation but not an erroneous one because it is possible
                    # that we were triggered to deliver messages that have already expired in the meantime,
                    # in which case we just log on info level rather than warn.
                    logger.info('No messages received ({}) for cid:`{}`, has_gd:`{}` and sub_key_list:`{}`'.format(
                        ctx.non_gd_msg_list, ctx.cid, ctx.has_gd, ctx.sub_key_list))
                    return

            logger.info('Handle new messages, cid:%s, gd:%d, sub_keys:%s, len_non_gd:%d bg:%d',
                ctx.cid, int(ctx.has_gd), ctx.sub_key_list, len(ctx.non_gd_msg_list), ctx.is_bg_call)

            gd_msg_list = {} # type: dict_[str, sqlmsglist]

            # We need to have the broad lock first to read in messages for all the sub keys
            with self.lock:

                # Get messages for all sub_keys on input and break them out by each sub_key separately,
                # provided that we have a flag indicating that there should be some GD messages around in the database.
                if ctx.has_gd:
                    gd_messages_by_sk_list = self._fetch_gd_messages_by_sk_list(ctx.sub_key_list, ctx.pub_time_max, session)
                    gd_messages_by_sk_list = list(gd_messages_by_sk_list)
                    for msg in gd_messages_by_sk_list:
                        _sk_msg_list = gd_msg_list.setdefault(msg.sub_key, [])
                        _sk_msg_list.append(msg)

                # Note how we substract delta seconds from current time - this is because
                # it is possible that there will be new messages enqueued in between our last
                # run and current time's generation - the difference will be likely just a few
                # milliseconds but to play it safe we use by default a generous slice of 60 seconds.
                # This is fine because any SQL queries depending on this value will also
                # include other filters such as delivery_status.
                new_now = utcnow_as_ms() - delta

                # Go over all sub_keys given on input and carry out all operations while holding a lock for each sub_key
                for sub_key in ctx.sub_key_list:

                    # Accept all input non-GD messages
                    if ctx.non_gd_msg_list:
                        self._add_non_gd_messages_by_sub_key(sub_key, ctx.non_gd_msg_list)

                    # Push all GD messages, if there are any at all for this sub_key
                    if ctx.has_gd and sub_key in gd_msg_list:

                        topic_name = self.pubsub.get_topic_name_by_sub_key(sub_key)
                        self._push_gd_messages_by_sub_key(sub_key, topic_name, gd_msg_list[sub_key])

                        self.last_gd_run[sub_key] = new_now

                        logger.info('Storing last_gd_run of `%r` for sub_key:%s (d:%s)', new_now, sub_key, delta)

        except Exception:
            e = format_exc()
            logger.warning(e)
            logger_zato.warning(e)

        finally:
            if session:
                session.commit()
                session.close()

# ################################################################################################################################

    def handle_new_messages(self, ctx:'HandleNewMessageCtx') -> 'None':
        self.msg_handler_counter += 1
        try:
            _ = spawn(self._handle_new_messages, ctx) # noqa: F841
        except Exception:
            e = format_exc()
            logger.warning(e)
            logger_zato.warning(e)

# ################################################################################################################################

    def _fetch_gd_messages_by_sk_list(self,
        sub_key_list, # type: strlist
        pub_time_max, # type: float
        session=None  # type: SASession | None
    ) -> 'sqlmsgiter':
        """ Part of the low-level implementation of enqueue_gd_messages_by_sub_key, must be called with a lock for input sub_key.
        """

        # These are messages that we have already queued up and,
        # if we happen to pick them up in the database, they should be ignored.
        ignore_list = set() # type: intset

        for sub_key in sub_key_list:
            for msg in self.delivery_lists[sub_key]:
                msg = cast(GDMessage, msg)
                if msg.has_gd:
                    ignore_list.add(msg.endp_msg_queue_id)

        logger.info('Fetching GD messages by sk_list:`%s`, ignore:`%s`', sub_key_list, ignore_list)

        if self.last_gd_run:
            if len(sub_key_list) == 1:
                # Use .get because it is possible we have not fetched messages for that particular sub_key before,
                # i.e. self.last_gd_run may be non-empty because there are last GD runs for other keys,
                # just not for this one.
                min_last_gd_run = self.last_gd_run.get(sub_key_list[0])
            else:
                min_last_gd_run = min(value for key, value in self.last_gd_run.items() if key in sub_key_list)
        else:
            min_last_gd_run = 0.0

        # Tell type-checkers that we really have a float here now
        min_last_gd_run = cast_(float, min_last_gd_run)

        logger.info('Using min last_gd_run `%r`', min_last_gd_run)

        for msg in self.pubsub.get_sql_messages_by_sub_key(session, sub_key_list, min_last_gd_run, pub_time_max, ignore_list):
            yield msg

# ################################################################################################################################

    def _push_gd_messages_by_sub_key(self, sub_key:'str', topic_name:'str', gd_msg_list:'sqlmsgiter') -> 'None':
        """ Pushes all input GD messages to a delivery task for the sub_key.
        """
        count = 0
        msg_ids = [] # type: strlist

        for msg in gd_msg_list:

            msg_ids.append(msg.pub_msg_id)
            gd_msg = GDMessage(sub_key, topic_name, msg.get_value())
            delivery_list = self.delivery_lists[sub_key]
            delivery_list.add(gd_msg)
            # logger.info('Adding a GD message `%s` to delivery_list=%s (%s)', gd_msg.pub_msg_id, hex(id(delivery_list)), sub_key)
            count += 1

        # logger.info('Pushing %d GD message{}to task:%s; msg_ids:%s'.format(' ' if count==1 else 's '), count, sub_key, msg_ids)

# ################################################################################################################################

    def _enqueue_gd_messages_by_sub_key(self, sub_key:'str', gd_msg_list:'sqlmsgiter') -> 'None':
        """ Low-level implementation of self.enqueue_gd_messages_by_sub_key which expects the message list on input.
        Must be called with self.sub_key_locks[sub_key] held.
        """
        topic_name = self.pubsub.get_topic_name_by_sub_key(sub_key)
        self._push_gd_messages_by_sub_key(sub_key, topic_name, gd_msg_list)

# ################################################################################################################################

    def enqueue_gd_messages_by_sub_key(self, sub_key:'str', session:'SASession | None'=None) -> 'None':
        """ Fetches GD messages from SQL for sub_key given on input and adds them to local queue of messages to deliver.
        """
        with self.sub_key_locks[sub_key]:
            gd_msg_list = self._fetch_gd_messages_by_sk_list([sub_key], utcnow_as_ms(), session)
            self._enqueue_gd_messages_by_sub_key(sub_key, gd_msg_list)

# ################################################################################################################################

    def enqueue_initial_messages(self, sub_key:'str', topic_name:'str', endpoint_name:'str', _group_size:'int'=400) -> 'None':
        """ Looks up any messages for input task in the database and pushes them all and enqueues in batches any found.
        """
        with self.sub_key_locks[sub_key]:

            pub_time_max = utcnow_as_ms()
            session = None

            try:

                # One SQL session for all queries
                session = self.pubsub.server.odb.session()

                # Get IDs of any messages already queued up so as to break them out into batches of messages to fetch
                msg_ids = self.pubsub.get_initial_sql_msg_ids_by_sub_key(session, sub_key, pub_time_max)
                msg_ids = [elem.pub_msg_id for elem in msg_ids]

                if msg_ids:
                    len_msg_ids = len(msg_ids)
                    suffix = ' ' if len_msg_ids == 1 else 's '
                    groups = list(grouper(_group_size, msg_ids)) # type: strlist
                    len_groups = len(groups)

                    # This, we log using both loggers because we also run during server startup so we should
                    # let users know that their server has to do something extra
                    for _logger in logger, logger_zato:
                        _logger.info('Found %d initial message%sto enqueue for sub_key:`%s` (%s -> %s), g:%d, gs:%d',
                            len_msg_ids, suffix, sub_key, topic_name, endpoint_name, len_groups, _group_size)

                    for _, group in enumerate(groups, 1):
                        group = cast_('strlist', group)
                        group_msg_ids = [elem for elem in group if elem] # type: strlist
                        # logger.info('Enqueuing group %d/%d (gs:%d) (%s, %s -> %s) `%s`',
                        #    idx, len_groups, _group_size, sub_key, topic_name, endpoint_name, group_msg_ids)

                        msg_list = self.pubsub.get_sql_messages_by_msg_id_list(session, sub_key, pub_time_max, group_msg_ids)
                        self._enqueue_gd_messages_by_sub_key(sub_key, msg_list)

            except Exception:
                for _logger in logger, logger_zato:
                    _logger.warning('Could not enqueue initial messages for `%s` (%s -> %s), e:`%s`',
                        sub_key, topic_name, endpoint_name, format_exc())

            finally:
                if session:
                    session.close()

# ################################################################################################################################

    def confirm_pubsub_msg_delivered(self, sub_key:'str', delivered_list:'strlist') -> 'None':
        self.pubsub.confirm_pubsub_msg_delivered(sub_key, delivered_list)

# ################################################################################################################################

    def get_queue_depth(self, sub_key:'str') -> 'tuple_[int, int]':
        """ Returns the number of GD and non-GD messages queued up for input sub_key.
        """
        return self.delivery_tasks[sub_key].get_queue_depth()

# ################################################################################################################################

    def handles_sub_key(self, sub_key:'str') -> 'bool':
        with self.lock:
            return sub_key in self.sub_keys

# ################################################################################################################################

    def get_delivery_task(self, sub_key:'str') -> 'DeliveryTask':
        with self.lock:
            return self.delivery_tasks[sub_key]

# ################################################################################################################################

    def get_delivery_tasks(self) -> 'ValuesView[DeliveryTask]':
        with self.lock:
            return self.delivery_tasks.values()

# ################################################################################################################################

    def delete_messages(self, sub_key:'str', msg_list:'strlist') -> 'None':
        """ Marks one or more to be deleted from the delivery task by the latter's sub_key.
        """
        self.delivery_tasks[sub_key].delete_messages(msg_list)

# ################################################################################################################################

    def get_messages(self, sub_key:'str', has_gd:'boolnone'=None) -> 'list_[Message]':
        """ Returns all messages enqueued for sub_key without deleting them from their queue.
        """
        return self.delivery_tasks[sub_key].get_messages(has_gd)

# ################################################################################################################################

    def pull_messages(self, sub_key:'str', has_gd:'bool'=False) -> 'dictlist':
        """ Implements pull-style delivery - returns messages enqueued for sub_key, deleting them in progress.
        """
        with self.lock:
            return self.delivery_tasks[sub_key].pull_messages()

# ################################################################################################################################

    def get_message(self, sub_key:'str', msg_id:'str') -> 'Message':
        """ Returns a particular message enqueued for sub_key.
        """
        return self.delivery_tasks[sub_key].get_message(msg_id)

# ################################################################################################################################
# ################################################################################################################################
