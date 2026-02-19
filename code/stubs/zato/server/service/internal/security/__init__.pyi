from typing import Any

from contextlib import closing
from zato.common.api import SEC_DEF_TYPE
from zato.common.const import ServiceConst
from zato.common.odb import query
from zato.common.odb.model import SecurityBase
from zato.server.service import Boolean, Integer, List
from zato.server.service.internal import AdminService, GetListAdminSIO
from zato.common.typing_ import any_

class GetByID(AdminService):
    def handle(self: Any) -> None: ...

class GetList(AdminService):
    def handle(self: Any) -> None: ...
