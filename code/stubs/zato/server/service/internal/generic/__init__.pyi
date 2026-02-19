from typing import Any

from zato.common.util.sql import get_instance_by_id, get_instance_by_name
from zato.server.service.internal import AdminService

class _BaseService(AdminService):
    def _get_instance_by_id(self: Any, session: Any, model_class: Any, id: Any) -> None: ...
    def _get_instance_by_name(self: Any, session: Any, model_class: Any, type_: Any, name: Any) -> None: ...
