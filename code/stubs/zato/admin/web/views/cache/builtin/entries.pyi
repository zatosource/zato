from typing import Any, TYPE_CHECKING

import logging
from base64 import b64decode, b64encode
from bunch import Bunch
from zato.admin.web import from_utc_to_user
from zato.admin.web.views import Delete as _Delete, Index as _Index
from zato.common.typing_ import any_, strdict


class CacheEntry:
    id: Any
    key: Any
    _value: Any
    last_read: Any
    prev_read: Any
    prev_write: Any
    expiry_op: Any
    expires_at: Any
    hits: Any
    position: Any
    server: Any
    def __init__(self: Any, id: Any = ..., key: Any = ..., value: Any = ..., last_read: Any = ..., prev_read: Any = ..., prev_write: Any = ..., expiry_op: Any = ..., expires_at: Any = ..., hits: Any = ..., position: Any = ..., server: Any = ...) -> None: ...
    @property
    def value(self: Any) -> None: ...
    def value(self: Any, value: Any) -> None: ...

class Index(_Index):
    method_allowed: Any
    url_name: Any
    template: Any
    service_name: Any
    output_class: Any
    paginate: Any
    def handle(self: Any) -> strdict: ...
    def on_before_append_item(self: Any, item: Any, _to_user_dt: Any = ...) -> None: ...

class Delete(_Delete):
    url_name: Any
    error_message: Any
    service_name: Any
    def get_input_dict(self: Any, *args: Any, **kwargs: Any) -> None: ...
