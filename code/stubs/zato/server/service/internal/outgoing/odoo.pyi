from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from six import add_metaclass
from contextlib import closing
from time import time
from uuid import uuid4
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import OutgoingOdoo
from zato.common.odb.query import out_odoo_list
from zato.common.util.api import ping_odoo
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

def instance_hook(service: Any, input: Any, instance: Any, attrs: Any) -> None: ...

def broker_message_hook(service: Any, input: Any, instance: Any, attrs: Any, service_type: Any) -> None: ...

class GetList(AdminService):
    _filter_by: Any

class Create(AdminService):
    ...

class Edit(AdminService):
    ...

class Delete(AdminService):
    ...

class ChangePassword(ChangePasswordBase):
    password_required: Any
    def handle(self: Any) -> None: ...

class Ping(AdminService):
    def handle(self: Any) -> None: ...
