from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from requests import Session as RequestsSession
from zato.common.api import CACHE, NotGiven
from zato.common.crypto.api import ServerCryptoManager
from zato.common.json_internal import dumps
from zato.common.util.api import as_bool, get_config, get_odb_session_from_server_dir, get_repo_dir_from_component_dir
from zato.common.odb.model import Cluster, HTTPBasicAuth, Server
from requests import Response as RequestsResponse


class CommandConfig:
    command: Any
    modifier: Any
    key: Any
    value: Any
    is_string_key: Any
    is_int_key: Any
    is_string_value: Any
    is_int_value: Any
    is_bool_value: Any
    format: Any
    def __init__(self: Any) -> None: ...
    def to_dict(self: Any) -> None: ...

class CommandResponse:
    key: Any
    text: Any
    has_value: Any
    def __init__(self: Any) -> None: ...

class Client:
    address: Any
    username: Any
    password: Any
    cache_name: Any
    session: Any
    def __init__(self: Any) -> None: ...
    @staticmethod
    def from_server_conf(server_dir: Any, cache_name: Any, is_https: Any) -> None: ...
    @staticmethod
    def from_dict(config: Any) -> None: ...
    def _request(self: Any, op: Any, key: Any, value: Any = ..., pattern: Any = ..., op_verb_map: Any = ...) -> None: ...
    def run_command(self: Any, config: Any) -> None: ...
