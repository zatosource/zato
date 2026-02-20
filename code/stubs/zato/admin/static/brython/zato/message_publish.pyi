from typing import Any

from browser import document as doc
from zato.common.json_internal import loads

class SelectChanger(object):
    data_source: Any
    select_source: Any
    select_target: Any
    data: Any
    def __init__(self: Any, select_source: Any, select_target: Any, data_source: Any = ...) -> None: ...
    def run(self: Any) -> None: ...
    def on_source_change(self: Any, e: Any) -> None: ...
