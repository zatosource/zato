from typing import Any

import logging
import os
from gzip import GzipFile
from hashlib import sha256
from http.client import BAD_REQUEST, FORBIDDEN, INTERNAL_SERVER_ERROR, METHOD_NOT_ALLOWED, NOT_FOUND, UNAUTHORIZED
from io import StringIO
from traceback import format_exc
from regex import compile as regex_compile
from zato.common.api import CHANNEL, CONTENT_TYPE, DATA_FORMAT, HTTP_SOAP, MISC, SEC_DEF_TYPE, SIMPLE_IO, TRACE1, URL_PARAMS_PRIORITY, ZATO_NONE
from zato.common.const import ServiceConst
from zato.common.exception import HTTP_RESPONSES, BackendInvocationError, ServiceMissingException
from zato.common.json_ import dumps
from zato.common.json_internal import loads
from zato.common.marshal_.api import Model, ModelValidationError
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool, utcnow
from zato.common.util.auth import enrich_with_sec_data, extract_basic_auth
from zato.common.util.exception import pretty_format_exception
from zato.common.util.http_ import get_form_data as util_get_form_data, QueryDict
from zato.cy.reqresp.payload import SimpleIOPayload as CySimpleIOPayload
from zato.server.connection.http_soap import BadRequest, ClientHTTPError, Forbidden, MethodNotAllowed, NotFound, TooManyRequests, Unauthorized
from zato.server.groups.ctx import SecurityGroupsCtx
from zato.server.service.internal import AdminService
from zato.broker.client import BrokerClient
from zato.common.typing_ import any_, anydict, anytuple, callable_, dictnone, stranydict, strlist, strstrdict
from zato.server.service import Service
from zato.server.base.parallel import ParallelServer
from zato.server.base.worker import WorkerStore
from zato.server.connection.http_soap.url_data import URLData

class ModuleCtx:
    Channel: Any
    No_URL_Match: Any
    Exception_Separator: Any
    SIO_JSON: Any
    SIO_FORM_DATA: Any
    Dict_Like: Any
    Form_Data_Content_Type: Any

def client_json_error(cid: str, details: any_) -> str: ...

def get_client_error_wrapper(transport: str, data_format: str) -> callable_: ...

class _CachedResponse:
    __slots__: Any
    payload: Any
    content_type: Any
    headers: Any
    status_code: Any
    def __init__(self: Any, payload: any_, content_type: str, headers: stranydict, status_code: int) -> None: ...

class _HashCtx:
    raw_request: Any
    channel_item: Any
    channel_params: Any
    wsgi_environ: Any
    def __init__(self: Any, raw_request: str, channel_item: any_, channel_params: stranydict, wsgi_environ: stranydict) -> None: ...

class RequestDispatcher:
    server: Any
    url_data: Any
    request_handler: Any
    simple_io_config: Any
    return_tracebacks: Any
    default_error_message: Any
    http_methods_allowed: Any
    def __init__(self: Any) -> None: ...
    def dispatch(self: Any, cid: str, req_timestamp: str, wsgi_environ: stranydict, worker_store: WorkerStore, user_agent: str, remote_addr: str, _needs_details: Any = ...) -> any_: ...
    def check_security_via_groups(self: Any, cid: str, channel_name: str, security_groups_ctx: SecurityGroupsCtx, wsgi_environ: stranydict) -> None: ...

class RequestHandler:
    server: Any
    def __init__(self: Any, server: ParallelServer) -> None: ...
    def _set_response_data(self: Any, service: Service, **kwargs: any_) -> None: ...
    def _get_flattened(self: Any, params: str) -> anydict: ...
    def create_channel_params(self: Any, path_params: strstrdict, channel_item: any_, wsgi_environ: stranydict, raw_request: str, post_data: dictnone = ...) -> strstrdict: ...
    def get_response_from_cache(self: Any, service: Service, raw_request: str, channel_item: any_, channel_params: stranydict, wsgi_environ: stranydict) -> anytuple: ...
    def set_response_in_cache(self: Any, channel_item: any_, key: str, response: any_) -> None: ...
    def handle(self: Any, cid: str, url_match: any_, channel_item: any_, wsgi_environ: stranydict, raw_request: str, worker_store: WorkerStore, simple_io_config: stranydict, post_data: dictnone, path_info: str, channel_params: stranydict, zato_response_headers_container: stranydict) -> any_: ...
    def _needs_admin_response(self: Any, service_instance: Service, service_invoker_name: str = ...) -> bool: ...
    def set_payload(self: Any, response: any_, data_format: str, transport: str, service_instance: Service) -> None: ...
    def set_content_type(self: Any, response: any_, data_format: str) -> None: ...
