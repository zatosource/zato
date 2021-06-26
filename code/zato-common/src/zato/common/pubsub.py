# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from logging import getLogger

# Python 2/3 compatibility
from past.builtins import unicode

# Zato
from zato.common.api import GENERIC
from zato.common.util.api import new_cid
from zato.common.util.time_ import utcnow_as_ms

# ################################################################################################################################

logger = getLogger('zato_pubsub.msg')
logger_zato = getLogger('zato')

# ################################################################################################################################

sk_lists = ('reply_to_sk', 'deliver_to_sk')

skip_to_external=('delivery_status', 'topic_id', 'cluster_id', 'pub_pattern_matched', 'sub_pattern_matched',
    'published_by_id', 'data_prefix', 'data_prefix_short', 'pub_time', 'expiration_time', 'recv_time',
    'pub_msg_id', 'pub_correl_id', 'zato_ctx') + sk_lists

_data_keys=('data', 'data_prefix', 'data_prefix_short')

msg_pub_attrs = ('topic', 'sub_key', 'pub_msg_id', 'pub_correl_id', 'in_reply_to', 'ext_client_id', 'group_id',
    'position_in_group', 'pub_time', 'ext_pub_time', 'data', 'data_prefix', 'data_prefix_short', 'mime_type', 'priority',
    'expiration', 'expiration_time', 'has_gd', 'delivery_status', 'size', 'published_by_id', 'topic_id',
    'is_in_sub_queue', 'topic_name', 'cluster_id', 'pub_time_iso', 'ext_pub_time_iso', 'expiration_time_iso',
    'recv_time', 'data_prefix_short', 'server_name', 'server_pid', 'pub_pattern_matched', 'sub_pattern_matched',
    'delivery_count', 'user_ctx', 'zato_ctx')

class MSG_PREFIX:
    GROUP_ID = 'zpsg'
    MSG_ID = 'zpsm'
    SUB_KEY = 'zpsk'
    SERVICE_SK = 'zpsk.srv'

# ################################################################################################################################

def new_msg_id(_new_cid=new_cid, _prefix=MSG_PREFIX.MSG_ID):
    return '%s%s' % (_prefix, _new_cid())

# ################################################################################################################################

def new_sub_key(endpoint_type, ext_client_id='', _new_cid=new_cid, _prefix=MSG_PREFIX.SUB_KEY):
    _ext_client_id = '.%s' % (ext_client_id,) if ext_client_id else (ext_client_id or '')
    return '%s.%s%s.%s' % (_prefix, endpoint_type, _ext_client_id, _new_cid(3))

# ################################################################################################################################

def new_group_id(_new_cid=new_cid, _prefix=MSG_PREFIX.GROUP_ID):
    return '%s%s' % (_prefix, _new_cid())

# ################################################################################################################################

class PubSubMessage(object):
    """ Base container class for pub/sub message wrappers.
    """
    # We are not using __slots__ because they can't be inherited by subclasses
    # and this class, as well as its subclasses, will be rewritten in Cython anyway.
    pub_attrs = msg_pub_attrs + sk_lists

    def __init__(self):
        self.recv_time = utcnow_as_ms()
        self.server_name = None
        self.server_pid = None
        self.topic = None
        self.sub_key = None
        self.pub_msg_id = None
        self.pub_correl_id = None
        self.in_reply_to = None
        self.ext_client_id = None
        self.group_id = None
        self.position_in_group = None
        self.pub_time = None
        self.ext_pub_time = None
        self.data = ''
        self.data_prefix = ''
        self.data_prefix_short = ''
        self.mime_type = None
        self.priority = None
        self.expiration = None
        self.expiration_time = None
        self.has_gd = None
        self.delivery_status = None
        self.pub_pattern_matched = None
        self.sub_pattern_matched = {}
        self.size = None
        self.published_by_id = None
        self.topic_id = None
        self.is_in_sub_queue = None
        self.topic_name = None
        self.cluster_id = None
        self.delivery_count = 0
        self.pub_time_iso = None
        self.ext_pub_time_iso = None
        self.expiration_time_iso = None
        self.reply_to_sk = []
        self.deliver_to_sk = []
        self.user_ctx = None
        self.zato_ctx = None
        self.serialized = None # May be set by hooks to provide an explicitly serialized output for this message
        setattr(self, GENERIC.ATTR_NAME, None) # To make this class look more like an SQLAlchemy one

    def to_dict(self, skip=None, needs_utf8_encode=False, add_id_attrs=False, _data_keys=_data_keys):
        """ Returns a dict representation of self.
        """
        skip = skip or []
        out = {}

        for key in sorted(PubSubMessage.pub_attrs):
            if key != 'topic' and key not in skip:
                value = getattr(self, key)
                if value is not None:
                    if needs_utf8_encode:
                        if key in _data_keys:
                            value = value.encode('utf8') if isinstance(value, unicode) else value
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

    # For compatibility with code that already expects dictalchemy objects with their .asdict method
    def asdict(self):
        out = self.to_dict()
        out[GENERIC.ATTR_NAME] = getattr(self, GENERIC.ATTR_NAME)
        return out

    def to_external_dict(self, skip=skip_to_external, needs_utf8_encode=False):
        """ Returns a dict representation of self ready to be delivered to external systems,
        i.e. without internal attributes on output.
        """
        out = self.to_dict(skip, needs_utf8_encode, True)
        if self.reply_to_sk:
            out['ctx'] = {
                'reply_to_sk': self.reply_to_sk
            }
        return out

# ################################################################################################################################

class SkipDelivery(Exception):
    """ Raised to indicate to delivery tasks that a given message should be skipped - but not deleted altogether,
    the delivery will be attempted in the next iteration of the task.
    """

# ################################################################################################################################

class HandleNewMessageCtx(object):
    """ Encapsulates information on new messages that a pubsub tool is about to process.
    """
    __slots__ = ('cid', 'has_gd', 'sub_key_list', 'non_gd_msg_list', 'is_bg_call', 'pub_time_max')

    def __init__(self, cid, has_gd, sub_key_list, non_gd_msg_list, is_bg_call, pub_time_max=None):
        self.cid = cid
        self.has_gd = has_gd
        self.sub_key_list = sub_key_list
        self.non_gd_msg_list = non_gd_msg_list
        self.is_bg_call = is_bg_call
        self.pub_time_max = pub_time_max

# ################################################################################################################################

class HookCtx(object):
    """ Data and metadata that pub/sub hooks receive on input to their methods.
    """
    __slots__ = ('msg', 'response', 'soap_suds_client')

    def __init__(self, msg, soap_suds_client=None):
        self.msg = msg
        self.soap_suds_client
        self.response = None

# ################################################################################################################################

# PubSub's attributes listed separately for ease of making them part of SimpleIO definitions
pubsub_main_data = 'cluster_id', 'server_name', 'server_pid', 'server_api_address', 'keep_running', 'subscriptions_by_topic', \
    'subscriptions_by_sub_key', 'sub_key_servers', 'endpoints', 'topics', 'sec_id_to_endpoint_id', \
    'ws_channel_id_to_endpoint_id', 'service_id_to_endpoint_id', 'topic_name_to_id', 'pub_buffer_gd', 'pub_buffer_non_gd', \
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

all_dict_keys = dict_keys.endpoint + dict_keys.subscription + dict_keys.topic + dict_keys.sks
all_dict_keys = list(set(all_dict_keys))

# ################################################################################################################################
