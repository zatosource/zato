# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import datetime
import logging
from dataclasses import dataclass, field
from typing import Dict, List

# Zato
from zato.common.typing_ import any_, anynone, strnone

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import TypeAlias

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato.pubsub.rest')

# ################################################################################################################################
# ################################################################################################################################

# Default message expiration in seconds (24 hours)
_default_expiration = 86400

# Default message priority (middle value)
_pri_min = 1
_pri_max = 9
_pri_def = 5

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=True)
class MessageData:
    """ Data structure representing a pub/sub message with all its metadata.
    """
    # Basic message identification
    msg_id:'str' = ''
    topic_name:'str' = ''
    
    # Message correlation fields
    correl_id:'strnone' = None
    in_reply_to:'strnone' = None
    
    # Message metadata
    priority:'int' = _pri_def
    mime_type:'str' = 'application/json'
    ext_client_id:'strnone' = None
    pub_time_iso:'str' = ''
    ext_pub_time_iso:'str' = ''
    recv_time_iso:'str' = ''
    expiration:'int' = _default_expiration
    expiration_time_iso:'str' = ''
    size:'int' = 0
    delivery_count:'int' = 0
    sub_key:'str' = ''
    
    # Message content
    data:'anynone' = None

    def to_dict(self) -> 'Dict':
        """ Convert message to a dictionary for JSON serialization.
        """
        return {
            'msg_id': self.msg_id,
            'topic_name': self.topic_name,
            'correl_id': self.correl_id or '',
            'in_reply_to': self.in_reply_to or '',
            'priority': self.priority,
            'mime_type': self.mime_type,
            'ext_client_id': self.ext_client_id or '',
            'pub_time_iso': self.pub_time_iso,
            'ext_pub_time_iso': self.ext_pub_time_iso,
            'recv_time_iso': self.recv_time_iso,
            'expiration': self.expiration,
            'expiration_time_iso': self.expiration_time_iso,
            'size': self.size,
            'delivery_count': self.delivery_count,
            'sub_key': self.sub_key,
            'data': self.data
        }

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=True)
class Subscription:
    """ Data structure representing a pub/sub subscription.
    """
    # Basic subscription identification
    sub_id:'str' = ''
    topic_name:'str' = ''
    endpoint_name:'str' = ''
    
    # Subscription patterns
    patterns:'List[str]' = field(default_factory=list)
    
    # Runtime data - the actual message queue for this subscription
    messages:'List[MessageData]' = field(default_factory=list)

    def to_dict(self) -> 'Dict':
        """ Convert subscription to a dictionary for JSON serialization.
        """
        return {
            'sub_id': self.sub_id,
            'topic_name': self.topic_name,
            'endpoint_name': self.endpoint_name,
            'patterns': self.patterns,
            'message_count': len(self.messages)
        }

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=True)
class Topic:
    """ Data structure representing a pub/sub topic.
    """
    # Basic topic identification
    name:'str' = ''
    
    # Subscriptions to this topic
    subscriptions:'Dict[str, Subscription]' = field(default_factory=dict)

    def to_dict(self) -> 'Dict':
        """ Convert topic to a dictionary for JSON serialization.
        """
        return {
            'name': self.name,
            'subscription_count': len(self.subscriptions),
            'subscriptions': [sub.to_dict() for sub in self.subscriptions.values()]
        }

# ################################################################################################################################
# ################################################################################################################################
