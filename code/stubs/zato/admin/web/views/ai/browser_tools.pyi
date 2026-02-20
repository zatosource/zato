from typing import Any

from logging import getLogger
from uuid import uuid4
from zato.admin.web.views.ai.common import get_redis_client
from zato.common.json_internal import dumps, loads
from zato.common.typing_ import any_, anydict

class BrowserToolExecutor:
    yield_event: Any
    redis_client: get_redis_client
    def __init__(self: Any, yield_event: callable) -> None: ...
    def _format_browser_tool_event(self: Any, request_id: str, tool_name: str, params: anydict) -> anydict: ...
    def execute(self: Any, tool_name: str, params: anydict) -> anydict: ...

def submit_browser_tool_result(request_id: str, result: anydict) -> None: ...

def get_browser_tool_schemas() -> list: ...

def is_browser_tool(tool_name: str) -> bool: ...
