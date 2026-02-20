from typing import Any

from zato.common.util.api import is_func_overridden
from zato.common.typing_ import any_, callable_

class HookTool:
    server: Any
    hook_ctx_class: Any
    hook_type_to_method: Any
    invoke_func: Any
    def __init__(self: Any, server: Any, hook_ctx_class: Any, hook_type_to_method: Any, invoke_func: Any) -> None: ...
    def is_hook_overridden(self: Any, service_name: Any, hook_type: Any) -> None: ...
    def get_hook_service_invoker(self: Any, service_name: str, hook_type: str) -> callable_: ...
