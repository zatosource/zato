from typing import Any, TYPE_CHECKING

import os
import subprocess
from base64 import b64decode, b64encode
from contextlib import closing
from operator import attrgetter
from traceback import format_exc
from uuid import uuid4
from builtins import bytes
from zato.common.ext.future.utils import iterkeys
from zato.common.api import BROKER, SCHEDULER
from zato.common.broker_message import SERVICE
from zato.common.const import ServiceConst
from zato.common.exception import BadRequest, ZatoException
from zato.common.ext.validate_ import is_boolean
from zato.common.json_ import dumps as json_dumps
from zato.common.json_internal import dumps, loads
from zato.common.marshal_.api import Model
from zato.common.odb.model import Cluster, ChannelAMQP, DeployedService, HTTPSOAP, Server, Service as ODBService
from zato.common.odb.query import service_deployment_list, service_list
from zato.common.scheduler import get_startup_job_services
from zato.common.util.api import hot_deploy, parse_extra_into_dict, payload_from_request
from zato.common.util.file_system import get_tmp_path
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service import Boolean, Integer, Service
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from datetime import datetime
from zato.common.typing_ import any_, anydict, strnone

Service = Service

class GetList(AdminService):
    _filter_by: Any
    def _get_data(self: Any, session: Any, return_internal: Any, include_list: Any, internal_del: Any) -> None: ...
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class IsDeployed(Service):
    input: Any
    output: Any
    def handle(self: Any) -> None: ...

class _Get(AdminService):
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class GetByName(_Get):
    def add_filter(self: Any, query: Any) -> None: ...

class GetByID(_Get):
    def add_filter(self: Any, query: Any) -> None: ...

class Edit(AdminService):
    def handle(self: Any) -> None: ...

class Delete(AdminService):
    def handle(self: Any) -> None: ...

class GetChannelList(AdminService):
    def handle(self: Any) -> None: ...

class Invoke(AdminService):
    def _get_payload_from_extra(self: Any, payload: any_) -> strnone: ...
    def _invoke_other_server_pid(self: Any, name: str, payload: any_, pid: int, data_format: str, skip_response_elem: bool) -> any_: ...
    def _invoke_current_server_pid(self: Any, id: any_, name: str, all_pids: bool, payload: any_, channel: str, data_format: str, transport: str, zato_response_headers_container: anydict, skip_response_elem: bool) -> any_: ...
    def _build_response(self: Any, response: any_) -> any_: ...
    def _run_async_invoke(self: Any, pid: int, id: any_, name: str, payload: any_, channel: str, data_format: str, transport: str, expiration: int) -> any_: ...
    def _run_sync_invoke(self: Any, pid: int, timeout: int, id: any_, name: str, all_pids: bool, payload: any_, channel: str, data_format: str, transport: str, zato_response_headers_container: anydict, skip_response_elem: bool) -> any_: ...
    def _build_response_time(self: Any, start_time: datetime) -> any_: ...
    def handle(self: Any) -> None: ...

class GetDeploymentInfoList(AdminService):
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class GetSourceInfo(AdminService):
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class UploadPackage(AdminService):
    def handle(self: Any) -> None: ...

class ServiceInvoker(AdminService):
    name: Any
    def _extract_payload_from_request(self: Any) -> None: ...
    def handle(self: Any, _internal: Any = ...) -> None: ...

class RPCServiceInvoker(AdminService):
    def handle(self: Any) -> None: ...
