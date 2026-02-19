from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from contextlib import closing
from traceback import format_exc
from six import add_metaclass
from zato.common.exception import ZatoException
from zato.common.odb.model import Server
from zato.common.odb.query import server_list
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.meta import GetListMeta

def response_hook(self: Any, input: Any, _ignored_instance: Any, attrs: Any, service_type: Any) -> None: ...

class GetList(AdminService):
    _filter_by: Any

class Edit(AdminService):
    def handle(self: Any) -> None: ...

class GetByID(AdminService):
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class Delete(AdminService):
    def handle(self: Any) -> None: ...
