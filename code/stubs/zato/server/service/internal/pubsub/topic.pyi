from typing import Any, TYPE_CHECKING

from contextlib import closing
from traceback import format_exc
from bunch import Bunch
from zato.common.broker_message import PUBSUB
from zato.common.odb.model import Cluster, PubSubTopic
from zato.common.odb.query import pubsub_topic_list
from zato.common.pubsub.matcher import PatternMatcher
from zato.common.pubsub.util import validate_topic_name
from zato.common.util.sql import elems_with_opaque, set_instance_opaque_attrs
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO


class GetList(AdminService):
    _filter_by: Any
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class Create(AdminService):
    def handle(self: Any) -> None: ...

class Edit(AdminService):
    def handle(self: Any) -> None: ...

class Delete(AdminService):
    def handle(self: Any) -> None: ...

class GetMatches(AdminService):
    def handle(self: Any) -> None: ...
