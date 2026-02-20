from typing import Any

from logging import getLogger
from requests import get as requests_get
from zato.client import AnyServiceInvoker
from zato.common.ext.dataclasses import dataclass
from zato.common.typing_ import any_, cast_, dict_field
from requests import Response
from typing import Callable
from zato.client import ServiceInvokeResponse
from zato.common.typing_ import anydict, anylist, callable_, intnone, stranydict, strordictnone
from zato.server.base.parallel import ParallelServer
from zato.server.connection.server.rpc.config import RPCServerInvocationCtx

class ServerInvocationResult:
    is_ok: bool
    has_data: bool
    data: anydict
    error_info: any_

class PerPIDResponse:
    is_ok: bool
    pid: int
    pid_data: strordictnone
    error_info: any_

class ServerInvoker:
    parallel_server: Any
    cluster_name: Any
    server_name: Any
    def __init__(self: Any, parallel_server: ParallelServer, cluster_name: str, server_name: str) -> None: ...
    def invoke(self: Any, *args: any_, **kwargs: any_) -> any_: ...
    def invoke_async(self: Any, *args: any_, **kwargs: any_) -> any_: ...
    def invoke_all_pids(self: Any, *args: any_, **kwargs: any_) -> anylist: ...

class LocalServerInvoker(ServerInvoker):
    def invoke(self: Any, *args: any_, **kwargs: any_) -> any_: ...
    def invoke_async(self: Any, *args: any_, **kwargs: any_) -> any_: ...
    def invoke_all_pids(self: Any, *args: any_, **kwargs: any_) -> anylist: ...

class RemoteServerInvoker(ServerInvoker):
    url_path: Any
    invocation_ctx: Any
    ping_address: Any.format
    ping_timeout: Any
    address: Any.format
    invoker: AnyServiceInvoker
    def __init__(self: Any, ctx: RPCServerInvocationCtx) -> None: ...
    def ping(self: Any, ping_timeout: intnone = ...) -> None: ...
    def close(self: Any) -> None: ...
    def _invoke(self: Any, invoke_func: Any, service: str, request: any_ = ..., *args: any_, **kwargs: any_) -> stranydict | anylist | str | None: ...
    def invoke(self: Any, *args: any_, **kwargs: any_) -> any_: ...
    def invoke_async(self: Any, *args: any_, **kwargs: any_) -> any_: ...
    def invoke_all_pids(self: Any, *args: any_, **kwargs: any_) -> any_: ...
