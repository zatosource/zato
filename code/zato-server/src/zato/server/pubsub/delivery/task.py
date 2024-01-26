# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pylint: disable=unused-import, unused-variable

# stdlib
from logging import getLogger
from threading import current_thread
from traceback import format_exc, format_exception
from typing import Iterable as iterable_

# gevent
from gevent import sleep, spawn
from gevent.lock import RLock
from gevent.thread import getcurrent

# Zato
from zato.common.api import PUBSUB
from zato.common.exception import RuntimeInvocationError
from zato.common.odb.api import SQLRow
from zato.common.typing_ import cast_, list_
from zato.common.util.time_ import utcnow_as_ms
from zato.server.pubsub.model import DeliveryResultCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, boolnone, callable_, callnone, dict_, dictlist, \
         strlist, tuple_
    from zato.server.pubsub import PubSub
    from zato.server.pubsub.delivery.message import GDMessage, Message
    from zato.server.pubsub.delivery._sorted_list import SortedList
    GDMessage = GDMessage

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_pubsub.task')
logger_zato = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

_hook_action = PUBSUB.HOOK_ACTION
_notify_methods = (PUBSUB.DELIVERY_METHOD.NOTIFY.id, PUBSUB.DELIVERY_METHOD.WEB_SOCKET.id)

run_deliv_sc = PUBSUB.RunDeliveryStatus.StatusCode
ReasonCode = PUBSUB.RunDeliveryStatus.ReasonCode

deliv_exc_msg = 'Exception {}/{} in delivery iter #{} for `{}` sk:{} -> {}'
getcurrent = cast_('callable_', getcurrent)

# ################################################################################################################################
# ################################################################################################################################

sqlmsglist = list_['SQLRow']
gdmsglist  = list_['GDMessage']
msgiter    = iterable_['Message']
msglist    = list_['Message']
sqlmsgiter = iterable_['SQLRow']

# ################################################################################################################################
# ################################################################################################################################

class DeliveryTask:
    """ Runs a greenlet responsible for delivery of messages for a given sub_key.
    """

    wait_sock_err: 'float'
    wait_non_sock_err: 'float'
    delivery_max_retry: 'int'

    def __init__(
        self,
        *,
        pubsub,        # type: PubSub
        sub_config,    # type: anydict
        sub_key,       # type: str
        delivery_lock, # type: RLock
        delivery_list, # type: SortedList
        deliver_pubsub_msg,              # type: callable_
        confirm_pubsub_msg_delivered_cb, # type: callable_
        enqueue_initial_messages_func,   # type: callable_
        pubsub_set_to_delete,               # type: callable_
        pubsub_get_before_delivery_hook,    # type: callable_
        pubsub_invoke_before_delivery_hook, # type: callable_
    ) -> 'None':

        self.keep_running = True
        self.pubsub = pubsub
        self.enqueue_initial_messages_func = enqueue_initial_messages_func
        self.pubsub_set_to_delete = pubsub_set_to_delete
        self.pubsub_get_before_delivery_hook = pubsub_get_before_delivery_hook
        self.pubsub_invoke_before_delivery_hook = pubsub_invoke_before_delivery_hook
        self.sub_key = sub_key
        self.delivery_lock = delivery_lock
        self.delivery_list = delivery_list
        self.deliver_pubsub_msg = deliver_pubsub_msg
        self.confirm_pubsub_msg_delivered_cb = confirm_pubsub_msg_delivered_cb
        self.sub_config = sub_config
        self.topic_name = sub_config['topic_name']
        self.last_iter_run = utcnow_as_ms()
        self.delivery_interval = self.sub_config['task_delivery_interval'] / 1000.0
        self.previous_delivery_method = self.sub_config['delivery_method']
        self.python_id = str(hex(id(self)))
        self.py_object = '<empty>'

        # Set attributes that may be potentially changed in runtime by users
        self._set_sub_config_attrs()

        # This is a total of delivery iterations
        self.delivery_iter = 0

        # This is a total of message batches processed so far
        self.len_batches = 0

        # A total of messages processed so far
        self.len_delivered = 0

        # A list of messages that were requested to be deleted while a delivery was in progress, checked before each delivery.
        self.delete_requested:list_['Message'] = []

        # This is a lock used for micro-operations such as changing or consulting the contents of self.delete_requested.
        self.interrupt_lock = RLock()

        # If self.wrap_in_list is True, messages will be always wrapped in a list,
        # even if there is only one message to send. Note that self.wrap_in_list will be False
        # only if both batch_size is 1 and wrap_one_msg_in_list is True.

        if self.sub_config['delivery_batch_size'] == 1:
            if self.sub_config['wrap_one_msg_in_list']:
                self.wrap_in_list = True
            else:
                self.wrap_in_list = False

        # With batch_size > 1, we always send a list, no matter what.
        else:
            self.wrap_in_list = True

        _ = spawn(self.run) # type: ignore

# ################################################################################################################################

    def is_running(self) -> 'bool':
        return self.keep_running

# ################################################################################################################################

    def _set_sub_config_attrs(self) -> 'None':
        self.wait_sock_err = float(self.sub_config['wait_sock_err'])
        self.wait_non_sock_err = float(self.sub_config['wait_non_sock_err'])
        self.delivery_max_retry = int(self.sub_config.get('delivery_max_retry', 0) or PUBSUB.DEFAULT.DELIVERY_MAX_RETRY)

# ################################################################################################################################

    def _delete_messages(self, to_delete:'msgiter') -> 'None':
        """ Actually deletes messages - must be called with self.interrupt_lock held.
        """
        logger.info('Deleting message(s) `%s` from `%s` (%s)', to_delete, self.sub_key, self.topic_name)

        # Mark as deleted in SQL
        self.pubsub_set_to_delete(self.sub_key, [msg.pub_msg_id for msg in to_delete])

        # Go through each of the messages that is to be deleted ..
        for msg in to_delete:

            # .. delete it from our in-RAM delivery list ..
            self.delivery_list.remove_pubsub_msg(msg)

# ################################################################################################################################

    def delete_messages(self, msg_list:'strlist', _notify:'str'=PUBSUB.DELIVERY_METHOD.NOTIFY.id) -> 'None':
        """ For notify tasks, requests that all messages from input list be deleted before the next delivery.
        Otherwise, deletes the messages immediately.
        """
        with self.interrupt_lock:

            # Build a list of actual messages to be deleted - we cannot use a msg_id list only
            # because the SortedList always expects actual message objects for comparison purposes.
            # This will not be called too often so it is fine to iterate over self.delivery_list
            # instead of employing look up dicts just in case a message would have to be deleted.
            to_delete = cast_('msglist', [])
            for msg in self.delivery_list:
                if msg.pub_msg_id in msg_list:
                    # We can trim it since we know it won't appear again
                    msg_list.remove(msg.pub_msg_id)
                    to_delete.append(msg)

            # We are a task that sends out notifications
            if self.sub_config['delivery_method'] == _notify:

                logger.info('Marking message(s) to be deleted `%s` from `%s` (%s)', msg_list, self.sub_key, self.topic_name)
                self.delete_requested.extend(to_delete)

            # We do not send notifications and self.run never runs so we need to delete the messages here
            else:
                self._delete_messages(to_delete)

# ################################################################################################################################

    def get_messages(self, has_gd:'boolnone') -> 'msglist': # type: ignore[valid-type]
        """ Returns all messages enqueued in the delivery list, without deleting them from self.delivery_list.
        """
        out: 'msglist' # type: ignore[valid-type]

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

    def pull_messages(self) -> 'dictlist':
        """ Implements pull-style delivery - returns messages enqueued for sub_key, deleting them in progress.
        """
        # Output to produce
        out      = [] # type: dictlist
        messages = [] # type: anylist

        # A function wrapper that will append to output
        _append_to_out_func = self._append_to_pull_messages(messages)

        # Runs the delivery with our custom function that handles all messages to be delivered
        _ = self.run_delivery(_append_to_out_func) # noqa: F841

        # OK, we have the output and can return it
        for elem in messages:
            out.append(elem.to_dict())
        return out

# ################################################################################################################################

    def _append_to_pull_messages(self, out:'any_') -> 'callable_':
        def _impl(sub_key:'str', to_deliver:'any_') -> None:
            if isinstance(to_deliver, list):
                out.extend(to_deliver)
            else:
                out.append(to_deliver)

        return _impl

# ################################################################################################################################

    def get_message(self, msg_id:'str') -> 'Message':
        """ Returns a particular message enqueued by this delivery task.
        """
        for msg in self.delivery_list:
            if msg.pub_msg_id == msg_id:
                return msg

        else:
            raise ValueError('No such message {}'.format(msg_id))

# ################################################################################################################################

    def _get_reason_code_from_exception(self, e:'Exception') -> 'int':

        if isinstance(e, IOError):
            reason_code = ReasonCode.Error_IO
        elif isinstance(e, RuntimeInvocationError):
            reason_code = ReasonCode.Error_Runtime_Invoke
        else:
            reason_code = ReasonCode.Error_Other

        return reason_code

# ################################################################################################################################

    def _get_messages_to_delete(
        self,
        current_batch:'msglist' # type: ignore[valid-type]
    ) -> 'msglist': # type: ignore[valid-type]

        # There may be requests to delete some of messages while we are running and we obtain the list of
        # such messages here.
        with self.interrupt_lock:
            to_delete = self.delete_requested[:]
            self.delete_requested.clear()

        # Go through each message and check if any has reached our delivery_max_retry.
        # Any such message should be deleted so we add it to to_delete. Note that we do it here
        # because we want for a sub hook to have access to them.
        for msg in current_batch: # type: ignore[attr-defined]
            if msg.delivery_count >= self.delivery_max_retry:
                to_delete.append(msg)

        return to_delete

# ################################################################################################################################

    def _invoke_before_delivery_hook(
        self,
        current_batch, # type: msglist   # type: ignore[valid-type]
        hook,          # type: callable_
        to_delete,     # type: msglist   # type: ignore[valid-type]
        to_deliver,    # type: msglist   # type: ignore[valid-type]
        to_skip        # type: msglist   # type: ignore[valid-type]
    ) -> 'None':

        messages = {
            _hook_action.DELETE: to_delete,
            _hook_action.DELIVER: to_deliver,
            _hook_action.SKIP: to_skip,
        } # type: dict_[str, msglist]

        # We pass the dict to the hook which will in turn update in place the lists that the dict contains.
        # This is why this method does not return anything, i.e. the lists are modified in place.
        self.pubsub_invoke_before_delivery_hook(
            hook, self.sub_config['topic_id'], self.sub_key, current_batch, messages)

# ################################################################################################################################

    def _log_delivered_success(self, len_delivered:'int', delivered_msg_id_list:'strlist') -> 'None':

        suffix = ' ' if len_delivered == 1 else 's '
        logger.info('Successfully delivered %s message%s%s to %s (%s -> %s) [lend:%d]',
            len_delivered, suffix, delivered_msg_id_list, self.sub_key, self.topic_name,
            self.sub_config['endpoint_name'], self.len_delivered)

# ################################################################################################################################

    def _update_delivery_counters(self, to_deliver:'msglist') -> 'None': # type: ignore[valid-type]

        # Update the delivery counter for each message
        with self.delivery_lock:
            for msg in to_deliver: # type: ignore[attr-defined]
                msg.delivery_count += 1

# ################################################################################################################################

    def run_delivery(self,
        deliver_pubsub_msg=None, # type: callnone
        status_code=run_deliv_sc # type: any_
    ) -> 'DeliveryResultCtx':
        """ Actually attempts to deliver messages. Each time it runs, it gets all the messages
        that are still to be delivered from self.delivery_list.
        """
        # Increase our delivery counter
        self.delivery_iter += 1

        # Try to deliver a batch of messages or a single message if batch size is 1
        # and we should not wrap it in a list.
        result = DeliveryResultCtx()
        result.delivery_iter = self.delivery_iter

        try:

            # For pull-type deliveries, this will be given on input. For notify-type deliveries,
            # we use the callback assigned to self.
            deliver_pubsub_msg = deliver_pubsub_msg if deliver_pubsub_msg else self.deliver_pubsub_msg

            # Deliver up to that many messages in one batch
            delivery_batch_size = self.sub_config['delivery_batch_size'] # type: int

            logger.info('Looking for current batch in delivery_list=%s (%s)', hex(id(self.delivery_list)), self.sub_key)

            current_batch = self.delivery_list[:delivery_batch_size]
            current_batch = cast_('msglist', current_batch)

            # For each message from batch we invoke a hook, if there is any, which will decide
            # whether the message should be delivered, skipped in this iteration or perhaps deleted altogether
            # without even trying to deliver it. If there is no hook, none of messages will be skipped or deleted.

            # An optional pub/sub hook - note that we are checking it here rather than in __init__
            # because users may change it any time for a topic.
            hook = self.pubsub_get_before_delivery_hook(self.sub_key)

            # Look up all the potential messages that we need to delete.
            to_delete = self._get_messages_to_delete(current_batch)

            # Delete these messages first, before starting any delivery.
            if to_delete:
                self._delete_messages(to_delete)

            # Clear out this list because we will be reusing it later in the delivery hook
            to_delete = []

            # It is possible that we do not have any messages to deliver here, e.g. because all of them were already deleted
            # via self._delete_messages, in which case, we can simply return.
            if not self.delivery_list:
                result.is_ok = True
                result.status_code = status_code.OK
                return result

            # Unlike to_delete, which has to be computed dynamically,
            # these two can be initialized to their respective empty lists directly.
            to_deliver:'msglist' = [] # type: ignore[valid-type]
            to_skip:'msglist'    = [] # type: ignore[valid-type]

            # There is a hook so we can invoke it - it will update in place the lists that we pass to it ..
            if hook:
                self._invoke_before_delivery_hook(current_batch, hook, to_delete, to_deliver, to_skip)

            # .. otherwise, without a hook, we will always try to deliver all messages that we have in a given batch
            else:
                to_deliver[:] = current_batch[:] # type: ignore[index]

            # Our hook may have indicated what to delete, in which case, do delete that now.
            if to_delete:
                self._delete_messages(to_delete)

            if to_skip:
                logger.info('Skipping messages `%s`', to_skip)

            # Update the delivery counter before trying to deliver the messages
            self._update_delivery_counters(to_deliver)

            # This is the call that actually delivers messages
            deliver_pubsub_msg(self.sub_key, to_deliver if self.wrap_in_list else to_deliver[0]) # type: ignore[index]

        except Exception as e:

            # Do not attempt to deliver any other message in case of an error. Our parent will sleep for a small amount of
            # time and then re-run us, thanks to which the next time we run we will again iterate over all the messages
            # currently queued up, including the ones that we were not able to deliver in current iteration.

            result.reason_code = self._get_reason_code_from_exception(e)
            result.status_code = status_code.Error
            result.exception_list.append(e)

        else:
            # On successful delivery, remove these messages from SQL and our own delivery_list
            try:
                # All message IDs that we have delivered
                delivered_msg_id_list = [msg.pub_msg_id for msg in to_deliver] # type: ignore[attr-defined]
                with self.delivery_lock:
                    self.confirm_pubsub_msg_delivered_cb(self.sub_key, delivered_msg_id_list)

            except Exception as update_err:
                result.status_code = status_code.Error
                result.reason_code = ReasonCode.Error_Other
                result.exception_list.append(update_err)
            else:
                with self.delivery_lock:
                    for msg in to_deliver: # type: ignore[attr-defined]
                        try:
                            self.delivery_list.remove_pubsub_msg(msg)
                        except Exception as remove_err:
                            result.status_code = status_code.Error
                            result.exception_list.append(remove_err)

                # Status of messages is updated in both SQL and RAM so we can now log success
                # unless, for some reason, we were not able to remove the messages from self.delivery_list.
                if result.status_code in (status_code.Error, status_code.Warning):
                    logger.warning('Could not remove delivered messages from self.delivery_list `%s` (%s) -> `%s`',
                        to_deliver, self.delivery_list, result.exception_list)
                else:
                    # This is reusable.
                    len_delivered = len(delivered_msg_id_list)

                    # Log success ..
                    self._log_delivered_success(len_delivered, delivered_msg_id_list)

                    # .. update internal metadata ..
                    self.len_batches += 1
                    self.len_delivered += len_delivered

                    # .. and indicate that we have successfully delivered all messages currently queued up
                    # and our delivery list is currently empty.
                    result.status_code = status_code.OK

        # No matter what, we always have a result object to return
        if result.status_code not in (status_code.Error, status_code.Warning):
            result.is_ok = True
            result.status_code = status_code.OK

        return result

# ################################################################################################################################

    def _should_wake(self, _now:'callable_'=utcnow_as_ms) -> 'bool':
        """ Returns True if the task should be woken up e.g. because its time has come already to process messages,
        assumming there are any waiting for it.
        """
        # Return quickly if we already know that there are some messages to deliver or clear ..
        if self.delivery_list:
            return True

        # .. otherwise, we will wait until self.delivery_interval lapsed.

        now = _now()
        diff = round(now - self.last_iter_run, 2)

        if diff >= self.delivery_interval:
            if self.delivery_list:
                logger.info('Waking task:%s now:%s last:%s diff:%s interval:%s len-list:%d',
                    self.sub_key, now, self.last_iter_run, diff, self.delivery_interval, len(self.delivery_list))
                return True

        # The above conditions are not met so we explicitly return False
        return False

# ################################################################################################################################

    def run(self,
        default_sleep_time=0.1,  # type: float
        status_code=run_deliv_sc # type: any_
    ) -> 'None':
        """ Runs the delivery task's main loop.
        """

        # Fill out Python-level metadata first
        _current_greenlet = cast_('any_', getcurrent())
        _greenlet_name = _current_greenlet.name
        _greenlet_name = cast_('str', _greenlet_name)

        self.py_object = '{}; {}; {}'.format(current_thread().name, _greenlet_name, self.python_id)

        logger.info('Starting delivery task for sub_key:`%s` (%s, %s, %s)',
            self.sub_key, self.topic_name, self.sub_config['delivery_method'], self.py_object)

        # First, make sure that the topic object already exists,
        # e.g. it is possible that our task is already started
        # even if other in-RAM structures are not populated yet,
        # which is why we need to wait for this topic.
        _ = self.pubsub.wait_for_topic(self.topic_name)

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
        self.enqueue_initial_messages_func(self.sub_key, self.topic_name, self.sub_config['endpoint_name'])

        try:
            while self.keep_running:

                # Reusable.
                delivery_method = self.sub_config['delivery_method']

                # We are a task that does not notify endpoints, i.e. we are pull-style and our subscribers
                # will query us themselves so in this case we can sleep for a while and repeat the loop -
                # perhaps before the next iteration of the loop begins someone will change delivery_method
                # to one that allows for notifications to be sent. If not, we will be simply looping forever,
                # checking periodically below if the delivery method is still the same.
                if delivery_method not in _notify_methods:
                    sleep(5)
                    continue

                # Apparently, our delivery method has changed since the last time our self.sub_config
                # was modified, so we can log this fact and store it for later use.
                if delivery_method != self.previous_delivery_method:

                    # First, log what happened ..
                    self._log_delivery_method_changed(delivery_method)

                    # .. now, the new value replaces the previous one - possibly to be replaced again and again in the future.
                    self.previous_delivery_method = delivery_method

                # Is there any message that we can try to deliver?
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
                            logger.info(msg, result, self.keep_running, self.len_delivered)
                            continue

                        if result.is_ok:
                            continue

                        # This was a runtime invocation error - for instance, a low-level WebSocket exception,
                        # which is unrecoverable and we need to stop our task. When the client reconnects,
                        # the delivery will pick up where we left.
                        elif result.reason_code == ReasonCode.Error_Runtime_Invoke:
                            self.stop()

                        # Sleep for a moment because we have just run out of all messages.
                        elif result.reason_code == ReasonCode.No_Msg:
                            sleep(default_sleep_time) # pyright: ignore[reportGeneralTypeIssues]

                        # Otherwise, sleep for a longer time because our endpoint must have returned an error.
                        # After this sleep, self.run_delivery will again attempt to deliver all messages
                        # we queued up. Note that we are the only delivery task for this sub_key  so when we sleep here
                        # for a moment, we do not block other deliveries.
                        else:

                            # We caught an error or warning ..
                            if not result.is_ok:

                                # Reusable.
                                len_exception_list = len(result.exception_list)

                                # Log all the exceptions received while trying to deliver the messages ..
                                self._log_warnings_from_delivery_task(result, len_exception_list)

                                # .. sleep only if there are still some messages to be delivered,
                                # .. as it is possible that our lists has been cleared out since the last time we run ..
                                if self.delivery_list:

                                    # .. sleep for a while but only if this was an error (not a warning).
                                    if result.status_code == status_code.Error:

                                        # .. OK, we can sleep now.
                                        self._sleep_on_delivery_error(result, len_exception_list)

                # There was no message to deliver in this turn ..
                else:

                    # .. thus, we can wait until one arrives.
                    sleep(default_sleep_time) # pyright: ignore[reportGeneralTypeIssues]

        except Exception as e:
            error_msg = 'Exception in delivery task for sub_key:`%s`, e:`%s`'
            e_formatted = format_exc()
            logger.warning(error_msg, self.sub_key, e_formatted)
            logger_zato.warning(error_msg, self.sub_key, e)

# ################################################################################################################################

    def _log_delivery_method_changed(self, current_delivery_method:'str') -> 'None':
        logger.info('Changed delivery_method from `%s` to `%s` for `%s` (%s -> %s)`',
            self.previous_delivery_method, current_delivery_method, self.sub_key,
            self.topic_name, self.sub_config['endpoint_name'])

# ################################################################################################################################

    def _log_warnings_from_delivery_task(self, result:'DeliveryResultCtx', len_exception_list:'int') -> 'None':

        # .. log all exceptions reported by the delivery task ..
        for idx, e in enumerate(result.exception_list, 1):

            msg_logger = deliv_exc_msg.format(
                idx, len_exception_list, result.delivery_iter, self.topic_name, self.sub_key,
                ''.join(format_exception(type(e), e, e.__traceback__)))

            msg_logger_zato = deliv_exc_msg.format(
                idx, len_exception_list, result.delivery_iter, self.topic_name, self.sub_key,
                e.args[0])

            logger.warning(msg_logger)
            logger_zato.warning(msg_logger_zato)

# ################################################################################################################################

    def _sleep_on_delivery_error(self, result:'DeliveryResultCtx', len_exception_list:'int') -> 'None':

        if result.reason_code == ReasonCode.Error_IO:
            sleep_time = self.wait_sock_err
        else:
            sleep_time = self.wait_non_sock_err

        exc_len_one = 'an exception'
        exc_len_multi = '{} exceptions'

        if len_exception_list == 1:
            exc_len_msg = exc_len_one
        else:
            exc_len_msg = exc_len_multi.format(len_exception_list)

        sleep_msg = 'Sleeping for {}s after {} in iter #{}'.format(
            sleep_time, exc_len_msg, result.delivery_iter)

        logger.warning(sleep_msg)
        logger_zato.warning(sleep_msg)

        sleep(sleep_time) # pyright: ignore[reportGeneralTypeIssues]

# ################################################################################################################################

    def stop(self) -> 'None':
        if self.keep_running:
            logger.info('Stopping delivery task for sub_key:`%s`', self.sub_key)
            self.keep_running = False

# ################################################################################################################################

    def clear(self) -> 'None':

        # For logging purposes ..
        gd, non_gd = self.get_queue_depth()

        # .. log details of what we are about to do ..
        logger.info('Removing messages from delivery list for sub_key:`%s, gd:%d, ngd:%d `%s`',
            self.sub_key, gd, non_gd, [elem.pub_msg_id for elem in self.delivery_list])

        # .. indicate what should be deleted in the next iteration of the self.run_delivery loop ..
        # self.delete_requested[:] = self.delivery_list[:]

        # .. clear the delivery list now ..
        self.delivery_list.clear()

        # .. and log a higher-level message now.
        msg = 'Cleared task messages for sub_key `%s` -> `%s`'
        logger.info(msg, self.sub_key, self.py_object)
        logger_zato.info(msg, self.sub_key, self.py_object)

# ################################################################################################################################

    def update_sub_config(self) -> 'None':
        self._set_sub_config_attrs()

# ################################################################################################################################

    def get_queue_depth(self) -> 'tuple_[int, int]':
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

    def get_gd_queue_depth(self) -> int:
        return self.get_queue_depth()[0]

# ################################################################################################################################

    def get_non_gd_queue_depth(self) -> 'int':
        return self.get_queue_depth()[1]

# ################################################################################################################################
# ################################################################################################################################
