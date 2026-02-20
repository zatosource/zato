from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from importlib import import_module
from logging import getLogger
from traceback import format_exc
from bunch import Bunch

class PhaseCtx:
    phase: Any
    args: Any
    kwargs: Any
    def __init__(self: Any, phase: Any, args: Any, kwargs: Any) -> None: ...

class StartupCallableTool:
    _callable_names: Any
    callable_list: Any
    def __init__(self: Any, server_config: Any) -> None: ...
    def init(self: Any) -> None: ...
    def invoke(self: Any, phase: Any, args: Any = ..., kwargs: Any = ...) -> None: ...

def default_callable(ctx: Any) -> None: ...
