# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pylint: disable=unused-import, redefined-builtin, unused-variable

# stdlib
import logging
import os
from contextlib import closing
from io import StringIO
from operator import attrgetter
from traceback import format_exc

# gevent
from gevent.lock import RLock

# Texttable
from texttable import Texttable

# Zato
from zato.common.api import PUBSUB
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.odb.model import WebSocketClientPubSubKeys
from zato.common.odb.query.pubsub.queue import set_to_delete
from zato.common.typing_ import cast_, dict_, optional
from zato.common.util.api import as_bool, spawn_greenlet, wait_for_dict_key, wait_for_dict_key_by_get_func
from zato.common.util.time_ import datetime_from_ms, utcnow_as_ms
from zato.server.pubsub.core.endpoint import EndpointAPI
from zato.server.pubsub.core.trigger import NotifyPubSubTasksTrigger
from zato.server.pubsub.core.hook import HookAPI
from zato.server.pubsub.core.pubapi import PubAPI
from zato.server.pubsub.core.sql import SQLAPI
from zato.server.pubsub.core.topic import TopicAPI
from zato.server.pubsub.model import inttopicdict, strsubdict, strtopicdict, Subscription, SubKeyServer
from zato.server.pubsub.publisher import Publisher
from zato.server.pubsub.sync import InRAMSync

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, anytuple, callable_, callnone, dictlist, intdict, \
        intlist, intnone, list_, stranydict, strnone, strstrdict, strlist, strlistdict, \
        strlistempty, strtuple, type_
    from zato.distlock import Lock
    from zato.server.base.parallel import ParallelServer
    from zato.server.pubsub.model import Endpoint, subnone, sublist, Topic, topiclist
    from zato.server.pubsub.delivery.task import msgiter
    from zato.server.pubsub.delivery.tool import PubSubTool
    from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato_pubsub.ps')
logger_zato = logging.getLogger('zato')
logger_overflow = logging.getLogger('zato_pubsub_overflow')

# ################################################################################################################################
# ################################################################################################################################

_ps_default = PUBSUB.DEFAULT
_end_srv_id = PUBSUB.ENDPOINT_TYPE.SERVICE.id

# ################################################################################################################################
# ################################################################################################################################

default_sk_server_table_columns = 6, 15, 8, 6, 17, 80
default_sub_pattern_matched = '(No sub pattern)'

# ################################################################################################################################
# ################################################################################################################################

class PubSub:

    endpoint_api: 'EndpointAPI'
    notify_pub_sub_tasks_trigger: 'NotifyPubSubTasksTrigger'

    def __init__(
        self,
        cluster_id,         # type: int
        server,             # type: ParallelServer
        broker_client=None, # type: any_
        *,
        sync_max_iters=None,      # type: intnone
        spawn_trigger_notify=True # type: bool
    ) -> 'None':

        self.cluster_id = cluster_id
        self.server = server
        self.broker_client = broker_client
        self.sync_max_iters = sync_max_iters
        self.lock = RLock()
        self.sk_server_table_columns = self.server.fs_server_config.pubsub.get('sk_server_table_columns') or \
            default_sk_server_table_columns # type: anytuple

        # This is a pub/sub tool for delivery of Zato services within this server
        self.service_pubsub_tool = None # type: optional[PubSubTool]

        self.has_meta_topic = self.server.fs_server_config.pubsub_meta_topic.enabled
        self.topic_meta_store_frequency = self.server.fs_server_config.pubsub_meta_topic.store_frequency

        self.log_if_deliv_server_not_found = \
            self.server.fs_server_config.pubsub.log_if_deliv_server_not_found # type: bool

        self.log_if_wsx_deliv_server_not_found = \
            self.server.fs_server_config.pubsub.log_if_wsx_deliv_server_not_found # type: bool

        # Manages Endpoint objects
        self.endpoint_api = EndpointAPI()

        # Topic name -> List of Subscription objects
        self.subscriptions_by_topic = {} # type: dict_[str, sublist]

        # Sub key -> Subscription object
        self._subscriptions_by_sub_key = {} # type: strsubdict

        # Sub key -> SubKeyServer server/PID handling it
        self.sub_key_servers = {} # type: dict_[str, SubKeyServer]

        # Sub key -> PubSubTool object
        self.pubsub_tool_by_sub_key = {} # type: dict_[str, PubSubTool]

        # A list of PubSubTool objects, each containing delivery tasks
        self.pubsub_tools = [] # type: list_[PubSubTool]

        # A backlog of messages that have at least one subscription, i.e. this is what delivery servers use.
        self.sync_backlog = InRAMSync(self)

        # How many messages have been published through this server, regardless of which topic they were for
        self.msg_pub_counter = 0

        # How many messages a given endpoint published, topic_id -> its message counter.
        self.endpoint_msg_counter = {} # type: intdict

        self.has_meta_endpoint = cast_('bool', self.server.fs_server_config.pubsub_meta_endpoint_pub.enabled)
        self.endpoint_meta_store_frequency = self.server.fs_server_config.pubsub_meta_endpoint_pub.store_frequency # type: int
        self.endpoint_meta_data_len = self.server.fs_server_config.pubsub_meta_endpoint_pub.data_len # type:int
        self.endpoint_meta_max_history = self.server.fs_server_config.pubsub_meta_endpoint_pub.max_history # type:int

        # How many bytes to use for look up purposes when conducting message searches
        self.data_prefix_len = self.server.fs_server_config.pubsub.data_prefix_len # type: int
        self.data_prefix_short_len = self.server.fs_server_config.pubsub.data_prefix_short_len # type: int

        # Creates SQL sessions
        self.new_session_func = self.server.odb.session

        # A low level implementation that publishes messages to SQL
        self.impl_publisher = Publisher(
            pubsub = self,
            server = self.server,
            marshal_api = self.server.marshal_api,
            service_invoke_func = self.invoke_service,
            new_session_func = self.new_session_func
        )

        # Manages hooks
        self.hook_api = HookAPI(
            lock = self.lock,
            server = self.server,
            invoke_service_func = self.invoke_service,
        )

        # Manages topics
        self.topic_api = TopicAPI(
            hook_api = self.hook_api,
            server_name = self.server.name,
            server_pid = self.server.pid,
            topic_meta_store_frequency = self.topic_meta_store_frequency,
            subscriptions_by_topic = self.subscriptions_by_topic,
            is_allowed_sub_topic_by_endpoint_id_func = self.is_allowed_sub_topic_by_endpoint_id,
        )

        # Provides access to SQL queries
        self.sql_api = SQLAPI(self.cluster_id, self.new_session_func)

        # Low-level implementation of the public pub/sub API
        self.pubapi = PubAPI(
            pubsub = self,
            cluster_id = self.server.cluster_id,
            service_store = self.server.service_store,
            topic_api = self.topic_api,
            endpoint_api = self.endpoint_api,
        )

        # This will trigger synchronization
        self.notify_pub_sub_tasks_trigger = NotifyPubSubTasksTrigger(
            lock = self.lock,
            topics = self.topic_api.get_topics(),
            sync_max_iters = self.sync_max_iters,
            invoke_service_func = self.invoke_service,
            set_sync_has_msg_func = self._set_sync_has_msg,
            get_subscriptions_by_topic_func = self.get_subscriptions_by_topic,
            get_delivery_server_by_sub_key_func = self.get_delivery_server_by_sub_key,
            sync_backlog_get_delete_messages_by_sub_keys_func = self.sync_backlog.get_delete_messages_by_sub_keys
        )

        if spawn_trigger_notify:
            _ = spawn_greenlet(self.notify_pub_sub_tasks_trigger.run)

# ################################################################################################################################

    def stop(self) -> 'None':
        """ Stops all pub/sub tools, which in turn stops all the delivery tasks.
        """
        for item in self.pubsub_tools:
            try:
                item.stop()
            except Exception:
                logger.info('Ignoring exception in PubSub.stop -> %s', format_exc())

# ################################################################################################################################

    @property
    def subscriptions_by_sub_key(self) -> 'strsubdict':
        return self._subscriptions_by_sub_key

# ################################################################################################################################

    def incr_pubsub_msg_counter(self, endpoint_id:'int') -> 'None':
        with self.lock:

            # Update the overall counter
            self.msg_pub_counter += 1

            # Update the per-endpoint counter too
            if endpoint_id in self.endpoint_msg_counter:
                self.endpoint_msg_counter[endpoint_id] += 1
            else:
                self.endpoint_msg_counter[endpoint_id] = 0

# ################################################################################################################################

    def needs_endpoint_meta_update(self, endpoint_id:'int') -> 'bool':
        with self.lock:
            return self.endpoint_msg_counter[endpoint_id] % self.endpoint_meta_store_frequency == 0

# ################################################################################################################################

    def get_subscriptions_by_topic(self, topic_name:'str', require_backlog_messages:'bool'=False) -> 'sublist':
        with self.lock:
            subs = self.subscriptions_by_topic.get(topic_name, [])
            subs = subs[:]
            if require_backlog_messages:
                out = [] # type: anylist
                for item in subs:
                    if self.sync_backlog.has_messages_by_sub_key(item.sub_key):
                        out.append(item)
                return out
            else:
                return subs

# ################################################################################################################################

    def get_all_subscriptions(self) -> 'strsubdict':
        """ Low-level method to return all the subscriptions by sub_key,
        must be called with self.lock held.
        """
        return self.subscriptions_by_sub_key

# ################################################################################################################################

    def _wait_for_sub_key(self, sub_key:'str') -> 'None':

        # Log what we are about to do
        logger.info('Waiting for sub_key -> %s', sub_key)

        # Make sure the key is there.
        wait_for_dict_key(self.subscriptions_by_sub_key, sub_key, timeout=180)

# ################################################################################################################################

    def _get_subscription_by_sub_key(self, sub_key:'str') -> 'Subscription':
        """ Low-level implementation of self.get_subscription_by_sub_key, must be called with self.lock held.
        """
        # Make sure the key is there ..
        # self._wait_for_sub_key(sub_key)

        # .. get the subscription ..
        sub = self.subscriptions_by_sub_key.get(sub_key)

        # .. and return it to the caller if it exists ..
        if sub:
            return sub

        # .. otherwise, raise an error ..
        else:
            msg = 'No such subscription `{}` among `{}`'.format(sub_key, sorted(self.subscriptions_by_sub_key))
            logger.info(msg)
            raise KeyError(msg)

# ################################################################################################################################

    def get_subscription_by_sub_key(self, sub_key:'str') -> 'subnone':
        with self.lock:
            try:
                return self._get_subscription_by_sub_key(sub_key)
            except KeyError:
                return None

# ################################################################################################################################

    def get_subscription_by_endpoint_id(
        self,
        endpoint_id,      # type: int
        topic_name,       # type: str
        needs_error=True, # type: bool
    ) -> 'subnone':

        with self.lock:
            for sub in self.get_all_subscriptions().values():
                if sub.endpoint_id == endpoint_id:
                    return sub
            else:
                msg = f'No sub to topic `{topic_name}` for endpoint_id `{endpoint_id}`'
                if needs_error:
                    raise KeyError(msg)
                else:
                    logger.info(msg)

# ################################################################################################################################

    def get_subscription_by_id(self, sub_id:'int') -> 'subnone':
        with self.lock:
            for sub in self.subscriptions_by_sub_key.values():
                if sub.id == sub_id:
                    return sub

# ################################################################################################################################

    def get_subscription_by_ext_client_id(self, ext_client_id:'str') -> 'subnone':
        with self.lock:
            for sub in self.subscriptions_by_sub_key.values():
                if sub.ext_client_id == ext_client_id:
                    return sub

# ################################################################################################################################

    def _write_log_sub_data(self, sub:'Subscription', out:'StringIO') -> 'None':
        items = sorted(sub.to_dict().items())

        _ = out.write('\n')
        for key, value in items:
            _ = out.write(' - {} {}'.format(key, value))
            if key == 'creation_time':
                _ = out.write('\n - creation_time_utc {}'.format(datetime_from_ms(value)))
            _ = out.write('\n')

# ################################################################################################################################

    def _log_subscriptions_dict(self, attr_name:'str', prefix:'str', title:'str') -> 'None':
        out = StringIO()
        _ = out.write('\n')

        attr = getattr(self, attr_name) # type: anydict

        for sub_key, sub_data in sorted(attr.items()):
            sub_key = cast_('str', sub_key)
            _ = out.write('* {}\n'.format(sub_key))

            if isinstance(sub_data, Subscription):
                self._write_log_sub_data(sub_data, out)
            else:
                sorted_sub_data = sorted(sub_data)
                for item in sorted_sub_data:
                    if isinstance(item, Subscription):
                        self._write_log_sub_data(item, out)
                    else:
                        item = cast_('any_', item)
                        _ = out.write(' - {}'.format(item))
                        _ = out.write('\n')

            _ = out.write('\n')

        logger_zato.info('\n === %s (%s) ===\n %s', prefix, title, out.getvalue())
        out.close()

# ################################################################################################################################

    def log_subscriptions_by_sub_key(self, title:'str', prefix:'str'='PubSub.subscriptions_by_sub_key') -> 'None':
        with self.lock:
            self._log_subscriptions_dict('subscriptions_by_sub_key', prefix, title)

# ################################################################################################################################

    def log_subscriptions_by_topic_name(self, title:'str', prefix:'str'='PubSub.subscriptions_by_topic') -> 'None':
        with self.lock:
            self._log_subscriptions_dict('subscriptions_by_topic', prefix, title)

# ################################################################################################################################

    def has_sub_key(self, sub_key:'str') -> 'bool':
        with self.lock:
            return sub_key in self.subscriptions_by_sub_key

# ################################################################################################################################

    def has_messages_in_backlog(self, sub_key:'str') -> 'bool':
        with self.lock:
            return self.sync_backlog.has_messages_by_sub_key(sub_key)

# ################################################################################################################################

    def _len_subscribers(self, topic_name:'str') -> 'int':
        """ Low-level implementation of self.len_subscribers, must be called with self.lock held.
        """
        return len(self.subscriptions_by_topic[topic_name])

# ################################################################################################################################

    def len_subscribers(self, topic_name:'str') -> 'int':
        """ Returns the amount of subscribers for a given topic.
        """
        with self.lock:
            return self._len_subscribers(topic_name)

# ################################################################################################################################

    def has_subscribers(self, topic_name:'str') -> 'bool':
        """ Returns True if input topic has at least one subscriber.
        """
        with self.lock:
            return self._len_subscribers(topic_name) > 0

# ################################################################################################################################

    def has_topic_by_name(self, topic_name:'str') -> 'bool':
        with self.lock:
            return self.topic_api.has_topic_by_name(topic_name)

# ################################################################################################################################

    def has_topic_by_id(self, topic_id:'int') -> 'bool':
        with self.lock:
            return self.topic_api.has_topic_by_id(topic_id)

# ################################################################################################################################

    def get_endpoint_by_id(self, endpoint_id:'int') -> 'Endpoint':
        with self.lock:
            return self.endpoint_api.get_by_id(endpoint_id)

# ################################################################################################################################

    def get_endpoint_by_name(self, endpoint_name:'str') -> 'Endpoint':
        with self.lock:
            return self.endpoint_api.get_by_name(endpoint_name)

# ################################################################################################################################

    def get_endpoint_by_ws_channel_id(self, ws_channel_id:'int') -> 'Endpoint':
        with self.lock:
            return self.endpoint_api.get_by_ws_channel_id(ws_channel_id)

# ################################################################################################################################

    def get_endpoint_id_by_sec_id(self, sec_id:'int') -> 'int':
        with self.lock:
            return self.endpoint_api.get_id_by_sec_id(sec_id)

# ################################################################################################################################

    def get_endpoint_id_by_ws_channel_id(self, ws_channel_id:'int') -> 'intnone':
        with self.lock:
            return self.endpoint_api.get_id_by_ws_channel_id(ws_channel_id)

# ################################################################################################################################

    def get_endpoint_id_by_service_id(self, service_id:'int') -> 'int':
        with self.lock:
            return self.endpoint_api.get_id_by_service_id(service_id)

# ################################################################################################################################

    def create_endpoint(self, config:'anydict') -> 'None':
        with self.lock:
            self.endpoint_api.create(config)

# ################################################################################################################################

    def delete_endpoint(self, endpoint_id:'int') -> 'None':
        with self.lock:

            # First, delete the endpoint object ..
            self.endpoint_api.delete(endpoint_id)

            # .. a list of of sub_keys for this endpoint ..
            sk_list = []

            # .. find all the sub_keys this endpoint held ..
            for sub in self.subscriptions_by_sub_key.values():
                if sub.endpoint_id == endpoint_id:
                    sk_list.append(sub.sub_key)

            # .. delete all references to the sub_keys found ..
            for sub_key in sk_list: # type: ignore

                # .. first, stop the delivery tasks ..
                _ = self._delete_subscription_by_sub_key(sub_key, ignore_missing=True)

# ################################################################################################################################

    def edit_endpoint(self, config:'stranydict') -> 'None':
        with self.lock:
            self.endpoint_api.delete(config['id'])
            self.endpoint_api.create(config)

# ################################################################################################################################

    def wait_for_endpoint(self, endpoint_name:'str', timeout:'int'=600) -> 'bool':
        return wait_for_dict_key_by_get_func(self.endpoint_api.get_by_name, endpoint_name, timeout, interval=0.5)

# ################################################################################################################################

    def get_endpoint_impl_getter(self, endpoint_type:'str') -> 'callable_':
        with self.lock:
            return self.endpoint_api.get_impl_getter(endpoint_type)

# ################################################################################################################################

    def set_endpoint_impl_getter(self, endpoint_type:'str', impl_getter:'callable_') -> 'None':
        with self.lock:
            return self.endpoint_api.set_impl_getter(endpoint_type, impl_getter)

# ################################################################################################################################

    def get_topic_id_by_name(self, topic_name:'str') -> 'int':
        with self.lock:
            return self.topic_api.get_topic_id_by_name(topic_name)

# ################################################################################################################################

    def get_non_gd_topic_depth(self, topic_name:'str') -> 'int':
        """ Returns of non-GD messages for a given topic by its name.
        """
        with self.lock:
            topic_id = self.topic_api.get_topic_id_by_name(topic_name)
            return self.sync_backlog.get_topic_depth(topic_id)

# ################################################################################################################################

    def get_topic_by_name(self, topic_name:'str') -> 'Topic':
        with self.lock:
            return self.get_topic_by_name_no_lock(topic_name)

# ################################################################################################################################

    def get_topic_by_name_no_lock(self, topic_name:'str') -> 'Topic':
        return self.topic_api.get_topic_by_name(topic_name)

# ################################################################################################################################

    def get_topic_by_id(self, topic_id:'int') -> 'Topic':
        with self.lock:
            return self.topic_api.get_topic_by_id(topic_id)

# ################################################################################################################################

    def get_topic_name_by_sub_key(self, sub_key:'str') -> 'str':
        with self.lock:
            return self._get_subscription_by_sub_key(sub_key).topic_name

# ################################################################################################################################

    def get_target_service_name_by_topic_id(self, topic_id:'int') -> 'strnone':
        with self.lock:
            topic = self.topic_api.get_topic_by_id(topic_id)
            return topic.config.get('target_service_name')

# ################################################################################################################################

    def get_sub_key_to_topic_name_dict(self, sub_key_list:'strlist') -> 'strstrdict':
        out = {} # type: strstrdict
        with self.lock:
            for sub_key in sub_key_list:
                out[sub_key] = self._get_subscription_by_sub_key(sub_key).topic_name

        return out

# ################################################################################################################################

    def _get_topic_by_sub_key(self, sub_key:'str') -> 'Topic':
        sub = self._get_subscription_by_sub_key(sub_key)
        return self.topic_api.get_topic_by_name(sub.topic_name)

# ################################################################################################################################

    def get_topic_by_sub_key(self, sub_key:'str') -> 'Topic':
        with self.lock:
            return self._get_topic_by_sub_key(sub_key)

# ################################################################################################################################

    def get_topic_list_by_sub_key_list(self, sk_list:'strlist') -> 'strtopicdict':
        out = cast_('strtopicdict', {})
        with self.lock:
            for sub_key in sk_list:
                out[sub_key] = self._get_topic_by_sub_key(sub_key)
        return out

# ################################################################################################################################

    def edit_subscription(self, config:'stranydict') -> 'None':

        # Make sure we are the only ones updating the configuration now ..
        with self.lock:

            # Reusable ..
            sub_key = config['sub_key']

            # .. such a subscription should exist ..
            sub = self._get_subscription_by_sub_key(config['sub_key'])

            # .. update the whole config of the subscription object in place ..
            for key, value in config.items():
                sub.config[key] = value

            # .. now, try obtain the PubSub tool responsible for this subscription ..
            # .. and trigger an update of the underlying delivery task's configuration as well, ..
            # .. note, however, that there may be no such ps_tool when we edit a WebSockets-based subscription ..
            # .. and the WebSocket client is not currently connected.
            if ps_tool := self._get_pubsub_tool_by_sub_key(sub_key):
                ps_tool.trigger_update_task_sub_config(sub_key)

# ################################################################################################################################

    def _add_subscription(self, config:'stranydict') -> 'None':
        """ Low-level implementation of self.add_subscription.
        """
        sub = Subscription(config)

        existing_by_topic = self.subscriptions_by_topic.setdefault(config['topic_name'], [])
        existing_by_topic.append(sub)

        logger_zato.info('Added sub `%s` -> `%s`', config['sub_key'], config['topic_name'])

        self.subscriptions_by_sub_key[config['sub_key']] = sub

# ################################################################################################################################

    def add_subscription(self, config:'stranydict') -> 'None':
        """ Creates a Subscription object and an associated mapping of the subscription to input topic.
        """
        with self.lock:

            # Creates a subscription ..
            self._add_subscription(config)

            # .. triggers a relevant hook, if any is configured.
            hook = self.get_on_subscribed_hook(config['sub_key'])
            if hook:
                _ = self.invoke_on_subscribed_hook(hook, config['topic_id'], config['sub_key'])

# ################################################################################################################################

    def _delete_subscription_from_subscriptions_by_topic(self, sub:'Subscription') -> 'None':

        # This is a list of all the subscriptions related to a given topic,
        # it may be potentially empty if we are trying to delete subscriptions
        # for a topic that has just been deleted ..
        sk_list = self.get_subscriptions_by_topic(sub.topic_name)

        # .. try to remove the subscription object from each list ..
        try:
            sk_list.remove(sub)
        except ValueError:
            # .. it is fine, this list did not contain the sub object.
            pass

# ################################################################################################################################

    def clear_task(self, sub_key:'str') -> 'None':
        with self.lock:
            # Clear the task but only if a given ps_tool exists at all.
            # It may be missing if the sub_key points to a WebSocket
            # that is not connected at the moment.
            if ps_tool := self._get_pubsub_tool_by_sub_key(sub_key):
                ps_tool.clear_task(sub_key)

# ################################################################################################################################

    def _delete_subscription_by_sub_key(
        self,
        sub_key,          # type: str
        ignore_missing,   # type: bool
        _invalid=object() # type: any_
    ) -> 'subnone':
        """ Deletes a subscription from the list of subscription. By default, it is not an error to call
        the method with an invalid sub_key. Must be invoked with self.lock held.
        """
        sub = self.subscriptions_by_sub_key.get(sub_key, _invalid) # type: Subscription

        #
        # There is no such subscription and we may either log it or raise an exception ..
        #
        if sub is _invalid:

            # If this is on, we only log information about the event ..
            if ignore_missing:
                logger.info('Could not find sub_key to delete `%s`', sub_key)

            # .. otherwise, we raise an entire exception.
            else:
                raise KeyError('No such sub_key `%s`', sub_key)

        #
        # If we are here, it means that the subscription is valid
        #
        else:

            # Now, delete the subscription
            sub = self.subscriptions_by_sub_key.pop(sub_key, _invalid)

            # Delete the subscription's sk_server first because it depends on the subscription
            # for sk_server table formatting.
            self.delete_sub_key_server(sub_key, sub_pattern_matched=sub.sub_pattern_matched)

            # Stop and remove the task for this sub_key ..
            if ps_tool := self._get_pubsub_tool_by_sub_key(sub_key):
                ps_tool.delete_by_sub_key(sub_key)

            # Remove the mapping from the now-removed sub_key to its ps_tool
            self._delete_subscription_from_subscriptions_by_topic(sub)

            # Remove the subscription from the mapping of topics-to-sub-objects
            self._delete_pubsub_tool_by_sub_key(sub_key)

            # Log what we have done ..
            logger.info('Deleted subscription object `%s` (%s)', sub.sub_key, sub.topic_name)

            return sub # Either valid or invalid but ignore_missing is True

# ################################################################################################################################

    def create_subscription_object(self, config:'stranydict') -> 'None':
        """ Low-level implementation of self.subscribe. Must be called with self.lock held.
        """
        with self.lock:

            # It's possible that we already have this subscription - this may happen if we are the server that originally
            # handled the request to create the subscription and we are now called again through
            # on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE. In such a case, we can just ignore it.
            if not self.has_sub_key(config['sub_key']):
                self._add_subscription(config)

            # Is this a WebSockets-based subscription?
            is_wsx = config['endpoint_type'] == PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id

            # .. we do not start dedicated tasks for WebSockets - they are all dynamic without a fixed server ..
            if is_wsx:
                pass

            # .. for other endpoint types, we create and start a delivery task here ..
            else:

                # We have a matching server..
                if config['cluster_id'] == self.cluster_id and config['server_id'] == self.server.id:

                    # .. but make sure only the first worker of this server will start delivery tasks, not all of them.
                    if self.server.is_first_worker:

                        # Store in shared RAM information that our process handles this key
                        if self.server.has_posix_ipc:
                            self.server.server_startup_ipc.set_pubsub_pid(self.server.pid)

                        config['server_pid'] = self.server.pid
                        config['server_name'] = self.server.name

                        # Starts the delivery task and notifies other servers that we are the one
                        # to handle deliveries for this particular sub_key.
                        _ = self.invoke_service('zato.pubsub.delivery.create-delivery-task', config)

                    # We are not the first worker of this server and the first one must have already stored
                    # in RAM the mapping of sub_key -> server_pid, so we can safely read it here to add
                    # a subscription server.
                    else:
                        if self.server.has_posix_ipc:
                            config['server_pid'] = self.server.server_startup_ipc.get_pubsub_pid()
                            config['server_name'] = self.server.name
                            self.set_sub_key_server(config)

# ################################################################################################################################

    def create_topic_object(self, config:'anydict') -> 'None':
        with self.lock:
            self.topic_api.create_topic_object(config)

# ################################################################################################################################

    def create_topic_for_service(self, service_name:'str', topic_name:'str') -> 'None':
        self.create_topic(topic_name, is_internal=True, target_service_name=service_name)
        logger.info('Created topic `%s` for service `%s`', topic_name, service_name)

# ################################################################################################################################

    def wait_for_topic(self, topic_name:'str', timeout:'int'=600) -> 'bool':
        return wait_for_dict_key_by_get_func(self.topic_api.get_topic_by_name, topic_name, timeout, interval=0.01)

# ################################################################################################################################

    def delete_topic(self, topic_id:'int') -> 'None':
        with self.lock:
            topic = self.topic_api.get_topic_by_id(topic_id)
            topic_name = topic.name
            subscriptions_by_topic = self.topic_api.delete_topic(topic_id, topic_name) # type: sublist

            for sub in subscriptions_by_topic:
                _ = self._delete_subscription_by_sub_key(sub.sub_key, ignore_missing=True)

# ################################################################################################################################

    def edit_topic(self, del_name:'str', config:'anydict') -> 'None':
        with self.lock:
            subscriptions_by_topic = self.subscriptions_by_topic.pop(del_name, [])
            _ = self.topic_api.delete_topic(config['id'], del_name)
            self.topic_api.create_topic_object(config)
            self.subscriptions_by_topic[config['name']] = subscriptions_by_topic

# ################################################################################################################################

    def set_config_for_service_subscription(
        self,
        sub_key, # type: str
        _endpoint_type=_end_srv_id # type: str
    ) -> 'None':

        if self.service_pubsub_tool:
            self.service_pubsub_tool.add_sub_key(sub_key)
        else:
            msg = 'No self.service_pubsub_tool to add sub key to (%s)'
            logger.warning(msg, sub_key)
            logger_zato.warning(msg, sub_key)

        self.set_sub_key_server({
            'sub_key': sub_key,
            'cluster_id': self.server.cluster_id,
            'server_name': self.server.name,
            'server_pid': self.server.pid,
            'endpoint_type': _endpoint_type,
        })

# ################################################################################################################################

    def is_allowed_pub_topic(self, name:'str', security_id:'int'=0, ws_channel_id:'int'=0) -> 'str | bool':
        return self.endpoint_api.is_allowed_pub_topic(
            name=name,
            security_id=security_id,
            ws_channel_id=ws_channel_id
        )

# ################################################################################################################################

    def is_allowed_pub_topic_by_endpoint_id(self, name:'str', endpoint_id:'int') -> 'str | bool':
        return self.endpoint_api.is_allowed_pub_topic_by_endpoint_id(
            name=name,
            endpoint_id=endpoint_id
        )

# ################################################################################################################################

    def is_allowed_sub_topic(self, name:'str', security_id:'int'=0, ws_channel_id:'int'=0) -> 'str | bool':
        return self.endpoint_api.is_allowed_sub_topic(
            name=name,
            security_id=security_id,
            ws_channel_id=ws_channel_id
        )

# ################################################################################################################################

    def is_allowed_sub_topic_by_endpoint_id(self, name:'str', endpoint_id:'int') -> 'str | bool':
        return self.endpoint_api.is_allowed_sub_topic_by_endpoint_id(
            name=name,
            endpoint_id=endpoint_id
        )

# ################################################################################################################################

    def get_topics(self) -> 'inttopicdict':
        """ Returns all topics in existence.
        """
        with self.lock:
            return self.topic_api.get_topics()

# ################################################################################################################################

    def get_sub_topics_for_endpoint(self, endpoint_id:'int') -> 'topiclist':
        """ Returns all topics to which endpoint_id can subscribe.
        """
        with self.lock:
            return self.topic_api.get_sub_topics_for_endpoint(endpoint_id)

# ################################################################################################################################

    def _is_subscribed_to(self, endpoint_id:'int', topic_name:'str') -> 'bool':
        """ Low-level implementation of self.is_subscribed_to.
        """
        for sub in self.subscriptions_by_topic.get(topic_name, []):
            if sub.endpoint_id == endpoint_id:
                return True
        else:
            return False

# ################################################################################################################################

    def is_subscribed_to(self, endpoint_id:'int', topic_name:'str') -> 'bool':
        """ Returns True if the endpoint is subscribed to the named topic.
        """
        with self.lock:
            return self._is_subscribed_to(endpoint_id, topic_name)

# ################################################################################################################################

    def _delete_pubsub_tool_by_sub_key(self, sub_key:'str') -> 'None':
        _ = self.pubsub_tool_by_sub_key.pop(sub_key, None)

# ################################################################################################################################

    def _get_pubsub_tool_by_sub_key(self, sub_key:'str') -> 'PubSubTool | None':
        return self.pubsub_tool_by_sub_key.get(sub_key)

# ################################################################################################################################

    def get_pubsub_tool_by_sub_key(self, sub_key:'str') -> 'PubSubTool | None':
        with self.lock:
            return self._get_pubsub_tool_by_sub_key(sub_key)

# ################################################################################################################################

    def add_wsx_client_pubsub_keys(
        self,
        session,          # type: any_
        sql_ws_client_id, # type: int
        sub_key,          # type: str
        channel_name,     # type: str
        pub_client_id,    # type: str
        wsx_info          # type: anydict
    ) -> 'None':
        """ Adds to SQL information that a given WSX client handles messages for sub_key.
        This information is transient - it will be dropped each time a WSX client disconnects
        """
        # Update state in SQL
        ws_sub_key = WebSocketClientPubSubKeys()
        ws_sub_key.client_id = sql_ws_client_id
        ws_sub_key.sub_key = sub_key
        ws_sub_key.cluster_id = self.cluster_id
        session.add(ws_sub_key)

        # Update in-RAM state of workers
        self.broker_client.publish({
            'action': BROKER_MSG_PUBSUB.SUB_KEY_SERVER_SET.value,
            'cluster_id': self.cluster_id,
            'server_name': self.server.name,
            'server_pid': self.server.pid,
            'sub_key': sub_key,
            'channel_name': channel_name,
            'pub_client_id': pub_client_id,
            'endpoint_type': PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id,
            'wsx_info': wsx_info,
            'source': 'pubsub.PubSub',
            'source_server_name': self.server.name,
            'source_server_pid': self.server.pid,
        })

# ################################################################################################################################

    def format_sk_servers(self, default:'str'='---', sub_pattern_matched:'str'=default_sub_pattern_matched) -> 'str':

        # Prepare the table
        len_columns = len(self.sk_server_table_columns)

        table = Texttable()
        _ = table.set_cols_width(self.sk_server_table_columns)
        _ = table.set_cols_dtype(['t'] * len_columns)
        _ = table.set_cols_align(['c'] * len_columns)
        _ = table.set_cols_valign(['m'] * len_columns)

        # Add headers
        rows = [['#', 'created', 'name', 'pid', 'channel_name', 'sub_key']] # type: anylist

        servers = list(self.sub_key_servers.values())
        servers.sort(key=attrgetter('creation_time', 'channel_name', 'sub_key'), reverse=True)

        for idx, item in enumerate(servers, 1):

            # Let the basic information contain both the sub_key and the pattern matched during subscription.
            sub = self.get_subscription_by_sub_key(item.sub_key)
            if sub:
                sub_pattern_matched = sub.sub_pattern_matched
            else:
                sub_pattern_matched = sub_pattern_matched or default_sub_pattern_matched
            basic_info = f'{item.sub_key} -> {sub_pattern_matched}'

            sub_key_info = [basic_info]

            if item.wsx_info:
                for name in ('swc', 'name', 'pub_client_id', 'peer_fqdn', 'forwarded_for_fqdn'):
                    if isinstance(name, bytes):
                        name = name.decode('utf8')
                    value = item.wsx_info[name]

                    if isinstance(value, bytes):
                        value = value.decode('utf8')

                    if isinstance(value, str):
                        value = value.strip()

                    sub_key_info.append('{}: {}'.format(name, value))

            rows.append([
                idx,
                item.creation_time,
                item.server_name,
                item.server_pid,
                item.channel_name or default,
                '\n'.join(sub_key_info),
            ])

        # Add all rows to the table
        _ = table.add_rows(rows)

        # And return already formatted output
        return cast_('str', table.draw())

# ################################################################################################################################

    def _set_sub_key_server(
        self,
        config, # type: stranydict
        *,
        ignore_missing_sub_key, # type: bool
        _endpoint_type=PUBSUB.ENDPOINT_TYPE # type: type_[PUBSUB.ENDPOINT_TYPE]
    ) -> 'None':
        """ Low-level implementation of self.set_sub_key_server - must be called with self.lock held.
        """

        try:
            # Try to see if we have such a subscription ..
            sub = self._get_subscription_by_sub_key(config['sub_key'])
        except KeyError:

            # .. if we do not, it may be because it was already deleted
            # before we have been invoked and this may be potentially ignored.

            if not ignore_missing_sub_key:
                raise

        else:

            sub_key:'str' = config['sub_key']
            sk_server = SubKeyServer(config)
            self.sub_key_servers[sub_key] = sk_server

            config['endpoint_id'] = sub.endpoint_id
            config['endpoint_name'] = self.endpoint_api.get_by_id(sub.endpoint_id)

            endpoint_type = config['endpoint_type']

            config['wsx'] = int(endpoint_type == _endpoint_type.WEB_SOCKETS.id)
            config['srv'] = int(endpoint_type == _endpoint_type.SERVICE.id)

            server_pid:'str' = config['server_pid']
            server_name:'str' = config['server_name']
            is_wsx:'int' = config['wsx']
            is_service:'int' = config['srv']
            pid_info:'str' = ' ' if config['server_pid'] else ' (no PID) '

            # This is basic information that we always log ..
            msg  = f'Set sk_server{pid_info}for sub_key `{sub_key}` (w/s:{is_wsx}/{is_service}) - {server_name}:{server_pid}'
            msg += f', len-sks:{len(self.sub_key_servers)}'

            # .. optionally, we log the full connection table too ..
            if as_bool(os.environ.get(PUBSUB.Env.Log_Table)):
                sks_table = self.format_sk_servers()
                msg += f', current sk_servers:\n{sks_table}'

            logger.info(msg)
            logger_zato.info(msg)

# ################################################################################################################################

    def set_sub_key_server(self, config:'anydict') -> 'None':
        with self.lock:
            self._set_sub_key_server(config, ignore_missing_sub_key=True)

# ################################################################################################################################

    def _get_sub_key_server(self, sub_key:'str', default:'any_'=None) -> 'sksnone': # type: ignore[valid-type]
        return self.sub_key_servers.get(sub_key, default)

# ################################################################################################################################

    def get_sub_key_server(self, sub_key:'str', default:'any_'=None) -> 'sksnone': # type: ignore[valid-type]
        with self.lock:
            return self._get_sub_key_server(sub_key, default)

# ################################################################################################################################

    def get_delivery_server_by_sub_key(self, sub_key:'str', needs_lock:'bool'=True) -> 'sksnone': # type: ignore[valid-type]
        if needs_lock:
            with self.lock:
                return self._get_sub_key_server(sub_key)
        else:
            return self._get_sub_key_server(sub_key)

# ################################################################################################################################

    def _delete_sub_key_server(self, sub_key:'str', sub_pattern_matched:'str'='') -> 'None':
        sub_key_server = self.sub_key_servers.get(sub_key)
        if sub_key_server:
            msg = 'Deleting sk_server for sub_key `%s`, was `%s:%s`'

            logger.info(msg, sub_key, sub_key_server.server_name, sub_key_server.server_pid)
            logger_zato.info(msg, sub_key, sub_key_server.server_name, sub_key_server.server_pid)

            _ = self.sub_key_servers.pop(sub_key, None)

            if as_bool(os.environ.get(PUBSUB.Env.Log_Table)):
                sks_table = self.format_sk_servers(sub_pattern_matched=sub_pattern_matched)
                msg_sks = 'Current sk_servers after deletion of `%s`:\n%s'

                logger.info(msg_sks, sub_key, sks_table)
                logger_zato.info(msg_sks, sub_key, sks_table)

        else:
            logger.info('Could not find sub_key `%s` while deleting sub_key server, current `%s` `%s`',
                sub_key, self.server.name, self.server.pid)

# ################################################################################################################################

    def delete_sub_key_server(self, sub_key:'str', sub_pattern_matched:'str'='') -> 'None':
        with self.lock:
            self._delete_sub_key_server(sub_key, sub_pattern_matched)

# ################################################################################################################################

    def remove_ws_sub_key_server(self, config:'stranydict') -> 'None':
        """ Called after a WSX client disconnects - provides a list of sub_keys that it handled
        which we must remove from our config because without this client they are no longer usable (until the client reconnects).
        """
        with self.lock:
            for sub_key in config['sub_key_list']:
                _ = self.sub_key_servers.pop(sub_key, None)

                # ->> Compare this loop with the .pop call above
                for server_info in self.sub_key_servers.values():
                    if server_info.sub_key == sub_key:
                        del self.sub_key_servers[sub_key]
                        break

# ################################################################################################################################

    def get_server_pid_for_sub_key(self, server_name:'str', sub_key:'str') -> 'intnone':
        """ Invokes a named server on current cluster and asks it for PID of one its processes that handles sub_key.
        Returns that PID or None if the information could not be obtained.
        """
        try:
            invoker = self.server.rpc.get_invoker_by_server_name(server_name)
            response = invoker.invoke('zato.pubsub.delivery.get-server-pid-for-sub-key', {
                'sub_key': sub_key,
            }) # type: anydict
        except Exception:
            msg = 'Could not invoke server `%s` to get PID for sub_key `%s`, e:`%s`'
            exc_formatted = format_exc()
            logger.warning(msg, server_name, sub_key, exc_formatted)
            logger_zato.warning(msg, server_name, sub_key, exc_formatted)
        else:
            return response['response']['server_pid']

# ################################################################################################################################

    def add_missing_server_for_sub_key(
        self,
        sub_key, # type: str
        is_wsx,  # type: bool
        _wsx=PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id # type: str
    ) -> 'None':
        """ Adds to self.sub_key_servers information from ODB about which server handles input sub_key.
        Must be called with self.lock held.
        """
        data = self.sql_api.get_delivery_server_for_sub_key(sub_key, is_wsx)

        if not data:
            if self.log_if_deliv_server_not_found:
                if is_wsx and (not self.log_if_wsx_deliv_server_not_found):
                    return
                msg = 'Could not find a delivery server in ODB for sub_key `%s` (wsx:%s)'
                logger.info(msg, sub_key, is_wsx)
        else:

            endpoint_type = _wsx if is_wsx else data.endpoint_type

            # This is common config that we already know is valid but on top of it
            # we will try to the server found and ask about PID that handles messages for sub_key.
            config = {
                'sub_key': sub_key,
                'cluster_id': data.cluster_id,
                'server_name': data.server_name,
                'endpoint_type': endpoint_type,
            } # type: anydict

            # Guaranteed to either set PID or None
            config['server_pid'] = self.get_server_pid_for_sub_key(data.server_name, sub_key)

            # OK, set up the server with what we found above
            self._set_sub_key_server(config, ignore_missing_sub_key=False)

# ################################################################################################################################

    def get_task_servers_by_sub_keys(self, sub_key_data:'dictlist') -> 'anytuple':
        """ Returns a dictionary keyed by (server_name, server_pid, pub_client_id, channel_name) tuples
        and values being sub_keys that a WSX client pointed to by each key has subscribed to.
        """
        with self.lock:
            found = {}     # type: anydict
            not_found = [] # type: anylist

            for elem in sub_key_data:

                sub_key = elem['sub_key']
                is_wsx = elem['is_wsx']

                # If we do not have a server for this sub_key we first attempt to find
                # if there is an already running server that handles it but we do not know it yet.
                # It may happen if our server is down, another server (for this sub_key) boots up
                # and notifies other servers about its existence and the fact that we handle this sub_key
                # but we are still down so we never receive this message. In this case we attempt to look up
                # the target server in ODB and then invoke it to get the PID of worker process that handles
                # sub_key, populating self.sub_key_servers as we go.
                if not sub_key in self.sub_key_servers:
                    self.add_missing_server_for_sub_key(sub_key, is_wsx)

                # At this point, if there is any information about this sub_key at all,
                # no matter if its server is running or not, info will not be None.
                info = self.sub_key_servers.get(sub_key)

                # We report that a server is found only if we know the server itself and its concrete PID,
                # which means that the server is currently running. Checking for server alone is not enough
                # because we may have read this information from self.add_missing_server_for_sub_key
                # and yet, self.get_server_pid_for_sub_key may have returned no information implying
                # that the server, even if found in ODB in principle, is still currently not running.
                if info and info.server_pid:
                    _key = (info.server_name, info.server_pid, info.pub_client_id, info.channel_name, info.endpoint_type)
                    _info = found.setdefault(_key, [])
                    _info.append(sub_key)
                else:
                    not_found.append(sub_key)

            return found, not_found

# ################################################################################################################################

    def get_sql_messages_by_sub_key(self, *args:'any_', **kwargs:'any_') -> 'anytuple':
        """ Returns all SQL messages queued up for all keys from sub_key_list.
        """
        return self.sql_api.get_sql_messages_by_sub_key(*args, **kwargs)

# ################################################################################################################################

    def get_initial_sql_msg_ids_by_sub_key(self, *args:'any_', **kwargs:'any_') -> 'anytuple':
        return self.sql_api.get_initial_sql_msg_ids_by_sub_key(*args, **kwargs)

# ################################################################################################################################

    def get_sql_messages_by_msg_id_list(self, *args:'any_', **kwargs:'any_') -> 'anytuple':
        return self.sql_api.get_sql_messages_by_msg_id_list(*args, **kwargs)

# ################################################################################################################################

    def confirm_pubsub_msg_delivered(self, *args:'any_', **kwargs:'any_') -> 'None':
        """ Sets in SQL delivery status of a given message to True.
        """
        self.sql_api.confirm_pubsub_msg_delivered(*args, **kwargs)

# ################################################################################################################################

    def store_in_ram(
        self,
        cid,        # type: str
        topic_id,   # type: int
        topic_name, # type: str
        sub_keys,   # type: strlist
        non_gd_msg_list, # type: dictlist
        error_source='', # type: str
        _logger=logger   # type: logging.Logger
    ) -> 'None':
        """ Stores in RAM up to input non-GD messages for each sub_key. A backlog queue for each sub_key
        cannot be longer than topic's max_depth_non_gd and overflowed messages are not kept in RAM.
        They are not lost altogether though, because, if enabled by topic's use_overflow_log, all such messages
        go to disk (or to another location that logger_overflown is configured to use).
        """
        _logger.info('Storing in RAM. CID:`%r`, topic ID:`%r`, name:`%r`, sub_keys:`%r`, ngd-list:`%r`, e:`%s`',
            cid, topic_id, topic_name, sub_keys, [elem['pub_msg_id'] for elem in non_gd_msg_list], error_source)

        with self.lock:

            # Store the non-GD messages in backlog ..
            topic = self.topic_api.get_topic_by_id(topic_id)
            self.sync_backlog.add_messages(cid, topic_id, topic_name, topic.max_depth_non_gd, sub_keys, non_gd_msg_list)

            # .. and set a flag to signal that there are some available.
            self._set_sync_has_msg(topic_id, False, True, 'PubSub.store_in_ram ({})'.format(error_source))

# ################################################################################################################################

    def unsubscribe(self, topic_sub_keys:'strlistdict') -> 'None':
        """ Removes subscriptions for all input sub_keys. Input topic_sub_keys is a dictionary keyed by topic_name,
        and each value is a list of sub_keys, possibly one-element long.
        """
        with self.lock:
            for topic_name, sub_keys in topic_sub_keys.items():

                # We receive topic_names on input but in-RAM backlog requires topic IDs.
                topic_id = self.topic_api.get_topic_id_by_name(topic_name)

                # Delete subscriptions, and any related messages, from RAM
                self.sync_backlog.unsubscribe(topic_id, topic_name, sub_keys)

                # Delete subscription metadata from local pubsub, note that we use .get
                # instead of deleting directly because this dictionary will be empty
                # right after a server starts but before any client for that topic (such as WSX) connects to it.
                subscriptions_by_topic = self.subscriptions_by_topic.get(topic_name, [])

                for sub in subscriptions_by_topic[:]:
                    if sub.sub_key in sub_keys:
                        subscriptions_by_topic.remove(sub)

                for sub_key in sub_keys:

                    # Remove mappings between sub_keys and sub objects but keep the subscription object around
                    # because an unsubscribe hook may need it.
                    deleted_sub = self._delete_subscription_by_sub_key(sub_key, ignore_missing=True)

                    # Find and stop all delivery tasks if we are the server that handles them
                    sub_key_server = self.sub_key_servers.get(sub_key)
                    if sub_key_server:

                        _cluster_id = sub_key_server.cluster_id
                        _server_name = sub_key_server.server_name
                        _server_pid = sub_key_server.server_pid

                        cluster_id = self.server.cluster_id
                        server_name = self.server.name
                        server_pid = self.server.pid

                        # If we are the server that handles this particular sub_key ..
                        if _cluster_id == cluster_id and _server_name == server_name and _server_pid == server_pid:

                            # .. then find the pubsub_tool that actually does it ..
                            for pubsub_tool in self.pubsub_tools:
                                if pubsub_tool.handles_sub_key(sub_key):

                                    # .. stop the delivery task ..
                                    pubsub_tool.remove_sub_key(sub_key)

                                    # and remove the mapping of sub_key -> pubsub_tool ..
                                    del self.pubsub_tool_by_sub_key[sub_key]

                                    # .. and invoke the unsubscription hook, if any is given.
                                    hook = self.get_on_unsubscribed_hook(sub=deleted_sub)
                                    if hook:
                                        self.invoke_on_unsubscribed_hook(hook, topic_id, deleted_sub)

                                    # No need to iterate further, there can be only one task for each sub_key
                                    break

# ################################################################################################################################

    def register_pubsub_tool(self, pubsub_tool:'PubSubTool') -> 'None':
        """ Registers a new pubsub_tool for this server, i.e. a new delivery task container.
        """
        self.pubsub_tools.append(pubsub_tool)

# ################################################################################################################################

    def set_pubsub_tool_for_sub_key(self, sub_key:'str', pubsub_tool:'PubSubTool') -> 'None':
        """ Adds a mapping between a sub_key and pubsub_tool handling its messages.
        """
        self.pubsub_tool_by_sub_key[sub_key] = pubsub_tool

# ################################################################################################################################

    def migrate_delivery_server(self, msg:'anydict') -> 'None':
        """ Migrates the delivery task for sub_key to a new server given by ID on input,
        including all current in-RAM messages. This method must be invoked in the same worker process that runs
        delivery task for sub_key.
        """
        _ = self.invoke_service('zato.pubsub.migrate.migrate-delivery-server', {
            'sub_key': msg['sub_key'],
            'old_delivery_server_id': msg['old_delivery_server_id'],
            'new_delivery_server_name': msg['new_delivery_server_name'],
            'endpoint_type': msg['endpoint_type'],
        })

# ################################################################################################################################

    def get_before_delivery_hook(self, sub_key:'str') -> 'callnone':
        """ Returns a hook for messages to be invoked right before they are about to be delivered
        or None if such a hook is not defined for sub_key's topic.
        """
        with self.lock:
            sub = self.get_subscription_by_sub_key(sub_key)
            if sub:
                topic = self.topic_api.get_topic_by_name(sub.topic_name)
                return topic.before_delivery_hook_service_invoker

# ################################################################################################################################

    def get_on_subscribed_hook(self, sub_key:'str') -> 'callnone':
        """ Returns a hook triggered when a new subscription is made to a particular topic.
        """
        with self.lock:
            sub = self.get_subscription_by_sub_key(sub_key)
            if sub:
                topic = self.topic_api.get_topic_by_name(sub.topic_name)
                return topic.on_subscribed_service_invoker

# ################################################################################################################################

    def get_on_unsubscribed_hook(self, sub_key:'str'='', sub:'subnone'=None) -> 'callnone':
        """ Returns a hook triggered when a client unsubscribes from a topic.
        """
        with self.lock:
            sub = sub or self.get_subscription_by_sub_key(sub_key)
            if sub:
                topic = self.topic_api.get_topic_by_name(sub.topic_name)
                return topic.on_unsubscribed_service_invoker

# ################################################################################################################################

    def get_on_outgoing_soap_invoke_hook(self, sub_key:'str') -> 'callnone':
        """ Returns a hook that sends outgoing SOAP Suds connections-based messages or None if there is no such hook
        for sub_key's topic.
        """
        with self.lock:
            sub = self.get_subscription_by_sub_key(sub_key)
            if sub:
                topic = self.topic_api.get_topic_by_name(sub.topic_name)
                return topic.on_outgoing_soap_invoke_invoker

# ################################################################################################################################

    def invoke_before_delivery_hook(
        self,
        hook,     # type: callable_
        topic_id, # type: int
        sub_key,  # type: str
        batch,    # type: msgiter
        messages, # type: anydict
        actions=tuple(PUBSUB.HOOK_ACTION()), # type: strtuple
        _deliver=PUBSUB.HOOK_ACTION.DELIVER  # type: str
    ) -> 'None':
        """ Invokes a hook service for each message from a batch of messages possibly to be delivered and arranges
        each one to a specific key in messages dict.
        """
        for msg in batch:
            topic = self.topic_api.get_topic_by_id(topic_id)
            response = hook(topic, msg)
            hook_action = response.get('hook_action', _deliver) # type: str

            if hook_action not in actions:
                raise ValueError('Invalid action returned `{}` for msg `{}`'.format(hook_action, msg))
            else:
                messages[hook_action].append(msg)

# ################################################################################################################################

    def invoke_on_outgoing_soap_invoke_hook(self, batch:'anylist', sub:'Subscription', http_soap:'any_') -> 'None':
        hook = self.get_on_outgoing_soap_invoke_hook(sub.sub_key)
        topic = self.get_topic_by_id(sub.config['topic_id'])
        if hook:
            hook(topic, batch, http_soap=http_soap)
        else:
            # We know that this service exists, it just does not implement the expected method
            service_info = self.server.service_store.get_service_info_by_id(topic.config['hook_service_id'])
            service_class = service_info['service_class'] # type: Service
            service_name = service_class.get_name()
            raise Exception('Hook service `{}` does not implement `on_outgoing_soap_invoke` method'.format(service_name))

# ################################################################################################################################

    def _invoke_on_sub_unsub_hook(
        self,
        hook,       # type: callable_
        topic_id,   # type: int
        sub_key='', # type: str
        sub=None    # type: subnone
    ) -> 'any_':
        sub = sub if sub else self._get_subscription_by_sub_key(sub_key)
        topic = self.topic_api.get_topic_by_id(topic_id)
        return hook(topic=topic, sub=sub)

# ################################################################################################################################

    def invoke_on_subscribed_hook(self, hook:'callable_', topic_id:'int', sub_key:'str') -> 'any_':
        return self._invoke_on_sub_unsub_hook(hook, topic_id, sub_key, sub=None)

# ################################################################################################################################

    def invoke_on_unsubscribed_hook(self, hook:'callable_', topic_id:'int', sub:'subnone') -> 'any_':
        return self._invoke_on_sub_unsub_hook(hook, topic_id, sub_key='', sub=sub)

# ################################################################################################################################

    def on_broker_msg_HOT_DEPLOY_CREATE_SERVICE(self, services_deployed:'intlist') -> 'None':
        """ Invoked after a package with one or more services is hot-deployed. Goes over all topics
        and updates hooks that any of these services possibly implements.
        """
        with self.lock:
            topics = self.topic_api.get_topics()
            for topic in topics.values():
                hook_service_id = topic.config.get('hook_service_id')
                if hook_service_id in services_deployed:
                    self.hook_api.set_topic_config_hook_data(topic.config)
                    topic.set_hooks()

# ################################################################################################################################

    def deliver_pubsub_msg(self, sub_key:'str', msg:'msgiter') -> 'any_':
        """ A callback method invoked by pub/sub delivery tasks for one or more message that is to be delivered.
        """
        return self.invoke_service('zato.pubsub.delivery.deliver-message', {
            'msg':msg,
            'subscription':self.get_subscription_by_sub_key(sub_key)
        })

# ################################################################################################################################

    def set_to_delete(self, sub_key:'str', msg_list:'strlistempty') -> 'None':
        """ Marks all input messages as ready to be deleted.
        """
        logger.info('Deleting messages set to be deleted `%s`', msg_list)

        with closing(self.new_session_func()) as session:
            set_to_delete(session, self.cluster_id, sub_key, msg_list, utcnow_as_ms())

# ################################################################################################################################

    def topic_lock(self, topic_name:'str') -> 'Lock':
        return self.server.zato_lock_manager('zato.pubsub.publish.%s' % topic_name)

# ################################################################################################################################

    def invoke_service(self, name:'str', msg:'any_', *args:'any_', **kwargs:'any_') -> 'any_':
        return self.server.invoke(name, msg, *args, **kwargs)

# ################################################################################################################################

    def after_gd_sync_error(self,
        topic_id,     # type: int
        source,       # type: str
        pub_time_max, # type: float
        _float_str=PUBSUB.FLOAT_STRING_CONVERT # type: str
    ) -> 'None':
        """ Invoked by the after-publish service in case there was an error with letting
        a delivery task know about GD messages it was to handle. Resets the topic's
        sync_has_gd_msg flag to True to make sure the notification will be resent
        in the main loop's next iteration.
        """
        # Get the topic object
        topic = self.topic_api.get_topic_by_id(topic_id) # type: Topic

        # Store information about what we are about to do
        logger.info('Will resubmit GD messages after sync error; topic:`%s`, src:`%s`', topic.name, source)

        with self.lock:

            # We need to use the correct value of pub_time_max - since we are resyncing
            # a failed message for a delivery task, it is possible that in the meantime
            # another message was published to the topic so in case topic's gd_pub_time_max
            # is bigger than our pub_time_max, the value from topic takes precedence.
            topic_gd_pub_time_max = topic.gd_pub_time_max

            if topic_gd_pub_time_max > pub_time_max:
                logger.warning('Choosing topic\'s gd_pub_time_max:`%s` over `%s`',
                    topic_gd_pub_time_max, _float_str.format(pub_time_max))
                new_pub_time_max = topic_gd_pub_time_max
            else:
                new_pub_time_max = pub_time_max

            self._set_sync_has_msg(topic_id, True, True, source, new_pub_time_max)

# ################################################################################################################################

    def _set_sync_has_msg(self,
        topic_id,            # type: int
        is_gd,               # type: bool
        value,               # type: bool
        source,              # type: str
        gd_pub_time_max=0.0  # type: float
    ) -> 'None':
        """ Updates a given topic's flags indicating that a message has been published since the last sync.
        Must be called with self.lock held.
        """
        topic = self.topic_api.get_topic_by_id(topic_id) # type: Topic

        if is_gd:
            topic.sync_has_gd_msg = value
            topic.gd_pub_time_max = gd_pub_time_max
        else:
            topic.sync_has_non_gd_msg = value

# ################################################################################################################################

    def set_sync_has_msg(
        self,
        *,
        topic_id,       # type: int
        is_gd,          # type: bool
        value,          # type: bool
        source,         # type: str
        gd_pub_time_max # type: float
    ) -> 'None':
        with self.lock:
            self._set_sync_has_msg(topic_id, is_gd, value, source, gd_pub_time_max)

# ################################################################################################################################

    def get_default_internal_pubsub_endpoint_id(self) -> 'int':
        return self.server.get_default_internal_pubsub_endpoint_id()

# ################################################################################################################################
# ################################################################################################################################

# Public API methods

# ################################################################################################################################
# ################################################################################################################################

    def publish(
        self,
        name:'any_',
        *args:'any_',
        **kwargs:'any_'
    ) -> 'any_':
        """ Publishes a new message to input name, which may point either to a topic or service.
        POST /zato/pubsub/topic/{topic_name}
        """
        return self.pubapi.publish(name, *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

    def get_messages(
        self,
        topic_name,            # type: str
        sub_key,               # type: str
        /,
        needs_details=False,   # type: bool
        needs_msg_id=False,    # type: bool
    ) -> 'anylist':
        """ Returns messages from a subscriber's queue, deleting them from the queue in progress.
        POST /zato/pubsub/topic/{topic_name}?sub_key=...
        """
        return self.pubapi.get_messages(topic_name, sub_key, needs_details, needs_msg_id)

# ################################################################################################################################
# ################################################################################################################################

    def read_messages(
        self,
        topic_name, # type: str
        sub_key,    # type: str
        has_gd,     # type: bool
        *args,      # type: any_
        **kwargs    # type: any_
    ) -> 'any_':
        """ Looks up messages in subscriber's queue by input criteria without deleting them from the queue.
        """
        return self.pubapi.read_messages(topic_name, sub_key, has_gd, *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

    def read_message(
        self,
        topic_name, # type: str
        msg_id,     # type: str
        has_gd,     # type: bool
        *args,      # type: any_
        **kwargs    # type: any_
    ) -> 'any_':
        """ Returns details of a particular message without deleting it from the subscriber's queue.
        """
        return self.pubapi.read_message(topic_name, msg_id, has_gd, *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

    def delete_message(
        self,
        sub_key,  # type: str
        msg_id,   # type: str
        has_gd,   # type: bool
        *args,    # type: anytuple
        **kwargs, # type: any_
    ) -> 'any_':
        """ Deletes a message from a subscriber's queue.
        DELETE /zato/pubsub/msg/{msg_id}
        """
        return self.pubapi.delete_message(sub_key, msg_id, has_gd, *args, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

    def subscribe(
        self,
        topic_name, # type: str
        **kwargs    # type: any_
    ) -> 'str':
        return self.pubapi.subscribe(topic_name, **kwargs)

# ################################################################################################################################
# ################################################################################################################################

    def resume_wsx_subscription(
        self,
        sub_key, # type: str
        service, # type: Service
    ) -> 'None':
        """ Invoked by WSX clients that want to resume deliveries of their messages after they reconnect.
        """
        return self.pubapi.resume_wsx_subscription(sub_key, service)

# ################################################################################################################################
# ################################################################################################################################

    def create_topic(self,
        name,                     # type: str
        has_gd=False,             # type: bool
        accept_on_no_sub=True,    # type: bool
        is_active=True,           # type: bool
        is_internal=False,        # type: bool
        is_api_sub_allowed=True,  # type: bool
        hook_service_id=None,     # type: intnone
        target_service_name=None, # type: strnone
        task_sync_interval=_ps_default.TASK_SYNC_INTERVAL,         # type: int
        task_delivery_interval=_ps_default.TASK_DELIVERY_INTERVAL, # type: int
        depth_check_freq=_ps_default.DEPTH_CHECK_FREQ,             # type: int
        max_depth_gd=_ps_default.TOPIC_MAX_DEPTH_GD,               # type: int
        max_depth_non_gd=_ps_default.TOPIC_MAX_DEPTH_NON_GD,       # type: int
        pub_buffer_size_gd=_ps_default.PUB_BUFFER_SIZE_GD,         # type: int
    ) -> 'None':

        self.pubapi.create_topic(
            name = name,
            has_gd = has_gd,
            accept_on_no_sub = accept_on_no_sub,
            is_active = is_active,
            is_internal = is_internal,
            is_api_sub_allowed = is_api_sub_allowed,
            hook_service_id = hook_service_id,
            target_service_name = target_service_name,
            task_sync_interval = task_sync_interval,
            task_delivery_interval = task_delivery_interval,
            depth_check_freq = depth_check_freq,
            max_depth_gd = max_depth_gd,
            max_depth_non_gd = max_depth_non_gd,
            pub_buffer_size_gd = pub_buffer_size_gd
        )

# ################################################################################################################################
# ################################################################################################################################

sksnone = optional[SubKeyServer]

# ################################################################################################################################
# ################################################################################################################################
