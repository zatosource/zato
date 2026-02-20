from typing import Any, TYPE_CHECKING

import logging
import os
import shutil
from copy import deepcopy
from datetime import timedelta
from json import loads
from logging import INFO, WARN
from pathlib import Path
from platform import system as platform_system
from random import seed as random_seed
from traceback import format_exc
from uuid import uuid4
from bunch import bunchify
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from zato.broker import BrokerMessageReceiver
from zato.broker.client import BrokerClient
from zato.bunch import Bunch
from zato.common.api import API_Key, DATA_FORMAT, EnvFile, EnvVariable, HotDeploy, SERVER_STARTUP, SEC_DEF_TYPE, SERVER_UP_STATUS, ZATO_ODB_POOL_NAME
from zato.common.audit import audit_pii
from zato.common.bearer_token import BearerTokenManager
from zato.common.broker_message import HOT_DEPLOY, PUBSUB
from zato.common.const import SECRETS
from zato.common.facade import SecurityFacade
from zato.common.json_internal import loads
from zato.common.log_streaming import LogStreamingManager
from zato.common.marshal_.api import MarshalAPI
from zato.common.odb.api import PoolStore
from zato.common.odb.post_process import ODBPostProcess
from zato.common.pubsub.consumer import start_internal_consumer
from zato.common.rules.api import RulesManager
from zato.common.typing_ import cast_, intnone, optional
from zato.common.util.api import absolutize, as_bool, get_config_from_file, get_user_config_name, fs_safe_name, invoke_startup_services as _invoke_startup_services, make_list_from_string_list, new_cid_server, register_diag_handlers, spawn_greenlet, StaticConfig, utcnow
from zato.common.util.env import populate_environment_from_file
from zato.common.util.file_transfer import path_string_list_to_list
from zato.common.util.file_system import get_python_files
from zato.common.util.hot_deploy_ import extract_pickup_from_items
from zato.common.util.json_ import BasicParser
from zato.common.util.platform_ import is_posix
from zato.common.util.time_ import TimeUtil
from zato.distlock import LockManager
from zato.server.base.parallel.config import ConfigLoader
from zato.server.base.parallel.http import HTTPHandler
from zato.server.base.worker import WorkerStore
from zato.server.config import ConfigStore
from zato.server.connection.server.rpc.api import ConfigCtx as _ServerRPC_ConfigCtx, ServerRPC
from zato.server.connection.server.rpc.config import ODBConfigSource
from zato.server.groups.base import GroupsManager
from zato.server.groups.ctx import SecurityGroupsCtxBuilder
from bunch import Bunch as bunch_
from ddtrace.trace import tracer as dd_tracer
from ddtrace._trace.tracer import Tracer as DatadogTracer
from kombu.transport.pyamqp import Message as KombuMessage
from opentelemetry.trace import Tracer as OTLPTracer
from zato.common.crypto.api import ServerCryptoManager
from zato.common.odb.api import ODBManager
from zato.common.odb.model import Cluster as ClusterModel
from zato.common.typing_ import any_, anydict, anylist, anyset, callable_, intset, strdict, strbytes, strlist, strorlistnone, strnone, strorlist, strset
from zato.server.connection.cache import Cache, CacheAPI
from zato.server.ext.zunicorn.arbiter import Arbiter
from zato.server.service.store import ServiceStore
from zato.simpleio import SIOServerConfig
from zato.server.startup_callable import StartupCallableTool
from zato.server.commands import CommandsFacade
from contextlib import closing
from zato.common.util.channel import ensure_django_channel_exists, ensure_openapi_channel_exists
import json
import tempfile
import zato.common.pubsub.server
import zato.server.service.internal.pubsub
import psutil
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from ddtrace.trace import tracer
from zato.common.util.api import find_internal_modules
from zato.server.service import internal
import sys

servernone = optional[ParallelServer]

class ParallelServer(BrokerMessageReceiver, ConfigLoader, HTTPHandler):
    odb: ODBManager
    config: ConfigStore
    crypto_manager: ServerCryptoManager
    sql_pool_store: PoolStore
    on_wsgi_request: any_
    cluster: ClusterModel
    worker_store: WorkerStore
    service_store: ServiceStore
    rpc: ServerRPC
    broker_client: BrokerClient
    zato_lock_manager: LockManager
    startup_callable_tool: StartupCallableTool
    bearer_token_manager: BearerTokenManager
    security_facade: SecurityFacade
    stop_after: intnone
    deploy_auto_from: str
    datadog_tracer: DatadogTracer
    otlp_tracer: OTLPTracer
    is_datadog_enabled: bool
    is_grafana_cloud_enabled: bool
    env_name: str
    groups_manager: GroupsManager
    security_groups_ctx_builder: SecurityGroupsCtxBuilder
    work_dir: str
    logger: Any
    host: Any
    port: Any
    use_tls: Any
    is_starting_first: Any
    odb_data: Bunch
    repo_location: Any
    soap11_content_type: Any
    soap12_content_type: Any
    plain_xml_content_type: Any
    json_content_type: Any
    service_modules: Any
    service_sources: Any
    base_dir: Any
    logs_dir: Any
    tls_dir: Any
    static_dir: Any
    hot_deploy_config: Bunch
    fs_server_config: Any
    fs_sql_config: Bunch
    pickup_config: Bunch
    logging_config: Bunch
    logging_conf_path: Any
    sio_config: SIOServerConfig
    connector_server_grace_time: Any
    id: Any
    name: Any
    process_cid: new_cid_server
    worker_id: Any
    worker_pid: Any
    cluster_id: Any
    cluster_name: Any
    startup_jobs: Any
    deployment_lock_expires: Any
    deployment_lock_timeout: Any
    deployment_key: Any
    has_gevent: Any
    delivery_store: Any
    static_config: Bunch
    component_enabled: Bunch
    client_address_headers: Any
    return_tracebacks: Any
    default_error_message: Any
    time_util: TimeUtil
    preferred_address: Any
    crypto_use_tls: Any
    pid: Any
    sync_internal: Any
    is_first_worker: Any
    process_idx: Any
    shmem_size: Any
    audit_pii: Any
    has_fg: Any
    env_file: Any
    _hash_secret_method: Any
    _hash_secret_rounds: Any
    _hash_secret_salt_size: Any
    platform_system: platform_system.lower
    user_config: Bunch
    stderr_path: Any
    marshal_api: MarshalAPI
    env_manager: Any
    enforce_service_invokes: Any
    json_parser: BasicParser
    api_key_header: Any
    api_key_header_wsgi: Any
    needs_x_zato_cid: Any
    _is_process_closing: Any
    internal_cache_patterns: Any
    internal_cache_lock_patterns: RLock
    gateway_services_allowed: Any
    gateway_services_allowed_lock: RLock
    user_ctx: Bunch
    user_ctx_lock: RLock
    http_methods_allowed: Any
    http_methods_allowed_re: Any
    access_logger: logging.getLogger
    access_logger_log: Any
    needs_access_log: self.access_logger.isEnabledFor
    needs_all_access_log: Any
    access_log_ignore: set
    rest_log_ignore: set
    is_enabled_for_warn: logging.getLogger.isEnabledFor
    is_admin_enabled_for_info: logging.getLogger.isEnabledFor
    rules: RulesManager
    log_streaming_manager: LogStreamingManager
    def __init__(self: Any) -> None: ...
    def maybe_on_first_worker(self: Any, server: ParallelServer) -> anyset: ...
    def get_full_name(self: Any) -> str: ...
    def add_pickup_conf_from_env(self: Any) -> None: ...
    def add_pickup_conf_from_auto_deploy(self: Any) -> None: ...
    def add_pickup_conf_from_code_dir(self: Any) -> None: ...
    def add_pickup_conf_from_local_path(self: Any, paths: str, source: str, path_patterns: strorlistnone = ...) -> None: ...
    def add_user_conf_from_env(self: Any) -> None: ...
    def _add_user_conf_from_path(self: Any, path: str, source: str) -> None: ...
    def add_pickup_conf_from_env_variables(self: Any) -> None: ...
    def add_pickup_conf_for_env_file(self: Any) -> None: ...
    def update_environment_variables_from_file(self: Any, file_path: str) -> None: ...
    def _after_init_common(self: Any, server: ParallelServer) -> anyset: ...
    def _read_user_config_from_directory(self: Any, dir_name: str) -> None: ...
    def read_user_config(self: Any) -> None: ...
    def set_up_user_config_location(self: Any) -> strlist: ...
    def set_up_odb(self: Any) -> None: ...
    def build_server_rpc(self: Any) -> ServerRPC: ...
    def handle_enmasse_auto_from(self: Any) -> None: ...
    def log_environment_details(self: Any) -> None: ...
    @staticmethod
    def start_server(parallel_server: ParallelServer, zato_deployment_key: str = ...) -> None: ...
    def _pre_initialize(self: Any) -> None: ...
    def reload_config(self: Any) -> None: ...
    def import_enmasse(self: Any, file_content: str, file_name: str, missing_wait_time: int = ...) -> str: ...
    def export_enmasse(self: Any) -> None: ...
    def import_test_pubsub_enmasse(self: Any) -> None: ...
    def download_pubsub_openapi(self: Any) -> None: ...
    def set_scheduler_address(self: Any, scheduler_address: str) -> None: ...
    def _stop_after_timeout(self: Any) -> None: ...
    def set_up_api_key_config(self: Any) -> None: ...
    def invoke_startup_services(self: Any) -> None: ...
    def _set_ide_password(self: Any, ide_username: str, ide_password: str) -> None: ...
    def apply_local_config(self: Any) -> None: ...
    def get_default_cache(self: Any) -> CacheAPI: ...
    def get_cache(self: Any, cache_type: str, cache_name: str) -> Cache: ...
    def get_from_cache(self: Any, cache_type: str, cache_name: str, key: str) -> any_: ...
    def set_in_cache(self: Any, cache_type: str, cache_name: str, key: str, value: any_) -> any_: ...
    def _remove_response_root_elem(self: Any, data: strdict) -> strdict: ...
    def _remove_response_elem(self: Any, data: strdict | anylist) -> strdict | anylist: ...
    def _set_up_grafana_cloud(self: Any) -> None: ...
    def _set_up_datadog(self: Any) -> None: ...
    def on_pubsub_message(self: Any, body: any_, amqp_msg: KombuMessage, name: str, config: dict) -> None: ...
    def invoke(self: Any, service: str, request: any_ = ..., *args: any_, **kwargs: any_) -> any_: ...
    def on_ipc_invoke_callback(self: Any, msg: bunch_) -> anydict: ...
    def invoke_async(self: Any, service: str, request: any_, callback: callable_, *args: any_, **kwargs: any_) -> any_: ...
    def encrypt(self: Any, data: any_, prefix: str = ...) -> strnone: ...
    def hash_secret(self: Any, data: str, name: str = ...) -> str: ...
    def verify_hash(self: Any, given: str, expected: str, name: str = ...) -> bool: ...
    def decrypt(self: Any, data: strbytes, _prefix: str = ..., _marker: str = ...) -> str: ...
    def decrypt_no_prefix(self: Any, data: str) -> str: ...
    @staticmethod
    def post_fork(arbiter: Arbiter, worker: any_) -> None: ...
    @staticmethod
    def on_starting(arbiter: Arbiter) -> None: ...
    @staticmethod
    def worker_exit(arbiter: Arbiter, worker: Any) -> None: ...
    @staticmethod
    def before_pid_kill(arbiter: Arbiter, worker: Any) -> None: ...
    def cleanup_on_stop(self: Any) -> None: ...
    def notify_new_package(self: Any, package_id: int) -> None: ...
    def api_service_store_get_service_name_by_id(self: Any, *args: any_, **kwargs: any_) -> any_: ...
    def api_worker_store_basic_auth_get_by_id(self: Any, *args: any_, **kwargs: any_) -> any_: ...
    def api_worker_store_reconnect_generic(self: Any, *args: any_, **kwargs: any_) -> any_: ...
