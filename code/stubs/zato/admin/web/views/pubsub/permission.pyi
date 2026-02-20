from typing import Any, TYPE_CHECKING

import logging
from django.http import JsonResponse
from django.views import View
from zato.admin.web.forms.pubsub.permission import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.admin.web.util import get_pubsub_security_definitions
from zato.common.odb.model import PubSubPermission


class Index(_Index):
    method_allowed: Any
    url_name: Any
    template: Any
    service_name: Any
    output_class: Any
    paginate: Any
    def handle(self: Any) -> None: ...

class GetSecurityDefinitions(View):
    url_name: Any
    def get(self: Any, request: Any) -> None: ...

class _CreateEdit(CreateEdit):
    method_allowed: Any
    def get_form_kwargs(self: Any) -> None: ...

class Create(_CreateEdit):
    action: Any
    error_message: Any
    url_name: Any
    service_name: Any
    form_class: Any
    def success_message(self: Any, item: Any) -> None: ...

class Edit(_CreateEdit):
    action: Any
    error_message: Any
    url_name: Any
    service_name: Any
    form_class: Any
    form_prefix: Any
    def success_message(self: Any, item: Any) -> None: ...

class Delete(_Delete):
    url_name: Any
    error_message: Any
    service_name: Any
    def success_message(self: Any, item: Any) -> None: ...
