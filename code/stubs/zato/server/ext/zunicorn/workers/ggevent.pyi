from typing import Any, TYPE_CHECKING

from datetime import datetime
from functools import partial
from traceback import format_exc
import errno
import os
import sys
import time
from zato.common.api import OS_Env
from zato.common.util.platform_ import is_windows
from zato.server.ext.zunicorn import SERVER_SOFTWARE
from zato.server.ext.zunicorn.http.wsgi import base_environ
from zato.server.ext.zunicorn.workers.base_async import AsyncWorker
from zato.server.ext.zunicorn.http.wsgi import sendfile as o_sendfile
from zato.server.ext.zunicorn.util import is_forking
from zato.server.ext.zunicorn.http import wsgi


def _gevent_sendfile(fdout: Any, fdin: Any, offset: Any, nbytes: Any) -> None: ...

def patch_sendfile() -> None: ...

class GeventWorker(AsyncWorker):
    server_class: Any
    wsgi_handler: Any
    def patch(self: Any) -> None: ...
    def notify(self: Any) -> None: ...
    def timeout_ctx(self: Any) -> None: ...
    def run(self: Any) -> None: ...
    def handle(self: Any, listener: Any, client: Any, addr: Any) -> None: ...
    def handle_request(self: Any, listener_name: Any, req: Any, sock: Any, addr: Any) -> None: ...
    def handle_quit(self: Any, sig: Any, frame: Any) -> None: ...
    def handle_usr1(self: Any, sig: Any, frame: Any) -> None: ...
    def init_process(self: Any) -> None: ...

class GeventResponse:
    status: Any
    headers: Any
    sent: Any
    status: Any
    headers: Any
    sent: Any
    def __init__(self: Any, status: Any, headers: Any, clength: Any) -> None: ...

class PyWSGIHandler(pywsgi.WSGIHandler):
    def log_request(self: Any) -> None: ...
    def get_environ(self: Any) -> None: ...

class PyWSGIServer(pywsgi.WSGIServer):
    ...

class GeventPyWSGIWorker(GeventWorker):
    server_class: Any
    wsgi_handler: Any
