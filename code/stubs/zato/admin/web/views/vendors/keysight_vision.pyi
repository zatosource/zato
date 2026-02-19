from typing import Any

from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.vendors.keysight_vision import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, method_allowed, ping_connection
from zato.common.api import Wrapper_Type
from zato.common.model.keysight_ import KeysightVisionConfigObject
from zato.common.typing_ import any_, strdict

class Index(_Index):
    method_allowed: Any
    url_name: Any
    template: Any
    service_name: Any
    output_class: Any
    paginate: Any
    wrapper_type: Any
    def handle(self: Any) -> strdict: ...

class _CreateEdit(CreateEdit):
    method_allowed: Any
    def populate_initial_input_dict(self: Any, initial_input_dict: strdict) -> None: ...
    def success_message(self: Any, item: any_) -> str: ...

class Create(_CreateEdit):
    url_name: Any
    service_name: Any

class Edit(_CreateEdit):
    url_name: Any
    form_prefix: Any
    service_name: Any

class Delete(_Delete):
    url_name: Any
    error_message: Any
    service_name: Any

def change_password(req: any_) -> any_: ...

def ping(req: any_, id: int, cluster_id: int) -> any_: ...
