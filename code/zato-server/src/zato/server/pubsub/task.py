# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from bisect import bisect_left
from copy import deepcopy
from json import loads
from logging import getLogger
from socket import error as SocketError
from threading import current_thread
from traceback import format_exc

# gevent
from gevent import sleep, spawn
from gevent.lock import RLock
from gevent.thread import getcurrent

# sortedcontainers
from sortedcontainers import SortedList as _SortedList

# Python 2/3 compatibility
from future.utils import iteritems

# Zato
from zato.common import GENERIC, PUBSUB
from zato.common.pubsub import PubSubMessage
from zato.common.util import grouper, spawn_greenlet
from zato.common.util.time_ import datetime_from_ms, utcnow_as_ms
from zato.server.pubsub import PubSub

# ################################################################################################################################

# For pyflakes
PubSub = PubSub

# ################################################################################################################################

logger = getLogger('zato_pubsub.task')
logger_zato = getLogger('zato')

# ################################################################################################################################

_hook_action = PUBSUB.HOOK_ACTION
_notify_methods = (PUBSUB.DELIVERY_METHOD.NOTIFY.id, PUBSUB.DELIVERY_METHOD.WEB_SOCKET.id)

# ################################################################################################################################

class SortedList(_SortedList):
    """ A custom subclass that knows how to remove pubsub messages from SortedList instances.
    """
    def remove_pubsub_msg(self, msg):
        """ Removes a pubsub message from a SortedList instance - we cannot use the regular .remove method
        because it may triggger __cmp__ per https://github.com/grantjenks/sorted_containers/issues/81.
        """
        logger.info('In remove_pubsub_msg msg:`%s`, self._maxes:`%s`', msg, self._maxes)
        pos = bisect_left(self._maxes, msg)

        if pos == len(self._maxes):
            raise ValueError('{0!r} not in list'.format(msg))

        for _list_idx, _list_msg in enumerate(self._lists[pos]):
            if msg.pub_msg_id == _list_msg.pub_msg_id:
                idx = _list_idx
                break
        else:
            raise ValueError('{0!r} not in list'.format(msg))

        self._delete(pos, idx)

# ################################################################################################################################

class DeliveryTask(object):
    """ Runs a greenlet responsible for delivery of messages for a given sub_key.
    """
    def __init__(self, pubsub_tool, pubsub, sub_key, delivery_lock, delivery_list, deliver_pubsub_msg,
            confirm_pubsub_msg_delivered_cb, sub_config):
        self.keep_running = True
        self.pubsub_tool = pubsub_tool
        self.pubsub = pubsub
        self.sub_key = sub_key
        self.delivery_lock = delivery_lock
        self.delivery_list = delivery_list
        self.deliver_pubsub_msg = deliver_pubsub_msg
        self.confirm_pubsub_msg_delivered_cb = confirm_pubsub_msg_delivered_cb
        self.sub_config = sub_config
        self.topic_name = sub_config.topic_name
        self.wait_sock_err = float(self.sub_config.wait_sock_err)
        self.wait_non_sock_err = float(self.sub_config.wait_non_sock_err)
        self.last_iter_run = utcnow_as_ms()
        self.delivery_interval = self.sub_config.task_delivery_interval / 1000.0
        self.delivery_max_retry = self.sub_config.delivery_max_retry
        self.previous_delivery_method = self.sub_config.delivery_method
        self.python_id = str(hex(id(self)))
        self.py_object = '<empty>'

        # This is a total of message batches processed so far
        self.len_batches = 0

        # A total of messages processed so far
        self.len_delivered = 0

        # A list of messages that were requested to be deleted while a delivery was in progress,
        # checked before each delivery.
        self.delete_requested = []

        # This is a lock used for micro-operations such as changing or consulting the contents of self.delete_requested.
        self.interrupt_lock = RLock()

        # If self.wrap_in_list is True, messages will be always wrapped in a list,
        # even if there is only one message to send. Note that self.wrap_in_list will be False
        # only if both batch_size is 1 and wrap_one_msg_in_list is True.

        if self.sub_config.delivery_batch_size == 1:
            if self.sub_config.wrap_one_msg_in_list:
                self.wrap_in_list = True
            else:
                self.wrap_in_list = False

        # With batch_size > 1, we always send a list, no matter what.
        else:
            self.wrap_in_list = True

        spawn_greenlet(self.run)

# ################################################################################################################################

    def is_running(self):
        return self.keep_running

# ################################################################################################################################

    def _delete_messages(self, to_delete):
        """ Actually deletes messages - must be called with self.interrupt_lock held.
        """
        logger.info('Deleting message(s) `%s` from `%s` (%s)', to_delete, self.sub_key, self.topic_name)

        # Mark as deleted in SQL
        self.pubsub.set_to_delete(self.sub_key, [msg.pub_msg_id for msg in to_delete])

        # Delete from our in-RAM delivery list
        for msg in to_delete:
            self.delivery_list.remove_pubsub_msg(msg)

# ################################################################################################################################

    def delete_messages(self, msg_list, _notify=PUBSUB.DELIVERY_METHOD.NOTIFY.id):
        """ For notify tasks, requests that all messages from input list be deleted before the next delivery.
        Otherwise, deletes the messages immediately.
        """
        with self.interrupt_lock:

            # Build a list of actual messages to be deleted - we cannot use a msg_id list only
            # because the SortedList always expects actual message objects for comparison purposes.
            # This will not be called too often so it is fine to iterate over self.delivery_list
            # instead of employing look up dicts just in case a message would have to be deleted.
            to_delete = []
            for msg in self.delivery_list:
                if msg.pub_msg_id in msg_list:
                    msg_list.remove(msg.pub_msg_id) # We can trim it since we know it won't appear again
                    to_delete.append(msg)

            # We are a task that sends out notifications
            if self.sub_config.delivery_method == _notify:

                logger.info('Marking message(s) to be deleted `%s` from `%s` (%s)', msg_list, self.sub_key, self.topic_name)
                self.delete_requested.extend(to_delete)

            # We do not send notifications and self.run never runs so we need to delete the messages here
            else:
                self._delete_messages(to_delete)

# ################################################################################################################################

    def get_messages(self, has_gd):
        """ Returns all messages enqueued in the delivery list, without deleting them from self.delivery_list.
        """
        if has_gd is None:
            out = [msg for msg in self.delivery_list]
            len_out = len(out)
        else:
            out = []
            for msg in self.delivery_list:
                if msg.has_gd is has_gd:
                    out.append(msg)
            len_out = len(out)

        logger.info('Returning %d message(s) for sub_key `%s` (gd:%s)', len_out, self.sub_key, has_gd)

        return out

# ################################################################################################################################

    def pull_messages(self):
        """ Implements pull-style delivery - returns messages enqueued for sub_key, deleting them in progress.
        """
        # Output to produce
        out = []

        # A function wrapper that will append to output
        _append_to_out_func = self._append_to_pull_messages(out)

        # Runs the delivery with our custom function that handles all messages to be delivered
        self.run_delivery(_append_to_out_func)

        # OK, we have the output and can return it
        return [elem.to_dict() for elem in out]

# ################################################################################################################################

    def _append_to_pull_messages(self, out):
        def _impl(sub_key, to_deliver):
            if isinstance(to_deliver, list):
                out.extend(to_deliver)
            else:
                out.append(to_deliver)

        return _impl

# ################################################################################################################################

    def get_message(self, msg_id):
        """ Returns a particular message enqueued by this delivery task.
        """
        for msg in self.delivery_list:
            if msg.pub_msg_id == msg_id:
                return msg

# ################################################################################################################################

    def run_delivery(self, deliver_pubsub_msg=None, _run_deliv_status=PUBSUB.RUN_DELIVERY_STATUS):
        """ Actually attempts to deliver messages. Each time it runs, it gets all the messages
        that are still to be delivered from self.delivery_list.
        """
        # Try to deliver a batch of messages or a single message if batch size is 1
        # and we should not wrap it in a list.
        try:

            # For pull-type deliveries, this will be given on input. For notify-type deliveries,
            # we use the callback assigned to self.
            deliver_pubsub_msg = deliver_pubsub_msg if deliver_pubsub_msg else self.deliver_pubsub_msg

            # Deliver up to that many messages in one batch
            current_batch = self.delivery_list[:self.sub_config.delivery_batch_size]

            # For each message from batch we invoke a hook, if there is any, which will decide
            # whether the message should be delivered, skipped in this iteration or perhaps deleted altogether
            # without even trying to deliver it. If there is no hook, none of messages will be skipped or deleted.

            # There may be requests to delete some of messages while we are running and we obtain the list of
            # such messages here.
            with self.interrupt_lock:
                to_delete = self.delete_requested[:]
                self.delete_requested[:] = []

            # An optional pub/sub hook - note that we are checking it here rather than once upfront
            # because users may change it any time for a topic.
            hook = self.pubsub.get_before_delivery_hook(self.sub_key)

            # Go through each message and check if any has reached our delivery_max_retry.
            # Any such message should be deleted so we add it to to_delete. Note that we do it here
            # because we want for a sub hook to have access to them.
            for msg in current_batch: # type: Message
                if msg.delivery_count >= self.delivery_max_retry:
                    to_delete.append(msg)

            to_deliver = []
            to_skip = []

            messages = {
                _hook_action.DELETE: to_delete,
                _hook_action.DELIVER: to_deliver,
                _hook_action.SKIP: to_skip,
            }

            # Without a hook we will always try to deliver all messages that we have in a given batch
            if not hook:
                to_deliver[:] = current_batch[:]
            else:
                # There is a hook so we can invoke it - it will update the 'messages' dict in place
                self.pubsub.invoke_before_delivery_hook(
                    hook, self.sub_config.topic_id, self.sub_key, current_batch, messages)

            # Delete these messages first, before starting any delivery, either because the hooks told us to
            # or because self.delete_requested was not empty before this iteration.
            if to_delete:
                self._delete_messages(to_delete)

            if to_skip:
                logger.info('Skipping messages `%s`', to_skip)

            # This is the call that actually delivers messages
            deliver_pubsub_msg(self.sub_key, to_deliver if self.wrap_in_list else to_deliver[0])

        except Exception as e:
            # Do not attempt to deliver any other message in case of an error. Our parent will sleep for a small amount of
            # time and then re-run us, thanks to which the next time we run we will again iterate over all the messages
            # currently queued up, including the ones that we were not able to deliver in current iteration.

            exc = format_exc()
            logger.warn('Could not deliver pub/sub messages, e:`%s`', exc)
            logger_zato.warn('Could not deliver pub/sub messages, e:`%s`', exc)

            return _run_deliv_status.SOCKET_ERROR if isinstance(e, SocketError) else _run_deliv_status.OTHER_ERROR

        else:
            # On successful delivery, remove these messages from SQL and our own delivery_list
            try:
                # All message IDs that we have delivered
                delivered_msg_id_list = [msg.pub_msg_id for msg in to_deliver]
                with self.delivery_lock:
                    self.confirm_pubsub_msg_delivered_cb(self.sub_key, delivered_msg_id_list)

            except Exception:
                e = format_exc()
                logger_zato.warn('Could not update delivery status for message(s):`%s`, e:`%s`', to_deliver, e)
                logger.warn('Could not update delivery status for message(s):`%s`, e:`%s`', to_deliver, e)
                return _run_deliv_status.OTHER_ERROR
            else:
                with self.delivery_lock:
                    for msg in to_deliver:
                        try:
                            msg.delivery_count += 1
                            self.delivery_list.remove_pubsub_msg(msg)
                        except Exception:
                            msg = 'Caught exception in run_delivery/remove_pubsub_msg, e:`%s`'
                            logger.warn(msg, format_exc())
                            logger_zato.warn(msg, format_exc())

                # Status of messages is updated in both SQL and RAM so we can now log success
                len_delivered = len(delivered_msg_id_list)
                suffix = ' ' if len_delivered == 1 else 's '
                logger.info('Successfully delivered %s message%s%s to %s (%s -> %s) [lend:%d]',
                    len_delivered, suffix, delivered_msg_id_list, self.sub_key, self.topic_name, self.sub_config.endpoint_name,
                    self.len_delivered)

                self.len_batches += 1
                self.len_delivered += len_delivered

                # Indicates that we have successfully delivered all messages currently queued up
                # and our delivery list is currently empty.
                return _run_deliv_status.OK

# ################################################################################################################################

    def _should_wake(self, _now=utcnow_as_ms):
        """ Returns True if the task should be woken up g. because its time has come already to process messages,
        assumming there are any waiting for it.
        """
        now = _now()
        diff = round(now - self.last_iter_run, 2)

        if diff >= self.delivery_interval:
            if self.delivery_list:
                logger.info('Waking task:%s now:%s last:%s diff:%s interval:%s len-list:%d',
                    self.sub_key, now, self.last_iter_run, diff, self.delivery_interval, len(self.delivery_list))
                return True

# ################################################################################################################################

    def run(self, default_sleep_time=0.1, _status=PUBSUB.RUN_DELIVERY_STATUS, _notify_methods=_notify_methods):
        """ Runs the delivery task's main loop.
        """
        # Fill out Python-level metadata first
        self.py_object = '{}; {}; {}'.format(current_thread().name, getcurrent().name, self.python_id)

        logger.info('Starting delivery task for sub_key:`%s` (%s, %s, %s)',
            self.sub_key, self.topic_name, self.sub_config.delivery_method, self.py_object)

        #
        # Before starting anything, check if there are any messages already queued up in the database for this task.
        # This may happen, for instance, if:
        #
        # * Our delivery_method is `pull`
        # * Some messages get published to topic but the subscribers never gets them
        # * Our server is restarted
        # * The server is ultimately brought up and we need to find these messages that were previously
        #   published but never delivered
        #
        # Since this is about messages taken from the database, by definition, all of them they must be GD ones.
        #
        self.pubsub_tool.enqueue_initial_messages(self.sub_key, self.topic_name, self.sub_config.endpoint_name)

        try:
            while self.keep_running:

                # We are a task that does not notify endpoints of nothing - they will query us themselves
                # so in such a case we can sleep for a while and repeat the loop - perhaps in the meantime
                # someone will change delivery_method to one that allows for notifications to be sent.
                # If not, we will be simply looping forever, checking periodically
                # if we can send notifications already.

                # Apparently, our delivery method has changed since the last time our self.sub_config
                # was modified, so we can log this fact and store it for later use.
                if self.sub_config.delivery_method != self.previous_delivery_method:
                    logger.info('Changed delivery_method from `%s` to `%s` for `%s` (%s -> %s)`',
                        self.previous_delivery_method, self.sub_config.delivery_method, self.sub_key,
                        self.topic_name, self.sub_config.endpoint_name)

                    # Our new value is now the last value too until potentially overridden at one point
                    self.previous_delivery_method = self.sub_config.delivery_method

                if self.sub_config.delivery_method not in _notify_methods:
                    sleep(5)
                    continue

                if self._should_wake():

                    with self.delivery_lock:

                        # Update last run time to be able to wake up in time for the next delivery
                        self.last_iter_run = utcnow_as_ms()

                        # Get the list of all message IDs for which delivery was successful,
                        # indicating whether all currently lined up messages have been
                        # successfully delivered.
                        result = self.run_delivery()

                        if not self.keep_running:
                            msg = 'Skipping delivery loop after r:%s, kr:%d [lend:%d]'
                            logger.warn(msg, result, self.keep_running, self.len_delivered)
                            continue

                        # On success, sleep for a moment because we have just run out of all messages.
                        if result == _status.OK:
                            continue

                        elif result == _status.NO_MSG:
                            sleep(default_sleep_time)

                        # Otherwise, sleep for a longer time because our endpoint must have returned an error.
                        # After this sleep, self.run_delivery will again attempt to deliver all messages
                        # we queued up. Note that we are the only delivery task for this sub_key  so when we sleep here
                        # for a moment, we do not block other deliveries.
                        else:
                            sleep_time = self.wait_sock_err if result == _status.SOCKET_ERROR else self.wait_non_sock_err
                            msg = 'Sleeping for {}s after `{}` in sub_key:`{}`'.format(sleep_time, result, self.sub_key)
                            logger.warn(msg)
                            logger_zato.warn(msg)
                            sleep(sleep_time)

                else:

                    # Wait for our turn
                    sleep(default_sleep_time)

# ################################################################################################################################

        except Exception:
            error_msg = 'Exception in delivery task for sub_key:`%s`, e:`%s`'
            e_formatted = format_exc()
            logger.warn(error_msg, self.sub_key, e_formatted)
            logger_zato.warn(error_msg, self.sub_key, e_formatted)

# ################################################################################################################################

    def stop(self):
        if self.keep_running:
            logger.info('Stopping delivery task for sub_key:`%s`', self.sub_key)
            self.keep_running = False

# ################################################################################################################################

    def clear(self):
        gd, non_gd = self.get_queue_depth()
        logger.info('Removing messages from delivery list for sub_key:`%s, gd:%d, ngd:%d `%s`', self.sub_key, gd, non_gd,
            [elem.pub_msg_id for elem in self.delivery_list])
        self.delivery_list.clear()

# ################################################################################################################################

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

    def get_gd_queue_depth(self):
        return self.get_queue_depth()[0]

# ################################################################################################################################

    def get_non_gd_queue_depth(self):
        return self.get_queue_depth()[1]

# ################################################################################################################################

class Message(PubSubMessage):
    """ Wrapper for messages adding __cmp__ which uses a custom comparison protocol,
    by priority, then ext_pub_time, then pub_time.
    """
    def __init__(self):
        super(Message, self).__init__()
        self.sub_key = None
        self.pub_msg_id = None
        self.pub_correl_id = None
        self.in_reply_to = None
        self.ext_client_id = None
        self.group_id = None
        self.position_in_group = None
        self.pub_time = None
        self.ext_pub_time = None
        self.data = None
        self.mime_type = None
        self.priority = None
        self.expiration = None
        self.expiration_time = None
        self.has_gd = None

        self.pub_time_iso = None
        self.ext_pub_time_iso = None
        self.expiration_time_iso = None

# ################################################################################################################################

    def __lt__(self, other, max_pri=9):

        self_priority = max_pri - self.priority
        other_priority = max_pri - other.priority

        if self_priority < other_priority:
            return True

        # Under Python 3, we must ensure these are not None,
        # because None < None is undefined (TypeError: unorderable types: NoneType() < NoneType())
        elif self.ext_pub_time and other.ext_pub_time:
            return self.ext_pub_time < other.ext_pub_time

        elif self.pub_time < other.pub_time:
            return True

# ################################################################################################################################

    def __repr__(self):
        return '<Msg d:{} pub:{!r} pri:{} id:{} extpub:{!r} gd:{}>'.format(
            self.data, self.pub_time, self.priority, self.pub_msg_id, self.ext_pub_time, self.has_gd)

# ################################################################################################################################

    def add_iso_times(self):
        """ Sets additional attributes for datetime in ISO-8601.
        """
        self.pub_time_iso = datetime_from_ms(self.pub_time * 1000)

        if self.ext_pub_time:
            self.ext_pub_time_iso = datetime_from_ms(self.ext_pub_time * 1000)

        if self.expiration_time:
            self.expiration_time_iso = datetime_from_ms(self.expiration_time * 1000)

# ################################################################################################################################

class GDMessage(Message):
    """ A guaranteed delivery message initialized from SQL data.
    """
    is_gd_message = True

    def __init__(self, sub_key, topic_name, msg, _sk_opaque=PUBSUB.DEFAULT.SK_OPAQUE, _gen_attr=GENERIC.ATTR_NAME,
        _loads=loads):

        logger.info('Building task message (gd) from `%s`', msg)

        super(GDMessage, self).__init__()
        self.endp_msg_queue_id = msg.endp_msg_queue_id
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
        self.has_gd = True
        self.topic_name = topic_name
        self.size = msg.size
        self.published_by_id = msg.published_by_id
        self.sub_pattern_matched = msg.sub_pattern_matched
        self.user_ctx = msg.user_ctx
        self.zato_ctx = msg.zato_ctx

        if self.zato_ctx:
            self.zato_ctx = loads(self.zato_ctx)

        # Load opaque attributes, if any were provided on input
        opaque = getattr(msg, _gen_attr, None)
        if opaque:
            opaque = _loads(opaque)
            for key, value in opaque.items():
                setattr(self, key, value)

        # Add times in ISO-8601 for external subscribers
        self.add_iso_times()

        logger.info('Built task message (gd) `%s`', self.to_dict(add_id_attrs=True))

# ################################################################################################################################

class NonGDMessage(Message):
    """ A non-guaranteed delivery message initialized from a Python dict.
    """
    is_gd_message = False

    def __init__(self, sub_key, server_name, server_pid, msg, _def_priority=PUBSUB.PRIORITY.DEFAULT,
            _def_mime_type=PUBSUB.DEFAULT.MIME_TYPE):

        logger.info('Building task message (ngd) from `%s`', msg)

        super(NonGDMessage, self).__init__()
        self.sub_key = sub_key
        self.server_name = server_name
        self.server_pid = server_pid
        self.pub_msg_id = msg['pub_msg_id']
        self.pub_correl_id = msg.get('pub_correl_id')
        self.in_reply_to = msg.get('in_reply_to')
        self.ext_client_id = msg.get('ext_client_id')
        self.group_id = msg.get('group_id')
        self.position_in_group = msg.get('position_in_group')
        self.pub_time = msg['pub_time']
        self.ext_pub_time = msg.get('ext_pub_time')
        self.data = msg['data']
        self.mime_type = msg.get('mime_type') or _def_mime_type
        self.priority = msg.get('priority') or _def_priority
        self.expiration = msg['expiration']
        self.expiration_time = msg['expiration_time']
        self.has_gd = False
        self.topic_name = msg['topic_name']
        self.size = msg['size']
        self.published_by_id = msg['published_by_id']
        self.pub_pattern_matched = msg['pub_pattern_matched']
        self.reply_to_sk = msg['reply_to_sk']
        self.deliver_to_sk = msg['deliver_to_sk']
        self.user_ctx = msg.get('user_ctx')
        self.zato_ctx = msg.get('zato_ctx')

        # msg.sub_pattern_matched is a shared dictionary of patterns for each subscriber - we .pop from it
        # so as not to keep this dictionary's contents for no particular reason. Since there can be only
        # one delivery task for each sub_key, we can .pop rightaway.
        self.sub_pattern_matched = msg['sub_pattern_matched'].pop(self.sub_key)

        # Add times in ISO-8601 for external subscribers
        self.add_iso_times()

        logger.info('Built task message (ngd) `%s`', self.to_dict(add_id_attrs=True))

# ################################################################################################################################

class PubSubTool(object):
    """ A utility object for pub/sub-related tasks.
    """
    def __init__(self, pubsub, parent, endpoint_type, is_for_services=False, deliver_pubsub_msg=None):
        self.pubsub = pubsub # type: PubSub
        self.parent = parent # This is our parent, e.g. an individual WebSocket on whose behalf we execute
        self.endpoint_type = endpoint_type

        self.server_name = self.pubsub.server.name
        self.server_pid = self.pubsub.server.pid

        # WSX connections will have their own callback but other connections use the default one
        self.deliver_pubsub_msg = deliver_pubsub_msg or self.pubsub.deliver_pubsub_msg

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

        # Last sync time - updated even if there are no messages in a given synchronization request,
        # which is unlike self.last_sync_time_by_sub_key which updates only if there are messages
        # for a particular sub_key.
        self.last_sync_time = None

        # Last sync time for any kind of messages, by sub_key, no matter if they are GD or not
        self.last_sync_time_by_sub_key = {}

        # Last time we tried to pull GD messages from SQL, by sub_key
        self.last_gd_run = {}

        # Register with this server's pubsub
        self.register_pubsub_tool()

        # How many times self.handle_new_messages has been called
        self.msg_handler_counter = 0

        # Is this tool solely dedicated to delivery of messages to Zato services
        self.is_for_services = is_for_services

# ################################################################################################################################

    def register_pubsub_tool(self):
        """ Registers ourselves with this server's pubsub to let the other control when we should shut down
        our delivery tasks for each sub_key.
        """
        self.pubsub.register_pubsub_tool(self)

# ################################################################################################################################

    def get_sub_keys(self):
        """ Returns all sub keys this task handles, as a list.
        """
        with self.lock:
            return list(self.sub_keys)

# ################################################################################################################################

    def add_sub_key_no_lock(self, sub_key):
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

        self.delivery_tasks[sub_key] = DeliveryTask(
            self, self.pubsub, sub_key, delivery_lock, delivery_list, self.deliver_pubsub_msg,
            self.confirm_pubsub_msg_delivered, sub.config)

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
                del self.sub_key_locks[sub_key]

                del self.delivery_lists[sub_key]
                self.delivery_tasks[sub_key].stop()
                del self.delivery_tasks[sub_key]

            except Exception:
                logger.warn('Exception during sub_key removal `%s`, e:`%s`', sub_key, format_exc())

# ################################################################################################################################

    def has_sub_key(self, sub_key):
        with self.lock:
            return sub_key in self.sub_keys

# ################################################################################################################################

    def remove_all_sub_keys(self):
        sub_keys = deepcopy(self.sub_keys)
        for sub_key in sub_keys:
            self.remove_sub_key(sub_key)

# ################################################################################################################################

    def _add_non_gd_messages_by_sub_key(self, sub_key, messages):
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

            self.delivery_lists[sub_key].add(NonGDMessage(sub_key, self.server_name, self.server_pid, msg))

# ################################################################################################################################

    def add_non_gd_messages_by_sub_key(self, sub_key, messages):
        """ Adds to local delivery queue all non-GD messages from input.
        """
        try:
            with self.sub_key_locks[sub_key]:
                self._add_non_gd_messages_by_sub_key(sub_key, messages)
        except Exception:
            e = format_exc()
            logger.warn(e)
            logger_zato.warn(e)

# ################################################################################################################################

    def _handle_new_messages(self, ctx, delta=60):
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

            gd_msg_list = {}

            # We need to have the broad lock first to read in messages for all the sub keys
            with self.lock:

                # Get messages for all sub_keys on input and break them out by each sub_key separately,
                # provided that we have a flag indicating that there should be some GD messages around in the database.
                if ctx.has_gd:
                    for msg in self._fetch_gd_messages_by_sub_key_list(ctx.sub_key_list, ctx.pub_time_max, session):
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

                    with self.sub_key_locks[sub_key]:

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
            logger.warn(e)
            logger_zato.warn(e)

        finally:
            if session:
                session.commit()
                session.close()

# ################################################################################################################################

    def handle_new_messages(self, ctx):
        self.msg_handler_counter += 1
        try:
            spawn(self._handle_new_messages, ctx)
        except Exception:
            e = format_exc()
            logger.warn(e)
            logger_zato.warn(e)

# ################################################################################################################################

    def _fetch_gd_messages_by_sub_key_list(self, sub_key_list, pub_time_max, session=None):
        """ Part of the low-level implementation of enqueue_gd_messages_by_sub_key, must be called with a lock for input sub_key.
        """
        # These are messages that we have already queued up so if we happen to pick them up
        # in the database, they should be ignored.
        ignore_list = set()
        for sub_key in sub_key_list:
            ignore_list.update([msg.endp_msg_queue_id for msg in self.delivery_lists[sub_key] if msg.has_gd])

        logger.info('Fetching GD messages by sk_list:`%s`, ignore:`%s`', sub_key_list, ignore_list)

        if self.last_gd_run:
            if len(sub_key_list) == 1:
                # Use .get because it is possible we have not fetched messages for that particular sub_key before,
                # i.e. self.last_gd_run may be non-empty because there are last GD runs for other keys,
                # just not for this one.
                min_last_gd_run = self.last_gd_run.get(sub_key_list[0])
            else:
                min_last_gd_run = min(value for key, value in iteritems(self.last_gd_run) if key in sub_key_list)
        else:
            min_last_gd_run = None

        logger.info('Using min last_gd_run `%r`', min_last_gd_run)

        for msg in self.pubsub.get_sql_messages_by_sub_key(session, sub_key_list, min_last_gd_run, pub_time_max, ignore_list):
            yield msg

# ################################################################################################################################

    def _push_gd_messages_by_sub_key(self, sub_key, topic_name, gd_msg_list):
        """ Pushes all input GD messages to a delivery task for the sub_key.
        """
        count = 0
        msg_ids = []

        for idx, msg in enumerate(gd_msg_list):

            msg_ids.append(msg.pub_msg_id)
            self.delivery_lists[sub_key].add(GDMessage(sub_key, topic_name, msg))
            count += 1

        logger.info('Pushing %d GD message{}to task:%s msg_ids:%s'.format(
            ' ' if count==1 else 's '), count, sub_key, msg_ids)

# ################################################################################################################################

    def _enqueue_gd_messages_by_sub_key(self, sub_key, gd_msg_list):
        """ Low-level implementation of self.enqueue_gd_messages_by_sub_key which expects the message list on input.
        Must be called with self.sub_key_locks[sub_key] held.
        """
        topic_name = self.pubsub.get_topic_name_by_sub_key(sub_key)
        self._push_gd_messages_by_sub_key(sub_key, topic_name, gd_msg_list)

# ################################################################################################################################

    def enqueue_gd_messages_by_sub_key(self, sub_key, session=None):
        """ Fetches GD messages from SQL for sub_key given on input and adds them to local queue of messages to deliver.
        """
        with self.sub_key_locks[sub_key]:
            gd_msg_list = self._fetch_gd_messages_by_sub_key_list([sub_key], utcnow_as_ms(), session)
            self._enqueue_gd_messages_by_sub_key(sub_key, gd_msg_list)

# ################################################################################################################################

    def enqueue_initial_messages(self, sub_key, topic_name, endpoint_name, _group_size=20):
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
                    groups = list(grouper(_group_size, msg_ids))
                    len_groups = len(groups)

                    # This we log using both loggers because we run during server startup so we should
                    # let users know that their server have to do something extra
                    for _logger in logger, logger_zato:
                        _logger.info('Found %d initial message%sto enqueue for sub_key:`%s` (%s -> %s), `%s`, g:%d, gs:%d',
                            len_msg_ids, suffix, sub_key, topic_name, endpoint_name, msg_ids, len(groups), _group_size)

                    for idx, group in enumerate(groups, 1):
                        group_msg_ids = [elem for elem in group if elem]
                        logger.info('Enqueuing group %d/%d (gs:%d) (%s, %s -> %s) `%s`',
                            idx, len_groups, _group_size, sub_key, topic_name, endpoint_name, group_msg_ids)

                        msg_list = self.pubsub.get_sql_messages_by_msg_id_list(session, sub_key, pub_time_max, group_msg_ids)
                        self._enqueue_gd_messages_by_sub_key(sub_key, msg_list)

            except Exception:
                for _logger in logger, logger_zato:
                    _logger.warn('Could not enqueue initial messages for `%s` (%s -> %s), e:`%s`',
                        sub_key, topic_name, endpoint_name, format_exc())

            finally:
                if session:
                    session.close()

# ################################################################################################################################

    def confirm_pubsub_msg_delivered(self, sub_key, delivered_list):
        self.pubsub.confirm_pubsub_msg_delivered(sub_key, delivered_list)

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

    def get_delivery_task(self, sub_key):
        with self.lock:
            return self.delivery_tasks[sub_key]

# ################################################################################################################################

    def get_delivery_tasks(self):
        with self.lock:
            return self.delivery_tasks.values()

# ################################################################################################################################

    def delete_messages(self, sub_key, msg_list):
        """ Marks one or more to be deleted from the delivery task by the latter's sub_key.
        """
        with self.lock:
            self.delivery_tasks[sub_key].delete_messages(msg_list)

# ################################################################################################################################

    def get_messages(self, sub_key, has_gd=None):
        """ Returns all messages enqueued for sub_key without deleting them from their queue.
        """
        with self.lock:
            return self.delivery_tasks[sub_key].get_messages(has_gd)

# ################################################################################################################################

    def pull_messages(self, sub_key, has_gd=None):
        """ Implements pull-style delivery - returns messages enqueued for sub_key, deleting them in progress.
        """
        with self.lock:
            return self.delivery_tasks[sub_key].pull_messages()

# ################################################################################################################################

    def get_message(self, sub_key, msg_id):
        """ Returns a particular message enqueued for sub_key.
        """
        with self.lock:
            return self.delivery_tasks[sub_key].get_message(msg_id)

# ################################################################################################################################
