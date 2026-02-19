from typing import Any

from contextlib import closing
from time import time
from six import add_metaclass
from zato.common.api import EMAIL as EMail_Common, Zato_None
from zato.common.broker_message import EMAIL
from zato.common.odb.model import IMAP
from zato.common.odb.query import email_imap_list
from zato.server.service import AsIs
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta
from bunch import Bunch
from zato.common.typing_ import any_
from zato.server.service import Service

def instance_hook(service: Service, input: Bunch, instance: any_, attrs: any_) -> None: ...

def response_hook(service: Service, input: Bunch, instance: any_, attrs: any_, hook_type: str) -> None: ...

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
