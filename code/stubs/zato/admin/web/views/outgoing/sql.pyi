from typing import Any

import logging
from traceback import format_exc
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse
from zato.admin.web.views import change_password as _change_password, parse_response_data
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.sql import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, method_allowed
from zato.common.api import engine_display_name
from zato.common.json_internal import dumps
from zato.common.odb.model import SQLConnectionPool

def _get_edit_create_message(params: Any, prefix: Any = ...) -> None: ...

def _edit_create_response(verb: Any, id: Any, name: Any, engine_display_name: Any, cluster_id: Any) -> None: ...

def index(req: Any) -> None: ...

def create(req: Any) -> None: ...

def edit(req: Any) -> None: ...

class Delete(_Delete):
    url_name: Any
    error_message: Any
    service_name: Any

def ping(req: Any, cluster_id: Any, id: Any) -> None: ...

def change_password(req: Any) -> None: ...
