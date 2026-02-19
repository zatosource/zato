from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
import socket
import ssl
from http.client import OK
from tempfile import NamedTemporaryFile
from threading import Thread
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from zato.common.py23_.past.builtins import xrange
from zato.common.api import ZATO_OK
from zato.common.test.tls_material import ca_cert, server1_cert, server1_key
import psutil

def get_free_port(start: Any = ..., end: Any = ...) -> None: ...

class _HTTPHandler(BaseHTTPRequestHandler):
    do_DELETE: Any
    do_OPTIONS: Any
    do_POST: Any
    do_PUT: Any
    do_PATCH: Any
    def do_GET(self: Any) -> None: ...
    def log_message(self: Any, *ignored_args: Any, **ignored_kwargs: Any) -> None: ...

class _TLSServer(HTTPServer):
    def __init__(self: Any, cert_reqs: Any, ca_cert: Any) -> None: ...
    def server_bind(self: Any) -> None: ...

class TLSServer(Thread):
    def __init__(self: Any, cert_reqs: Any = ..., ca_cert: Any = ...) -> None: ...
    def get_port(self: Any) -> None: ...
    def stop(self: Any) -> None: ...
    def run(self: Any) -> None: ...
