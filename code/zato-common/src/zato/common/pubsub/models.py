# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# Zato
from zato.common.typing_ import dict_, list_, optional, str as str_

# ################################################################################################################################
# ################################################################################################################################

# Default values
DEFAULT_PRIORITY = 5
DEFAULT_EXPIRATION = 86400  # 24 hours in seconds

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class PubMessage:
    """ Model representing a message to be published to a topic.
    """
    data: Any
    priority: int = DEFAULT_PRIORITY
    expiration: int = DEFAULT_EXPIRATION
    correl_id: str = ''
    in_reply_to: str = ''
    ext_client_id: str = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class PubResponse:
    """ Response model for publish operations.
    """
    is_ok: bool
    msg_id: str = ''
    cid: str = ''
    details: str = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Message:
    """ Model for a single message as returned by retrieve/read operations.
    """
    data: Any
    topic_name: str
    msg_id: str
    correl_id: str = ''
    in_reply_to: str = ''
    priority: int = DEFAULT_PRIORITY
    mime_type: str = 'application/json'
    ext_client_id: str = ''
    pub_time_iso: str = ''
    ext_pub_time_iso: str = ''
    recv_time_iso: str = ''
    expiration: int = DEFAULT_EXPIRATION
    expiration_time_iso: str = ''
    size: int = 0
    delivery_count: int = 0
    sub_key: str = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class MessagesResponse:
    """ Response model containing a list of messages.
    """
    is_ok: bool
    messages: List[Message] = field(default_factory=list)

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class SimpleResponse:
    """ Generic response model with just an is_ok field.
    """
    is_ok: bool

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class User:
    """ Model representing a user with username and password.
    """
    username: str
    password: str

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Subscription:
    """ Model representing a subscription to a topic.
    """
    topic_name: str
    endpoint_name: str
    sub_key: str
    creation_time: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Topic:
    """ Model representing a topic.
    """
    name: str
    creation_time: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

# ################################################################################################################################
# ################################################################################################################################

# Type aliases for collections
users_dict = dict_[str, str]
user_list = list_[User]
subscription_list = list_[Subscription]
message_list = list_[Message]
topic_list = list_[Topic]

# Optional types
message_optional = optional[Message]
subscription_optional = optional[Subscription]
topic_optional = optional[Topic]

# ################################################################################################################################
# ################################################################################################################################
