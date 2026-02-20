from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
import logging
from traceback import format_exc
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse
from zato.admin.settings import delivery_friendly_name
from zato.admin.web.forms.outgoing.amqp_ import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, Index as _Index, invoke_action_handler, method_allowed
from zato.common.json_internal import dumps
from zato.common.odb.model import OutgoingAMQP


def _get_edit_create_message(params: Any, prefix: Any = ...) -> None: ...

def _edit_create_response(verb: Any, id: Any, name: Any, delivery_mode_text: Any) -> None: ...

class Index(_Index):
    method_allowed: Any
    url_name: Any
    template: Any
    service_name: Any
    output_class: Any
    paginate: Any
    def handle(self: Any) -> None: ...

def create(req: Any) -> None: ...

def edit(req: Any) -> None: ...

class Delete(_Delete):
    url_name: Any
    error_message: Any
    service_name: Any

def invoke(req: Any, conn_id: Any, conn_name: Any, conn_slug: Any) -> None: ...

def invoke_action(req: Any, conn_name: Any) -> None: ...
