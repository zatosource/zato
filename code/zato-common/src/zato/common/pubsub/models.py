# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from dataclasses import dataclass, field
from http.client import BAD_REQUEST, METHOD_NOT_ALLOWED, NOT_IMPLEMENTED, OK, UNAUTHORIZED
from typing import TypedDict

# Zato
from zato.common.api import PubSub
from zato.common.typing_ import union_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from datetime import datetime
    from zato.common.typing_ import any_, dataclass, field, list_

# ################################################################################################################################
# ################################################################################################################################

class PubMessage(TypedDict, total=False):
    """ Model representing a message to be published to a topic.
    """
    data: 'any_'
    priority: 'int'  # Default: PubSub.Message.Priority_Default
    expiration: 'int'  # Default: PubSub.Message.Default_Expiration
    correl_id: 'str'  # Default: ''
    in_reply_to: 'str'  # Default: ''
    ext_client_id: 'str'  # Default: ''
    pub_time: 'str'  # Default: ''

# ################################################################################################################################
# ################################################################################################################################

class PubResponse(TypedDict, total=False):
    """ Response model for publish operations.
    """
    is_ok: 'bool'
    msg_id: 'str'  # Default: ''
    cid: 'str'  # Default: ''
    details: 'str'  # Default: ''
    status: 'str'  # Default: OK

# ################################################################################################################################
# ################################################################################################################################

class Message(TypedDict, total=False):
    """ Model for a single message as returned by retrieve/read operations.
    """
    data: 'any_'
    topic_name: 'str'
    msg_id: 'str'
    correl_id: 'str'  # Default: ''
    in_reply_to: 'str'  # Default: ''
    priority: 'int'  # Default: PubSub.Message.Priority_Default
    mime_type: 'str'  # Default: 'application/json'
    ext_client_id: 'str'  # Default: ''
    pub_time_iso: 'str'  # Default: ''
    ext_pub_time_iso: 'str'  # Default: ''
    recv_time_iso: 'str'  # Default: ''
    expiration: 'int'  # Default: PubSub.Message.Default_Expiration
    expiration_time_iso: 'str'  # Default: ''
    size: 'int'  # Default: 0
    sub_key: 'str'  # Default: ''

# ################################################################################################################################
# ################################################################################################################################

class MessagesResponse(TypedDict, total=False):
    """ Response model containing a list of messages.
    """
    is_ok: 'bool'
    messages: 'list_[Message]'  # Default: []
    status: 'str'  # Default: OK

# ################################################################################################################################
# ################################################################################################################################

class StatusResponse(TypedDict, total=False):
    is_ok: 'bool'
    status: 'str'  # Default: OK

# ################################################################################################################################
# ################################################################################################################################

class APIResponse(TypedDict, total=False):
    """ Base API response model with common fields.
    """
    is_ok: 'bool'
    cid: 'str'
    details: 'str'  # Default: ''
    status: 'str'  # Default: OK
    msg_id: 'str'  # Default: ''
    meta: 'dict'
    data: 'any_'  # Default: None
    messages: 'list_'  # Default: []
    message_count: 'int'  # Default: 0

# ################################################################################################################################
# ################################################################################################################################

class ErrorResponse(APIResponse):
    """ Error response with default is_ok=False.
    """
    is_ok: 'bool'  # Default: False

# ################################################################################################################################
# ################################################################################################################################

class UnauthorizedResponse(ErrorResponse):
    """ 401 Unauthorized response.
    """
    details: 'str'  # Default: 'Authentication failed'
    status: 'str'  # Default: UNAUTHORIZED

# ################################################################################################################################
# ################################################################################################################################

class BadRequestResponse(ErrorResponse):
    """ 400 Bad Request response.
    """
    details: 'str'  # Default: 'Invalid request data'
    status: 'str'  # Default: BAD_REQUEST

# ################################################################################################################################
# ################################################################################################################################

class MethodNotAllowedResponse(ErrorResponse):
    """ 405 Method Not Allowed response.
    """
    details: 'str'  # Default: 'Method not allowed'
    status: 'str'  # Default: METHOD_NOT_ALLOWED

# ################################################################################################################################
# ################################################################################################################################

class NotImplementedResponse(ErrorResponse):
    """ 501 Not Implemented response.
    """
    details: 'str'  # Default: 'Endpoint not implemented'
    status: 'str'  # Default: NOT_IMPLEMENTED

# ################################################################################################################################
# ################################################################################################################################

class HealthCheckResponse(TypedDict, total=False):
    """ Health check response.
    """
    status: 'str'  # Default: 'ok' or OK

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
    topic_name: 'str' = ''
    username: 'str' = ''
    sub_key: 'str' = ''
    creation_time: 'datetime'
    is_active: 'bool' = True

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Topic:
    """ Model representing a topic.
    """
    name: 'str'
    creation_time: 'datetime'
    is_active: 'bool' = True

# ################################################################################################################################
# ################################################################################################################################

# Type aliases for collections
users_dict = 'dict_[str, str]'
user_list = 'list_[User]'
subscription_list = 'list_[Subscription]'
message_list = 'list_[Message]'
topic_list = 'list_[Topic]'

# Optional types
message_optional = 'optional[Message]'
subscription_optional = 'optional[Subscription]'
topic_optional = 'optional[Topic]'

# Union type for all response types
_base_response = union_[
    APIResponse,
    ErrorResponse,
    UnauthorizedResponse,
    BadRequestResponse,
    MethodNotAllowedResponse,
    NotImplementedResponse,
    HealthCheckResponse,
    StatusResponse,
    MessagesResponse,
    PubResponse
]

# ################################################################################################################################
# ################################################################################################################################
