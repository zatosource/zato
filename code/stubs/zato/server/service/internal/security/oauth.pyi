from typing import Any, TYPE_CHECKING

from contextlib import closing
from traceback import format_exc
from uuid import uuid4
from zato.common.api import SEC_DEF_TYPE
from zato.common.broker_message import SECURITY
from zato.common.odb.model import Cluster, OAuth
from zato.common.odb.query import oauth_list
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO
from zato.common.typing_ import any_, anylist


class GetList(AdminService):
    _filter_by: Any
    def get_data(self: Any, session: any_) -> anylist: ...
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
