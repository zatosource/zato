# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from copy import deepcopy
from logging import getLogger
from random import randint
from traceback import format_exc

# gevent
from gevent import sleep
from gevent.lock import RLock

# sortedcontainers
from sortedcontainers import SortedList

# Zato
from zato.common.time_util import datetime_from_ms
from zato.common.util import spawn_greenlet
from zato.server.pubsub import PubSub

# For pyflakes
PubSub = PubSub

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

class PubSubTask(object):
    """ A background task responsible for delivery of pub/sub messages each pub/sub endpoint may possibly subscribe to.
    """
    def __init__(self, sql_conn_func):
        self.sql_conn_func = sql_conn_func
        self.lock = RLock()

# ################################################################################################################################

class DeliveryTask(object):
    """ Runs a greenlet responsible for delivery of messages for a given sub_key.
    """
    def __init__(self, sub_key, delivery_lock, delivery_list, deliver_pubsub_msg_cb, confirm_pubsub_msg_delivered_cb):
        self.keep_running = True
        self.sub_key = sub_key
        self.delivery_lock = delivery_lock
        self.delivery_list = delivery_list
        self.deliver_pubsub_msg_cb = deliver_pubsub_msg_cb
        self.confirm_pubsub_msg_delivered_cb = confirm_pubsub_msg_delivered_cb

        spawn_greenlet(self.run)

    def _run_delivery(self):
        """ Actually attempts to deliver messages. Each time it runs, it gets all the messages
        that are still to be delivered from self.delivery_list.
        """
        for msg in self.delivery_list:
            try:
                self.deliver_pubsub_msg_cb(msg)

            except Exception, e:
                logger.warn('Could not deliver pub/sub message, e:`%s`', format_exc(e))

                # Do not attempt to deliver any other message, simply return and our
                # parent will sleep for a small amount of time and then re-run us,
                # thanks to which the next time we run we will again iterate over all the messages
                # currently queued up
                return

            else:
                # On successful delivery, remove this messages from SQL and our own delivery_list
                try:
                    self.confirm_pubsub_msg_delivered_cb(self.sub_key, msg.pub_msg_id)
                except Exception, e:
                    logger.warn('Could not update delivery status for msg:`%s`, e:`%s`', msg, format_exc(e))
                else:
                    with self.delivery_lock:
                        self.delivery_list.remove(msg)

        # Indicates that we have successfully delivered all messages currently queued up
        return True

    def run(self, no_msg_sleep_time=1):
        logger.info('Starting delivery task for sub_key:`%s`', self.sub_key)
        try:
            while self.keep_running:
                if not self.delivery_list:
                    sleep(no_msg_sleep_time) # No need to wake up too often if there is not much to do
                else:

                    # Get the list of all messaged IDs for which delivery was successful,
                    # indicating whether all currently lined up messages have been
                    # successfully delivered.
                    success = self._run_delivery()

                    # On success, sleep for a moment because we have just run out of all messages.
                    if success:
                        sleep(no_msg_sleep_time)

                    # Otherwise, sleep for a longer time because our endpoint must have returned an error.
                    # After this sleep, self._run_delivery will again attempt to deliver all messages
                    # we queued up. Note that we are the only delivery task for this sub_key  so when we sleep here
                    # for a moment, we do not block other deliveries.
                    else:
                        sleep(randint(10, 20))
        except Exception, e:
            logger.warn('Exception in delivery task for sub_key:`%s`, e:`%s`', self.sub_key, format_exc(e))

    def stop(self):
        logger.info('Stopping delivery task for sub_key:`%s`', self.sub_key)
        self.keep_running = False

    def get_queue_depth(self):
        """ Returns the number of GD and non-GD messages in delivery list.
        """
        gd = 0
        non_gd = 0

        for msg in self.delivery_list:
            if msg.has_gd:
                gd += 1
            else:
                non_gd += 1

        return gd, non_gd

# ################################################################################################################################

class Message(object):
    """ Wrapper for messages adding __cmp__ which uses a custom comparison protocol,
    by priority, then ext_pub_time, then pub_time.
    """
    def __cmp__(self, other, max_pri=9):
        return cmp(
            (max_pri - self.priority, self.ext_pub_time, self.pub_time),
            (max_pri - other.priority, other.ext_pub_time, other.pub_time)
        )

    def __repr__(self):
        return '<Msg sk:{} id:{} ext:{} exp:{} gd:{}>'.format(
            self.sub_key, self.pub_msg_id, self.ext_client_id, datetime_from_ms(self.expiration_time), self.has_gd)

    def to_dict(self):
        return {
            'pub_msg_id': self.pub_msg_id,
            'has_gd': self.has_gd,
        }

# ################################################################################################################################

class GDMessage(Message):
    """ A guaranteed delivery message initialized from SQL data.
    """
    def __init__(self, sub_key, msg):
        self.sub_key = sub_key
        self.pub_msg_id = msg.pub_msg_id
        self.pub_correl_id = msg.pub_correl_id
        self.in_reply_to = msg.in_reply_to
        self.ext_client_id = msg.ext_client_id
        self.group_id = msg.group_id
        self.position_in_group = msg.position_in_group
        self.pub_time = msg.pub_time
        self.ext_pub_time = msg.ext_pub_time
        self.data = msg.data
        self.mime_type = msg.mime_type
        self.priority = msg.priority
        self.expiration = msg.expiration
        self.expiration_time = msg.expiration_time
        self.has_gd = msg.has_gd

# ################################################################################################################################

class NonGDMessage(Message):
    """ A non-guaranteed delivery message initialized from a Python dict.
    """
    def __init__(self, sub_key, msg):
        self.sub_key = sub_key
        self.pub_msg_id = msg['pub_msg_id']
        self.pub_correl_id = msg['pub_correl_id']
        self.in_reply_to = msg['in_reply_to']
        self.ext_client_id = msg['ext_client_id']
        self.group_id = msg['group_id']
        self.position_in_group = msg['position_in_group']
        self.pub_time = msg['pub_time']
        self.ext_pub_time = msg['ext_pub_time']
        self.data = msg['data']
        self.mime_type = msg['mime_type']
        self.priority = msg['priority']
        self.expiration = msg['expiration']
        self.expiration_time = msg['expiration_time']
        self.has_gd = msg['has_gd']

# ################################################################################################################################

class PubSubTool(object):
    """ A utility object for pub/sub-related tasks.
    """
    def __init__(self, pubsub, parent, endpoint_type):
        self.pubsub = pubsub # type: PubSub
        self.parent = parent # This is our parent, e.g. an individual WebSocket on whose behalf we execute
        self.endpoint_type = endpoint_type

        # A broad lock for generic pub/sub matters
        self.lock = RLock()

        # Each sub_key will get its own lock for operations related to that key only
        self.sub_key_locks = {}

        # How many messages to send in a single delivery group,
        # may be set individually for each subscription, defaults to 1
        self.batch_size = {}

        # Which sub_keys this pubsub_tool handles
        self.sub_keys = set()

        # A sorted list of message references for each sub_key
        self.delivery_lists = {}

        # A pub/sub delivery task for each sub_key
        self.delivery_tasks = {}

        # For each sub key, when was an SQL query last executed
        # that SELECT-ed latest messages for that sub_key.
        self.last_sql_run = {}

        # Register with this server's pubsub
        self.register_pubsub_tool()

# ################################################################################################################################

    def register_pubsub_tool(self):
        """ Registers ourselves with this server's pubsub to let the other control when we should shut down
        our delivery tasks for each sub_key.
        """
        self.pubsub.register_pubsub_tool(self)

# ################################################################################################################################

    def add_sub_key_no_lock(self, sub_key):
        """ Adds metadata about a given sub_key - must be called with self.lock held.
        """
        # Already seen it - can be ignored
        if sub_key in self.sub_keys:
            return

        self.sub_keys.add(sub_key)
        self.batch_size[sub_key] = 1
        self.last_sql_run[sub_key] = None

        delivery_list = SortedList()
        delivery_lock = RLock()

        self.delivery_lists[sub_key] = delivery_list
        self.delivery_tasks[sub_key] = DeliveryTask(
            sub_key, delivery_lock, delivery_list, self.parent.deliver_pubsub_msg, self.confirm_pubsub_msg_delivered)

        self.sub_key_locks[sub_key] = delivery_lock

# ################################################################################################################################

    def add_sub_key(self, sub_key):
        """ Same as self.add_sub_key_no_lock but holds self.lock.
        """
        with self.lock:
            self.add_sub_key_no_lock(sub_key)
            self.pubsub.set_pubsub_tool_for_sub_key(sub_key, self)

# ################################################################################################################################

    def remove_sub_key(self, sub_key):
        with self.lock:
            try:
                self.sub_keys.remove(sub_key)
                del self.batch_size[sub_key]
                del self.last_sql_run[sub_key]
                del self.sub_key_locks[sub_key]

                del self.delivery_lists[sub_key]
                self.delivery_tasks[sub_key].stop()
                del self.delivery_tasks[sub_key]

            except Exception, e:
                logger.warn('Exception during sub_key removal `%s`, e:`%s`', sub_key, format_exc(e))

# ################################################################################################################################

    def remove_all_sub_keys(self):
        sub_keys = deepcopy(self.sub_keys)
        for sub_key in sub_keys:
            self.remove_sub_key(sub_key)

# ################################################################################################################################

    def _add_non_gd_messages_by_sub_key(self, sub_key, messages):
        """ Low-level implementation of add_non_gd_messages_by_sub_key,
        must be called with a lock for input sub_key.
        """
        for msg in messages:
            self.delivery_lists[sub_key].add(NonGDMessage(sub_key, msg))

# ################################################################################################################################

    def add_non_gd_messages_by_sub_key(self, sub_key, messages):
        """ Adds to local delivery queue all non-GD messages from input.
        """
        with self.sub_key_locks[sub_key]:
            self._add_non_gd_messages_by_sub_key(sub_key, messages)

# ################################################################################################################################

    def handle_new_messages(self, cid, has_gd, sub_key_list, non_gd_msg_list):
        """ A callback invoked when there is at least one new message to be handled for input sub_keys.
        If has_gd is True, it means that at least one GD message available. If non_gd_msg_list is not empty,
        it is a list of non-GD message for sub_keys.
        """
        if not has_gd:
            if not non_gd_msg_list:
                raise ValueError('No messages received ({}) for cid:`{}`, has_gd:`{}` and sub_key_list:`{}`'.format(
                    non_gd_msg_list, cid, has_gd, sub_key_list))
        # Iterate over all input sub keys and carry out all operations while holding a lock for each sub_key
        for sub_key in sub_key_list:
            with self.sub_key_locks[sub_key]:

                # Fetch all GD messages, if there are any at all
                if has_gd:
                    self._fetch_gd_messages_by_sub_key(sub_key)

                # Accept all input non-GD messages
                if non_gd_msg_list:
                    self._add_non_gd_messages_by_sub_key(sub_key, non_gd_msg_list)

# ################################################################################################################################

    def _fetch_gd_messages_by_sub_key(self, sub_key, session=None):
        """ Low-level implementation of fetch_gd_messages_by_sub_key,
        must be called with a lock for input sub_key.
        """
        for msg in self.pubsub.get_sql_messages_by_sub_key(sub_key, self.last_sql_run[sub_key], session):
            self.delivery_lists[sub_key].add(GDMessage(sub_key, msg))

# ################################################################################################################################

    def fetch_gd_messages_by_sub_key(self, sub_key, session=None):
        """ Fetches GD messages from SQL for sub_key given on input and adds them to local queue of messages to deliver.
        """
        with self.sub_key_locks[sub_key]:
            self._fetch_gd_messages_by_sub_key(sub_key, session)

# ################################################################################################################################

    def confirm_pubsub_msg_delivered(self, sub_key, pub_msg_id):
        self.pubsub.confirm_pubsub_msg_delivered(sub_key, pub_msg_id)

# ################################################################################################################################

    def get_queue_depth(self, sub_key):
        """ Returns the number of GD and non-GD messages queued up for input sub_key.
        """
        with self.sub_key_locks[sub_key]:
            return self.delivery_tasks[sub_key].get_queue_depth()

# ################################################################################################################################

    def handles_sub_key(self, sub_key):
        with self.lock:
            return sub_key in self.sub_keys

# ################################################################################################################################
