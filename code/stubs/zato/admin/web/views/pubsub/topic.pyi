from typing import Any

import json
import logging
from django.http import HttpResponse
from zato.admin.web.forms.pubsub.topic import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.odb.model import PubSubTopic

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

def get_matches(req: Any) -> None: ...
