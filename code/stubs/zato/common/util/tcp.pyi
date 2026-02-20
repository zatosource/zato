from typing import Any, TYPE_CHECKING

import errno
from datetime import datetime, timedelta
from logging import getLogger
from socket import timeout as SocketTimeoutException
from time import sleep
from traceback import format_exc
from uuid import uuid4
from platform_ import is_linux
import psutil
from requests import get as requests_get
from zato.common.util.api import wait_for_predicate


class SocketReaderCtx:
    conn_id: Any
    socket: Any
    max_wait_time: Any
    max_msg_size: Any
    read_buffer_size: Any
    recv_timeout: Any
    should_log_messages: Any
    buffer: Any
    is_ok: Any
    reason: Any
    def __init__(self: Any, conn_id: Any, socket: Any, max_wait_time: Any, max_msg_size: Any, read_buffer_size: Any, recv_timeout: Any, should_log_messages: Any) -> None: ...

def get_free_port(start: Any = ...) -> None: ...

def is_port_taken(port: Any) -> None: ...

def _is_port_ready(port: Any, needs_taken: Any) -> None: ...

def _wait_for_port(port: Any, timeout: Any, interval: Any, needs_taken: Any) -> None: ...

def wait_for_zato(address: Any, url_path: Any, timeout: Any = ..., interval: Any = ..., needs_log: Any = ...) -> None: ...

def wait_for_zato_ping(address: Any, timeout: Any = ..., interval: Any = ..., needs_log: Any = ...) -> None: ...

def wait_until_port_taken(port: Any, timeout: Any = ..., interval: Any = ...) -> None: ...

def wait_until_port_free(port: Any, timeout: Any = ..., interval: Any = ...) -> None: ...

def get_fqdn_by_ip(ip_address: Any, default: Any, log_msg_prefix: Any) -> None: ...

def read_from_socket(ctx: Any, _utcnow: Any = ..., _timedelta: Any = ...) -> bytes: ...

def parse_address(address: Any) -> None: ...

def get_current_ip() -> None: ...

class ZatoStreamServer(StreamServer):
    def shutdown(self: Any) -> None: ...
    @classmethod
    def get_listener(self: Any, address: Any, backlog: Any = ..., family: Any = ...) -> None: ...
    @staticmethod
    def _make_socket(address: Any, backlog: Any = ..., reuse_addr: Any = ..., family: Any = ...) -> None: ...
