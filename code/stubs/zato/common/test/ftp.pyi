from typing import Any, TYPE_CHECKING

from tempfile import gettempdir
from threading import Thread
from pyftpdlib.authorizers import DummyAuthorizer as _DummyAuthorizer
from pyftpdlib.handlers import FTPHandler as _FTPHandler
from pyftpdlib.servers import FTPServer as _ImplFTPServer


class config:
    port: Any
    username: Any
    password: Any
    directory: Any

def create_ftp_server() -> None: ...

class FTPServer(Thread):
    impl: create_ftp_server
    def __init__(self: Any) -> None: ...
    def stop(self: Any) -> None: ...
