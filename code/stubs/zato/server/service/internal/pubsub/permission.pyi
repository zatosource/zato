from typing import Any

from contextlib import closing
from zato.common.broker_message import PUBSUB
from zato.common.odb.model import PubSubPermission, SecurityBase
from zato.common.odb.query import pubsub_permission_list
from zato.common.util.sql import set_instance_opaque_attrs
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

class GetList(AdminService):
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class Create(AdminService):
    def handle(self: Any) -> None: ...

class Edit(AdminService):
    def handle(self: Any) -> None: ...

class Delete(AdminService):
    def handle(self: Any) -> None: ...
