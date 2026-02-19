from typing import Any

from contextlib import closing
from traceback import format_exc
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import OutgoingAMQP
from zato.common.odb.query import out_amqp_list
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

class GetList(AdminService):
    name: Any
    _filter_by: Any
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class Create(AdminService):
    name: Any
    def handle(self: Any) -> None: ...

class Edit(AdminService):
    name: Any
    def handle(self: Any) -> None: ...

class Delete(AdminService):
    name: Any
    def handle(self: Any) -> None: ...

class Publish(AdminService):
    name: Any
    def handle(self: Any) -> None: ...
