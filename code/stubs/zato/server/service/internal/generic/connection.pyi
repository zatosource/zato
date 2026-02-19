from typing import Any

from contextlib import closing
from copy import deepcopy
from datetime import datetime
from traceback import format_exc
from uuid import uuid4
from zato.common.api import GENERIC as COMMON_GENERIC, generic_attrs, SEC_DEF_TYPE, SEC_DEF_TYPE_NAME, ZATO_NONE
from zato.common.broker_message import GENERIC
from zato.common.json_internal import dumps, loads
from zato.common.odb.model import GenericConn as ModelGenericConn
from zato.common.odb.query.generic import connection_list
from zato.common.typing_ import cast_
from zato.common.util.api import parse_simple_type
from zato.common.util.config import replace_query_string_items_in_dict
from zato.common.util.time_ import utcnow
from zato.server.generic.connection import GenericConnection
from zato.server.service import AsIs, Int
from zato.server.service.internal import AdminService, AdminSIO, ChangePasswordBase, GetListAdminSIO
from zato.server.service.internal.generic import _BaseService
from zato.server.service.meta import DeleteMeta
from six import add_metaclass
from bunch import Bunch
from zato.common.typing_ import any_, anydict, anylist, strdict
from zato.server.service import Service
from json import dumps, loads
from urllib.parse import parse_qs, urlsplit
from O365 import Account

def ensure_ints(data: strdict) -> None: ...

class _CreateEditSIO(AdminSIO):
    input_required: Any
    input_optional: Any
    force_empty_keys: Any

class _CreateEdit(_BaseService):
    is_create: bool
    is_edit: bool
    def handle(self: Any) -> None: ...

class Create(_CreateEdit):
    is_create: Any
    is_edit: Any

class Edit(_CreateEdit):
    is_create: Any
    is_edit: Any

class Delete(AdminService):
    ...

class GetList(AdminService):
    _filter_by: Any
    def get_data(self: Any, session: any_) -> any_: ...
    def _add_custom_conn_dict_fields(self: Any, conn_dict: anydict) -> None: ...
    def _enrich_conn_dict(self: Any, conn_dict: anydict) -> None: ...
    def handle(self: Any) -> None: ...

class ChangePassword(ChangePasswordBase):
    password_required: Any
    def _run_pre_handle_tasks_CLOUD_MICROSOFT_365(self: Any, session: any_, instance: any_) -> None: ...
    def _run_pre_handle_tasks(self: Any, session: any_, instance: any_) -> None: ...
    def handle(self: Any) -> None: ...

class Ping(_BaseService):
    def handle(self: Any) -> None: ...

class Invoke(AdminService):
    def handle(self: Any) -> None: ...
