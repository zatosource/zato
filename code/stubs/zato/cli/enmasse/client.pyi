from typing import Any

import logging
import os
import time
from traceback import format_exc
from sqlalchemy import MetaData, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from zato.common.crypto.api import ServerCryptoManager
from zato.common.ext.configobj_ import ConfigObj
from zato.common.odb.model import to_json
from zato.common.odb.query import service_list
from zato.common.util.api import get_config, get_odb_session_from_server_config, get_repo_dir_from_component_dir, utcnow
from zato.common.util.cli import read_stdin_data
from zato.common.typing_ import any_, anydict, bool_, strnone

def get_session_from_server_dir(server_dir: str, stdin_data: strnone = ...) -> any_: ...

def cleanup(prefixes: list[str], server_dir: str, stdin_data: strnone = ...) -> None: ...

def cleanup_enmasse() -> None: ...

def wait_for_services(config_dict: anydict, server_dir: str, stdin_data: strnone = ..., timeout_seconds: int = ..., log_after_seconds: int = ...) -> bool_: ...
