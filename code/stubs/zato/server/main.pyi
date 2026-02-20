from typing import Any, TYPE_CHECKING

import warnings
import logging
import os
import locale
import sys
from logging.config import dictConfig
from zato.common.microopt import logging_Logger_log
from logging import Logger
import yaml
from zato.common.api import SERVER_STARTUP, TRACE1, ZATO_CRYPTO_WELL_KNOWN_DATA
from zato.common.crypto.api import ServerCryptoManager
from zato.common.ext.configobj_ import ConfigObj
from zato.common.ipaddress_ import get_preferred_ip
from zato.common.odb.api import ODBManager, PoolStore
from zato.common.repo import RepoManager
from zato.common.simpleio_ import get_sio_server_config
from zato.common.util.api import asbool, get_config, is_encrypted, parse_cmd_line_options, register_diag_handlers, store_pidfile
from zato.common.util.env import populate_environment_from_file
from zato.common.util.platform_ import is_linux, is_mac, is_windows
from zato.common.util.open_ import open_r
from zato.server.base.parallel import ParallelServer
from zato.server.ext import zunicorn
from zato.server.ext.zunicorn.app.base import Application
from zato.server.service.store import ServiceStore
from zato.server.startup_callable import StartupCallableTool
from sqlalchemy import exc as sa_exc
import oracledb
import cloghandler
from ddtrace import patch as dd_patch
from bunch import Bunch
from zato.common.typing_ import any_, callable_, dictnone, strintnone
from zato.server.ext.zunicorn.config import Config as ZunicornConfig
from zato.common.util.cli import read_stdin_data
from zato_environment import EnvironmentManager
import requests as _r
import redis as redis_lib


class ModuleCtx:
    num_threads: Any
    bind_host: Any
    bind_port: Any
    Env_Num_Threads: Any
    Env_Bind_Host: Any
    Env_Bind_Port: Any
    Env_Map: Any

class ZatoGunicornApplication(Application):
    cfg: ZunicornConfig
    zato_wsgi_app: Any
    repo_location: Any
    config_main: Any
    crypto_config: Any
    zato_host: Any
    zato_port: Any
    zato_config: Any
    def __init__(self: Any, zato_wsgi_app: ParallelServer, repo_location: str, config_main: Bunch, crypto_config: Bunch, *args: any_, **kwargs: any_) -> None: ...
    def get_config_value(self: Any, config_key: str) -> strintnone: ...
    def init(self: Any, *ignored_args: any_, **ignored_kwargs: any_) -> None: ...
    def load(self: Any) -> None: ...

def get_bin_dir() -> str: ...

def get_code_dir(bin_dir: str) -> str: ...

def get_util_dir(code_dir: str) -> str: ...

def get_env_manager_base_dir(code_dir: str) -> str: ...

def run(base_dir: str, start_gunicorn_app: bool = ..., options: dictnone = ...) -> ParallelServer | None: ...

def start_wsgi_app(zato_gunicorn_app: any_, start_gunicorn_app: bool) -> None: ...
