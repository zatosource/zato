# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.api import PubSub
from zato.common.typing_ import any_, dataclass, dict_, field, list_, optional, str
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class PubMessage:
    """ Model representing a message to be published to a topic.
    """
    data: any_
    priority: 'int' = PubSub.Message.Default_Priority
    expiration: 'int' = PubSub.Message.Default_Expiration
    correl_id: 'str' = ''
    in_reply_to: 'str' = ''
    ext_client_id: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class PubResponse:
    """ Response model for publish operations.
    """
    is_ok: 'bool'
    msg_id: 'str' = ''
    cid: 'str' = ''
    details: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Message:
    """ Model for a single message as returned by retrieve/read operations.
    """
    data: any_
    topic_name: 'str'
    msg_id: 'str'
    correl_id: 'str' = ''
    in_reply_to: 'str' = ''
    priority: 'int' = PubSub.Message.Default_Priority
    mime_type: 'str' = 'application/json'
    ext_client_id: 'str' = ''
    pub_time_iso: 'str' = ''
    ext_pub_time_iso: 'str' = ''
    recv_time_iso: 'str' = ''
    expiration: 'int' = PubSub.Message.Default_Expiration
    expiration_time_iso: 'str' = ''
    size: 'int' = 0
    delivery_count: 'int' = 0
    sub_key: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class MessagesResponse:
    """ Response model containing a list of messages.
    """
    is_ok: 'bool'
    messages: list_[Message] = field(default_factory=list)

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class SimpleResponse:
    """ Generic response model with just an is_ok field.
    """
    is_ok: 'bool'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class APIResponse:
    """ Base API response model with common fields.
    """
    is_ok: 'bool'
    cid: 'str' = ''
    details: 'str' = ''
    http_status: 'str' = '200 OK'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ErrorResponse(APIResponse):
    """ Error response with default is_ok=False.
    """
    is_ok: 'bool' = False

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class NotFoundResponse(ErrorResponse):
    """ 404 Not Found response.
    """
    details: 'str' = 'Unknown request path'
    http_status: 'str' = '404 Not Found'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class UnauthorizedResponse(ErrorResponse):
    """ 401 Unauthorized response.
    """
    details: 'str' = 'Authentication failed'
    http_status: 'str' = '401 Unauthorized'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class BadRequestResponse(ErrorResponse):
    """ 400 Bad Request response.
    """
    details: 'str' = 'Invalid request data'
    http_status: 'str' = '400 Bad Request'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class NotImplementedResponse(ErrorResponse):
    """ 501 Not Implemented response.
    """
    details: 'str' = 'Endpoint not implemented'
    http_status: 'str' = '501 Not Implemented'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class HealthCheckResponse:
    """ Health check response.
    """
    status: 'str' = 'ok'
    http_status: 'str' = '200 OK'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class User:
    """ Model representing a user with username and password.
    """
    username: 'str'
    password: 'str'

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Subscription:
    """ Model representing a subscription to a topic.
    """
    topic_name: 'str'
    endpoint_name: 'str'
    sub_key: 'str'
    creation_time: 'datetime' = field(default_factory=utcnow)
    is_active: 'bool' = True

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class Topic:
    """ Model representing a topic.
    """
    name: 'str'
    creation_time: 'datetime' = field(default_factory=sutcnow)
    is_active: 'bool' = True

# ################################################################################################################################
# ################################################################################################################################

# Type aliases for collections
users_dict = dict_[str, str]
user_list = list_[User]
subscription_list = list_[Subscription]
message_list = list_[Message]
topic_list = list_[Topic]

endpoint_subscriptions = dict_[str, Subscription]  # endpoint_name -> Subscription
topic_subscriptions = dict_[str, endpoint_subscriptions]  # topic_name -> {endpoint_name -> Subscription}

# Optional types
message_optional = optional[Message]
subscription_optional = optional[Subscription]
topic_optional = optional[Topic]

# ################################################################################################################################
# ################################################################################################################################
