from typing import Any

from copy import deepcopy
from dataclasses import dataclass
from zato.cli import common_odb_opts, common_scheduler_server_api_client_opts, common_scheduler_server_address_opts, sql_conf_contents, ZatoCommand
from zato.common.api import CONTENT_TYPE, Default_Service_File_Data, NotGiven, SCHEDULER
from zato.common.crypto.api import ServerCryptoManager
from zato.common.simpleio_ import simple_io_conf_contents
from zato.common.util.api import as_bool, get_demo_py_fs_locations
from zato.common.util.config import get_scheduler_api_client_for_server_password, get_scheduler_api_client_for_server_username
from zato.common.util.open_ import open_r, open_w
from zato.common.typing_ import any_
import os
import uuid
import platform
from datetime import datetime
from traceback import format_exc
from cryptography.fernet import Fernet
from sqlalchemy.exc import IntegrityError
from six import PY3
from zato.common.api import SERVER_JOIN_STATUS
from zato.common.crypto.const import well_known_data
from zato.common.defaults import http_plain_server_port
from zato.common.odb.model import Cluster, Server
from zato.common.util.logging_ import get_logging_conf_contents

class SchedulerConfigForServer:
    scheduler_host: str
    scheduler_port: int
    scheduler_use_tls: bool

class Create(ZatoCommand):
    needs_empty_dir: Any
    opts: any_
    def __init__(self: Any, args: any_) -> None: ...
    def allow_empty_secrets(self: Any) -> None: ...
    def prepare_directories(self: Any, show_output: bool) -> None: ...
    def _get_scheduler_config(self: Any, args: any_, secret_key: bytes) -> SchedulerConfigForServer: ...
    def _add_demo_service(self: Any, fs_location: str, full_path: str) -> None: ...
    def execute(self: Any, args: any_, default_http_port: any_ = ..., show_output: bool = ..., return_server_id: bool = ...) -> int | None: ...
