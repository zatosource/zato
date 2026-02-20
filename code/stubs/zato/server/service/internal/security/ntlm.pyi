from typing import Any, TYPE_CHECKING

from contextlib import closing
from traceback import format_exc
from uuid import uuid4
from zato.common.api import SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import Cluster, NTLM
from zato.common.odb.query import ntlm_list
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO
from zato.common.typing_ import any_


class GetList(AdminService):
    _filter_by: Any
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class Create(AdminService):
    def handle(self: Any) -> None: ...

class Edit(AdminService):
    def handle(self: Any) -> None: ...

class ChangePassword(ChangePasswordBase):
    password_required: Any
    def handle(self: Any) -> None: ...

class Delete(AdminService):
    def handle(self: Any) -> None: ...
