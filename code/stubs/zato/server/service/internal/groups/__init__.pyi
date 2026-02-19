from typing import Any

from json import dumps
from operator import itemgetter
from zato.common.api import CONNECTION, Groups
from zato.common.broker_message import Groups as Broker_Message_Groups
from zato.common.odb.model import GenericObject as ModelGenericObject
from zato.server.service import AsIs, Service
from zato.common.typing_ import any_, strlist

class GetList(Service):
    input: any_
    def handle(self: Any) -> None: ...

class Create(Service):
    input: any_
    output: any_
    def handle(self: Any) -> None: ...

class Edit(Service):
    input: any_
    output: any_
    def handle(self: Any) -> None: ...

class Delete(Service):
    input: any_
    def handle(self: Any) -> None: ...

class GetMemberList(Service):
    input: any_
    def handle(self: Any) -> None: ...

class GetMemberCount(Service):
    input: any_
    def handle(self: Any) -> None: ...

class EditMemberList(Service):
    input: any_
    def _get_member_id_list_from_name_list(self: Any, member_name_list: any_) -> strlist: ...
    def handle(self: Any) -> None: ...
