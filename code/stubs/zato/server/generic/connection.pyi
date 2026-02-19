from typing import Any

from bunch import bunchify
from zato.common.api import GENERIC
from zato.common.json_internal import dumps, loads
from zato.server.generic import attrs_gen_conn

class GenericConnection:
    __slots__: Any
    from_bunch: Any
    def __init__(self: Any) -> None: ...
    @staticmethod
    def from_dict(data: Any, skip: Any = ...) -> None: ...
    def to_dict(self: Any, needs_bunch: Any = ...) -> None: ...
    @staticmethod
    def from_model(data: Any) -> None: ...
    def to_sql_dict(self: Any, needs_bunch: Any = ..., skip: Any = ...) -> None: ...
