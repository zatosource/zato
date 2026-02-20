from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from logging import getLogger
from traceback import format_exc
from zato.common.util.api import spawn_greenlet
import typing
from bunch import Bunch
from zato.server.base.parallel import ParallelServer

class Wrapper:
    needs_self_client: Any
    wrapper_type: Any
    required_secret_attr: Any
    required_secret_label: Any
    build_if_not_active: Any
    config: Any
    server: Any
    _impl: Any
    delete_requested: Any
    is_connected: Any
    update_lock: RLock
    def __init__(self: Any, config: Any, server: Any = ...) -> None: ...
    @property
    def client(self: Any) -> None: ...
    def build_wrapper(self: Any, should_spawn: Any = ...) -> None: ...
    def _init(self: Any) -> None: ...
    def _init_impl(self: Any) -> None: ...
    def _delete(self: Any) -> None: ...
    def _ping(self: Any) -> None: ...
    def delete(self: Any) -> None: ...
    def ping(self: Any) -> None: ...
