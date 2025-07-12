# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass, field

# Zato
from zato.common.api import PubSub
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, dataclass, dict_, field, list_, optional

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PubMessage:
    """ Model representing a message to be published to a topic.
    """
    data: 'any_'
    priority: 'int' = PubSub.Message.Default_Priority
    expiration: 'int' = PubSub.Message.Default_Expiration
    correl_id: 'str' = ''
    in_reply_to: 'str' = ''
    ext_client_id: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PubResponse:
    """ Response model for publish operations.
    """
    is_ok: 'bool'
    msg_id: 'str' = ''
    cid: 'str' = ''
    details: 'str' = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Message:
    """ Model for a single message as returned by retrieve/read operations.
    """
    data: 'any_'
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

@dataclass(init=False)
class MessagesResponse:
    """ Response model containing a list of messages.
    """
    is_ok: 'bool'
    messages: 'list_[Message]' = field(default_factory=list)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SimpleResponse:
    """ Generic response model with just an is_ok field.
    """
    is_ok: 'bool'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class APIResponse:
    """ Base API response model with common fields.
    """
    is_ok: 'bool'
    cid: 'str'
    details: 'str' = ''
    status: 'str' = '200 OK'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ErrorResponse(APIResponse):
    """ Error response with default is_ok=False.
    """
    is_ok: 'bool' = False

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class UnauthorizedResponse(ErrorResponse):
    """ 401 Unauthorized response.
    """
    details: 'str' = 'Authentication failed'
    status: 'str' = '401 Unauthorized'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class BadRequestResponse(ErrorResponse):
    """ 400 Bad Request response.
    """
    details: 'str' = 'Invalid request data'
    status: 'str' = '400 Bad Request'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class NotImplementedResponse(ErrorResponse):
    """ 501 Not Implemented response.
    """
    details: 'str' = 'Endpoint not implemented'
    status: 'str' = '501 Not Implemented'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class HealthCheckResponse:
    """ Health check response.
    """
    status: 'str' = 'ok'
    status: 'str' = '200 OK'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class User:
    """ Model representing a user with username and password.
    """
    username: 'str'
    password: 'str'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
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

@dataclass(init=False)
class Topic:
    """ Model representing a topic.
    """
    name: 'str'
    creation_time: 'datetime' = field(default_factory=utcnow)
    is_active: 'bool' = True

# ################################################################################################################################
# ################################################################################################################################

# Type aliases for collections
users_dict = 'dict_[str, str]'
user_list = 'list_[User]'
subscription_list = 'list_[Subscription]'
message_list = 'list_[Message]'
topic_list = 'list_[Topic]'

endpoint_subscriptions = 'dict_[str, Subscription]'  # endpoint_name -> Subscription
topic_subscriptions = 'dict_[str, endpoint_subscriptions]'  # topic_name -> {endpoint_name -> Subscription}

# Optional types
message_optional = 'optional[Message]'
subscription_optional = 'optional[Subscription]'
topic_optional = 'optional[Topic]'

# ################################################################################################################################
# ################################################################################################################################
