from typing import Any, TYPE_CHECKING

from contextlib import closing
from logging import getLogger
from zato.common.ext.dataclasses import dataclass
from zato.common.odb.query import server_by_name, server_list
from zato.common.typing_ import cast_
from zato.common.odb.api import SessionWrapper
from zato.common.odb.model import SecurityBase as SecurityBaseModel, Server as ServerModel
from zato.common.typing_ import callable_, intnone, list_, strnone
from zato.server.base.parallel import ParallelServer


class CredentialsConfig:
    sec_def_name: Any
    api_user: Any

class RPCServerInvocationCtx:
    cluster_name: strnone
    server_name: strnone
    address: strnone
    port: intnone
    username: strnone
    password: strnone
    needs_ping: bool
    crypto_use_tls: bool

class InvocationCredentials:
    username: strnone
    password: strnone

class ConfigSource:
    current_cluster_name: Any
    current_server_name: Any
    decrypt_func: Any
    def __init__(self: Any, cluster_name: str, server_name: str, decrypt_func: callable_) -> None: ...
    def get_server_ctx(self: Any, parallel_server: Any, cluster_name: str, server_name: str) -> RPCServerInvocationCtx: ...
    def get_server_ctx_list(self: Any, cluster_name: str) -> list_[RPCServerInvocationCtx]: ...
    def get_invocation_credentials(self: Any, cluster_name: str) -> InvocationCredentials: ...

class ODBConfigSource(ConfigSource):
    odb: Any
    def __init__(self: Any, odb: SessionWrapper, cluster_name: str, server_name: str, decrypt_func: callable_) -> None: ...
    def get_invocation_credentials(self: Any, _unused_session: Any, cluster_name: str) -> None: ...
    def build_server_ctx(self: Any, server_model: ServerModel, credentials: InvocationCredentials) -> RPCServerInvocationCtx: ...
    def get_server_ctx(self: Any, _ignored_parallel_server: Any, cluster_name: Any, server_name: Any) -> RPCServerInvocationCtx: ...
    def get_server_ctx_list(self: Any, cluster_name: str) -> list_[RPCServerInvocationCtx]: ...
