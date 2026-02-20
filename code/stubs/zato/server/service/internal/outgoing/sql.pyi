from typing import Any, TYPE_CHECKING

from contextlib import closing
from operator import itemgetter
from traceback import format_exc
from uuid import uuid4
from zato.common.py23_.past.builtins import unicode
from zato.common.api import ZATO_ODB_POOL_NAME
from zato.common.exception import ZatoException
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import Cluster, SQLConnectionPool
from zato.common.odb.query import out_sql_list
from zato.common.util.api import get_sql_engine_display_name
from zato.server.service import AsIs, Integer
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO


class _SQLService:
    def notify_worker_threads(self: Any, params: Any, action: Any = ...) -> None: ...
    def validate_extra(self: Any, cid: Any, extra: Any) -> None: ...

class GetList(AdminService):
    _filter_by: Any
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class Create(AdminService, _SQLService):
    def handle(self: Any) -> None: ...

class Edit(AdminService, _SQLService):
    def handle(self: Any) -> None: ...

class Delete(AdminService, _SQLService):
    def handle(self: Any) -> None: ...

class ChangePassword(ChangePasswordBase):
    def handle(self: Any) -> None: ...

class Ping(AdminService):
    def handle(self: Any) -> None: ...

class AutoPing(AdminService):
    def handle(self: Any) -> None: ...

class GetEngineList(AdminService):
    def get_data(self: Any) -> None: ...
    def handle(self: Any) -> None: ...
