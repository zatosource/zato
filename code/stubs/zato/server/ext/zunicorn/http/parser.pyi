from typing import Any

from zato.server.ext.zunicorn.http.message import Request
from zato.server.ext.zunicorn.http.unreader import SocketUnreader, IterUnreader

class Parser:
    mesg_class: Any
    next: Any
    cfg: Any
    mesg: Any
    req_count: Any
    unreader: IterUnreader
    def __init__(self: Any, cfg: Any, source: Any) -> None: ...
    def __iter__(self: Any) -> None: ...
    def __next__(self: Any) -> None: ...

class RequestParser(Parser):
    mesg_class: Any
