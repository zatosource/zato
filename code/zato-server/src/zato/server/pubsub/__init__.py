# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from contextlib import closing
from datetime import datetime
from operator import attrgetter
from traceback import format_exc

# gevent
from gevent import sleep, spawn
from gevent.lock import RLock

# globre
from globre import compile as globre_compile

# Texttable
from texttable import Texttable

# Python 2/3 compatibility
from future.utils import iteritems, itervalues

# Zato
from zato.common import DATA_FORMAT, PUBSUB, SEARCH
from zato.common.broker_message import PUBSUB as BROKER_MSG_PUBSUB
from zato.common.exception import BadRequest
from zato.common.odb.model import WebSocketClientPubSubKeys
from zato.common.odb.query.pubsub.delivery import confirm_pubsub_msg_delivered as _confirm_pubsub_msg_delivered, \
     get_delivery_server_for_sub_key, get_sql_messages_by_msg_id_list as _get_sql_messages_by_msg_id_list, \
     get_sql_messages_by_sub_key as _get_sql_messages_by_sub_key, get_sql_msg_ids_by_sub_key as _get_sql_msg_ids_by_sub_key
from zato.common.odb.query.pubsub.queue import set_to_delete
from zato.common.pubsub import dict_keys, skip_to_external
from zato.common.util import make_repr, new_cid, spawn_greenlet
from zato.common.util.event import EventLog
from zato.common.util.hook import HookTool
from zato.common.util.pubsub import make_short_msg_copy_from_dict
from zato.common.util.python_ import get_current_stack
from zato.common.util.time_ import utcnow_as_ms
from zato.common.util.wsx import find_wsx_environ

# ################################################################################################################################

logger = logging.getLogger('zato_pubsub.ps')
logger_zato = logging.getLogger('zato')
logger_overflow = logging.getLogger('zato_pubsub_overflow')

# ################################################################################################################################

hook_type_to_method = {
    PUBSUB.HOOK_TYPE.BEFORE_PUBLISH: 'before_publish',
    PUBSUB.HOOK_TYPE.BEFORE_DELIVERY: 'before_delivery',
    PUBSUB.HOOK_TYPE.ON_OUTGOING_SOAP_INVOKE: 'on_outgoing_soap_invoke',
    PUBSUB.HOOK_TYPE.ON_SUBSCRIBED: 'on_subscribed',
    PUBSUB.HOOK_TYPE.ON_UNSUBSCRIBED: 'on_unsubscribed',
}

# ################################################################################################################################

_service_read_messages_gd = 'zato.pubsub.endpoint.get-endpoint-queue-messages-gd'
_service_read_messages_non_gd = 'zato.pubsub.endpoint.get-endpoint-queue-messages-non-gd'

_service_read_message_gd = 'zato.pubsub.message.get-from-queue-gd'
_service_read_message_non_gd = 'zato.pubsub.message.get-from-queue-non-gd'

_service_delete_message_gd = 'zato.pubsub.message.queue-delete-gd'
_service_delete_message_non_gd = 'zato.pubsub.message.queue-delete-non-gd'

# ################################################################################################################################

_pub_role = (PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id, PUBSUB.ROLE.PUBLISHER.id)
_sub_role = (PUBSUB.ROLE.PUBLISHER_SUBSCRIBER.id, PUBSUB.ROLE.SUBSCRIBER.id)

# ################################################################################################################################

_update_attrs = ('data', 'size', 'expiration', 'priority', 'pub_correl_id', 'in_reply_to', 'mime_type',
    'expiration', 'expiration_time')

# ################################################################################################################################

_does_not_exist = object()

# ################################################################################################################################

_default_expiration = PUBSUB.DEFAULT.EXPIRATION
default_sk_server_table_columns = 6, 15, 8, 6, 17, 80

# ################################################################################################################################

_PRIORITY=PUBSUB.PRIORITY
_JSON=DATA_FORMAT.JSON
_page_size = SEARCH.ZATO.DEFAULTS.PAGE_SIZE.value

class msg:
    wsx_sub_resumed = 'WSX subscription resumed, sk:`%s`, peer:`%s`'

# ################################################################################################################################

def get_priority(cid, input, _pri_min=_PRIORITY.MIN, _pri_max=_PRIORITY.MAX, _pri_def=_PRIORITY.DEFAULT):
    """ Get and validate message priority.
    """
    priority = input.get('priority')
    if priority:
        if priority < _pri_min or priority > _pri_max:
            raise BadRequest(cid, 'Priority `{}` outside of allowed range {}-{}'.format(priority, _pri_min, _pri_max))
    else:
        priority = _pri_def

    return priority

# ################################################################################################################################

def get_expiration(cid, input, default_expiration=_default_expiration):
    """ Get and validate message expiration.
    Returns (2 ** 31 - 1) * 1000 milliseconds (around 68 years) if expiration is not set explicitly.
    """
    expiration = input.get('expiration')
    if expiration is not None and expiration < 0:
        raise BadRequest(cid, 'Expiration `{}` must not be negative'.format(expiration))

    return expiration or default_expiration

# ################################################################################################################################

class EventType:

    class Topic:
        set_hooks = 'set_hooks'
        incr_topic_msg_counter = 'incr_topic_msg_counter'
        update_task_sync_time_before = 'update_task_sync_time_before'
        update_task_sync_time_after = 'update_task_sync_time_after'
        needs_task_sync_before = 'needs_task_sync_before'
        needs_task_sync_after = 'needs_task_sync_after'

    class PubSub:
        loop_topic_id_dict = 'loop_topic_id_dict'
        loop_sub_keys = 'loop_sub_keys'
        loop_before_has_msg = 'loop_before_has_msg'
        loop_has_msg = 'loop_has_msg'
        loop_before_sync = 'loop_before_sync'
        _set_sync_has_msg = '_set_sync_has_msg'
        about_to_subscribe = 'about_to_subscribe'
        about_to_access_sub_sk = 'about_to_access_sub_sk'
        in_subscribe_impl = 'in_subscribe_impl'

# ################################################################################################################################

class ToDictBase(object):
    _to_dict_keys = None

    def to_dict(self):
        out = {}

        for name in self._to_dict_keys:
            value = getattr(self, name, _does_not_exist)
            if value is _does_not_exist:
                value = self.config[name]
            out[name] = value

        return out

# ################################################################################################################################

class Endpoint(ToDictBase):
    """ A publisher/subscriber in pub/sub workflows.
    """
    _to_dict_keys = dict_keys.endpoint

    def __init__(self, config):
        self.config = config
        self.id = config.id
        self.name = config.name
        self.endpoint_type = config.endpoint_type
        self.role = config.role
        self.is_active = config.is_active
        self.is_internal = config.is_internal

        self.topic_patterns = config.topic_patterns or ''

        self.pub_topic_patterns = []
        self.sub_topic_patterns = []

        self.pub_topics = {}
        self.sub_topics = {}

        self.set_up_patterns()

# ################################################################################################################################

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

    def get_id(self):
        return '{};{};{}'.format(self.id, self.endpoint_type, self.name)

# ################################################################################################################################

    def to_dict(self, _replace=('pub_topic_patterns', 'sub_topic_patterns')):
        out = super(Endpoint, self).to_dict()
        for key, value in out.items():
            if key in _replace:
                if value:
                    out[key] = sorted([(elem[0], str(elem[1])) for elem in value])
        return out

# ################################################################################################################################

    def set_up_patterns(self):
        data = {
            'topic': self.topic_patterns,
        }

        # is_pub, is_topic -> target set
        targets = {
            (True, True): self.pub_topic_patterns,
            (False, True): self.sub_topic_patterns,
        }

        for key, config in iteritems(data):
            is_topic = key == 'topic'

            for line in config.splitlines():
                line = line.strip()
                if line.startswith('pub=') or line.startswith('sub='):
                    is_pub = line.startswith('pub=')

                    matcher = line[line.find('=')+1:]
                    matcher = globre_compile(matcher)

                    source = (is_pub, is_topic)
                    target = targets[source]
                    target.append([line, matcher])

                else:
                    logger.warn('Ignoring invalid {} pattern `{}` for `{}` (role:{}) (reason: no pub=/sub= prefix found)'.format(
                        key, line, self.name, self.role))

# ################################################################################################################################

class Topic(ToDictBase):
    """ An individiual topic in in pub/sub workflows.
    """
    _to_dict_keys = dict_keys.topic

    def __init__(self, config, server_name, server_pid):
        self.config = config
        self.server_name = server_name
        self.server_pid = server_pid
        self.id = config.id
        self.name = config.name
        self.is_active = config.is_active
        self.is_internal = config.is_internal
        self.max_depth_gd = config.max_depth_gd
        self.max_depth_non_gd = config.max_depth_non_gd
        self.has_gd = config.has_gd
        self.depth_check_freq = config.depth_check_freq
        self.pub_buffer_size_gd = config.pub_buffer_size_gd
        self.task_delivery_interval = config.task_delivery_interval
        self.meta_store_frequency = config.meta_store_frequency
        self.event_log = EventLog('t.{}.{}.{}'.format(self.server_name, self.server_pid, self.name))
        self.set_hooks()

        # For now, task sync interval is the same for GD and non-GD messages
        # so we can arbitrarily pick the former to serve for both types of messages.
        self.task_sync_interval = config.task_sync_interval / 1000.0

        # How many messages have been published to this topic from current server,
        # i.e. this is not a global counter.
        self.msg_pub_counter = 0
        self.msg_pub_counter_gd = 0
        self.msg_pub_counter_non_gd = 0

        # When were subscribers last notified about messages from current server,
        # again, this is not a global counter.
        self.last_synced = utcnow_as_ms()

        # Flags to indicate if there has been a GD or non-GD message published for this topic
        # since the last time self.last_synced has been updated. They are changed through PubSub
        # with a lock for this topic held.
        self.sync_has_gd_msg = False
        self.sync_has_non_gd_msg = False

        # The last time a GD message was published to this topic
        self.gd_pub_time_max = None

# ################################################################################################################################

    def _emit_set_hooks(self, ctx=None, _event=EventType.Topic.set_hooks):
        self.event_log.emit(_event, ctx)

    def _emit_incr_topic_msg_counter(self, ctx=None, _event=EventType.Topic.incr_topic_msg_counter):
        self.event_log.emit(_event, ctx)

    def _emit_update_task_sync_time_before(self, ctx=None, _event=EventType.Topic.update_task_sync_time_before):
        self.event_log.emit(_event, ctx)

    def _emit_update_task_sync_time_after(self, ctx=None, _event=EventType.Topic.update_task_sync_time_after):
        self.event_log.emit(_event, ctx)

    def _emit_needs_task_sync_before(self, ctx=None, _event=EventType.Topic.needs_task_sync_before):
        self.event_log.emit(_event, ctx)

    def _emit_needs_task_sync_after(self, ctx=None, _event=EventType.Topic.needs_task_sync_after):
        self.event_log.emit(_event, ctx)

# ################################################################################################################################

    def get_id(self):
        return '{};{}'.format(self.name, self.id)

# ################################################################################################################################

    def get_event_list(self):
        return self.event_log.get_event_list()

# ################################################################################################################################

    def set_hooks(self):
        self.on_subscribed_service_invoker = self.config.get('on_subscribed_service_invoker')
        self.on_unsubscribed_service_invoker = self.config.get('on_unsubscribed_service_invoker')
        self.before_publish_hook_service_invoker = self.config.get('before_publish_hook_service_invoker')
        self.before_delivery_hook_service_invoker = self.config.get('before_delivery_hook_service_invoker')
        self.on_outgoing_soap_invoke_invoker = self.config.get('on_outgoing_soap_invoke_invoker')

        #
        # Event log
        #
        self._emit_set_hooks({
            'on_subscribed_service_invoker': self.on_subscribed_service_invoker,
            'on_unsubscribed_service_invoker': self.on_unsubscribed_service_invoker,
            'before_publish_hook_service_invoker': self.before_publish_hook_service_invoker,
            'before_delivery_hook_service_invoker': self.before_delivery_hook_service_invoker,
            'on_outgoing_soap_invoke_invoker': self.on_outgoing_soap_invoke_invoker,
        })

# ################################################################################################################################

    def incr_topic_msg_counter(self, has_gd, has_non_gd):
        """ Increases counter of messages published to this topic from current server.
        """
        self.msg_pub_counter += 1

        if has_gd:
            self.msg_pub_counter_gd += 1

        if has_non_gd:
            self.msg_pub_counter_non_gd += 1

        #
        # Event log
        #
        self._emit_incr_topic_msg_counter({
            'has_gd': has_gd,
            'has_non_gd': has_non_gd,
            'msg_pub_counter': self.msg_pub_counter,
            'msg_pub_counter_gd': self.msg_pub_counter_gd,
            'msg_pub_counter_non_gd': self.msg_pub_counter_non_gd,
        })

# ################################################################################################################################

    def update_task_sync_time(self, _utcnow_as_ms=utcnow_as_ms):
        """ Increases counter of messages published to this topic from current server.
        """

        #
        # Event log
        #
        self._emit_update_task_sync_time_before({
            'last_synced': self.last_synced
        })

        self.last_synced = _utcnow_as_ms()

        #
        # Event log
        #
        self._emit_update_task_sync_time_after({
            'last_synced': self.last_synced
        })

# ################################################################################################################################

    def needs_task_sync(self, _utcnow_as_ms=utcnow_as_ms):

        now = _utcnow_as_ms()
        needs_sync = now - self.last_synced >= self.task_sync_interval

        #
        # Event log
        #
        self._emit_needs_task_sync_before({
            'now': now,
            'last_synced': self.last_synced,
            'last_synced': self.task_sync_interval,
            'needs_sync': needs_sync
        })

        return needs_sync

# ################################################################################################################################

    def needs_msg_cleanup(self):
        return self.msg_pub_counter_gd % 10000 == 0

# ################################################################################################################################

    def needs_depth_check(self):
        return self.msg_pub_counter_gd % self.depth_check_freq == 0

# ################################################################################################################################

    def needs_meta_update(self):
        return self.msg_pub_counter % self.meta_store_frequency == 0

# ################################################################################################################################

class Subscription(ToDictBase):
    """ Describes an existing subscription object.
    Note that, for WSX clients, it may exist even if the WebSocket is not currently connected.
    """
    _to_dict_keys = dict_keys.subscription

    def __init__(self, config):
        self.config = config
        self.id = config.id
        self.creation_time = config.creation_time * 1000.0
        self.sub_key = config.sub_key
        self.endpoint_id = config.endpoint_id
        self.topic_id = config.topic_id
        self.topic_name = config.topic_name
        self.sub_pattern_matched = config.sub_pattern_matched
        self.task_delivery_interval = config.task_delivery_interval
        self.unsub_on_wsx_close = config.get('unsub_on_wsx_close')
        self.ext_client_id = config.ext_client_id

        # Object ws_channel_id is an ID of a WSX channel this subscription potentially belongs to,
        # otherwise it is None.
        self.is_wsx = bool(self.config.ws_channel_id)

# ################################################################################################################################

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

    def get_id(self):
        return self.sub_key

# ################################################################################################################################

class HookCtx(object):
    __slots__ = ('hook_type', 'msg', 'topic', 'sub', 'http_soap', 'outconn_name')

    def __init__(self, hook_type, topic=None, msg=None, *args, **kwargs):
        self.hook_type = hook_type
        self.msg = msg
        self.topic = topic
        self.sub = kwargs.get('sub')
        self.http_soap = kwargs.get('http_soap', {})
        self.outconn_name = self.http_soap.get('config', {}).get('name')

# ################################################################################################################################

class SubKeyServer(ToDictBase):
    """ Holds information about which server has subscribers to an individual sub_key.
    """
    _to_dict_keys = dict_keys.sks

    def __init__(self, config, _utcnow=datetime.utcnow):
        self.config = config
        self.sub_key = config['sub_key']
        self.cluster_id = config['cluster_id']
        self.server_name = config['server_name']
        self.server_pid = config['server_pid']
        self.endpoint_type = config['endpoint_type']

        # Attributes below are only for WebSockets
        self.channel_name = config.get('channel_name', '')
        self.pub_client_id = config.get('pub_client_id', '')
        self.ext_client_id = config.get('ext_client_id', '')
        self.wsx_info = config.get('wsx_info')

        # When this object was created - we have both
        self.creation_time = _utcnow()

# ################################################################################################################################

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

    def get_id(self):
        return '{};{};{}'.format(self.server_name, self.server_pid, self.sub_key)

# ################################################################################################################################

class InRAMSyncBacklog(object):
    """ A backlog of messages kept in RAM for whom there are subscriptions - that is, they are known to have subscribers
    and will be ultimately delivered to them. Stores a list of sub_keys and all messages that a sub_key points to.
    It acts as a multi-key dict and keeps only a single copy of message for each sub_key.
    """
    def __init__(self, pubsub):
        self.pubsub = pubsub        # type: PubSub
        self.sub_key_to_msg_id = {} # Sub key  -> Msg ID set --- What messages are available for a given subcriber
        self.msg_id_to_sub_key = {} # Msg ID   -> Sub key set  - What subscribers are interested in a given message
        self.msg_id_to_msg = {}     # Msg ID   -> Message data - What is the actual contents of each message
        self.topic_msg_id = {}      # Topic ID -> Msg ID set --- What messages are available for each topic (no matter sub_key)
        self.lock = RLock()

        # Start in background a cleanup task that deletes all expired and removed messages
        spawn_greenlet(self.run_cleanup_task)

# ################################################################################################################################

    def add_messages(self, cid, topic_id, topic_name, max_depth, sub_keys, messages, _default_pri=PUBSUB.PRIORITY.DEFAULT):
        """ Adds all input messages to sub_keys for the topic.
        """
        with self.lock:

            # Local aliases
            msg_ids = [msg['pub_msg_id'] for msg in messages]
            len_messages = len(messages)
            topic_messages = self.topic_msg_id.setdefault(topic_id, set())

            # Try to append the messages for each of their subscribers ..
            for sub_key in sub_keys:

                # .. but first, make sure that storing these messages would not overflow the topic's depth,
                # if it could exceed the max depth, store the messages in log files only ..
                if len(topic_messages) + len_messages > max_depth:
                    self.log_messages_to_store(cid, topic_name, max_depth, sub_key, messages)

                    # .. skip this sub_key in such a case ..
                    continue

                # .. otherwise, we make it known that the sub_key is interested in this message ..
                sub_key_msg = self.sub_key_to_msg_id.setdefault(sub_key, set())
                sub_key_msg.update(msg_ids)

            # For each message given on input, store its actual contents ..
            for msg in messages:
                self.msg_id_to_msg[msg['pub_msg_id']] = msg

                # .. attach server metadata ..
                msg['server_name'] = self.pubsub.server.name
                msg['server_pid'] = self.pubsub.server.pid

                # .. set default priority if none was given ..
                if 'priority' not in msg:
                    msg['priority'] = _default_pri

                # .. add a reverse mapping, from message ID to sub_key ..
                msg_sub_key = self.msg_id_to_sub_key.setdefault(msg['pub_msg_id'], set())
                msg_sub_key.update(sub_keys)

            # .. and add a reference to it to the topic.
            topic_messages.update(msg_ids)

# ################################################################################################################################

    def update_msg(self, msg, _update_attrs=_update_attrs, _warn='No such message in sync backlog `%s`'):
        with self.lock:
            _msg = self.msg_id_to_msg.get(msg['msg_id'])
            if not _msg:
                logger.warn(_warn, msg['msg_id'])
                logger_zato.warn(_warn, msg['msg_id'])
                return False # No such message
            else:
                for attr in _update_attrs:
                    _msg[attr] = msg[attr]

                # Ok, found and updated
                return True

# ################################################################################################################################

    def delete_msg_by_id(self, msg_id):
        """ Deletes a message by its ID.
        """
        return self.delete_messages([msg_id])

# ################################################################################################################################

    def _delete_messages(self, msg_list):
        """ Low-level implementation of self.delete_messages - must be called with self.lock held.
        """
        logger.info('Deleting non-GD messages `%s`', msg_list)

        for msg_id in list(msg_list):

            found_to_sub_key = self.msg_id_to_sub_key.pop(msg_id, None)
            found_to_msg = self.msg_id_to_msg.pop(msg_id, None)

            _has_topic_msg = False # Was the ID found for at least one topic
            _has_sk_msg = False     # Ditto but for sub_keys

            for _topic_msg_set in itervalues(self.topic_msg_id):
                try:
                    _topic_msg_set.remove(msg_id)
                except KeyError:
                    pass # This is fine, msg_id did not belong to this topic
                else:
                    _has_topic_msg = True

            for _sk_msg_set in itervalues(self.sub_key_to_msg_id):
                try:
                    _sk_msg_set.remove(msg_id)
                except KeyError:
                    pass # This is fine, msg_id did not belong to this topic
                else:
                    _has_sk_msg = True

            if not found_to_sub_key:
                logger.warn('Message not found (msg_id_to_sub_key) %s', msg_id)
                logger_zato.warn('Message not found (msg_id_to_sub_key) %s', msg_id)

            if not found_to_msg:
                logger.warn('Message not found (msg_id_to_msg) %s', msg_id)
                logger_zato.warn('Message not found (msg_id_to_msg) %s', msg_id)

            if not _has_topic_msg:
                logger.warn('Message not found (_has_topic_msg) %s', msg_id)
                logger_zato.warn('Message not found (_has_topic_msg) %s', msg_id)

            if not _has_sk_msg:
                logger.warn('Message not found (_has_sk_msg) %s', msg_id)
                logger_zato.warn('Message not found (_has_sk_msg) %s', msg_id)

# ################################################################################################################################

    def delete_messages(self, msg_list):
        """ Deletes all messages from input msg_list.
        """
        with self.lock:
            self._delete_messages(msg_list)

# ################################################################################################################################

    def has_messages_by_sub_key(self, sub_key):
        with self.lock:
            return len(self.sub_key_to_msg_id.get(sub_key, [])) > 0

# ################################################################################################################################

    def clear_topic(self, topic_id):
        logger.info('Clearing topic `%s` (id:%s)', self.pubsub.get_topic_by_id(topic_id).name, topic_id)

        with self.lock:
            # Not all servers will have messages for the topic, hence .get
            messages = self.topic_msg_id.get(topic_id) or []
            if messages:
                messages = list(messages) # We need a copy so as not to change the input set during iteration later on
            self._delete_messages(messages)

# ################################################################################################################################

    def _get_delete_messages_by_sub_keys(self, topic_id, sub_keys, delete_msg=True, delete_sub=False):
        """ Low-level implementation of retrieve_messages_by_sub_keys which must be called with self.lock held.
        """
        now = utcnow_as_ms() # We cannot return expired messages
        msg_seen = set() # We cannot have duplicates on output
        out = []

        # A list of messages that will be optionally deleted before they are returned
        to_delete_msg = set()

        # First, collect data for all sub_keys ..
        for sub_key in sub_keys:

            for msg_id in self.sub_key_to_msg_id.get(sub_key, []):

                # We already had this message marked for output
                if msg_id in msg_seen:
                    continue
                else:
                    # Mark as already seen
                    msg_seen.add(msg_id)

                    # Filter out expired messages
                    msg = self.msg_id_to_msg.get(msg_id)
                    if not msg:
                        logger.warn('Msg `%s` not found in self.msg_id_to_msg', msg_id)
                        continue
                    if now >= msg['expiration_time']:
                        continue
                    else:
                        out.append(self.msg_id_to_msg[msg_id])

                if delete_msg:
                    to_delete_msg.add(msg_id)

        # Explicitly delete a left-over name from the loop above
        del sub_key

        # Delete all messages marked to be deleted ..
        for msg_id in to_delete_msg:

            # .. first, direct mappings ..
            self.msg_id_to_msg.pop(msg_id, None)

            logger.info('Deleting msg from mapping dict `%s`', msg_id)

            # .. now, remove the message from topic ..
            self.topic_msg_id[topic_id].remove(msg_id)

            logger.info('Deleting msg from mapping topic `%s`', msg_id)

            # .. now, find the message for each sub_key ..
            for sub_key in sub_keys:
                sub_key_to_msg_id = self.sub_key_to_msg_id.get(sub_key)

                # We need this if statement because it is possible that a client is subscribed to a topic
                # but it will not receive a particular message. This is possible if the message is a response
                # to a previous request and the latter used reply_to_sk, in which case only that one sub_key pointed to
                # by reply_to_sk will get the response, which ultimately means that self.sub_key_to_msg_id
                # will not have this response for current sub_key.
                if sub_key_to_msg_id:

                    # .. delete the message itself - but we need to catch ValueError because
                    # to_delete_msg is a list of all messages to be deleted and we do not know
                    # if this particular message belonged to this particular sub_key or not.
                    try:
                        sub_key_to_msg_id.remove(msg_id)
                    except KeyError:
                        pass # OK, message was not found for this sub_key

                    # .. now delete the sub_key either because we are explicitly told to (e.g. during unsubscribe)
                    if delete_sub:# or (not sub_key_to_msg_id):
                        del self.sub_key_to_msg_id[sub_key]

        return out

# ################################################################################################################################

    def retrieve_messages_by_sub_keys(self, topic_id, sub_keys):
        """ Retrieves and returns all messages matching input - messages are deleted from RAM.
        """
        with self.lock:
            return self._get_delete_messages_by_sub_keys(topic_id, sub_keys)

# ################################################################################################################################

    def get_messages_by_topic_id(self, topic_id, needs_short_copy, query=None):
        """ Returns messages for topic by its ID, optionally with pagination and filtering by input query.
        """
        with self.lock:
            msg_id_list = self.topic_msg_id.get(topic_id, [])
            if not msg_id_list:
                return []

            # A list of messages to be returned - we actually need to build a whole list instead of using
            # generators because the underlying container is an unsorted set and we need a sorted result on output.
            msg_list = []

            for msg_id in msg_id_list:
                msg = self.msg_id_to_msg[msg_id]
                if query:
                    if query not in msg['data'][:self.pubsub.data_prefix_len]:
                        continue

                if needs_short_copy:
                    out_msg = make_short_msg_copy_from_dict(msg, self.pubsub.data_prefix_len, self.pubsub.data_prefix_short_len)
                else:
                    out_msg = msg

                msg_list.append(out_msg)

            return msg_list

# ################################################################################################################################

    def get_message_by_id(self, msg_id):
        with self.lock:
            return self.msg_id_to_msg[msg_id]

# ################################################################################################################################

    def unsubscribe(self, topic_id, topic_name, sub_keys, pattern='Removing subscription info for `%s` from topic `%s`'):
        """ Unsubscribes all the sub_keys from the input topic.
        """
        # Always acquire a lock for this kind of operation
        with self.lock:

            # For each sub_key ..
            for sub_key in sub_keys:

                # .. get all messages waiting for this subscriber, assuming there are any at all ..
                msg_ids = self.sub_key_to_msg_id.pop(sub_key, [])

                # .. for each message found we need to check if it is needed by any other subscriber,
                # and if it's not, then we delete all the reference to this message. Otherwise, we leave it
                # as is, because there is at least one other subscriber waiting for it.
                for msg_id in msg_ids:

                    # Get all subscribers interested in this message ..
                    current_subs = self.msg_id_to_sub_key[msg_id]
                    current_subs.remove(sub_key)

                    # .. if the list is empty, it means that there no some subscribers left for that message,
                    # in which case we may deleted references to this message from other look-up structures.
                    if not current_subs:
                        del self.msg_id_to_msg[msg_id]
                        topic_msg = self.topic_msg_id[topic_id]
                        topic_msg.remove(msg_id)

        logger.info(pattern, sub_keys, topic_name)
        logger_zato.info(pattern, sub_keys, topic_name)

# ################################################################################################################################

    def run_cleanup_task(self, _utcnow=utcnow_as_ms, _sleep=sleep):
        """ A background task waking up periodically to remove all expired and retrieved messages from backlog.
        """
        while True:
            try:
                with self.lock:

                    # Local alias
                    publishers = {}

                    # We keep them separate so as not to modify any objects during iteration.
                    expired_msg = []

                    # Calling it once will suffice.
                    now = _utcnow()

                    for msg_id, msg in iteritems(self.msg_id_to_msg):

                        if now >= msg['expiration_time']:

                            # It's possible that there will be many expired messages all sent by the same publisher
                            # so there is no need to query self.pubsub for each message.
                            if msg['published_by_id'] not in publishers:
                                publishers[msg['published_by_id']] = self.pubsub.get_endpoint_by_id(msg['published_by_id'])

                            # We can be sure that it is always found
                            publisher = publishers[msg['published_by_id']]

                            # Log the message to make sure the expiration event is always logged ..
                            logger_zato.info('Found an expired msg:`%s`, topic:`%s`, publisher:`%s`, pub_time:`%s`, exp:`%s`',
                                msg['pub_msg_id'], msg['topic_name'], publisher.name, msg['pub_time'], msg['expiration'])

                            # .. and append it to the list of messages to be deleted.
                            expired_msg.append((msg['pub_msg_id'], msg['topic_id']))

                    # For logging what was done
                    len_expired = len(expired_msg)

                    # Iterate over all the expired messages found and delete them from in-RAM structures
                    for msg_id, topic_id in expired_msg:

                        # Get all sub_keys waiting for these messages and delete the message from each one,
                        # but note that there may be possibly no subscribers at all if the message was published
                        # to a topic without any subscribers.
                        for sub_key in self.msg_id_to_sub_key.pop(msg_id):
                            self.sub_key_to_msg_id[sub_key].remove(msg_id)

                        # Remove all references to the message from topic
                        self.topic_msg_id[topic_id].remove(msg_id)

                        # And finally, remove the message's contents
                        del self.msg_id_to_msg[msg_id]

                suffix = 's' if (len_expired==0 or len_expired > 1) else ''
                len_messages = len(self.msg_id_to_msg)
                if len_expired or len_messages:
                    logger.info('In-RAM. Deleted %s pub/sub message%s. Left:%s' % (len_expired, suffix, self.msg_id_to_msg))

                # Sleep for a moment before checking again but don't do it with self.lock held.
                _sleep(2)

            except Exception:
                e = format_exc()
                log_msg = 'Could not remove messages from in-RAM backlog, e:`%s`'
                logger.warn(log_msg, e)
                logger_zato.warn(log_msg, e)
                _sleep(0.1)

# ################################################################################################################################

    def log_messages_to_store(self, cid, topic_name, max_depth, sub_key, messages):
        # Used by both loggers
        msg = 'Reached max in-RAM delivery depth of %r for topic `%r` (cid:%r). Extra messages will be stored in logs.'
        args = (max_depth, topic_name, cid)

        # Log in pub/sub log and the main one as well, just to make sure it will be easily found
        logger.warn(msg, *args)
        logger_zato.warn(msg, *args)

        # Store messages in logger - by default will go to disk
        logger_overflow.info('CID:%s, topic:`%s`, sub_key:%s, messages:%s', cid, topic_name, sub_key, messages)

# ################################################################################################################################

    def get_topic_depth(self, topic_id, _default=set()):
        """ Returns depth of a given in-RAM queue for the topic.
        """
        with self.lock:
            return len(self.topic_msg_id.get(topic_id, _default))

# ################################################################################################################################

class PubSub(object):

    def __init__(self, cluster_id, server, broker_client=None):
        self.cluster_id = cluster_id
        self.server = server
        self.broker_client = broker_client
        self.event_log = EventLog('ps.{}.{}.{}'.format(self.cluster_id, self.server.name, self.server.pid))
        self.lock = RLock()
        self.keep_running = True
        self.sk_server_table_columns = self.server.fs_server_config.pubsub.get('sk_server_table_columns') or \
            default_sk_server_table_columns

        self.log_if_deliv_server_not_found = self.server.fs_server_config.pubsub.log_if_deliv_server_not_found
        self.log_if_wsx_deliv_server_not_found = self.server.fs_server_config.pubsub.log_if_wsx_deliv_server_not_found

        self.subscriptions_by_topic = {}       # Topic name     -> List of Subscription objects
        self._subscriptions_by_sub_key = {}     # Sub key        -> Subscription object
        self.sub_key_servers = {}              # Sub key        -> Server/PID handling it

        self.endpoints = {}                    # Endpoint ID    -> Endpoint object
        self.topics = {}                       # Topic ID       -> Topic object

        self.sec_id_to_endpoint_id = {}        # Sec def ID     -> Endpoint ID
        self.ws_channel_id_to_endpoint_id = {} # WS chan def ID -> Endpoint ID
        self.service_id_to_endpoint_id = {}    # Service ID     -> Endpoint ID
        self.topic_name_to_id = {}             # Topic name     -> Topic ID
        self.pub_buffer_gd = {}                # Topic ID       -> GD message buffered for that topic
        self.pub_buffer_non_gd = {}            # Topic ID       -> Non-GD message buffered for that topic

        self.pubsub_tool_by_sub_key = {}       # Sub key        -> PubSubTool object
        self.pubsub_tools = []                 # A list of PubSubTool objects, each containing delivery tasks

        # A backlog of messages that have at least one subscription, i.e. this is what delivery servers use.
        self.sync_backlog = InRAMSyncBacklog(self)

        # Getter methods for each endpoint type that return actual endpoints,
        # e.g. REST outgoing connections. Values are set by worker store.
        self.endpoint_impl_getter = dict.fromkeys(PUBSUB.ENDPOINT_TYPE())

        # How many messages have been published through this server, regardless of which topic they were for
        self.msg_pub_counter = 0

        # How many messages a given endpoint published
        self.endpoint_msg_counter = {}

        # How often to update metadata about topics and endpoints, if at all
        self.has_meta_topic = server.fs_server_config.pubsub_meta_topic.enabled
        self.topic_meta_store_frequency = server.fs_server_config.pubsub_meta_topic.store_frequency

        self.has_meta_endpoint = server.fs_server_config.pubsub_meta_endpoint_pub.enabled
        self.endpoint_meta_store_frequency = server.fs_server_config.pubsub_meta_endpoint_pub.store_frequency
        self.endpoint_meta_data_len = server.fs_server_config.pubsub_meta_endpoint_pub.data_len
        self.endpoint_meta_max_history = server.fs_server_config.pubsub_meta_endpoint_pub.max_history

        # How many bytes to use for look up purposes when conducting message searches
        self.data_prefix_len = server.fs_server_config.pubsub.data_prefix_len
        self.data_prefix_short_len = server.fs_server_config.pubsub.data_prefix_short_len

        # Manages access to service hooks
        self.hook_tool = HookTool(self.server, HookCtx, hook_type_to_method, self.invoke_service)

        spawn_greenlet(self.trigger_notify_pubsub_tasks)

# ################################################################################################################################

    @property
    def subscriptions_by_sub_key(self):
        self.emit_about_to_access_sub_sk({'sub_sk':sorted(self._subscriptions_by_sub_key), 'stack':get_current_stack()})
        return self._subscriptions_by_sub_key

# ################################################################################################################################

    def incr_pubsub_msg_counter(self, endpoint_id):
        with self.lock:

            # Update the overall counter
            self.msg_pub_counter += 1

            # Update the per-endpoint counter too
            if endpoint_id in self.endpoint_msg_counter:
                self.endpoint_msg_counter[endpoint_id] += 1
            else:
                self.endpoint_msg_counter[endpoint_id] = 0

# ################################################################################################################################

    def needs_endpoint_meta_update(self, endpoint_id):
        with self.lock:
            return self.endpoint_msg_counter[endpoint_id] % self.endpoint_meta_store_frequency == 0

# ################################################################################################################################

    def get_subscriptions_by_topic(self, topic_name, require_backlog_messages=False):
        with self.lock:
            subs = self.subscriptions_by_topic.get(topic_name, [])
            if require_backlog_messages:
                out = []
                for item in subs:
                    if self.sync_backlog.has_messages_by_sub_key(item.sub_key):
                        out.append(item)
                return out
            else:
                return subs

# ################################################################################################################################

    def _get_subscription_by_sub_key(self, sub_key):
        """ Low-level implementation of self.get_subscription_by_sub_key, must be called with self.lock held.
        """
        return self.subscriptions_by_sub_key[sub_key]

# ################################################################################################################################

    def get_subscription_by_sub_key(self, sub_key):
        with self.lock:
            try:
                return self._get_subscription_by_sub_key(sub_key)
            except KeyError:
                return None

# ################################################################################################################################

    def get_subscription_by_id(self, sub_id):
        with self.lock:
            for sub in itervalues(self.subscriptions_by_sub_key):
                if sub.id == sub_id:
                    return sub

# ################################################################################################################################

    def get_subscription_by_ext_client_id(self, ext_client_id):
        with self.lock:
            for sub in itervalues(self.subscriptions_by_sub_key):
                if sub.ext_client_id == ext_client_id:
                    return sub

# ################################################################################################################################

    def has_sub_key(self, sub_key):
        with self.lock:
            return sub_key in self.subscriptions_by_sub_key

# ################################################################################################################################

    def has_messages_in_backlog(self, sub_key):
        with self.lock:
            return self.sync_backlog.has_messages_by_sub_key(sub_key)

# ################################################################################################################################

    def _len_subscribers(self, topic_name):
        """ Low-level implementation of self.len_subscribers, must be called with self.lock held.
        """
        return len(self.subscriptions_by_topic[topic_name])

# ################################################################################################################################

    def len_subscribers(self, topic_name):
        """ Returns the amount of subscribers for a given topic.
        """
        with self.lock:
            return self._len_subscribers(topic_name)

# ################################################################################################################################

    def has_subscribers(self, topic_name):
        """ Returns True if input topic has at least one subscriber.
        """
        with self.lock:
            return self._len_subscribers(topic_name) > 0

# ################################################################################################################################

    def has_topic_by_name(self, topic_name):
        with self.lock:
            try:
                self._get_topic_by_name(topic_name)
            except KeyError:
                return False
            else:
                return True

# ################################################################################################################################

    def has_topic_by_id(self, topic_id):
        with self.lock:
            try:
                self.topics[topic_id]
            except KeyError:
                return False
            else:
                return True

# ################################################################################################################################

    def get_endpoint_by_id(self, endpoint_id):
        with self.lock:
            return self.endpoints[endpoint_id]

# ################################################################################################################################

    def get_endpoint_by_name(self, endpoint_name):
        with self.lock:
            for endpoint in self.endpoints.values():
                if endpoint.name == endpoint_name:
                    return endpoint
            else:
                raise KeyError('Could not find endpoint by name `{}` among `{}`'.format(endpoint_name, self.endpoints))

# ################################################################################################################################

    def get_endpoint_id_by_sec_id(self, sec_id):
        with self.lock:
            return self.sec_id_to_endpoint_id[sec_id]

# ################################################################################################################################

    def get_endpoint_id_by_ws_channel_id(self, ws_channel_id):
        with self.lock:
            return self.ws_channel_id_to_endpoint_id[ws_channel_id]

# ################################################################################################################################

    def get_endpoint_by_ws_channel_id(self, ws_channel_id):
        with self.lock:
            endpoint_id = self.ws_channel_id_to_endpoint_id[ws_channel_id]
            return self.endpoints[endpoint_id]

# ################################################################################################################################

    def get_endpoint_id_by_service_id(self, service_id):
        with self.lock:
            return self.service_id_to_endpoint_id[service_id]

# ################################################################################################################################

    def _get_topic_id_by_name(self, topic_name):
        return self.topic_name_to_id[topic_name]

# ################################################################################################################################

    def get_topic_id_by_name(self, topic_name):
        with self.lock:
            return self._get_topic_id_by_name(topic_name)

# ################################################################################################################################

    def get_non_gd_topic_depth(self, topic_name):
        """ Returns of non-GD messages for a given topic by its name.
        """
        with self.lock:
            return self.sync_backlog.get_topic_depth(self._get_topic_id_by_name(topic_name))

# ################################################################################################################################

    def _get_topic_by_name(self, topic_name):
        """ Low-level implementation of self.get_topic_by_name.
        """
        return self.topics[self._get_topic_id_by_name(topic_name)]

# ################################################################################################################################

    def get_topic_by_name(self, topic_name):
        with self.lock:
            return self._get_topic_by_name(topic_name)

# ################################################################################################################################

    def _get_topic_by_id(self, topic_id):
        """ Low-level implementation of self.get_topic_by_id, must be called with self.lock held.
        """
        return self.topics[topic_id]

# ################################################################################################################################

    def get_topic_by_id(self, topic_id):
        with self.lock:
            return self._get_topic_by_id(topic_id)

# ################################################################################################################################

    def get_topic_name_by_sub_key(self, sub_key):
        with self.lock:
            return self._get_subscription_by_sub_key(sub_key).topic_name

# ################################################################################################################################

    def _get_endpoint_by_id(self, endpoint_id):
        """ Returns an endpoint by ID, must be called with self.lock held.
        """
        return self.endpoints[endpoint_id]

# ################################################################################################################################

    def get_sub_key_to_topic_name_dict(self, sub_key_list):
        out = {}
        with self.lock:
            for sub_key in sub_key_list:
                out[sub_key] = self._get_subscription_by_sub_key(sub_key).topic_name

        return out

# ################################################################################################################################

    def _get_topic_by_sub_key(self, sub_key):
        return self._get_topic_by_name(self._get_subscription_by_sub_key(sub_key).topic_name)

# ################################################################################################################################

    def get_topic_by_sub_key(self, sub_key):
        with self.lock:
            return self._get_topic_by_sub_key(sub_key)

# ################################################################################################################################

    def get_topic_list_by_sub_key_list(self, sk_list):
        out = {}
        with self.lock:
            for sub_key in sk_list:
                out[sub_key] = self._get_topic_by_sub_key(sub_key)
        return out

# ################################################################################################################################

    def _create_endpoint(self, config):
        self.endpoints[config.id] = Endpoint(config)

        if config['security_id']:
            self.sec_id_to_endpoint_id[config['security_id']] = config.id

        if config['ws_channel_id']:
            self.ws_channel_id_to_endpoint_id[config['ws_channel_id']] = config.id

        if config['service_id']:
            self.service_id_to_endpoint_id[config['service_id']] = config.id

# ################################################################################################################################

    def create_endpoint(self, config):
        with self.lock:
            self._create_endpoint(config)

# ################################################################################################################################

    def _delete_endpoint(self, endpoint_id):
        del self.endpoints[endpoint_id]

        sec_id = None
        ws_chan_id = None
        service_id = None

        for key, value in iteritems(self.sec_id_to_endpoint_id):
            if value == endpoint_id:
                sec_id = key
                break

        for key, value in iteritems(self.ws_channel_id_to_endpoint_id):
            if value == endpoint_id:
                ws_chan_id = key
                break

        for key, value in iteritems(self.service_id_to_endpoint_id):
            if value == endpoint_id:
                service_id = key
                break

        if sec_id:
            del self.sec_id_to_endpoint_id[sec_id]

        if ws_chan_id:
            del self.ws_channel_id_to_endpoint_id[ws_chan_id]

        if service_id:
            del self.service_id_to_endpoint_id[service_id]

# ################################################################################################################################

    def delete_endpoint(self, endpoint_id):
        with self.lock:
            self._delete_endpoint(endpoint_id)

# ################################################################################################################################

    def edit_endpoint(self, config):
        with self.lock:
            self._delete_endpoint(config.id)
            self._create_endpoint(config)

# ################################################################################################################################

    def edit_subscription(self, config):
        with self.lock:
            sub = self._get_subscription_by_sub_key(config.sub_key)
            for key, value in iteritems(config):
                sub.config[key] = value

# ################################################################################################################################

    def _add_subscription(self, config):
        """ Low-level implementation of self.add_subscription.
        """
        sub = Subscription(config)

        existing_by_topic = self.subscriptions_by_topic.setdefault(config.topic_name, [])
        existing_by_topic.append(sub)

        self.subscriptions_by_sub_key[config.sub_key] = sub

# ################################################################################################################################

    def add_subscription(self, config):
        """ Creates a Subscription object and an associated mapping of the subscription to input topic.
        """
        with self.lock:

            # Creates a subscription ..
            self._add_subscription(config)

            # .. triggers a relevant hook, if any is configured.
            hook = self.get_on_subscribed_hook(config.sub_key)
            if hook:
                self.invoke_on_subscribed_hook(hook, config.topic_id, config.sub_key)

# ################################################################################################################################

    def _delete_subscription_by_sub_key(self, sub_key, ignore_missing=True, _invalid=object()):
        """ Deletes a subscription from the list of subscription. By default, it is not an error to call
        the method with an invalid sub_key. Must be invoked with self.lock held.
        """
        sub = self.subscriptions_by_sub_key.pop(sub_key, _invalid)
        if sub is _invalid and (not ignore_missing):
            raise KeyError('No such sub_key `%s`', sub_key)
        else:
            return sub # Either valid or invalid but ignore_missing is True

# ################################################################################################################################

    def _subscribe(self, config):
        """ Low-level implementation of self.subscribe. Must be called with self.lock held.
        """
        with self.lock:

            # It's possible that we already have this subscription - this may happen if we are the server that originally
            # handled the request to create the subscription and we are now called again through
            # on_broker_msg_PUBSUB_SUBSCRIPTION_CREATE. In such a case, we can just ignore it.
            if not self.has_sub_key(config.sub_key):
                self._add_subscription(config)

            # We don't start dedicated tasks for WebSockets - they are all dynamic without a fixed server.
            # But for other endpoint types, we create and start a delivery task here.
            if config.endpoint_type != PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id:

                # We have a matching server..
                if config.cluster_id == self.cluster_id and config.server_id == self.server.id:

                    # .. but make sure only the first worker of this server will start delivery tasks, not all of them.
                    if self.server.is_first_worker:

                        # Store in shared RAM information that our process handles this key
                        self.server.server_startup_ipc.set_pubsub_pid(self.server.pid)

                        config.server_pid = self.server.pid
                        config.server_name = self.server.name

                        # Starts the delivery task and notifies other servers that we are the one
                        # to handle deliveries for this particular sub_key.
                        self.invoke_service('zato.pubsub.delivery.create-delivery-task', config)

                    # We are not the first worker of this server and the first one must have already stored
                    # in RAM the mapping of sub_key -> server_pid, so we can safely read it here to add
                    # a subscription server.
                    else:
                        config.server_pid = self.server.server_startup_ipc.get_pubsub_pid()
                        config.server_name = self.server.name
                        self.set_sub_key_server(config)

# ################################################################################################################################

    def _set_topic_config_hook_data(self, config):
        if config.hook_service_id:

            # Invoked when a new subscription to topic is created
            config.on_subscribed_service_invoker = self.hook_tool.get_hook_service_invoker(
                config.hook_service_name, PUBSUB.HOOK_TYPE.ON_SUBSCRIBED)

            # Invoked when an existing subscription to topic is deleted
            config.on_unsubscribed_service_invoker = self.hook_tool.get_hook_service_invoker(
                config.hook_service_name, PUBSUB.HOOK_TYPE.ON_UNSUBSCRIBED)

            # Invoked before messages are published
            config.before_publish_hook_service_invoker = self.hook_tool.get_hook_service_invoker(
                config.hook_service_name, PUBSUB.HOOK_TYPE.BEFORE_PUBLISH)

            # Invoked before messages are delivered
            config.before_delivery_hook_service_invoker = self.hook_tool.get_hook_service_invoker(
                config.hook_service_name, PUBSUB.HOOK_TYPE.BEFORE_DELIVERY)

            # Invoked for outgoing SOAP connections
            config.on_outgoing_soap_invoke_invoker = self.hook_tool.get_hook_service_invoker(
                config.hook_service_name, PUBSUB.HOOK_TYPE.ON_OUTGOING_SOAP_INVOKE)
        else:
            config.hook_service_invoker = None

# ################################################################################################################################

    def _create_topic(self, config):
        self._set_topic_config_hook_data(config)
        config.meta_store_frequency = self.topic_meta_store_frequency

        self.topics[config.id] = Topic(config, self.server.name, self.server.pid)
        self.topic_name_to_id[config.name] = config.id

# ################################################################################################################################

    def create_topic(self, config):
        with self.lock:
            self._create_topic(config)

# ################################################################################################################################

    def _delete_topic(self, topic_id, topic_name):
        del self.topic_name_to_id[topic_name]
        self.subscriptions_by_topic.pop(topic_name, None) # May have no subscriptions hence .pop instead of del
        del self.topics[topic_id]

# ################################################################################################################################

    def delete_topic(self, topic_id):
        with self.lock:
            topic_name = self.topics[topic_id].name
            self._delete_topic(topic_id, topic_name)

# ################################################################################################################################

    def edit_topic(self, del_name, config):
        with self.lock:
            subscriptions_by_topic = self.subscriptions_by_topic.pop(del_name, [])
            self._delete_topic(config.id, del_name)
            self._create_topic(config)
            self.subscriptions_by_topic[config.name] = subscriptions_by_topic

# ################################################################################################################################

    def get_topic_event_list(self, topic_name):
        return self.topics[topic_name].get_event_list()

# ################################################################################################################################

    def get_event_list(self):
        return self.event_log.get_event_list()

# ################################################################################################################################

    def _is_allowed(self, target, name, is_pub, security_id, ws_channel_id, endpoint_id=None,
        _pub_role=_pub_role, _sub_role=_sub_role):

        if not endpoint_id:

            if not(security_id or ws_channel_id):
                raise ValueError(
                    'Either security_id or ws_channel_id must be given on input instead of `{}` `{}`'.format(
                    security_id, ws_channel_id))

            if security_id:
                source, id = self.sec_id_to_endpoint_id, security_id
            else:
                source, id = self.ws_channel_id_to_endpoint_id, ws_channel_id

            endpoint_id = source[id]

        # One way or another, we have an endpoint object now ..
        endpoint = self.endpoints[endpoint_id]

        # .. make sure this endpoint may publish or subscribe, depending on what is needed.
        if is_pub:
            if not endpoint.role in _pub_role:
                return
        else:
            if not endpoint.role in _sub_role:
                return

        # Alright, this endpoint has the correct role, but are there are any matching patterns for this topic?
        for orig, matcher in getattr(endpoint, target):
            if matcher.match(name):
                return orig

# ################################################################################################################################

    def is_allowed_pub_topic(self, name, security_id=None, ws_channel_id=None):
        return self._is_allowed('pub_topic_patterns', name, True, security_id, ws_channel_id)

# ################################################################################################################################

    def is_allowed_pub_topic_by_endpoint_id(self, name, endpoint_id):
        return self._is_allowed('pub_topic_patterns', name, True, None, None, endpoint_id)

# ################################################################################################################################

    def is_allowed_sub_topic(self, name, security_id=None, ws_channel_id=None):
        return self._is_allowed('sub_topic_patterns', name, False, security_id, ws_channel_id)

# ################################################################################################################################

    def is_allowed_sub_topic_by_endpoint_id(self, name, endpoint_id):
        return self._is_allowed('sub_topic_patterns', name, False, None, None, endpoint_id)

# ################################################################################################################################

    def get_topics(self):
        """ Returns all topics in existence.
        """
        with self.lock:
            return self.topics

# ################################################################################################################################

    def get_sub_topics_for_endpoint(self, endpoint_id):
        """ Returns all topics to which endpoint_id can subscribe.
        """
        out = []
        with self.lock:
            for topic in self.topics.values():
                if self.is_allowed_sub_topic_by_endpoint_id(topic.name, endpoint_id):
                    out.append(topic)

        return out

# ################################################################################################################################

    def _is_subscribed_to(self, endpoint_id, topic_name):
        """ Low-level implementation of self.is_subscribed_to.
        """
        for sub in self.subscriptions_by_topic.get(topic_name, []):
            if sub.endpoint_id == endpoint_id:
                return True

# ################################################################################################################################

    def is_subscribed_to(self, endpoint_id, topic_name):
        """ Returns True if the endpoint is subscribed to the named topic.
        """
        with self.lock:
            return self._is_subscribed_to(endpoint_id, topic_name)

# ################################################################################################################################

    def get_pubsub_tool_by_sub_key(self, sub_key):
        with self.lock:
            return self.pubsub_tool_by_sub_key[sub_key]

# ################################################################################################################################

    def add_wsx_client_pubsub_keys(self, session, sql_ws_client_id, sub_key, channel_name, pub_client_id, wsx_info):
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
            'wsx_info': wsx_info
        })

# ################################################################################################################################

    def format_sk_servers(self, default='---'):

        # Prepare the table
        len_columns = len(self.sk_server_table_columns)

        table = Texttable()
        table.set_cols_width(self.sk_server_table_columns)
        table.set_cols_dtype(['t'] * len_columns)
        table.set_cols_align(['c'] * len_columns)
        table.set_cols_valign(['m'] * len_columns)

        # Add headers
        rows = [['#', 'created', 'name', 'pid', 'channel_name', 'sub_key']]

        servers = list(itervalues(self.sub_key_servers))
        servers.sort(key=attrgetter('creation_time', 'channel_name', 'sub_key'), reverse=True)

        for idx, item in enumerate(servers, 1):

            sub_key_info = item.sub_key

            if item.wsx_info:
                for name in ('swc', 'name', 'pub_client_id', 'peer_fqdn', 'forwarded_for_fqdn', 'python_id', 'sock'):
                    sub_key_info += '\n'
                    sub_key_info += '{}: {}'.format(name, item.wsx_info[name])

            rows.append([
                idx,
                item.creation_time,
                item.server_name,
                item.server_pid,
                item.channel_name or default,
                sub_key_info.encode('utf8'),
            ])


        # Add all rows to the table
        table.add_rows(rows)

        # And return already formatted output
        return table.draw()

# ################################################################################################################################

    def _set_sub_key_server(self, config):
        """ Low-level implementation of self.set_sub_key_server - must be called with self.lock held.
        """
        sub = self._get_subscription_by_sub_key(config['sub_key'])
        config['endpoint_id'] = sub.endpoint_id
        config['endpoint_name'] = self._get_endpoint_by_id(sub.endpoint_id)
        config['wsx'] = int(config['endpoint_type'] == PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id)
        self.sub_key_servers[config['sub_key']] = SubKeyServer(config)

        sks_table = self.format_sk_servers()
        msg = 'Set sk_server{}for sub_key `%(sub_key)s` (wsx:%(wsx)s) - `%(server_name)s:%(server_pid)s`, '\
            'current sk_servers:\n{}'.format(' ' if config['server_pid'] else ' (no PID) ', sks_table)

        logger.info(msg, config)
        logger_zato.info(msg, config)

# ################################################################################################################################

    def set_sub_key_server(self, config):
        with self.lock:
            self._set_sub_key_server(config)

# ################################################################################################################################

    def _get_sub_key_server(self, sub_key, default=None):
        return self.sub_key_servers.get(sub_key, default)

# ################################################################################################################################

    def get_sub_key_server(self, sub_key, default=None):
        with self.lock:
            return self._get_sub_key_server(sub_key, default)

# ################################################################################################################################

    def get_delivery_server_by_sub_key(self, sub_key, needs_lock=True):
        if needs_lock:
            with self.lock:
                return self._get_sub_key_server(sub_key)
        else:
            return self._get_sub_key_server(sub_key)

# ################################################################################################################################

    def delete_sub_key_server(self, sub_key):
        with self.lock:
            sub_key_server = self.sub_key_servers.get(sub_key)
            if sub_key_server:
                msg = 'Deleting info about delivery server for sub_key `%s`, was `%s:%s`'

                logger.info(msg, sub_key, sub_key_server.server_name, sub_key_server.server_pid)
                logger_zato.info(msg, sub_key, sub_key_server.server_name, sub_key_server.server_pid)

                del self.sub_key_servers[sub_key]
            else:
                logger.info('Could not find sub_key `%s` while deleting sub_key server, current `%s` `%s`',
                    sub_key, self.server.name, self.server.pid)

# ################################################################################################################################

    def remove_ws_sub_key_server(self, config):
        """ Called after a WSX client disconnects - provides a list of sub_keys that it handled
        which we must remove from our config because without this client they are no longer usable (until the client reconnects).
        """
        with self.lock:
            for sub_key in config.sub_key_list:
                self.sub_key_servers.pop(sub_key, None)
                for server_info in self.sub_key_servers.values():
                    if server_info.sub_key == sub_key:
                        del self.sub_key_servers[sub_key]
                        break

# ################################################################################################################################

    def get_server_pid_for_sub_key(self, server_name, sub_key):
        """ Invokes a named server on current cluster and asks it for PID of one its processes that handles sub_key.
        Returns that PID or None if the information could not be obtained.
        """
        try:
            response = self.server.servers[server_name].invoke('zato.pubsub.delivery.get-server-pid-for-sub-key', {
                'sub_key': sub_key,
            })
        except Exception:
            msg = 'Could not invoke server `%s` to get PID for sub_key `%s`, e:`%s`'
            exc_formatted = format_exc()
            logger.warn(msg, server_name, sub_key, exc_formatted)
            logger_zato.warn(msg, server_name, sub_key, exc_formatted)
        else:
            return response['response']['server_pid']

# ################################################################################################################################

    def add_missing_server_for_sub_key(self, sub_key, is_wsx):
        """ Adds to self.sub_key_servers information from ODB about which server handles input sub_key.
        Must be called with self.lock held.
        """
        with closing(self.server.odb.session()) as session:
            data = get_delivery_server_for_sub_key(session, self.server.cluster_id, sub_key, is_wsx)

        if not data:
            if self.log_if_deliv_server_not_found:
                if is_wsx and (not self.log_if_wsx_deliv_server_not_found):
                    return
                msg = 'Could not find a delivery server in ODB for sub_key `%s` (wsx:%s)'
                logger.info(msg, sub_key, is_wsx)
        else:

            # This is common config that we already know is valid but on top of it
            # we will try to the server found and ask about PID that handles messages for sub_key.
            config = {
                'sub_key': sub_key,
                'cluster_id': data.cluster_id,
                'server_name': data.server_name,
                'endpoint_type': data.endpoint_type,
            }

            # Guaranteed to either set PID or None
            config['server_pid'] = self.get_server_pid_for_sub_key(data.server_name, sub_key)

            # OK, set up the server with what we found above
            self._set_sub_key_server(config)

# ################################################################################################################################

    def get_task_servers_by_sub_keys(self, sub_key_data):
        """ Returns a dictionary keyed by (server_name, server_pid, pub_client_id, channel_name) tuples
        and values being sub_keys that a WSX client pointed to by each key has subscribed to.
        """
        with self.lock:
            found = {}
            not_found = []

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

    def get_sql_messages_by_sub_key(self, session, sub_key_list, last_sql_run, pub_time_max, ignore_list):
        """ Returns all SQL messages queued up for all keys from sub_key_list.
        """
        if not session:
            session = self.server.odb.session()
            needs_close = True
        else:
            needs_close = False

        try:
            return _get_sql_messages_by_sub_key(session, self.server.cluster_id, sub_key_list,
                last_sql_run, pub_time_max, ignore_list)
        finally:
            if needs_close:
                session.close()

# ################################################################################################################################

    def get_initial_sql_msg_ids_by_sub_key(self, session, sub_key, pub_time_max):
        return _get_sql_msg_ids_by_sub_key(session, self.server.cluster_id, sub_key, None, pub_time_max).\
               all()

# ################################################################################################################################

    def get_sql_messages_by_msg_id_list(self, session, sub_key, pub_time_max, msg_id_list):
        return _get_sql_messages_by_msg_id_list(session, self.server.cluster_id, sub_key, pub_time_max, msg_id_list).\
               all()

# ################################################################################################################################

    def confirm_pubsub_msg_delivered(self, sub_key, delivered_pub_msg_id_list):
        """ Sets in SQL delivery status of a given message to True.
        """
        with closing(self.server.odb.session()) as session:
            _confirm_pubsub_msg_delivered(session, self.server.cluster_id, sub_key, delivered_pub_msg_id_list, utcnow_as_ms())
            session.commit()

# ################################################################################################################################

    def store_in_ram(self, cid, topic_id, topic_name, sub_keys, non_gd_msg_list, from_error=0, _logger=logger):
        """ Stores in RAM up to input non-GD messages for each sub_key. A backlog queue for each sub_key
        cannot be longer than topic's max_depth_non_gd and overflowed messages are not kept in RAM.
        They are not lost altogether though, because, if enabled by topic's use_overflow_log, all such messages
        go to disk (or to another location that logger_overflown is configured to use).
        """
        _logger.info('Storing in RAM. CID:`%s`, topic ID:`%s`, name:`%s`, sub_keys:`%s`, ngd-list:`%s`, e:`%d`',
            cid, topic_id, topic_name, sub_keys, [elem['pub_msg_id'] for elem in non_gd_msg_list], from_error)

        with self.lock:

            # Store the non-GD messages in backlog ..
            self.sync_backlog.add_messages(cid, topic_id, topic_name, self.topics[topic_id].max_depth_non_gd,
                sub_keys, non_gd_msg_list)

            # .. and set a flag to signal that there are some available.
            self._set_sync_has_msg(topic_id, False, True, 'PubSub.store_in_ram')

# ################################################################################################################################

    def unsubscribe(self, topic_sub_keys):
        """ Removes subscriptions for all input sub_keys. Input topic_sub_keys is a dictionary keyed by topic_name,
        and each value is a list of sub_keys, possibly one-element long.
        """
        with self.lock:
            for topic_name, sub_keys in topic_sub_keys.items():

                # We receive topic_names on input but in-RAM backlog requires topic IDs.
                topic_id = self.topic_name_to_id[topic_name]

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
                    deleted_sub = self._delete_subscription_by_sub_key(sub_key)

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

    def register_pubsub_tool(self, pubsub_tool):
        """ Registers a new pubsub_tool for this server, i.e. a new delivery task container.
        """
        self.pubsub_tools.append(pubsub_tool)

# ################################################################################################################################

    def set_pubsub_tool_for_sub_key(self, sub_key, pubsub_tool):
        """ Adds a mapping between a sub_key and pubsub_tool handling its messages.
        """
        self.pubsub_tool_by_sub_key[sub_key] = pubsub_tool

# ################################################################################################################################

    def migrate_delivery_server(self, msg):
        """ Migrates the delivery task for sub_key to a new server given by ID on input,
        including all current in-RAM messages. This method must be invoked in the same worker process that runs
        delivery task for sub_key.
        """
        self.invoke_service('zato.pubsub.migrate.migrate-delivery-server', {
            'sub_key': msg.sub_key,
            'old_delivery_server_id': msg.old_delivery_server_id,
            'new_delivery_server_name': msg.new_delivery_server_name,
            'endpoint_type': msg.endpoint_type,
        })

# ################################################################################################################################

    def get_before_delivery_hook(self, sub_key):
        """ Returns a hook for messages to be invoked right before they are about to be delivered
        or None if such a hook is not defined for sub_key's topic.
        """
        with self.lock:
            sub = self.get_subscription_by_sub_key(sub_key)
            return self._get_topic_by_name(sub.topic_name).before_delivery_hook_service_invoker

# ################################################################################################################################

    def get_on_subscribed_hook(self, sub_key):
        """ Returns a hook triggered when a new subscription is made to a particular topic.
        """
        with self.lock:
            sub = self.get_subscription_by_sub_key(sub_key)
            return self._get_topic_by_name(sub.topic_name).on_subscribed_service_invoker

# ################################################################################################################################

    def get_on_unsubscribed_hook(self, sub_key=None, sub=None):
        """ Returns a hook triggered when a client unsubscribes from a topic.
        """
        with self.lock:
            sub = sub or self.get_subscription_by_sub_key(sub_key)
            return self._get_topic_by_name(sub.topic_name).on_unsubscribed_service_invoker

# ################################################################################################################################

    def get_on_outgoing_soap_invoke_hook(self, sub_key):
        """ Returns a hook that sends outgoing SOAP Suds connections-based messages or None if there is no such hook
        for sub_key's topic.
        """
        with self.lock:
            sub = self.get_subscription_by_sub_key(sub_key)
            return self._get_topic_by_name(sub.topic_name).on_outgoing_soap_invoke_invoker

# ################################################################################################################################

    def invoke_before_delivery_hook(self, hook, topic_id, sub_key, batch, messages, actions=list(PUBSUB.HOOK_ACTION()),
        _deliver=PUBSUB.HOOK_ACTION.DELIVER):
        """ Invokes a hook service for each message from a batch of messages possibly to be delivered and arranges
        each one to a specific key in messages dict.
        """
        for msg in batch:
            response = hook(self.topics[topic_id], msg)
            hook_action = response['hook_action'] or _deliver

            if hook_action and hook_action not in actions:
                raise ValueError('Invalid action returned `{}` for msg `{}`'.format(hook_action, msg))
            else:
                messages[hook_action].append(msg)

# ################################################################################################################################

    def invoke_on_outgoing_soap_invoke_hook(self, batch, sub, http_soap):
        hook = self.get_on_outgoing_soap_invoke_hook(sub.sub_key)
        topic = self.get_topic_by_id(sub.config.topic_id)
        if hook:
            hook(topic, batch, http_soap=http_soap)
        else:
            # We know that this service exists, it just does not implement the expected method
            service_info = self.server.service_store.get_service_class_by_id(topic.config.hook_service_id)
            service_class = service_info['service_class']
            service_name = service_class.get_name()
            raise Exception('Hook service `{}` does not implement `on_outgoing_soap_invoke` method'.format(service_name))

# ################################################################################################################################

    def _invoke_on_sub_unsub_hook(self, hook, topic_id, sub_key=None, sub=None):
        sub = sub if sub else self._get_subscription_by_sub_key(sub_key)
        return hook(topic=self._get_topic_by_id(topic_id), sub=sub)

# ################################################################################################################################

    def invoke_on_subscribed_hook(self, hook, topic_id, sub_key):
        return self._invoke_on_sub_unsub_hook(hook, topic_id, sub_key)

# ################################################################################################################################

    def invoke_on_unsubscribed_hook(self, hook, topic_id, sub):
        return self._invoke_on_sub_unsub_hook(hook, topic_id, sub=sub)

# ################################################################################################################################

    def on_broker_msg_HOT_DEPLOY_CREATE_SERVICE(self, services_deployed):
        """ Invoked after a package with one or more services is hot-deployed. Goes over all topics
        and updates hooks that any of these services possibly implements.
        """
        with self.lock:
            for topic in self.topics.values():
                hook_service_id = topic.config.get('hook_service_id')
                if hook_service_id in services_deployed:
                    self._set_topic_config_hook_data(topic.config)
                    topic.set_hooks()

# ################################################################################################################################

    def deliver_pubsub_msg(self, sub_key, msg):
        """ A callback method invoked by pub/sub delivery tasks for one or more message that is to be delivered.
        """
        return self.invoke_service('zato.pubsub.delivery.deliver-message', {
            'msg':msg,
            'subscription':self.get_subscription_by_sub_key(sub_key)
        })

# ################################################################################################################################

    def set_to_delete(self, sub_key, msg_list):
        """ Marks all input messages as ready to be deleted.
        """
        logger.info('Deleting messages set to be deleted `%s`', msg_list)

        with closing(self.server.odb.session()) as session:
            set_to_delete(session, self.cluster_id, sub_key, msg_list, utcnow_as_ms())

# ################################################################################################################################

    def topic_lock(self, topic_name):
        return self.server.zato_lock_manager('zato.pubsub.publish.%s' % topic_name)

# ################################################################################################################################

    def invoke_service(self, name, msg, *args, **kwargs):
        return self.server.invoke(name, msg, *args, **kwargs)

# ################################################################################################################################

    def _set_sync_has_msg(self, topic_id, is_gd, value, source, gd_pub_time_max=None):
        """ Updates a given topic's flags indicating that a message has been published since the last sync.
        Must be called with self.lock held.
        """
        topic = self.topics[topic_id] # type: Topic
        if is_gd:
            topic.sync_has_gd_msg = value
            topic.gd_pub_time_max = gd_pub_time_max
        else:
            topic.sync_has_non_gd_msg = value

        self.emit_set_sync_has_msg({
            'topic_id': topic_id,
            'is_gd': is_gd,
            'value': value,
            'source': source,
            'gd_pub_time_max': gd_pub_time_max,
            'topic.name': topic.name,
            'topic.sync_has_gd_msg': topic.sync_has_gd_msg,
            'topic.gd_pub_time_max': topic.gd_pub_time_max,
            'topic.sync_has_non_gd_msg': topic.sync_has_non_gd_msg
        })

# ################################################################################################################################

    def set_sync_has_msg(self, topic_id, is_gd, value, source, gd_pub_time_max):
        with self.lock:
            self._set_sync_has_msg(topic_id, is_gd, value, source, gd_pub_time_max)

# ################################################################################################################################

    def emit_loop_topic_id_dict(self, ctx=None, _event=EventType.PubSub.loop_topic_id_dict):
        self.event_log.emit(_event, ctx)

    def emit_loop_sub_keys(self, ctx=None, _event=EventType.PubSub.loop_sub_keys):
        self.event_log.emit(_event, ctx)

    def emit_loop_before_has_msg(self, ctx=None, _event=EventType.PubSub.loop_before_has_msg):
        self.event_log.emit(_event, ctx)

    def emit_loop_has_msg(self, ctx=None, _event=EventType.PubSub.loop_has_msg):
        self.event_log.emit(_event, ctx)

    def emit_loop_before_sync(self, ctx=None, _event=EventType.PubSub.loop_before_sync):
        self.event_log.emit(_event, ctx)

    def emit_set_sync_has_msg(self, ctx=None, _event=EventType.PubSub._set_sync_has_msg):
        self.event_log.emit(_event, ctx)

    def emit_about_to_subscribe(self, ctx=None, _event=EventType.PubSub.about_to_subscribe):
        self.event_log.emit(_event, ctx)

    def emit_about_to_access_sub_sk(self, ctx=None, _event=EventType.PubSub.about_to_access_sub_sk):
        self.event_log.emit(_event, ctx)

    def emit_in_subscribe_impl(self, ctx=None, _event=EventType.PubSub.in_subscribe_impl):
        self.event_log.emit(_event, ctx)

# ################################################################################################################################

    def trigger_notify_pubsub_tasks(self):
        """ A background greenlet which periodically lets delivery tasks that there are perhaps
        new GD messages for the topic this class represents.
        """

        # Local aliases

        _self_emit_loop_topic_id_dict  = self.emit_loop_topic_id_dict
        _self_emit_loop_sub_keys       = self.emit_loop_sub_keys
        _self_emit_loop_before_has_msg = self.emit_loop_before_has_msg
        _self_emit_loop_before_sync    = self.emit_loop_before_sync

        _new_cid      = new_cid
        _spawn        = spawn
        _sleep        = sleep
        _self_lock    = self.lock
        _self_topics  = self.topics
        _keep_running = self.keep_running

        _logger_info      = logger.info
        _logger_warn      = logger.warn
        _logger_zato_warn = logger_zato.warn

        _self_invoke_service   = self.invoke_service
        _self_set_sync_has_msg = self._set_sync_has_msg

        _self_get_subscriptions_by_topic     = self.get_subscriptions_by_topic
        _self_get_delivery_server_by_sub_key = self.get_delivery_server_by_sub_key

        _sync_backlog_get_delete_messages_by_sub_keys = self.sync_backlog._get_delete_messages_by_sub_keys

# ################################################################################################################################

        def _cmp_non_gd_msg(elem):
            return elem['pub_time']

# ################################################################################################################################

        def _do_emit_loop_topic_id_dict(_topic_id_dict):
            _self_emit_loop_topic_id_dict({
                'topic_id_dict': _topic_id_dict
            })

# ################################################################################################################################

        def _do_emit_loop_sub_keys(topic_id, topic_name, sub_keys):
            _self_emit_loop_sub_keys({
                'topic_id': topic_id,
                'topic.name': topic_name,
                'sub_keys': sub_keys
            })

# ################################################################################################################################

        def _do_emit_loop_before_has_msg(topic_id, topic_name, topic_sync_has_gd_msg, topic_sync_has_non_gd_msg):
            _self_emit_loop_before_has_msg({
                'topic_id': topic_id,
                'topic.name': topic_name,
                'topic.sync_has_gd_msg': topic_sync_has_gd_msg,
                'topic.sync_has_non_gd_msg': topic_sync_has_non_gd_msg,
            })

# ################################################################################################################################

        def _do_emit_loop_before_sync(topic_id, topic_name, topic_sync_has_gd_msg, topic_sync_has_non_gd_msg,
            non_gd_msg_list_msg_id_list, pub_time_max):
            _self_emit_loop_before_sync({
                'topic_id': topic_id,
                'topic.name': topic_name,
                'topic.sync_has_gd_msg': topic_sync_has_gd_msg,
                'topic.sync_has_non_gd_msg': topic_sync_has_non_gd_msg,
                'non_gd_msg_list': non_gd_msg_list_msg_id_list,
                'pub_time_max': pub_time_max
            })

# ################################################################################################################################

        # Loop forever or until stopped
        while _keep_running:

            # Sleep for a while before continuing - the call to sleep is here because this while loop is quite long
            # so it would be inconvenient to have it down below.
            _sleep(0.01)

            # Blocks other pub/sub processes for a moment
            with _self_lock:

                # Will map a few temporary objects down below
                topic_id_dict = {}

                # Get all topics ..
                for _topic in _self_topics.values(): # type: Topic

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
                    subs = _self_get_subscriptions_by_topic(_topic.name)

                    # .. if there are any subscriptions at all, we store that information for later use.
                    if subs:
                        topic_id_dict[_topic.id] = (_topic.name, subs)

                # OK, if we had any subscriptions for at least one topic and there are any messages waiting,
                # we can continue.
                try:

                    if topic_id_dict:

                        #
                        # Event log
                        #
                        _do_emit_loop_topic_id_dict(topic_id_dict)

                    for topic_id in topic_id_dict:

                        topic = _self_topics[topic_id]

                        # .. get the temporary metadata object stored earlier ..
                        topic_name, subs = topic_id_dict[topic_id]

                        cid = _new_cid()
                        _logger_info('Triggering sync for `%s` len_s:%d gd:%d ngd:%d cid:%s' % (
                            topic_name, len(subs), topic.sync_has_gd_msg, topic.sync_has_non_gd_msg, cid))

                        # Build a list of sub_keys for whom we know what their delivery server is which will
                        # allow us to send messages only to tasks that are known to be up.
                        sub_keys = []
                        for item in subs:
                            if _self_get_delivery_server_by_sub_key(item.sub_key):
                                sub_keys.append(item.sub_key)

                        # Continue only if there are actually any sub_keys left = any tasks up and running ..
                        if sub_keys:

                            #
                            # Event log
                            #
                            _do_emit_loop_sub_keys(topic_id, topic.name, sub_keys)

                            non_gd_msg_list = _sync_backlog_get_delete_messages_by_sub_keys(topic_id, sub_keys)

                            #
                            # Event log
                            #
                            _do_emit_loop_before_has_msg(topic_id, topic.name, topic.sync_has_gd_msg, topic.sync_has_non_gd_msg)

                            # .. also, continue only if there are still messages for the ones that are up ..
                            if topic.sync_has_gd_msg or topic.sync_has_non_gd_msg:

                                if non_gd_msg_list:
                                    non_gd_msg_list = sorted(non_gd_msg_list, key=_cmp_non_gd_msg)
                                    pub_time_max = non_gd_msg_list[-1]['pub_time']
                                else:
                                    pub_time_max = topic.gd_pub_time_max

                                non_gd_msg_list_msg_id_list = [elem['pub_msg_id'] for elem in non_gd_msg_list]

                                #
                                # Event log
                                #
                                _do_emit_loop_before_sync(topic_id, topic.name, topic.sync_has_gd_msg, topic.sync_has_non_gd_msg,
                                    non_gd_msg_list_msg_id_list, pub_time_max)

                                _logger_info('Syncing messages for `%s` ngd-list:%s (sk_list:%s) cid:%s' % (
                                    topic_name, non_gd_msg_list_msg_id_list, sub_keys, cid))

                                # .. and notify all the tasks in background.
                                _spawn(_self_invoke_service, 'zato.pubsub.after-publish', {
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

# Public API methods

# ################################################################################################################################

    def _find_wsx_environ(self, service):
        wsx_environ = service.wsgi_environ.get('zato.request_ctx.async_msg', {}).get('environ')
        if not wsx_environ:
            raise Exception('Could not find `[\'zato.request_ctx.async_msg\'][\'environ\']` in WSGI environ `{}`'.format(
                service.wsgi_environ))
        else:
            return wsx_environ

# ################################################################################################################################
# ################################################################################################################################

    def publish(self, topic_name, *args, **kwargs):
        """ Publishes a new message to input topic_name.
        POST /zato/pubsub/topic/{topic_name}
        """
        data = kwargs.get('data') or ''
        data_list = kwargs.get('data_list') or []
        msg_id = kwargs.get('msg_id') or ''
        has_gd = kwargs.get('has_gd')
        priority = kwargs.get('priority')
        expiration = kwargs.get('expiration')
        mime_type = kwargs.get('mime_type')
        correl_id = kwargs.get('correl_id')
        in_reply_to = kwargs.get('in_reply_to')
        ext_client_id = kwargs.get('ext_client_id')
        ext_pub_time = kwargs.get('ext_pub_time')
        endpoint_id = kwargs.get('endpoint_id')
        reply_to_sk = kwargs.get('reply_to_sk')
        deliver_to_sk = kwargs.get('deliver_to_sk')

        response = self.invoke_service('zato.pubsub.publish.publish', {
            'topic_name': topic_name,
            'data': data,
            'data_list': data_list,
            'msg_id': msg_id,
            'has_gd': has_gd,
            'priority': priority,
            'expiration': expiration,
            'mime_type': mime_type,
            'correl_id': correl_id,
            'in_reply_to': in_reply_to,
            'ext_client_id': ext_client_id,
            'ext_pub_time': ext_pub_time,
            'endpoint_id': endpoint_id or self.server.default_internal_pubsub_endpoint_id,
            'reply_to_sk': reply_to_sk,
            'deliver_to_sk': deliver_to_sk,
        }, serialize=False)

        return response.response['msg_id']

# ################################################################################################################################
# ################################################################################################################################

    def get_messages(self, topic_name, sub_key, needs_details=False, _skip=skip_to_external):
        """ Returns messages from a subscriber's queue, deleting them from the queue in progress.
        POST /zato/pubsub/topic/{topic_name}?sub_key=...
        """
        response = self.invoke_service('zato.pubsub.endpoint.get-delivery-messages', {
            'cluster_id': self.server.cluster_id,
            'sub_key': sub_key,
        }, serialize=False).response

        # Already includes all the details ..
        if needs_details:
            return response

        # .. otherwise, we need to make sure they are not returned
        out = []
        for item in response:
            for name in _skip:
                item.pop(name, None)
            out.append(item)
        return out

# ################################################################################################################################
# ################################################################################################################################

    def read_messages(self, topic_name, sub_key, has_gd, *args, **kwargs):
        """ Looks up messages in subscriber's queue by input criteria without deleting them from the queue.
        """
        service_name = _service_read_messages_gd if has_gd else _service_read_messages_non_gd

        paginate = kwargs.get('paginate') or True
        query = kwargs.get('query') or ''
        cur_page = kwargs.get('cur_page') or 1

        return self.invoke_service(service_name, {
            'cluster_id': self.server.cluster_id,
            'sub_key': sub_key,
            'paginate': paginate,
            'query': query,
            'cur_page': cur_page,
        }, serialize=False).response

# ################################################################################################################################
# ################################################################################################################################

    def read_message(self, topic_name, msg_id, has_gd, *args, **kwargs):
        """ Returns details of a particular message without deleting it from the subscriber's queue.
        """
        if has_gd:
            service_name = _service_read_message_gd
            service_data = {
                'cluster_id': self.server.cluster_id,
                'msg_id': msg_id
            }
        else:
            sub_key = kwargs.get('sub_key')
            server_name = kwargs.get('server_name')
            server_pid = kwargs.get('server_pid')

            if not(sub_key and server_name and server_pid):
                raise Exception('All of sub_key, server_name and server_pid are required for non-GD messages')

            service_name = _service_read_message_non_gd
            service_data = {
                'cluster_id': self.server.cluster_id,
                'msg_id': msg_id,
                'sub_key': sub_key,
                'server_name': server_name,
                'server_pid': server_pid,
            }

        return self.invoke_service(service_name, service_data, serialize=False).response

# ################################################################################################################################
# ################################################################################################################################

    def delete_message(self, sub_key, msg_id, has_gd, *args, **kwargs):
        """ Deletes a message from a subscriber's queue.
        DELETE /zato/pubsub/msg/{msg_id}
        """
        service_data = {
            'sub_key': sub_key,
            'msg_id': msg_id,
        }
        if has_gd:
            service_name = _service_delete_message_gd
            service_data['cluster_id'] = self.server.cluster_id
        else:
            server_name = kwargs.get('server_name')
            server_pid = kwargs.get('server_pid')

            if not(sub_key and server_name and server_pid):
                raise Exception('All of sub_key, server_name and server_pid are required for non-GD messages')

            service_name = _service_delete_message_non_gd
            service_data['server_name'] = server_name
            service_data['server_pid'] = server_pid

        # There is no response currently but one may be added at a later time
        return self.invoke_service(service_name, service_data, serialize=False)

# ################################################################################################################################
# ################################################################################################################################

    def subscribe(self, topic_name, _find_wsx_environ=find_wsx_environ, **kwargs):

        # Are we going to subscribe a WSX client?
        use_current_wsx = kwargs.get('use_current_wsx')

        # This is always needed to invoke the subscription service
        request = {
            'topic_name': topic_name,
            'wrap_one_msg_in_list': kwargs.get('wrap_one_msg_in_list', True),
            'delivery_batch_size': kwargs.get('delivery_batch_size', PUBSUB.DEFAULT.DELIVERY_BATCH_SIZE)
        }

        # This is a subscription for a WebSocket client ..
        if use_current_wsx:
            service = kwargs.get('service')

            if use_current_wsx and (not service):
                raise Exception('Parameter `service` is required if `use_current_wsx` is True')

            # If the caller wants to subscribe a WebSocket, make sure the WebSocket's metadata
            # is given to us on input - the call below will raise an exception if it was not,
            # otherwise it will return WSX metadata out which we can extract our WebSocket object.
            wsx_environ = _find_wsx_environ(service)
            wsx = wsx_environ['web_socket']

            # All set, we can carry on with other steps now
            sub_service_name = PUBSUB.SUBSCRIBE_CLASS.get(PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id)
            wsgi_environ = service.wsgi_environ or kwargs.get('wsgi_environ')
            wsgi_environ['zato.request_ctx.pubsub.unsub_on_wsx_close'] = kwargs.get('unsub_on_wsx_close')

        # .. this is a subscription for any client that is not WebSockets-based
        else:

            # Non-WSX endpoints always need to be identified by their names
            endpoint_name = kwargs.get('endpoint_name')
            if not endpoint_name:
                raise Exception('Parameter `endpoint_name` is required for non-WebSockets subscriptions')
            else:
                endpoint = self.get_endpoint_by_name(endpoint_name)

            # Required to subscribe non-WSX endpoints
            request['endpoint_id'] = endpoint.id

            sub_service_name = PUBSUB.SUBSCRIBE_CLASS.get(endpoint.endpoint_type)
            wsgi_environ = {}

        # Actually subscribe the caller
        response = self.invoke_service(sub_service_name, request, wsgi_environ=wsgi_environ, serialize=False)

        # If this was a WebSocket caller, we can now update its pub/sub metadata
        if use_current_wsx:
            wsx.set_last_interaction_data('pubsub.subscribe')

        return response.sub_key

# ################################################################################################################################
# ################################################################################################################################

    def resume_wsx_subscription(self, sub_key, service, _find_wsx_environ=find_wsx_environ):
        """ Invoked by WSX clients that want to resume deliveries of their messages after they reconnect.
        """
        # Get metadata and the WebSocket itself
        wsx_environ = _find_wsx_environ(service)
        wsx = wsx_environ['web_socket']

        # Actual resume subscription
        self.invoke_service('zato.pubsub.resume-wsx-subscription', {
            'sql_ws_client_id': wsx_environ['sql_ws_client_id'],
            'channel_name': wsx_environ['ws_channel_config']['name'],
            'pub_client_id': wsx_environ['pub_client_id'],
            'web_socket': wsx,
            'sub_key': sub_key
        }, wsgi_environ=service.wsgi_environ)

        # If we get here, it means the service succeeded so we can update that WebSocket's pub/sub metadata
        wsx.set_last_interaction_data('wsx.resume_wsx_subscription')

        # All done, we can store a new entry in logs now
        peer_info = wsx.get_peer_info_pretty()

        logger.info(msg.wsx_sub_resumed, sub_key, peer_info)
        logger_zato.info(msg.wsx_sub_resumed, sub_key, peer_info)

# ################################################################################################################################
# ################################################################################################################################
