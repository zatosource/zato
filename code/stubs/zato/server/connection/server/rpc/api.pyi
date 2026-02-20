from typing import Any, TYPE_CHECKING

from logging import getLogger
from zato.common.ext.dataclasses import dataclass
from zato.common.typing_ import cast_, list_field
from zato.server.connection.server.rpc.invoker import LocalServerInvoker, RemoteServerInvoker
from zato.common.typing_ import any_, anylist, generator_, stranydict
from zato.server.base.parallel import ParallelServer
from zato.server.connection.server.rpc.config import ConfigSource, RPCServerInvocationCtx
from zato.server.connection.server.rpc.invoker import PerPIDResponse, ServerInvoker


class InvokeAllResult:
    is_ok: bool
    data: anylist

class ConfigCtx:
    config_source: Any
    parallel_server: Any
    local_server_invoker_class: Any
    remote_server_invoker_class: Any
    def __init__(self: Any, config_source: Any, parallel_server: Any, local_server_invoker_class: Any = ..., remote_server_invoker_class: Any = ...) -> None: ...
    def get_remote_server_invoker(self: Any, server_name: str) -> RemoteServerInvoker: ...
    def get_remote_server_invoker_list(self: Any) -> generator_[ServerInvoker, None, None]: ...

class ServerRPC:
    config_ctx: Any
    current_cluster_name: Any
    _invokers: Any
    logger: getLogger
    def __init__(self: Any, config_ctx: ConfigCtx) -> None: ...
    def _get_invoker_by_server_name(self: Any, server_name: str) -> ServerInvoker: ...
    def get_invoker_by_server_name(self: Any, server_name: str) -> ServerInvoker: ...
    def populate_invokers(self: Any) -> None: ...
    def invoke_all(self: Any, service: Any, request: Any = ..., *args: Any, **kwargs: Any) -> InvokeAllResult: ...
