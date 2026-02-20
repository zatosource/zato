from typing import Any

import errno
import socket
import ssl
import sys
import zato.server.ext.zunicorn.http as http
import zato.server.ext.zunicorn.http.wsgi as wsgi
import zato.server.ext.zunicorn.util as util
import zato.server.ext.zunicorn.workers.base as base
from zato.server.ext.zunicorn import six

class AsyncWorker(base.Worker):
    worker_connections: Any
    def __init__(self: Any, *args: Any, **kwargs: Any) -> None: ...
    def timeout_ctx(self: Any) -> None: ...
    def is_already_handled(self: Any, respiter: Any) -> None: ...
    def handle(self: Any, listener: Any, client: Any, addr: Any, RequestParser: Any = ..., util_close: Any = ...) -> None: ...
    def handle_request(self: Any, listener_name: Any, req: Any, sock: Any, addr: Any, ALREADY_HANDLED: Any = ...) -> None: ...
