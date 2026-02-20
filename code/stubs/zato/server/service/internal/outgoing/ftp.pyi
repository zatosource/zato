from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from contextlib import closing
from traceback import format_exc
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import OutgoingFTP
from zato.common.odb.query import out_ftp, out_ftp_list
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service import Boolean
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO


class _FTPService(AdminService):
    def notify_worker_threads(self: Any, params: Any, action: Any = ...) -> None: ...

class GetByID(AdminService):
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class GetList(AdminService):
    _filter_by: Any
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class Create(_FTPService):
    def handle(self: Any) -> None: ...

class Edit(_FTPService):
    def handle(self: Any) -> None: ...

class Delete(_FTPService):
    def handle(self: Any) -> None: ...

class ChangePassword(ChangePasswordBase):
    def handle(self: Any) -> None: ...
