from typing import Any

import os
from json import dumps
from logging import getLogger
from traceback import format_exc
from uuid import uuid4
from bunch import Bunch
from zato.common.api import ZATO_ODB_POOL_NAME
from zato.common.broker_message import code_to_name
from zato.common.crypto.api import CryptoManager
from zato.common.odb.api import ODBManager, PoolStore
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool, absjoin, get_config, is_encrypted, new_cid, set_up_logging
from zato.common.util.auth import check_basic_auth
from zato.common.util.json_ import json_loads
from zato.common.typing_ import any_, anydict, byteslist, callable_, callnone, intnone, strdict, strnone, type_
from zato.common.util.cli import read_stdin_data

class StatusCode:
    OK: Any
    InternalError: Any
    ServiceUnavailable: Any

class AuxServerConfig:
    odb: ODBManager
    username: str
    password: str
    env_key_username: str
    env_key_password: str
    env_key_auth_required: str
    server_type: str
    callback_func: callable_
    conf_file_name: str
    crypto_manager: CryptoManager
    crypto_manager_class: type_[CryptoManager]
    parent_server_name: str
    parent_server_pid: int
    raw_config: Bunch
    def __init__(self: Any) -> None: ...
    @staticmethod
    def get_odb(config: AuxServerConfig) -> ODBManager: ...
    def set_credentials_from_env(self: Any) -> bool: ...
    @classmethod
    def from_repo_location(class_: Any, server_type: Any, repo_location: Any, conf_file_name: Any, crypto_manager_class: Any, needs_odb: Any = ...) -> AuxServerConfig: ...

class AuxServer:
    needs_logging_setup: bool
    api_server: WSGIServer
    cid_prefix: str
    server_type: str
    conf_file_name: str
    config_class: type_[AuxServerConfig]
    crypto_manager_class: type_[CryptoManager]
    needs_odb: bool
    has_credentials: bool
    parent_server_name: str
    parent_server_pid: int
    def __init__(self: Any, config: AuxServerConfig) -> None: ...
    @classmethod
    def before_config_hook(class_: type_[AuxServer]) -> None: ...
    @classmethod
    def after_config_hook(class_: Any, config: Any, repo_location: Any) -> None: ...
    @classmethod
    def start_from_repo_location(class_: Any) -> None: ...
    @classmethod
    def start_from_config(class_: type_[AuxServer], config: AuxServerConfig) -> None: ...
    @classmethod
    def _start(class_: type_[AuxServer], config: AuxServerConfig) -> None: ...
    def serve_forever(self: Any) -> None: ...
    def get_action_func_impl(self: Any, action_name: str) -> callable_: ...
    def _check_credentials(self: Any, credentials: str) -> None: ...
    def should_check_credentials(self: Any) -> bool: ...
    def handle_api_request(self: Any, data: bytes, credentials: str) -> any_: ...
    def __call__(self: Any, env: anydict, start_response: callable_) -> byteslist: ...
