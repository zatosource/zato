from typing import Any

import os
from copy import deepcopy
from dataclasses import dataclass
from bunch import Bunch
from zato.cli import common_odb_opts, common_scheduler_server_address_opts, common_scheduler_server_api_client_opts, sql_conf_contents, ZatoCommand
from zato.common.api import SCHEDULER
from zato.common.const import ServiceConst
from zato.common.crypto.api import SchedulerCryptoManager
from zato.common.crypto.const import well_known_data
from zato.common.odb.model import Cluster
from zato.common.scheduler import startup_jobs
from zato.common.util.config import get_scheduler_api_client_for_server_auth_required, get_scheduler_api_client_for_server_password, get_scheduler_api_client_for_server_username
from zato.common.util.open_ import open_w
from zato.common.util.platform_ import is_linux
from argparse import Namespace
from zato.common.typing_ import any_, anydict, strdict
from zato.common.util.api import get_server_client_auth
from zato.common.util.logging_ import get_logging_conf_contents

class ServerConfigForScheduler:
    server_host: str
    server_port: int
    server_path: str
    server_use_tls: bool
    is_auth_from_server_required: bool

class Create(ZatoCommand):
    needs_empty_dir: Any
    opts: any_
    def __init__(self: Any, args: any_) -> None: ...
    def allow_empty_secrets(self: Any) -> None: ...
    def _get_cluster_id(self: Any, args: any_) -> any_: ...
    def _get_server_admin_invoke_credentials(self: Any, cm: SchedulerCryptoManager, odb_config: anydict) -> any_: ...
    def _get_server_config(self: Any, args: any_, cm: SchedulerCryptoManager, odb_config: strdict) -> ServerConfigForScheduler: ...
    def execute(self: Any, args: Namespace, show_output: bool = ..., needs_created_flag: bool = ...) -> None: ...
