from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
import logging
from django.http import HttpResponse, HttpResponseServerError
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.email.smtp import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, id_only_service, Index as _Index, method_allowed
from zato.common.api import EMAIL
from zato.common.odb.model import SMTP

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

def ping(req: Any, id: Any, cluster_id: Any) -> None: ...

def change_password(req: Any) -> None: ...
