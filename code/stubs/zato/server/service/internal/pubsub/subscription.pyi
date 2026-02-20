from typing import Any, TYPE_CHECKING

from contextlib import closing
from operator import itemgetter
from traceback import format_exc
from urllib.parse import quote
from bunch import Bunch, bunchify
from zato.common.broker_message import PUBSUB
from zato.common.api import PubSub
from zato.common.odb.model import Cluster, HTTPSOAP, PubSubSubscription, PubSubSubscriptionTopic, PubSubTopic, SecurityBase
from zato.common.odb.query import pubsub_subscription_list
from zato.common.pubsub.util import evaluate_pattern_match, get_security_definition, set_time_since
from zato.common.util.api import as_bool, new_sub_key, utcnow
from zato.common.util.sql import elems_with_opaque
from zato.server.service import AsIs, PubSubMessage, Service
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO
from bunch import Bunch
from zato.common.typing_ import strdict, strlist

_push_type = PubSub.Push_Type

def _build_topic_objects_list(topic_data_list: Any = ..., topics: Any = ..., topic_data_by_name: Any = ...) -> None: ...

class ModuleCtx:
    Action_Subsctibe: Any
    Action_Unsubsctibe: Any

def get_topic_link(topic_name: str, is_pub_enabled: bool, is_delivery_enabled: bool) -> str: ...

class GetList(AdminService):
    _filter_by: Any
    def get_data(self: Any, session: Any) -> None: ...
    def handle(self: Any) -> None: ...

class Create(AdminService):
    def handle(self: Any) -> None: ...

class Edit(AdminService):
    def handle(self: Any) -> None: ...

class Delete(AdminService):
    skip_before_handle: Any
    def handle(self: Any) -> None: ...

class _BaseModifyTopicList(AdminService):
    action: Any
    def _modify_topic_list(self: Any, existing_topic_names: strlist, new_topic_names: strlist) -> strlist: ...
    def _get_subscriptions_by_sec(self: Any, cluster_id: Any, sec_base_id: Any) -> None: ...
    def handle(self: Any) -> None: ...

class Subscribe(_BaseModifyTopicList):
    action: Any
    def _modify_topic_list(self: Any, existing_topic_names: strlist, new_topic_names: strlist) -> strlist: ...

class Unsubscribe(_BaseModifyTopicList):
    action: Any
    def _modify_topic_list(self: Any, existing_topic_names: strlist, new_topic_names: strlist) -> strlist: ...

class HandleDelivery(Service):
    def build_business_message(self: Any, input: strdict, sub_key: str, delivery_count: int) -> PubSubMessage: ...
    def build_rest_message(self: Any, input: strdict, outconn_config: strdict) -> strdict: ...
    def handle(self: Any) -> None: ...
