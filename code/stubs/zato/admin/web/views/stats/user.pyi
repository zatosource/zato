from typing import Any, TYPE_CHECKING

import logging
from enum import Enum, unique
from json import dumps, loads
from bunch import Bunch
from django.http import HttpResponse
from zato.admin.web.views import Index as _Index
from zato.common.typing_ import cast_
from django.core.handlers.wsgi import WSGIRequest
from zato.common.typing_ import any_

default_action = Action.Index.value

class BaseEnum(Enum):
    @classmethod
    def has_value(cls: any_, value: str) -> bool: ...

class Action(BaseEnum):
    Index: Any
    BrowseStats: Any
    DisplayStats: Any
    CompareStats: Any

class Index(_Index):
    method_allowed: Any
    url_name: Any
    paginate: Any
    clear_self_items: Any
    update_request_with_self_input: Any
    def before_invoke_admin_service(self: Any) -> None: ...
    def should_extract_top_level(self: Any, _keys: Any) -> None: ...
    def handle_item_list(self: Any, item_list: Any, is_extracted: Any) -> None: ...
    def get_initial_input(self: Any) -> None: ...
    def on_after_set_input(self: Any) -> None: ...
    def get_output_class(self: Any) -> any_: ...
    def get_service_name(self: Any, _: WSGIRequest) -> str: ...
    def get_template_name(self: Any) -> None: ...
    def _handle_item(self: Any, item: any_) -> any_: ...
    def handle_return_data(self: Any, return_data: any_) -> any_: ...

def get_updates(req: Any) -> None: ...
