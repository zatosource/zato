from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from zato.common.ext.dictalchemy.utils import asdict
from six import add_metaclass
from zato.common.api import CACHE as _COMMON_CACHE
from zato.common.broker_message import CACHE
from zato.common.odb.model import CacheBuiltin
from zato.common.odb.query import cache_builtin_list
from zato.server.service import Bool, Int
from zato.server.service.internal import AdminService, AdminSIO
from zato.server.service.internal.cache import common_instance_hook
from zato.server.service.meta import CreateEditMeta, DeleteMeta, GetListMeta

model = CacheBuiltin
broker_message = CACHE
list_func = cache_builtin_list

def instance_hook(self: Any, input: Any, instance: Any, attrs: Any) -> None: ...

def response_hook(self: Any, input: Any, _ignored: Any, attrs: Any, service_type: Any) -> None: ...

def broker_message_hook(self: Any, input: Any, instance: Any, attrs: Any, service_type: Any) -> None: ...

class Get(AdminService):
    def handle(self: Any) -> None: ...

class GetList(AdminService):
    _filter_by: Any

class Create(AdminService):
    ...

class Edit(AdminService):
    ...

class Delete(AdminService):
    ...

class Clear(AdminService):
    def handle(self: Any) -> None: ...
