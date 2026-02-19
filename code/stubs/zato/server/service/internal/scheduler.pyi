from typing import Any

from contextlib import closing
from traceback import format_exc
from zato.common.api import scheduler_date_time_format, SCHEDULER, ZATO_NONE
from zato.common.broker_message import SCHEDULER as SCHEDULER_MSG
from zato.common.exception import ServiceMissingException, ZatoException
from zato.common.odb.model import Cluster, Job, IntervalBasedJob, Service as ODBService
from zato.common.odb.query import job_by_id, job_by_name, job_list
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from zato.common.util.api import parse_datetime
from dateutil.parser import parse as parse_datetime

def _create_edit(action: Any, cid: Any, input: Any, payload: Any, logger: Any, session: Any, broker_client: Any, response: Any, should_ignore_existing: Any) -> None: ...

class _CreateEdit(AdminService):
    def handle(self: Any) -> None: ...

class _Get(AdminService):
    ...

class GetList(_Get):
    _filter_by: Any
    name: Any
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class GetByID(_Get):
    name: Any
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class GetByName(_Get):
    name: Any
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class Create(_CreateEdit):
    name: Any

class Edit(_CreateEdit):
    name: Any

class Delete(AdminService):
    name: Any
    def handle(self: Any) -> None: ...

class Execute(AdminService):
    name: Any
    def handle(self: Any) -> None: ...
