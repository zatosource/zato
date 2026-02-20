from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from contextlib import closing
from time import time
from six import add_metaclass
from zato.common.api import SMTPMessage
from zato.common.broker_message import EMAIL
from zato.common.odb.model import SMTP
from zato.common.version import get_version
from zato.common.odb.query import email_smtp_list
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

model = SMTP
broker_message = EMAIL
list_func = email_smtp_list

def instance_hook(service: Any, input: Any, instance: Any, attrs: Any) -> None: ...

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
