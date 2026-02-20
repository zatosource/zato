from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from contextlib import closing
from time import time
from uuid import uuid4
from six import add_metaclass
from zato.common.broker_message import OUTGOING
from zato.common.odb.model import OutgoingSAP
from zato.common.odb.query import out_sap_list
from zato.common.util.api import ping_sap
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

model = OutgoingSAP
broker_message = OUTGOING
list_func = out_sap_list

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
