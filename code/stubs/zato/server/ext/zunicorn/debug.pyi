from typing import Any

import sys
import linecache
import re
import inspect

class Spew:
    def __init__(self: Any, trace_names: Any = ..., show_values: Any = ...) -> None: ...
    def __call__(self: Any, frame: Any, event: Any, arg: Any) -> None: ...

def spew(trace_names: Any = ..., show_values: Any = ...) -> None: ...

def unspew() -> None: ...
