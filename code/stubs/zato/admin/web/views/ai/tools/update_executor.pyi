from typing import Any

from logging import getLogger
from traceback import format_exc
from zato.common.api import CONNECTION, GENERIC, URL_TYPE
from zato.common.typing_ import any_, anydict

def _find_object_by_name(client: Any, cluster_id: Any, list_service: Any, list_params: Any, target_name: Any) -> None: ...

def _build_edit_request(existing_object: Any, updates: Any, cluster_id: Any, extra_params: Any = ...) -> None: ...

def execute_update_security(client: Any, cluster_id: Any, arguments: anydict) -> anydict: ...

def execute_update_tool(client: Any, cluster_id: Any, cluster: Any, tool_name: str, arguments: anydict) -> anydict: ...
