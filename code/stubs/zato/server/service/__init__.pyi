from typing import Any

from __future__ import annotations
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from http.client import BAD_REQUEST, METHOD_NOT_ALLOWED, OK
from inspect import isclass
from re import findall
from traceback import format_exc
from typing import TYPE_CHECKING
from bunch import bunchify
from lxml.etree import _Element as EtreeElement
from lxml.objectify import ObjectifiedElement
from zato.common.py23_ import maxint
from zato.bunch import Bunch
from zato.common.api import BROKER, CHANNEL, DATA_FORMAT, NotGiven, PARAMS_PRIORITY, RESTAdapterResponse, zato_no_op_marker
from zato.common.exception import Inactive, Reportable, ZatoException
from zato.common.facade import SecurityFacade
from zato.common.json_internal import dumps
from zato.common.monitoring.logger_ import DatadogLogger
from zato.common.monitoring.metrics import ServiceMetrics
from zato.common.typing_ import cast_, type_
from zato.common.util.api import make_repr, new_cid, payload_from_request, service_name_from_impl, spawn_greenlet, uncamelify
from zato.common.util.python_ import get_module_name_by_path
from zato.common.util.time_ import utcnow
from zato.server.commands import CommandsFacade
from zato.server.connection.cache import CacheAPI
from zato.server.connection.email import EMailAPI
from zato.server.connection.facade import KeysightContainer, RESTFacade, SchedulerFacade
from zato.server.connection.http_soap.outgoing import current_datadog_cid, current_datadog_context, current_datadog_env_name, current_datadog_process_name, current_datadog_service_name
from zato.server.connection.search import SearchAPI
from zato.server.pattern.api import FanOut
from zato.server.pattern.api import InvokeRetry
from zato.server.pattern.api import ParallelExec
from zato.server.service.reqresp import AMQPRequestData, Cloud, Outgoing, Request
from zato.cy.reqresp.payload import SimpleIOPayload
from zato.cy.reqresp.response import Response
from zato.common.ext.dataclasses import dataclass
from zato.common.marshal_.api import Model, ModelCtx
from zato.server.connection.cloud.microsoft_dataverse import DataverseClient
from zato.simpleio import AsIs, CSV, Bool, Date, DateTime, Dict, Decimal, DictList, Elem as SIOElem, Float, Int, List, Opaque, Text, UTC, UUID
from ddtrace._trace.context import Context as DatadogContext
from logging import Logger
from zato.broker.client import BrokerClient
from zato.common.audit import AuditPII
from zato.common.crypto.api import ServerCryptoManager
from zato.common.odb.api import ODBManager
from zato.common.rules.api import RulesManager
from zato.common.typing_ import any_, anydict, anydictnone, boolnone, callable_, callnone, dictnone, intnone, listnone, modelnone, strdict, strdictnone, strstrdict, strnone, strlist
from zato.common.util.time_ import TimeUtil
from zato.distlock import Lock
from zato.server.connection.ftp import FTPStore
from zato.server.connection.http_soap.outgoing import RESTWrapper
from zato.server.base.worker import WorkerStore
from zato.server.base.parallel import ParallelServer
from zato.server.config import ConfigDict, ConfigStore
from zato.simpleio import CySimpleIO

def call_hook_no_service(hook: callable_) -> None: ...

def call_hook_with_service(hook: callable_, service: Service) -> None: ...

class ModuleCtx:
    HTTP_Channels: Any
    Channel_Scheduler: Any
    Channel_Service: Any
    Pattern_Call_Channels: Any

class AsyncCtx:
    calling_service: str
    service_name: str
    cid: str
    data: str
    data_format: str
    zato_ctx: any_
    environ: anydict
    callback: listnone

class ChannelInfo:
    __slots__: Any
    def __init__(self: Any, id: intnone, name: strnone, type: strnone, data_format: strnone, is_internal: boolnone, match_target: any_, security: ChannelSecurityInfo, impl: any_, gateway_service_list: strnone = ...) -> None: ...
    def __repr__(self: Any) -> str: ...
    def to_dict(self: Any, needs_impl: bool = ...) -> strdict: ...

class ChannelSecurityInfo:
    __slots__: Any
    def __init__(self: Any, id: intnone, name: strnone, type: strnone, username: strnone, impl: any_) -> None: ...
    def to_dict(self: Any, needs_impl: bool = ...) -> strdict: ...

class AMQPFacade:
    __slots__: Any

class PatternsFacade:
    __slots__: Any
    def __init__(self: Any, invoking_service: Service, cache: anydict, lock: RLock) -> None: ...

class Service:
    process_name: str
    rest: RESTFacade
    schedule: SchedulerFacade
    security: SecurityFacade
    call_hooks: bool
    _filter_by: Any
    enforce_service_invokes: bool
    invokes: Any
    http_method_handlers: Any
    cloud: Any
    odb: ODBManager
    static_config: Bunch
    email: EMailAPI | None
    search: SearchAPI | None
    patterns: PatternsFacade | None
    amqp: Any
    commands: Any
    _worker_store: WorkerStore
    _worker_config: ConfigStore
    _has_before_job_hooks: bool
    _has_after_job_hooks: bool
    _before_job_hooks: Any
    _after_job_hooks: Any
    has_sio: bool
    _sio: CySimpleIO
    crypto: ServerCryptoManager
    audit_pii: AuditPII
    keysight: KeysightContainer
    server: ParallelServer
    broker_client: BrokerClient
    time: TimeUtil
    chan: ChannelInfo
    channel: ChannelInfo
    invocation_time: datetime
    handle_return_time: datetime
    processing_time_raw: timedelta
    processing_time: float
    needs_datadog_logging: bool
    datadog_context: DatadogContext
    metrics: ServiceMetrics
    rules: RulesManager
    component_enabled_odoo: bool
    component_enabled_email: bool
    component_enabled_search: bool
    cache: CacheAPI
    spawn: Any
    def __init__(self: Any, *ignored_args: any_, **ignored_kwargs: any_) -> None: ...
    @staticmethod
    def get_name_static(class_: type[Service]) -> str: ...
    @classmethod
    def get_name(class_: type_[Service]) -> str: ...
    @classmethod
    def get_impl_name(class_: type_[Service]) -> str: ...
    @staticmethod
    def convert_impl_name(name: str) -> str: ...
    @classmethod
    def zato_set_module_name(class_: type_[Service], path: str) -> str: ...
    @classmethod
    def add_http_method_handlers(class_: type_[Service]) -> None: ...
    def _init(self: Any, may_have_wsgi_environ: bool = ...) -> None: ...
    def set_response_data(self: Any, service: Service, **kwargs: any_) -> any_: ...
    def _invoke(self: Any, service: Service, channel: str) -> None: ...
    def extract_target(self: Any, name: str) -> tuple[str, str]: ...
    def update_handle(self: Any, set_response_func: Any, service: Any, raw_request: Any, channel: Any, data_format: Any, transport: Any, server: Any, broker_client: Any, worker_store: Any, cid: Any, simple_io_config: Any, *args: any_, **kwargs: any_) -> any_: ...
    def invoke_by_impl_name(self: Any, impl_name: Any, payload: Any = ..., channel: Any = ..., data_format: Any = ..., transport: Any = ..., serialize: Any = ..., as_bunch: Any = ..., timeout: Any = ..., raise_timeout: Any = ..., **kwargs: any_) -> any_: ...
    def invoke(self: Any, zato_name: any_, *args: any_, **kwargs: any_) -> any_: ...
    def invoke_by_id(self: Any, service_id: int, *args: any_, **kwargs: any_) -> any_: ...
    def invoke_async(self: Any, name: Any, payload: Any = ..., channel: Any = ..., data_format: Any = ..., transport: Any = ..., expiration: Any = ..., to_json_string: Any = ..., cid: Any = ..., callback: Any = ..., zato_ctx: Any = ..., environ: Any = ...) -> str: ...
    def _invoke_async(self: Any, ctx: Any, channel: Any, _async_callback: Any = ...) -> None: ...
    def publish(self: Any, topic: str, msg: any_) -> None: ...
    def handle(self: Any) -> None: ...
    def lock(self: Any, name: str = ..., *args: any_, **kwargs: any_) -> Lock: ...
    def sleep(self: Any, timeout: int = ...) -> None: ...
    def accept(self: Any, _zato_no_op_marker: any_ = ...) -> bool: ...
    def run_in_thread(self: Any, *args: any_, **kwargs: any_) -> any_: ...
    @classmethod
    def before_add_to_store(cls: Any, logger: Logger) -> bool: ...
    def before_job(self: Any, _zato_no_op_marker: Any = ...) -> None: ...
    def before_one_time_job(self: Any, _zato_no_op_marker: Any = ...) -> None: ...
    def before_interval_based_job(self: Any, _zato_no_op_marker: Any = ...) -> None: ...
    def before_handle(self: Any, _zato_no_op_marker: Any = ..., *args: Any, **kwargs: Any) -> None: ...
    def after_job(self: Any, _zato_no_op_marker: Any = ...) -> None: ...
    def after_one_time_job(self: Any, _zato_no_op_marker: Any = ...) -> None: ...
    def after_interval_based_job(self: Any, _zato_no_op_marker: Any = ...) -> None: ...
    def after_handle(self: Any, _zato_no_op_marker: Any = ...) -> None: ...
    def finalize_handle(self: Any, _zato_no_op_marker: Any = ...) -> None: ...
    @staticmethod
    def after_add_to_store(logger: Any) -> None: ...
    def validate_input(self: Any, _zato_no_op_marker: Any = ...) -> None: ...
    def validate_output(self: Any, _zato_no_op_marker: Any = ...) -> None: ...
    def get_request_hash(self: Any, _zato_no_op_marker: Any = ..., *args: Any, **kwargs: Any) -> None: ...
    @staticmethod
    def update(service: Any, channel_type: Any, server: Any, broker_client: Any, _ignored: Any, cid: Any, payload: Any, raw_request: Any, transport: Any = ..., simple_io_config: Any = ..., data_format: Any = ..., wsgi_environ: Any = ..., job_type: Any = ..., channel_params: Any = ..., merge_channel_params: Any = ..., params_priority: Any = ..., in_reply_to: Any = ..., environ: Any = ..., init: Any = ..., channel_info: Any = ..., channel_item: Any = ..., _AMQP: Any = ...) -> None: ...
    def new_instance(self: Any, service_name: str, *args: any_, **kwargs: any_) -> Service: ...

class _Hook(Service):
    _hook_func_name: strdict
    def handle(self: Any) -> None: ...

class RESTAdapter(Service):
    model: Any
    conn_name: Any
    auth_scopes: Any
    sec_def_name: Any
    log_response: Any
    map_response: Any
    get_conn_name: Any
    get_auth_scopes: Any
    get_path_params: Any
    get_method: Any
    get_request: Any
    get_headers: Any
    get_query_string: Any
    get_auth_bearer: Any
    get_sec_def_name: Any
    needs_raw_response: Any
    max_retries: Any
    retry_sleep_time: Any
    retry_backoff_threshold: Any
    retry_backoff_multiplier: Any
    has_query_string_id: Any
    query_string_id_param: Any
    has_json_id: Any
    json_id_param: Any
    method: Any
    def rest_call(self: Any, conn_name: Any) -> None: ...
    def handle(self: Any) -> None: ...

class BusinessCentralAdapter(Service):
    model: Any
    conn_name: Any
    base_url: Any
    endpoint: Any
    def _find_placeholders(self: Any, text: str, pattern: str = ...) -> strlist: ...
    def _replace_placeholders_by_input(self: Any, text: str, placeholders: strlist) -> str: ...
    def _replace_placeholders_by_file(self: Any, text: str, placeholder: str) -> str: ...
    def _replace_placeholders(self: Any, text: str) -> str: ...
    def get_model(self: Any) -> any_: ...
    def get_conn_name(self: Any) -> str: ...
    def get_base_url(self: Any) -> str: ...
    def _invoke_business_central(self: Any, endpoint: str, base_url: str | None) -> anydictnone: ...
    def handle(self: Any) -> None: ...

class PubSubHookMessage:
    phase: str
    message: any_

class PubSubHook(Service):
    ...

class PubSubMessage:
    msg_id: str
    correl_id: str
    data: any_
    size: int
    publisher: str
    pub_time_iso: str
    recv_time_iso: str
    priority: int
    delivery_count: int
    expiration: int
    expiration_time_iso: str
    ext_client_id: str
    in_reply_to: str
    sub_key: str
    topic_name: str
