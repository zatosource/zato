from typing import Any

import logging
from contextlib import closing
from copy import deepcopy
from json import loads
from traceback import format_exc
from zato.common.py23_.past.builtins import basestring
from zato.common.api import SECRET_SHADOW, ZATO_NONE
from zato.common.broker_message import MESSAGE_TYPE, SECURITY
from zato.common.odb.model import Cluster
from zato.common.util.api import get_response_value, make_cid_public
from zato.common.util.sql import search as sql_search
from zato.server.service import AsIs, Bool, Int, Service
from zato.common.typing_ import anylist

class SearchTool:
    _search_attrs: Any
    def __init__(self: Any, *criteria: Any) -> None: ...
    def __nonzero__(self: Any) -> None: ...
    def set_output_meta(self: Any, result: Any) -> None: ...

class AdminSIO:
    ...

class GetListAdminSIO:
    input_optional: Any

class AdminService(Service):
    output_optional: Any
    skip_before_handle: Any
    def __init__(self: Any) -> None: ...
    def _init(self: Any, is_http: Any) -> None: ...
    def before_handle(self: Any) -> None: ...
    def handle(self: Any, *args: Any, **kwargs: Any) -> None: ...
    def _new_zato_instance_with_cluster(self: Any, instance_class: Any, cluster_id: Any = ..., **kwargs: Any) -> None: ...
    def after_handle(self: Any) -> None: ...
    def get_data(self: Any, *args: Any, **kwargs: Any) -> None: ...
    def _search(self: Any, search_func: Any, session: Any = ..., cluster_id: Any = ..., *args: Any, **kwargs: Any) -> anylist: ...

class Ping(AdminService):
    name: Any
    def handle(self: Any) -> None: ...

class ServerInvoker(AdminService):
    name: Any
    def handle(self: Any) -> None: ...

class ChangePasswordBase(AdminService):
    password_required: Any
    def _handle(self: Any, class_: Any, auth_func: Any, action: Any, name_func: Any = ..., instance_id: Any = ..., msg_type: Any = ..., *args: Any, **kwargs: Any) -> None: ...
