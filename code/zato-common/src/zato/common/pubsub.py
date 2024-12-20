# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# ujson
from json import dumps

# Zato
from zato.common.api import GENERIC, PUBSUB
from zato.common.odb.model import PubSubSubscription
from zato.common.odb.query.pubsub.subscription import pubsub_sub_key_list
from zato.common.typing_ import cast_
from zato.common.util.api import new_cid
from zato.common.util.time_ import utcnow_as_ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy import Column
    from sqlalchemy.orm.session import Session as SQLSession
    from zato.common.typing_ import any_, anylist, anytuple, callable_, commondict, optional, stranydict, \
        strlist, strlistempty, strnone, strorfloat, strtuple, tupnone
    from zato.server.connection.http_soap.outgoing import SudsSOAPWrapper
    from zato.server.pubsub.model import Topic
    anytuple = anytuple
    tupnone = tupnone
    Column = Column

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger('zato_pubsub.msg')
logger_zato = getLogger('zato')

# ################################################################################################################################
# ################################################################################################################################

class MSG_PREFIX:
    GROUP_ID = 'zpsg'
    MSG_ID = 'zpsm'
    SUB_KEY = 'zpsk'
    SERVICE_SK = 'zpsk.srv'

prefix_group_id = MSG_PREFIX.GROUP_ID
prefix_msg_id   = MSG_PREFIX.MSG_ID
prefix_sk       = MSG_PREFIX.SUB_KEY

# ################################################################################################################################
# ################################################################################################################################

sk_lists = ('reply_to_sk', 'deliver_to_sk')

# ################################################################################################################################

skip_to_external = (
    'delivery_status', 'topic_id', 'cluster_id', 'pub_pattern_matched', 'sub_pattern_matched',
    'published_by_id', 'data_prefix', 'data_prefix_short', 'pub_time', 'expiration_time', 'recv_time',
    'pub_msg_id', 'pub_correl_id', 'zato_ctx', 'is_in_sub_queue', 'has_gd', 'server_name', 'server_pid'
) + sk_lists

# ################################################################################################################################

_data_keys = (
    'data', 'data_prefix', 'data_prefix_short'
)

# ################################################################################################################################

msg_pub_attrs = (
    'topic', 'sub_key', 'pub_msg_id', 'pub_correl_id', 'in_reply_to', 'ext_client_id', 'group_id',
    'position_in_group', 'pub_time', 'ext_pub_time', 'data', 'data_prefix', 'data_prefix_short', 'mime_type', 'priority',
    'expiration', 'expiration_time', 'has_gd', 'delivery_status', 'size', 'published_by_id', 'topic_id',
    'is_in_sub_queue', 'topic_name', 'cluster_id', 'pub_time_iso', 'ext_pub_time_iso', 'expiration_time_iso',
    'recv_time', 'recv_time_iso', 'data_prefix_short', 'server_name', 'server_pid', 'pub_pattern_matched', 'sub_pattern_matched',
    'delivery_count', 'user_ctx', 'zato_ctx'
)

# ################################################################################################################################

# These public attributes need to be ignored when the message is published
msg_pub_ignore = (
    'delivery_count',
    'deliver_to_sk',
    'delivery_status',
    'recv_time',
    'recv_time_iso',
    'reply_to_sk',
    'expiration_time_iso',
    'ext_pub_time_iso',
    'pub_time_iso',
    'server_name',
    'sub_key',
    'server_pid',
)

# ################################################################################################################################

def new_msg_id(_new_cid:'callable_'=new_cid, _prefix:'str'=prefix_msg_id) -> 'str':
    return '%s%s' % (_prefix, _new_cid())

# ################################################################################################################################

def new_sub_key(
    endpoint_type,    # type: str
    ext_client_id='', # type: str
    _new_cid=new_cid, # type: callable_
    _prefix=prefix_sk # type: str
    ) -> 'str':
    _ext_client_id = '.%s' % (ext_client_id,) if ext_client_id else (ext_client_id or '')
    return '%s.%s%s.%s' % (_prefix, endpoint_type, _ext_client_id, _new_cid(3))

# ################################################################################################################################

def new_group_id(_new_cid:'callable_'=new_cid, _prefix:'str'=prefix_group_id) -> 'str':
    return '%s%s' % (_prefix, _new_cid())

# ################################################################################################################################
# ################################################################################################################################

class PubSubMessage:
    """ Base container class for pub/sub message wrappers.
    """
    # We are not using __slots__ because they can't be inherited by subclasses
    # and this class, as well as its subclasses, will be rewritten in Cython anyway.
    pub_attrs = msg_pub_attrs + sk_lists

    recv_time:     'float'
    recv_time_iso: 'str'
    server_name:   'str'
    server_pid:    'int'
    topic:         'optional[Topic]'
    sub_key:       'str'
    pub_msg_id:    'str'
    pub_correl_id: 'strnone'
    in_reply_to:   'strnone'
    ext_client_id: 'str'

    group_id:          'strnone'
    position_in_group: 'int'
    pub_time:          'strorfloat'
    ext_pub_time:      'strorfloat | None'
    data:              'any_'
    data_prefix:       'str'
    data_prefix_short: 'str'
    mime_type:         'str'
    priority:          'int'
    expiration:        'int'
    expiration_time:   'float'
    has_gd:            'bool'
    delivery_status:   'str'

    pub_pattern_matched: 'str'
    sub_pattern_matched: 'stranydict'

    size:             'int'
    published_by_id:  'int'
    topic_id:         'int'
    is_in_sub_queue:  'bool'
    topic_name:       'str'
    cluster_id:       'int'
    delivery_count:   'int'
    pub_time_iso:     'str'
    ext_pub_time_iso: 'str'
    expiration_time_iso: 'str'

    reply_to_sk:   'strlistempty'
    deliver_to_sk: 'strlistempty'
    user_ctx:      'any_'
    zato_ctx:      'any_'
    serialized:    'any_'
    opaque1:       'any_'

    def __init__(self) -> 'None':
        self.recv_time = utcnow_as_ms()
        self.recv_time_iso = ''
        self.server_name = ''
        self.server_pid = 0
        self.topic = None
        self.sub_key = ''
        self.pub_msg_id = ''
        self.pub_correl_id = ''
        self.in_reply_to = None
        self.ext_client_id = ''
        self.group_id = ''
        self.position_in_group = -1
        self.pub_time = 0.0
        self.ext_pub_time = 0.0
        self.data = ''
        self.data_prefix = ''
        self.data_prefix_short = ''
        self.mime_type = ''
        self.priority = PUBSUB.PRIORITY.DEFAULT
        self.expiration = -1
        self.expiration_time = 0.0
        self.has_gd = False
        self.delivery_status = ''
        self.pub_pattern_matched = ''
        self.sub_pattern_matched = {}
        self.size = -1
        self.published_by_id = 0
        self.topic_id = 0
        self.is_in_sub_queue = False
        self.topic_name = ''
        self.cluster_id = 0
        self.delivery_count = 0
        self.pub_time_iso = ''
        self.ext_pub_time_iso = ''
        self.expiration_time_iso = ''
        self.reply_to_sk = []
        self.deliver_to_sk = []
        self.user_ctx = None
        self.zato_ctx = {}
        self.serialized = None # May be set by hooks to provide an explicitly serialized output for this message
        setattr(self, GENERIC.ATTR_NAME, None) # To make this class look more like an SQLAlchemy one

# ################################################################################################################################

    def to_dict(
        self,
        skip=None,               # type: tupnone
        needs_utf8_encode=False, # type: bool
        needs_utf8_decode=False, # type: bool
        add_id_attrs=False,      # type: bool
        _data_keys=_data_keys    # type: strtuple
        ) -> 'commondict':
        """ Returns a dict representation of self.
        """

        _skip = skip or () # type: anytuple
        out = {} # type: stranydict

        for key in sorted(PubSubMessage.pub_attrs):
            if key != 'topic' and key not in _skip:
                value = getattr(self, key)
                if value is not None:

                    if needs_utf8_encode:
                        if key in _data_keys:
                            value = value.encode('utf8') if isinstance(value, str) else value

                    if needs_utf8_decode:
                        if key in _data_keys:
                            value = value.decode('utf8') if isinstance(value, bytes) else value

                    out[key] = value

        if add_id_attrs:
            out['msg_id'] = self.pub_msg_id
            if self.pub_correl_id:
                out['correl_id'] = self.pub_correl_id

        # Append the generic opaque attribute to make the output look as though it was produced from an SQLAlchemy object
        # but do it only if there is any value, otherwise skip it.
        opaque_value = getattr(self, GENERIC.ATTR_NAME)
        if opaque_value:
            out[GENERIC.ATTR_NAME] = opaque_value

        return out

# ################################################################################################################################

    # For compatibility with code that already expects dictalchemy objects with their .asdict method
    def asdict(self) -> 'commondict':
        out = self.to_dict()
        out[GENERIC.ATTR_NAME] = getattr(self, GENERIC.ATTR_NAME)
        return out

# ################################################################################################################################

    def to_external_dict(self, skip:'strtuple'=skip_to_external, needs_utf8_encode:'bool'=False) -> 'commondict':
        """ Returns a dict representation of self ready to be delivered to external systems,
        i.e. without internal attributes on output.
        """
        out = self.to_dict(skip, needs_utf8_encode=needs_utf8_encode, add_id_attrs=True)
        if self.reply_to_sk:
            out['ctx'] = {
                'reply_to_sk': self.reply_to_sk
            }
        return out

# ################################################################################################################################

    def to_json(self, *args:'any_', **kwargs:'any_') -> 'str':
        data = self.to_dict(*args, **kwargs)
        return dumps(data)

# ################################################################################################################################

    def to_external_json(self, *args:'any_', **kwargs:'any_') -> 'str':
        data = self.to_external_dict(*args, **kwargs)
        return dumps(data)

# ################################################################################################################################
# ################################################################################################################################

class SkipDelivery(Exception):
    """ Raised to indicate to delivery tasks that a given message should be skipped - but not deleted altogether,
    the delivery will be attempted in the next iteration of the task.
    """

# ################################################################################################################################
# ################################################################################################################################

class HandleNewMessageCtx:
    """ Encapsulates information on new messages that a pubsub tool is about to process.
    """
    __slots__ = ('cid', 'has_gd', 'sub_key_list', 'non_gd_msg_list', 'is_bg_call', 'pub_time_max')

    cid:             'str'
    has_gd:          'bool'
    sub_key_list:    'strlist'
    non_gd_msg_list: 'anylist'
    is_bg_call:      'bool'
    pub_time_max:    'float'

    def __init__(
        self,
        cid,               # type: str
        has_gd,            # type: bool
        sub_key_list,      # type: strlist
        non_gd_msg_list,   # type: anylist
        is_bg_call,        # type: bool
        pub_time_max=0.0   # type: float
    ) -> 'None':
        self.cid = cid
        self.has_gd = has_gd
        self.sub_key_list = sub_key_list
        self.non_gd_msg_list = non_gd_msg_list
        self.is_bg_call = is_bg_call
        self.pub_time_max = pub_time_max

# ################################################################################################################################
# ################################################################################################################################

class HookCtx:
    """ Data and metadata that pub/sub hooks receive on input to their methods.
    """
    __slots__ = ('msg', 'response', 'soap_suds_client')

    msg: 'any_'
    soap_suds_client: 'optional[SudsSOAPWrapper]'
    response: 'any_'

    def __init__(self, msg:'any_', soap_suds_client:'optional[SudsSOAPWrapper]'=None) -> 'None':
        self.msg = msg
        self.soap_suds_client = soap_suds_client
        self.response = None

# ################################################################################################################################

# PubSub's attributes listed separately for ease of making them part of SimpleIO definitions
pubsub_main_data = 'cluster_id', 'server_name', 'server_pid', 'server_api_address', 'keep_running', 'subscriptions_by_topic', \
    'subscriptions_by_sub_key', 'sub_key_servers', 'endpoints', 'topics', 'sec_id_to_endpoint_id', \
    'ws_channel_id_to_endpoint_id', 'service_id_to_endpoint_id', 'topic_name_to_id', \
    'pubsub_tool_by_sub_key', 'pubsub_tools', 'sync_backlog', 'msg_pub_counter', 'has_meta_endpoint', \
    'endpoint_meta_store_frequency', 'endpoint_meta_data_len', 'endpoint_meta_max_history', 'data_prefix_len', \
    'data_prefix_short_len'

# ################################################################################################################################

class dict_keys:
    endpoint = 'id', 'name', 'endpoint_type', 'role', 'is_active', 'is_internal', 'topic_patterns', \
        'pub_topic_patterns', 'sub_topic_patterns'

    subscription = 'id', 'creation_time', 'sub_key', 'endpoint_id', 'endpoint_name', 'topic_id', 'topic_name', \
        'sub_pattern_matched', 'task_delivery_interval', 'unsub_on_wsx_close', 'ext_client_id'

    topic = 'id', 'name', 'is_active', 'is_internal', 'max_depth_gd', 'max_depth_non_gd', 'has_gd', 'depth_check_freq',\
        'pub_buffer_size_gd', 'task_delivery_interval', 'meta_store_frequency', 'task_sync_interval', 'msg_pub_counter', \
        'msg_pub_counter_gd', 'msg_pub_counter_non_gd', 'last_synced', 'sync_has_gd_msg', 'sync_has_non_gd_msg', \
        'gd_pub_time_max'

    sks = 'sub_key', 'cluster_id', 'server_name', 'server_pid', 'endpoint_type', 'channel_name', 'pub_client_id', \
        'ext_client_id', 'wsx_info', 'creation_time', 'endpoint_id'

# ################################################################################################################################

all_dict_keys = dict_keys.endpoint + dict_keys.subscription + dict_keys.topic + dict_keys.sks
all_dict_keys = set(all_dict_keys)  # type: ignore[assignment]
all_dict_keys = list(all_dict_keys) # type: ignore[assignment]

# ################################################################################################################################
# ################################################################################################################################

def ensure_subs_exist(
    session:     'SQLSession',
    topic_name:  'str',
    gd_msg_list: 'anylist',
    sub_key_aware_objects:'anylist',
    log_action:'str',
    context_str:'str',
) -> 'anylist':

    # A list of input objects that we will return, which will mean that they do exist in the database
    out = [] # type: anylist

    # Length of what we have on input, for logging purposes
    len_orig_sk_list = len(sub_key_aware_objects)

    # A list of sub keys from which we will potentially remove subscriptions that do not exist
    sk_set = {elem['sub_key'] for elem in sub_key_aware_objects}

    query = pubsub_sub_key_list(session) # type: ignore
    query = query.filter(cast_('Column', PubSubSubscription.sub_key).in_(sk_set)) # type: ignore

    existing_sk_list = query.all() # type: ignore
    existing_sk_set  = {elem.sub_key for elem in existing_sk_list} # type: ignore

    # Find the intersection (shared elements) of what we have on input and what the database actually contains ..
    shared = sk_set & existing_sk_set

    # .. populate the output list ..
    for sub in sub_key_aware_objects:
        if sub['sub_key'] in shared:
            out.append(sub)

    # .. log if there was anything removed ..
    to_remove = sk_set - shared

    if to_remove:
        logger.info('Removed sub_keys -> %s -> %s before %s `%s`; len_orig:%s, len_out:%s;  left %s -> %s',
            context_str,
            to_remove,
            log_action,
            topic_name,
            len_orig_sk_list,
            len(out),
            sorted(elem['sub_key']    for elem in out), # type: ignore
            sorted(elem['pub_msg_id'] for elem in gd_msg_list)
        )

    # .. and return the result to our caller.
    return out

# ################################################################################################################################
# ################################################################################################################################
