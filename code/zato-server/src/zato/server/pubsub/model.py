# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from datetime import datetime

# globre
from globre import compile as globre_compile

# Python 2/3 compatibility
from future.utils import iteritems

# Zato
from zato.common import DATA_FORMAT, PUBSUB, SEARCH
from zato.common.exception import BadRequest
from zato.common.pubsub import dict_keys
from zato.common.util import make_repr
from zato.common.util.event import EventLog
from zato.common.util.time_ import utcnow_as_ms

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
