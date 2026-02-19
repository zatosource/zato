from typing import Any

from django.template.response import TemplateResponse
from zato.admin.web.forms.cloud.salesforce import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, invoke_action_handler, method_allowed, ping_connection
from zato.common.api import GENERIC, generic_attrs
from zato.common.model.salesforce import SalesforceConfigObject

class Index(_Index):
    method_allowed: Any
    url_name: Any
    template: Any
    service_name: Any
    output_class: Any
    paginate: Any
    def handle(self: Any) -> None: ...

class _CreateEdit(CreateEdit):
    method_allowed: Any
    def populate_initial_input_dict(self: Any, initial_input_dict: Any) -> None: ...
    def success_message(self: Any, item: Any) -> None: ...

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

def invoke(req: Any, conn_id: Any, max_wait_time: Any, conn_name: Any, conn_slug: Any) -> None: ...

def invoke_action(req: Any, conn_name: Any) -> None: ...

def ping(req: Any, id: Any, cluster_id: Any) -> None: ...
