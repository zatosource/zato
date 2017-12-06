# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.util import new_cid

# ################################################################################################################################

def new_msg_id(_new_cid=new_cid):
    return 'zpsm%s' % _new_cid()

# ################################################################################################################################

def new_sub_key(_new_cid=new_cid):
    return 'zpsk%s' % _new_cid()

# ################################################################################################################################

def new_group_id(_new_cid=new_cid):
    return 'zpsg%s' % _new_cid()

# ################################################################################################################################

class PubSubMessage(object):
    """ Base container class for pub/sub message wrappers.
    """
    __slots__ = ('topic', 'sub_key', 'pub_msg_id', 'pub_correl_id', 'in_reply_to', 'ext_client_id', 'group_id',
        'position_in_group', 'pub_time', 'data', 'mime_type', 'priority', 'expiration', 'expiration_time', 'has_gd',
        'delivery_status', 'pattern_matched', 'size', 'published_by_id', 'topic_id', 'cluster_id', 'ext_pub_time',
        'data_prefix', 'data_prefix_short')

    def __init__(self):
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
        self.data = None
        self.data_prefix = None
        self.data_prefix_short = None
        self.mime_type = None
        self.priority = None
        self.expiration = None
        self.expiration_time = None
        self.has_gd = None
        self.delivery_status = None
        self.pattern_matched = None
        self.size = None
        self.published_by_id = None
        self.topic_id = None
        self.cluster_id = None

    def to_dict(self):
        out = {}
        for key in PubSubMessage.__slots__:
            if key != 'topic':
                out[key] = getattr(self, key)

        return out

# ################################################################################################################################

class SkipDelivery(Exception):
    """ Raised to indicate to delivery tasks that a given message should be skipped - but not deleted altogether,
    the delivery will be attempted in the next iteration of the task.
    """
