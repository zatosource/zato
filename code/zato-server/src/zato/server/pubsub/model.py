# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pylint: disable=unused-import, redefined-builtin, unused-variable

# stdlib
import logging
from dataclasses import dataclass, field as dc_field
from datetime import datetime

# globre
from globre import compile as globre_compile

# Python 2/3 compatibility
from zato.common.ext.future.utils import iteritems

# Zato
from zato.common.api import PUBSUB
from zato.common.exception import BadRequest
from zato.common.pubsub import dict_keys
from zato.common.typing_ import cast_, dict_, list_, optional
from zato.common.util.api import make_repr
from zato.common.util.time_ import utcnow_as_ms

# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist, callable_, intnone, strlist, strtuple
    from zato.server.pubsub.delivery.message import msgnone
    anylist = anylist
    intnone = intnone

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

_does_not_exist = object()

# ################################################################################################################################

_default_expiration = PUBSUB.DEFAULT.EXPIRATION
default_sk_server_table_columns = 6, 15, 8, 6, 17, 80

# ################################################################################################################################

_PRIORITY=PUBSUB.PRIORITY

_pri_min=_PRIORITY.MIN
_pri_max=_PRIORITY.MAX
_pri_def=_PRIORITY.DEFAULT

# ################################################################################################################################

def get_priority(
    cid,   # type: str
    input, # type: anydict
    _pri_min=_pri_min, # type: int
    _pri_max=_pri_max, # type: int
    _pri_def=_pri_def  # type: int
) -> 'int':
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

def get_expiration(cid:'str', input:'anydict', default_expiration:'int'=_default_expiration) -> 'int':
    """ Get and validate message expiration.
    Returns (2 ** 31 - 1) * 1000 milliseconds (around 70 years) if expiration is not set explicitly.
    """
    expiration = input.get('expiration') # type: intnone
    if expiration is not None and expiration < 0:
        raise BadRequest(cid, 'Expiration `{}` must not be negative'.format(expiration))

    return expiration or default_expiration

# ################################################################################################################################
# ################################################################################################################################

class EventType:

    class Topic:
        set_hooks = 'set_hooks'
        incr_topic_msg_counter       = 'incr_topic_msg_counter'
        update_task_sync_time_before = 'update_task_sync_time_before'
        update_task_sync_time_after  = 'update_task_sync_time_after'
        needs_task_sync_before       = 'needs_task_sync_before'
        needs_task_sync_after        = 'needs_task_sync_after'

    class PubSub:
        loop_topic_id_dict     = 'loop_topic_id_dict'
        loop_sub_keys          = 'loop_sub_keys'
        loop_before_has_msg    = 'loop_before_has_msg'
        loop_has_msg           = 'loop_has_msg'
        loop_before_sync       = 'loop_before_sync'
        _set_sync_has_msg      = '_set_sync_has_msg'
        about_to_subscribe     = 'about_to_subscribe'
        about_to_access_sub_sk = 'about_to_access_sub_sk'
        in_subscribe_impl      = 'in_subscribe_impl'

# ################################################################################################################################
# ################################################################################################################################

class ToDictBase:

    _to_dict_keys:'tuple'
    config:'anydict'

    def to_dict(self) -> 'anydict':
        out = {} # type: anydict

        for name in self._to_dict_keys:
            name = cast_('str', name)
            value = getattr(self, name, _does_not_exist) # type: any_
            if value is _does_not_exist:
                value = self.config[name]
            out[name] = value

        return out

# ################################################################################################################################
# ################################################################################################################################

class Endpoint(ToDictBase):
    """ A publisher/subscriber in pub/sub workflows.
    """
    _to_dict_keys = dict_keys.endpoint

    config: 'anydict'
    id: 'int'
    name: 'str'
    endpoint_type: 'str'
    role: 'str'
    is_active: 'bool'
    is_internal: 'bool'

    topic_patterns: 'str'

    pub_topic_patterns: 'strlist'
    sub_topic_patterns: 'strlist'

    pub_topics: 'anydict'
    sub_topics: 'anydict'

    def __init__(self, config:'anydict') -> 'None':
        self.config = config
        self.id = config['id']
        self.name = config['name']
        self.endpoint_type = config['endpoint_type']
        self.role = config['role']
        self.is_active = config['is_active']
        self.is_internal = config['is_internal']
        self.service_id = config['service_id']

        self.topic_patterns = config.get('topic_patterns', '')

        self.pub_topic_patterns = []
        self.sub_topic_patterns = []

        self.pub_topics = {}
        self.sub_topics = {}

        self.set_up_patterns()

# ################################################################################################################################

    def __repr__(self) -> 'str':
        return make_repr(self)

# ################################################################################################################################

    def get_id(self) -> 'str':
        return '{};{};{}'.format(self.id, self.endpoint_type, self.name)

# ################################################################################################################################

    def to_dict(self, _replace:'strtuple'=('pub_topic_patterns', 'sub_topic_patterns')) -> 'anydict':
        out = super(Endpoint, self).to_dict()
        for key, value in out.items():
            if key in _replace:
                if value:
                    out[key] = sorted([(elem[0], str(elem[1])) for elem in value])
        return out

# ################################################################################################################################

    def set_up_patterns(self) -> 'None':
        data = {
            'topic': self.topic_patterns,
        }

        # is_pub, is_topic -> target set
        targets = {
            (True, True): self.pub_topic_patterns,
            (False, True): self.sub_topic_patterns,
        } # type: anydict

        for key, config in iteritems(data):
            is_topic = key == 'topic' # type: bool

            for line in (config or '').splitlines():
                line = line.strip()
                if line.startswith('pub=') or line.startswith('sub='):
                    is_pub = line.startswith('pub=') # type: bool

                    matcher = line[line.find('=')+1:]
                    matcher = globre_compile(matcher)

                    source = (is_pub, is_topic)
                    target = targets[source] # type: anylist
                    target.append([line, matcher])

                else:
                    msg = 'Ignoring invalid %s pattern `%s` for `%s` (role:%s) (reason: no pub=/sub= prefix found)'
                    logger.warning(msg, key, line, self.name, self.role)

# ################################################################################################################################
# ################################################################################################################################

class Topic(ToDictBase):
    """ An individiual topic in in pub/sub workflows.
    """
    _to_dict_keys = dict_keys.topic

    config: 'anydict'

    id:          'int'
    name:        'str'
    is_active:   'bool'
    is_internal: 'bool'
    has_gd:      'bool'

    server_name: 'str'
    server_pid:  'int'

    max_depth_gd:     'int'
    max_depth_non_gd: 'int'

    last_synced:         'float'
    gd_pub_time_max:     'float'
    sync_has_gd_msg:     'bool'
    sync_has_non_gd_msg: 'bool'

    depth_check_freq:   'int'
    pub_buffer_size_gd: 'int'

    msg_pub_counter:        'int'
    msg_pub_counter_gd:     'int'
    msg_pub_counter_non_gd: 'int'

    task_sync_interval:     'float'
    meta_store_frequency:   'int'
    task_delivery_interval: 'int'

    limit_retention: 'int'
    limit_message_expiry: 'int'
    limit_sub_inactivity: 'int'

    def __init__(self, config:'anydict', server_name:'str', server_pid:'int') -> 'None':
        self.config = config
        self.server_name = server_name
        self.server_pid = server_pid
        self.id = config['id']
        self.name = config['name']
        self.is_active = config['is_active']
        self.is_internal = config['is_internal']
        self.max_depth_gd = config['max_depth_gd']
        self.max_depth_non_gd = config['max_depth_non_gd']
        self.has_gd = config['has_gd']
        self.depth_check_freq = config['depth_check_freq']
        self.pub_buffer_size_gd = config['pub_buffer_size_gd']
        self.task_delivery_interval = config['task_delivery_interval']
        self.meta_store_frequency = config['meta_store_frequency']
        self.limit_retention = config.get('limit_retention') or PUBSUB.DEFAULT.LimitTopicRetention
        self.limit_message_expiry = config.get('limit_message_expiry') or PUBSUB.DEFAULT.LimitMessageExpiry
        self.limit_sub_inactivity = config.get('limit_sub_inactivity') or PUBSUB.DEFAULT.LimitSubInactivity
        self.set_hooks()

        # For now, task sync interval is the same for GD and non-GD messages
        # so we can arbitrarily pick the former to serve for both types of messages.
        self.task_sync_interval = config['task_sync_interval'] / 1000.0

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
        self.gd_pub_time_max = 0.0 # type: float

# ################################################################################################################################

    def get_id(self) -> 'str':
        return '{};{}'.format(self.name, self.id)

# ################################################################################################################################

    def set_hooks(self) -> 'None':
        self.on_subscribed_service_invoker = self.config.get('on_subscribed_service_invoker')
        self.on_unsubscribed_service_invoker = self.config.get('on_unsubscribed_service_invoker')
        self.before_publish_hook_service_invoker = self.config.get('before_publish_hook_service_invoker')
        self.before_delivery_hook_service_invoker = self.config.get('before_delivery_hook_service_invoker')
        self.on_outgoing_soap_invoke_invoker = self.config.get('on_outgoing_soap_invoke_invoker')

# ################################################################################################################################

    def incr_topic_msg_counter(self, has_gd:'bool', has_non_gd:'bool') -> 'None':
        """ Increases counter of messages published to this topic from current server.
        """
        self.msg_pub_counter += 1

        if has_gd:
            self.msg_pub_counter_gd += 1

        if has_non_gd:
            self.msg_pub_counter_non_gd += 1

# ################################################################################################################################

    def update_task_sync_time(self, _utcnow_as_ms:'callable_'=utcnow_as_ms) -> 'None':
        """ Increases counter of messages published to this topic from current server.
        """
        self.last_synced = _utcnow_as_ms()

# ################################################################################################################################

    def needs_task_sync(self, _utcnow_as_ms:'callable_'=utcnow_as_ms) -> 'bool':

        now = _utcnow_as_ms()
        needs_sync = now - self.last_synced >= self.task_sync_interval

        return needs_sync

# ################################################################################################################################

    def needs_depth_check(self) -> 'bool':
        return self.msg_pub_counter_gd % self.depth_check_freq == 0

# ################################################################################################################################

    def needs_meta_update(self) -> 'bool':
        return self.msg_pub_counter % self.meta_store_frequency == 0

# ################################################################################################################################
# ################################################################################################################################

class Subscription(ToDictBase):
    """ Describes an existing subscription object.
    Note that, for WSX clients, it may exist even if the WebSocket is not currently connected.
    """
    _to_dict_keys = dict_keys.subscription

    config: 'anydict'
    id: 'int'
    creation_time: 'float'
    sub_key: 'str'
    endpoint_id: 'int'
    topic_id: 'int'
    topic_name: 'str'
    sub_pattern_matched: 'str'
    task_delivery_interval: 'int'
    unsub_on_wsx_close: 'bool'
    ext_client_id: 'str'

    def __init__(self, config:'anydict') -> 'None':
        self.config = config
        self.id = config['id']
        self.creation_time = config['creation_time'] * 1000.0
        self.sub_key = config['sub_key']
        self.endpoint_id = config['endpoint_id']
        self.topic_id = config['topic_id']
        self.topic_name = config['topic_name']
        self.sub_pattern_matched = config['sub_pattern_matched']
        self.task_delivery_interval = config['task_delivery_interval']
        self.unsub_on_wsx_close = config.get('unsub_on_wsx_close', PUBSUB.DEFAULT.UnsubOnWSXClose)
        self.ext_client_id = config['ext_client_id']

        # Object ws_channel_id is an ID of a WSX channel this subscription potentially belongs to,
        # otherwise it is None.
        self.is_wsx = bool(self.config['ws_channel_id'])

# ################################################################################################################################

    def __getitem__(self, key:'str') -> 'any_':
        return getattr(self, key)

# ################################################################################################################################

    def __lt__(self, other:'Subscription') -> 'bool':
        return self.sub_key < other.sub_key

# ################################################################################################################################

    def __repr__(self) -> 'str':
        return make_repr(self)

# ################################################################################################################################

    def get_id(self) -> 'str':
        return self.sub_key

# ################################################################################################################################
# ################################################################################################################################

class HookCtx:

    __slots__ = ('hook_type', 'msg', 'topic', 'sub', 'http_soap', 'outconn_name')

    msg:          'msgnone'
    sub:          'subnone'   # type: ignore[valid-type]
    topic:        'topicnone' # type: ignore[valid-type]
    hook_type:    'str'
    http_soap:    'anydict'
    outconn_name: 'str'

    def __init__(
        self,
        hook_type,      # type: str
        topic=None,     # type: topicnone # type: ignore[valid-type]
        msg=None,       # type: msgnone
        **kwargs        # type: any_
        ) -> 'None':

        self.hook_type = hook_type
        self.msg = msg
        self.topic = cast_(Topic, topic)
        self.sub = kwargs.get('sub')
        self.http_soap = kwargs.get('http_soap', {})
        self.outconn_name = self.http_soap.get('config', {}).get('name', '')

# ################################################################################################################################
# ################################################################################################################################

class SubKeyServer(ToDictBase):
    """ Holds information about which server has subscribers to an individual sub_key.
    """
    _to_dict_keys = dict_keys.sks

    config:        'anydict'
    sub_key:       'str'
    cluster_id:    'int'
    server_name:   'str'
    server_pid:    'int'
    endpoint_type: 'str'
    creation_time: 'datetime'

    # Attributes below are only for WebSockets
    channel_name:  'str'
    pub_client_id: 'str'
    ext_client_id: 'str'
    wsx_info:      'anydict'

    def __init__(self, config:'anydict', _utcnow:'callable_'=datetime.utcnow) -> 'None':
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
        self.wsx_info = config.get('wsx_info', {})

        # When this object was created
        self.creation_time = _utcnow()

# ################################################################################################################################

    def __repr__(self) -> 'str':
        return make_repr(self)

# ################################################################################################################################

    def get_id(self) -> 'str':
        return '{};{};{}'.format(self.server_name, self.server_pid, self.sub_key)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=True)
class DeliveryResultCtx:
    delivery_iter: int = 0
    is_ok: bool = False
    status_code: int = 0
    reason_code: int = 0
    exception_list: list_[Exception] = dc_field(default_factory=list)

# ################################################################################################################################
# ################################################################################################################################

subnone    = optional[Subscription]
sublist    = list_[Subscription]
strsubdict = dict_[str, Subscription]

topicnone  = optional[Topic]
topiclist  = list_[Topic]

strtopicdict = dict_[str, Topic]
inttopicdict = dict_[int, Topic]

# ################################################################################################################################
# ################################################################################################################################
