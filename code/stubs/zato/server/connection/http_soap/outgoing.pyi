from typing import Any

import os
from contextvars import ContextVar
from copy import deepcopy
from http.client import OK
from io import StringIO
from logging import DEBUG, getLogger
from time import sleep
from traceback import format_exc
from urllib.parse import urlencode
from ddtrace import tracer as datadog_tracer
from requests import Response as _RequestsResponse
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout as RequestsTimeout
from requests.sessions import Session as RequestsSession
from requests_ntlm import HttpNtlmAuth
from requests_toolbelt import MultipartEncoder
from prometheus_client import Counter, Histogram
from zato.common.api import ContentType, CONTENT_TYPE, DATA_FORMAT, NotGiven, SEC_DEF_TYPE, URL_TYPE
from zato.common.exception import BadRequest, Inactive, BackendInvocationError
from zato.common.json_ import dumps, loads
from zato.common.marshal_.api import extract_model_class, is_list, Model
from zato.common.typing_ import cast_
from zato.common.util.api import get_component_name, utcnow
from zato.common.util.config import extract_param_placeholders
from zato.common.util.open_ import open_rb
from sqlalchemy.orm.session import Session as SASession
from zato.common.bearer_token import BearerTokenInfoResult
from zato.common.typing_ import any_, callnone, dictnone, list_, stranydict, strdictnone, strstrdict, type_
from zato.server.base.parallel import ParallelServer
from zato.server.config import ConfigDict
from prometheus_client import REGISTRY

class Response(_RequestsResponse):
    data: strdictnone
    zato_method: str
    zato_address: str
    zato_qs_params: strdictnone

class HTTPSAdapter(HTTPAdapter):
    def clear_pool(self: Any) -> None: ...

class BaseHTTPSOAPWrapper:
    auth: Any
    config: Any
    config_no_sensitive: deepcopy
    RequestsSession: Any
    server: cast_
    session: RequestsSession
    https_adapter: HTTPSAdapter
    _component_name: get_component_name
    default_content_type: self.get_default_content_type
    address: Any
    path_params: Any
    base_headers: Any
    sec_type: Any
    soap: Any
    def __init__(self: Any, config: Any, _requests_session: Any = ..., server: Any = ...) -> None: ...
    def _push_metrics(self: Any, start_time: Any, status_code: Any) -> None: ...
    def set_auth(self: Any) -> None: ...
    def _get_auth(self: Any) -> any_: ...
    def invoke_http(self: Any, cid: str, method: str, address: str, data: str, headers: strstrdict, hooks: any_, *args: any_, **kwargs: any_) -> _RequestsResponse: ...
    def _get_bearer_token_auth(self: Any, sec_def_name: str, scopes: str, data_format: str) -> BearerTokenInfoResult: ...
    def ping(self: Any, cid: str, return_response: bool = ..., log_verbose: bool = ...) -> any_: ...
    def get_default_content_type(self: Any) -> str: ...
    def _create_headers(self: Any, cid: str, user_headers: strstrdict, now: str = ...) -> strstrdict: ...
    def set_address_data(self: Any) -> None: ...

class HTTPSOAPWrapper(BaseHTTPSOAPWrapper):
    __repr__: Any
    impl: Any
    send: Any
    server: Any
    def __init__(self: Any, server: Any, config: Any, requests_module: Any = ...) -> None: ...
    def __str__(self: Any) -> str: ...
    def format_address(self: Any, cid: str, params: stranydict) -> tuple[str, stranydict]: ...
    def _impl(self: Any) -> RequestsSession: ...
    def _enforce_is_active(self: Any) -> None: ...
    def _soap_data(self: Any, data: str | bytes, headers: stranydict) -> tuple[any_, stranydict]: ...
    def http_request(self: Any, method: str, cid: str, data: any_ = ..., params: dictnone = ..., *args: any_, **kwargs: any_) -> Response: ...
    def get(self: Any, cid: str, params: dictnone = ..., *args: any_, **kwargs: any_) -> Response: ...
    def delete(self: Any, cid: str, data: any_ = ..., params: dictnone = ..., *args: any_, **kwargs: any_) -> Response: ...
    def options(self: Any, cid: str, data: any_ = ..., params: dictnone = ..., *args: any_, **kwargs: any_) -> Response: ...
    def post(self: Any, cid: str, data: any_ = ..., params: dictnone = ..., *args: any_, **kwargs: any_) -> Response: ...
    def put(self: Any, cid: str, data: str = ..., params: dictnone = ..., *args: any_, **kwargs: any_) -> Response: ...
    def patch(self: Any, cid: str, data: str = ..., params: dictnone = ..., *args: any_, **kwargs: any_) -> Response: ...
    def upload(self: Any, cid: Any, item: Any, field_name: Any = ..., mime_type: Any = ...) -> Response: ...
    def rest_call(self: Any) -> any_: ...
