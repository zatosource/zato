from typing import Any, TYPE_CHECKING

import os
from logging import getLogger
from traceback import format_exc
from zato.common.typing_ import any_
from zato.common.util.auth import check_basic_auth, extract_basic_auth
from werkzeug.routing import Map, Rule
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST, Info
from prometheus_client.platform_collector import PlatformCollector
from prometheus_client.process_collector import ProcessCollector
from zato.broker.client import BrokerClient
from zato.common.api import PubSub
from zato.common.util.api import as_bool, new_cid_pubsub, utcnow
from zato.common.pubsub.backend.rest_backend import RESTBackend
from zato.common.typing_ import any_, strdict, strdictnone

_default_priority = PubSub.Message.Priority_Default
_default_expiration = PubSub.Message.Default_Expiration

class ModuleCtx:
    Exchange_Name: Any

class UnauthorizedException(Exception):
    cid: Any
    def __init__(self: Any, cid: str, *args: any_, **kwargs: any_) -> None: ...

class BadRequestException(Exception):
    cid: Any
    message: Any
    def __init__(self: Any, cid: str, message: str, *args: any_, **kwargs: any_) -> None: ...

class BaseServer:
    server_type: str
    host: Any
    port: Any
    users: Any
    broker_client: BrokerClient
    backend: RESTBackend
    topics: Any
    subs_by_topic: Any
    url_map: Map
    def __init__(self: Any, host: str, port: int, should_init_broker_client: bool = ...) -> None: ...
    def _authenticate(self: Any, cid: str, environ: strdict, users: strdictnone = ...) -> strnone: ...
    def init_broker_client(self: Any) -> None: ...
    def _load_users(self: Any, cid: str) -> None: ...
    def _load_topics(self: Any, cid: str) -> None: ...
    def _load_subscriptions(self: Any, cid: str) -> None: ...
    def _load_permissions(self: Any, cid: str) -> int: ...
    def create_user(self: Any, cid: str, sec_name: str, username: str, password: str) -> None: ...
    def edit_user(self: Any, cid: str, old_sec_name: str, new_sec_name: str, old_username: str, new_username: str) -> None: ...
    def get_user_config(self: Any, username: str) -> strdict: ...
    def setup(self: Any) -> None: ...
    def on_metrics(self: Any, cid: str, environ: anydict, start_response: any_) -> bytes: ...
