from typing import Any, TYPE_CHECKING

from logging import getLogger
from traceback import format_exc
from zato.common.api import CONNECTION, GENERIC, Groups, URL_TYPE
from zato.common.typing_ import anydict


def _find_object_id_by_name(client: Any, cluster_id: Any, list_service: Any, list_params: Any, target_name: Any, name_field: Any = ...) -> None: ...

def _delete_object_by_id(client: Any, cluster_id: Any, delete_service: Any, object_id: Any, id_field: Any = ...) -> None: ...

def execute_delete_security(client: Any, cluster_id: Any, arguments: anydict) -> anydict: ...

def execute_delete_tool(client: Any, cluster_id: Any, tool_name: str, arguments: anydict) -> anydict: ...
