# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime

# Zato
from zato.common.typing_ import any_, dataclass, dict_, field, list_, optional, str_

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
    data: any_
    priority: int = DEFAULT_PRIORITY
    expiration: int = DEFAULT_EXPIRATION
    correl_id: str_ = ''
    in_reply_to: str_ = ''
    ext_client_id: str_ = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class PubResponse:
    """ Response model for publish operations.
    """
    is_ok: bool
    msg_id: str_ = ''
    cid: str_ = ''
    details: str_ = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Message:
    """ Model for a single message as returned by retrieve/read operations.
    """
    data: any_
    topic_name: str_
    msg_id: str_
    correl_id: str_ = ''
    in_reply_to: str_ = ''
    priority: int = DEFAULT_PRIORITY
    mime_type: str_ = 'application/json'
    ext_client_id: str_ = ''
    pub_time_iso: str_ = ''
    ext_pub_time_iso: str_ = ''
    recv_time_iso: str_ = ''
    expiration: int = DEFAULT_EXPIRATION
    expiration_time_iso: str_ = ''
    size: int = 0
    delivery_count: int = 0
    sub_key: str_ = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class MessagesResponse:
    """ Response model containing a list of messages.
    """
    is_ok: bool
    messages: list_[Message] = field(default_factory=list)

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
class APIResponse:
    """ Base API response model with common fields.
    """
    is_ok: bool
    cid: str_ = ''
    details: str_ = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ErrorResponse(APIResponse):
    """ Error response with default is_ok=False.
    """
    is_ok: bool = False

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class NotFoundResponse(ErrorResponse):
    """ 404 Not Found response.
    """
    details: str_ = 'Unknown request path'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class UnauthorizedResponse(ErrorResponse):
    """ 401 Unauthorized response.
    """
    details: str_ = 'Authentication failed'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class BadRequestResponse(ErrorResponse):
    """ 400 Bad Request response.
    """
    details: str_ = 'Invalid request data'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class NotImplementedResponse(ErrorResponse):
    """ 501 Not Implemented response.
    """
    details: str_ = 'Endpoint not implemented'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HealthCheckResponse:
    """ Health check response.
    """
    status: str_ = 'ok'
    timestamp: str_ = ''  # ISO format timestamp

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class User:
    """ Model representing a user with username and password.
    """
    username: str_
    password: str_

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Subscription:
    """ Model representing a subscription to a topic.
    """
    topic_name: str_
    endpoint_name: str_
    sub_key: str_
    creation_time: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Topic:
    """ Model representing a topic.
    """
    name: str_
    creation_time: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

# ################################################################################################################################
# ################################################################################################################################

# Type aliases for collections
users_dict = dict_[str_, str_]
user_list = list_[User]
subscription_list = list_[Subscription]
message_list = list_[Message]
topic_list = list_[Topic]

endpoint_subscriptions = dict_[str_, Subscription]  # endpoint_name -> Subscription
topic_subscriptions = dict_[str_, endpoint_subscriptions]  # topic_name -> {endpoint_name -> Subscription}

# Optional types
message_optional = optional[Message]
subscription_optional = optional[Subscription]
topic_optional = optional[Topic]

# ################################################################################################################################
# ################################################################################################################################
