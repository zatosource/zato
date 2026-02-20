from typing import Any, TYPE_CHECKING

from contextlib import closing
from traceback import format_exc
from zato.common.broker_message import CHANNEL
from zato.common.exception import ServiceMissingException
from zato.common.odb.model import ChannelAMQP, Cluster, Service
from zato.common.odb.query import channel_amqp_list
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
