from typing import Any, TYPE_CHECKING

import os
from logging import captureWarnings, getLogger
from zato.broker.client import BrokerClient
from zato.common.api import SCHEDULER
from zato.common.aux_server.base import AuxServer, AuxServerConfig
from zato.common.crypto.api import SchedulerCryptoManager
from zato.common.typing_ import cast_
from zato.common.util.api import as_bool, get_config, store_pidfile
from zato.scheduler.api import SchedulerAPI
from zato.scheduler.util import set_up_zato_client
from zato.common.typing_ import callable_, type_
from logging import getLogger


class SchedulerServerConfig(AuxServerConfig):
    current_status: str
    env_key_status: Any
    env_key_username: Any
    env_key_password: Any
    env_key_auth_required: Any
    startup_jobs: Any
    on_job_executed_cb: callable_
    job_log_level: Any
    _add_startup_jobs: Any
    _add_scheduler_jobs: Any
    def __init__(self: Any) -> None: ...

class SchedulerServer(AuxServer):
    needs_logging_setup: Any
    cid_prefix: Any
    server_type: Any
    conf_file_name: Any
    config_class: Any
    crypto_manager_class: Any
    zato_client: set_up_zato_client
    should_run_scheduler: Any
    scheduler_api: SchedulerAPI
    def __init__(self: Any, config: AuxServerConfig) -> None: ...
    def should_check_credentials(self: Any) -> bool: ...
    @classmethod
    def before_config_hook(class_: type_[AuxServer]) -> None: ...
    @classmethod
    def after_config_hook(class_: Any, config: Any, repo_location: Any) -> None: ...
    def get_action_func_impl(self: Any, action_name: str) -> callable_: ...
    def serve_forever(self: Any) -> None: ...
