from typing import Any

import os
import gc
import time
import threading
import psutil
from http.client import BAD_REQUEST, INTERNAL_SERVER_ERROR, METHOD_NOT_ALLOWED, NOT_IMPLEMENTED, OK, responses as http_responses, UNAUTHORIZED
import orjson
from logging import getLogger
from traceback import format_exc
from yaml import dump as yaml_dump
from prometheus_client import Histogram, Gauge, Counter
import requests
from requests.auth import HTTPBasicAuth
from werkzeug.exceptions import MethodNotAllowed, NotFound
from werkzeug.wrappers import Request
from zato.common.api import PubSub
from zato.common.util.api import as_bool, new_cid_pubsub
from zato.common.pubsub.models import APIResponse, _base_response, HealthCheckResponse
from zato.common.pubsub.server.base import BaseServer
from zato.common.pubsub.util import get_broker_config
from zato.common.typing_ import any_, anydict, dict_, list_
from zato.common.pubsub.util import validate_topic_name

class UnauthorizedException(Exception):
    cid: Any
    def __init__(self: Any, cid: str, *args: any_, **kwargs: any_) -> None: ...

class BadRequestException(Exception):
    cid: Any
    message: Any
    def __init__(self: Any, cid: str, message: str, *args: any_, **kwargs: any_) -> None: ...

class BaseRESTServer(BaseServer):
    _broker_config: get_broker_config
    _broker_auth: HTTPBasicAuth
    _broker_api_base_url: Any
    def __init__(self: Any, host: str, port: int, should_init_broker_client: bool = ...) -> None: ...
    def authenticate(self: Any, cid: str, environ: anydict) -> str: ...
    def _parse_json(self: Any, cid: str, request: Request) -> dict_: ...
    def _json_response(self: Any, start_response: any_, data: _base_response) -> list_[bytes]: ...
    def _call(self: Any, environ: anydict, start_response: any_) -> list_[bytes]: ...
    def __call__(self: Any, environ: anydict, start_response: any_) -> list_[bytes]: ...
    def on_status_check(self: Any, cid: str, environ: anydict, start_response: any_) -> HealthCheckResponse: ...
    def on_admin_diagnostics(self: Any, cid: str, environ: anydict, start_response: any_) -> APIResponse: ...
    def list_connections(self: Any, cid: str, management_port: int = ...) -> dict_: ...
    def on_subscribe(self: Any, cid: str, environ: anydict, start_response: any_, topic_name: str) -> APIResponse: ...
    def on_unsubscribe(self: Any, cid: str, environ: anydict, start_response: any_, topic_name: str) -> APIResponse: ...
    def _wsgi_wrapper(self: Any, environ: Any, start_response: Any) -> None: ...
    def run(self: Any) -> None: ...
