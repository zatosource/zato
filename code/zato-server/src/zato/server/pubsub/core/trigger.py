# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pylint: disable=unused-import, redefined-builtin, unused-variable

# stdlib
import logging
from traceback import format_exc

# gevent
from gevent import sleep, spawn
from zato.common.typing_ import cast_
from zato.common.util.api import new_cid

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent.lock import RLock
    from zato.common.typing_ import anydict, callable_, intanydict, intnone
    from zato.server.pubsub.model import inttopicdict, sublist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato_pubsub.ps')
logger_zato = logging.getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class NotifyPubSubTasksTrigger:

    def __init__(
        self,
        *,
        lock,           # type: RLock
        topics,         # type: inttopicdict
        sync_max_iters, # type: intnone
        invoke_service_func,   # type: callable_
        set_sync_has_msg_func, # type: callable_
        get_subscriptions_by_topic_func,     # type: callable_
        get_delivery_server_by_sub_key_func, # type: callable_
        sync_backlog_get_delete_messages_by_sub_keys_func # type: callable_
    ) -> 'None':

        self.lock = lock
        self.topics = topics
        self.sync_max_iters = sync_max_iters
        self.invoke_service_func = invoke_service_func
        self.set_sync_has_msg_func = set_sync_has_msg_func
        self.get_subscriptions_by_topic_func = get_subscriptions_by_topic_func
        self.get_delivery_server_by_sub_key_func = get_delivery_server_by_sub_key_func
        self.sync_backlog_get_delete_messages_by_sub_keys_func = sync_backlog_get_delete_messages_by_sub_keys_func

        self.keep_running = True

# ################################################################################################################################

    def run(self) -> 'None':
        """ A background greenlet which periodically lets delivery tasks know that there are perhaps
        new GD messages for the topic that this class represents.
        """

        # Local aliases

        _current_iter = 0
        _new_cid      = new_cid
        _spawn        = cast_('callable_', spawn)
        _sleep        = cast_('callable_', sleep)
        _self_lock    = self.lock
        _self_topics  = self.topics

        _logger_info      = logger.info
        _logger_warn      = logger.warning
        _logger_zato_warn = logger_zato.warning

        _self_invoke_service   = self.invoke_service_func
        _self_set_sync_has_msg = self.set_sync_has_msg_func

        _self_get_subscriptions_by_topic     = self.get_subscriptions_by_topic_func
        _self_get_delivery_server_by_sub_key = self.get_delivery_server_by_sub_key_func

        _sync_backlog_get_delete_messages_by_sub_keys = self.sync_backlog_get_delete_messages_by_sub_keys_func

        def _cmp_non_gd_msg(elem:'anydict') -> 'float':
            return elem['pub_time']

        # Loop forever or until stopped
        while self.keep_running:

            # Optionally, we may have a limit on how many iterations this loop should last
            # and we need to check if we have reached it.
            if self.sync_max_iters:
                if _current_iter >= self.sync_max_iters:
                    self.keep_running = False

            # This may be handy for logging purposes, even if there is no max. for the loop iters
            _current_iter += 1

            # Sleep for a while before continuing - the call to sleep is here because this while loop is quite long
            # so it would be inconvenient to have it down below.
            _sleep(0.01)

            # Blocks other pub/sub processes for a moment
            with _self_lock:

                # Will map a few temporary objects down below
                topic_id_dict = {} # type: intanydict

                # Get all topics ..
                for _topic in _self_topics.values():

                    # Does the topic require task synchronization now?
                    if not _topic.needs_task_sync():
                        continue
                    else:
                        _topic.update_task_sync_time()

                    # OK, the time has come for this topic to sync its state with subscribers
                    # but still skip it if we know that there have been no messages published to it since the last time.
                    if not (_topic.sync_has_gd_msg or _topic.sync_has_non_gd_msg):
                        continue

                    # There are some messages, let's see if there are subscribers ..
                    subs = [] # type: sublist
                    _subs = _self_get_subscriptions_by_topic(_topic.name)

                    # Filter out subscriptions for whom we have no subscription servers
                    for _sub in _subs:
                        if _self_get_delivery_server_by_sub_key(_sub.sub_key):
                            subs.append(_sub)

                    # .. if there are any subscriptions at all, we store that information for later use.
                    if subs:
                        topic_id_dict[_topic.id] = (_topic.name, subs)

                # OK, if we had any subscriptions for at least one topic and there are any messages waiting,
                # we can continue.
                try:

                    for topic_id in topic_id_dict:

                        topic = _self_topics[topic_id]

                        # .. get the temporary metadata object stored earlier ..
                        topic_name, subs = topic_id_dict[topic_id]

                        cid = _new_cid()
                        _logger_info('Triggering sync for `%s` len_s:%d gd:%d ngd:%d cid:%s',
                            topic_name, len(subs), topic.sync_has_gd_msg, topic.sync_has_non_gd_msg, cid)

                        # Build a list of sub_keys for whom we know what their delivery server is which will
                        # allow us to send messages only to tasks that are known to be up.
                        sub_keys = [item.sub_key for item in subs]

                        # Continue only if there are actually any sub_keys left = any tasks up and running ..
                        if sub_keys:

                            non_gd_msg_list = _sync_backlog_get_delete_messages_by_sub_keys(topic_id, sub_keys)

                            # .. also, continue only if there are still messages for the ones that are up ..
                            if topic.sync_has_gd_msg or topic.sync_has_non_gd_msg:

                                # Note that we may have both GD and non-GD messages on input
                                # and we need to have a max that takes both into account.
                                max_gd = 0
                                max_non_gd = 0

                                # If there are any non-GD messages, get their max. pub time
                                if non_gd_msg_list:
                                    non_gd_msg_list = sorted(non_gd_msg_list, key=_cmp_non_gd_msg)
                                    max_non_gd = non_gd_msg_list[-1]['pub_time']

                                # This will be always available, even if with a value of 0.0
                                max_gd = topic.gd_pub_time_max

                                # Now, we can build a max. pub time that takes GD and non-GD into account.
                                pub_time_max = max(max_gd, max_non_gd)

                                non_gd_msg_list_msg_id_list = [elem['pub_msg_id'] for elem in non_gd_msg_list]

                                _logger_info('Forwarding messages to a task for `%s` ngd-list:%s (sk_list:%s) cid:%s',
                                    topic_name, non_gd_msg_list_msg_id_list, sub_keys, cid)

                                # .. and notify all the tasks in background.
                                _ = _spawn(_self_invoke_service, 'zato.pubsub.after-publish', {
                                    'cid': cid,
                                    'topic_id':topic_id,
                                    'topic_name':topic_name,
                                    'subscriptions': subs,
                                    'non_gd_msg_list': non_gd_msg_list,
                                    'has_gd_msg_list': topic.sync_has_gd_msg,
                                    'is_bg_call': True, # This is a background call, i.e. issued by this trigger,
                                    'pub_time_max': pub_time_max, # Last time either a non-GD or GD message was received
                                })

                        # OK, we can now reset message flags for the topic
                        _self_set_sync_has_msg(topic_id, True, False, 'PubSub.loop')
                        _self_set_sync_has_msg(topic_id, False, False, 'PubSub.loop')

                except Exception:
                    e_formatted = format_exc()
                    _logger_zato_warn(e_formatted)
                    _logger_warn(e_formatted)

# ################################################################################################################################
# ################################################################################################################################
