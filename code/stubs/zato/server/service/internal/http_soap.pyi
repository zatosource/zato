from typing import Any, TYPE_CHECKING

from contextlib import closing
from traceback import format_exc
from zato.common.api import CONNECTION, DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, Groups, HTTP_SOAP_SERIALIZATION_TYPE, MISC, PARAMS_PRIORITY, SEC_DEF_TYPE, URL_PARAMS_PRIORITY, URL_TYPE, ZATO_NONE
from zato.common.broker_message import CHANNEL, OUTGOING
from zato.common.exception import ServiceMissingException
from zato.common.json_internal import dumps
from zato.common.odb.model import Cluster, HTTPSOAP, SecurityBase, Service
from zato.common.odb.query import cache_by_id, http_soap, http_soap_list
from zato.common.util.api import as_bool
from zato.common.util.sql import elems_with_opaque, get_dict_with_opaque, get_security_by_id, parse_instance_opaque_attr, set_instance_opaque_attrs
from zato.server.connection.http_soap import BadRequest
from zato.server.service import AsIs, Boolean, Integer
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from zato.common.typing_ import any_, anylist, strdict, strintdict


class _HTTPSOAPService:
    def notify_worker_threads(self: Any, params: Any, action: Any) -> None: ...
    def _handle_security_info(self: Any, session: Any, security_id: Any, connection: Any, transport: Any) -> None: ...

class _BaseGet(AdminService):
    def _get_security_groups_info(self: Any, item: any_, security_groups_member_count: strintdict) -> strdict: ...

class Get(_BaseGet):
    def handle(self: Any) -> None: ...

class GetList(_BaseGet):
    _filter_by: Any
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class _CreateEdit(AdminService, _HTTPSOAPService):
    def _raise_error(self: Any, name: Any, url_path: Any, http_accept: Any, http_method: Any, soap_action: Any, source: Any) -> None: ...
    def ensure_channel_is_unique(self: Any, session: Any, url_path: Any, http_accept: Any, http_method: Any, soap_action: Any, cluster_id: Any) -> None: ...
    def _preprocess_security_groups(self: Any, input: Any) -> None: ...
    def _get_service_from_input(self: Any, session: Any, input: Any) -> None: ...

class Create(_CreateEdit):
    def handle(self: Any) -> None: ...

class Edit(_CreateEdit):
    def handle(self: Any) -> None: ...

class Delete(AdminService, _HTTPSOAPService):
    def handle(self: Any) -> None: ...

class Ping(AdminService):
    def handle(self: Any) -> None: ...

class GetURLSecurity(AdminService):
    def handle(self: Any) -> None: ...
