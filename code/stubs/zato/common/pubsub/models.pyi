from typing import Any

from dataclasses import dataclass, field
from http.client import BAD_REQUEST, METHOD_NOT_ALLOWED, NOT_IMPLEMENTED, OK, UNAUTHORIZED
from typing import TypedDict
from zato.common.api import PubSub
from zato.common.typing_ import union_
from datetime import datetime
from zato.common.typing_ import any_, dataclass, field, list_

class PubMessage(TypedDict):
    data: any_
    priority: int
    expiration: int
    correl_id: str
    in_reply_to: str
    ext_client_id: str
    pub_time: str

class PubResponse(TypedDict):
    is_ok: bool
    msg_id: str
    cid: str
    details: str
    status: int | str

class Message(TypedDict):
    data: any_
    topic_name: str
    msg_id: str
    correl_id: str
    in_reply_to: str
    priority: int
    mime_type: str
    ext_client_id: str
    pub_time_iso: str
    ext_pub_time_iso: str
    recv_time_iso: str
    expiration: int
    expiration_time_iso: str
    size: int
    sub_key: str

class MessagesResponse(TypedDict):
    is_ok: bool
    messages: list_[Message]
    status: int | str

class StatusResponse(TypedDict):
    is_ok: bool
    status: int | str

class APIResponse(TypedDict):
    is_ok: bool
    cid: str
    details: str
    status: int | str
    msg_id: str
    meta: dict
    data: any_
    messages: list_
    message_count: int

class ErrorResponse(APIResponse):
    is_ok: bool

class UnauthorizedResponse(ErrorResponse):
    details: str
    status: int | str

class BadRequestResponse(ErrorResponse):
    details: str
    status: int | str

class MethodNotAllowedResponse(ErrorResponse):
    details: str
    status: int | str

class NotImplementedResponse(ErrorResponse):
    details: str
    status: int | str

class HealthCheckResponse(TypedDict):
    status: int | str

class User:
    username: str
    password: str

class Subscription:
    topic_name: str
    username: str
    sub_key: str
    creation_time: datetime
    is_delivery_active: bool
    is_pub_active: bool
    is_pub_enabled: bool
    is_delivery_enabled: bool

class Topic:
    name: str
    creation_time: datetime
    is_active: bool
