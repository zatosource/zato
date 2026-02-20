from typing import Any

from bunch import bunchify
from zato.common.api import GENERIC
from zato.common.json_internal import dumps, loads
from zato.server.generic import attrs_gen_conn

class GenericConnection:
    __slots__: Any
    from_bunch: Any
    id: Any
    name: Any
    type_: Any
    is_active: Any
    is_internal: Any
    cache_expiry: Any
    address: Any
    port: Any
    timeout: Any
    data_format: Any
    opaque: Any
    is_channel: Any
    is_outconn: Any
    version: Any
    extra: Any
    pool_size: Any
    username: Any
    username_type: Any
    secret: Any
    secret_type: Any
    conn_def_id: Any
    cache_id: Any
    cluster_id: Any
    def __init__(self: Any) -> None: ...
    @staticmethod
    def from_dict(data: Any, skip: Any = ...) -> None: ...
    def to_dict(self: Any, needs_bunch: Any = ...) -> None: ...
    @staticmethod
    def from_model(data: Any) -> None: ...
    def to_sql_dict(self: Any, needs_bunch: Any = ..., skip: Any = ...) -> None: ...
