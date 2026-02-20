from typing import Any, TYPE_CHECKING

import csv
import os
from pathlib import PurePath
from time import sleep
from traceback import format_exc
from bunch import Bunch
from zato.common.api import EnvFile
from zato.common.broker_message import ValueConstant, HOT_DEPLOY, MESSAGE_TYPE
from zato.common.typing_ import cast_, dataclass, from_dict, optional
from zato.common.util.api import get_config, get_user_config_name
from zato.common.util.open_ import open_r
from zato.server.service import Service
from zato.common.typing_ import any_, stranydict


class UpdateCtx:
    data: str
    full_path: str
    file_name: str
    relative_dir: optional[str]

class _Logger(Service):
    pickup_data_type: Any
    def handle(self: Any) -> None: ...

class LogJSON(_Logger):
    pickup_data_type: Any

class LogXML(_Logger):
    pickup_data_type: Any

class LogCSV(Service):
    def handle(self: Any) -> None: ...

class _Updater(Service):
    pickup_action: ValueConstant
    def handle(self: Any) -> None: ...

class UpdateStatic(_Updater):
    pickup_action: Any

class UpdateUserConf(_Updater):
    pickup_action: Any

class UpdateEnmasse(Service):
    def handle(self: Any) -> None: ...

class _OnUpdate(Service):
    update_type: Any
    def handle(self: Any) -> None: ...
    def _get_update_type(self: Any, file_path: str) -> str: ...
    def get_update_type(self: Any, file_path: str) -> str: ...
    def sync_pickup_file_in_ram(self: Any, *args: any_, **kwargs: any_) -> None: ...

class OnUpdateUserConf(_OnUpdate):
    update_type: Any
    def _is_env_file(self: Any, file_path: str) -> bool: ...
    def _is_rules_file(self: Any, file_path: str) -> bool: ...
    def sync_pickup_file_in_ram(self: Any, ctx: UpdateCtx) -> None: ...
    def _get_update_type(self: Any, file_path: str) -> str: ...

class OnUpdateStatic(_OnUpdate):
    update_type: Any
    def sync_pickup_file_in_ram(self: Any, ctx: UpdateCtx) -> None: ...
