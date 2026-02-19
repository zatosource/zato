from typing import Any

import logging
from traceback import format_exc
from django.http import HttpResponse, HttpResponseServerError
from zato.admin.web.forms.channel.amqp_ import CreateForm, EditForm
from zato.admin.web.views import Delete as _Delete, Index as _Index, method_allowed
from zato.common.json_internal import dumps
from zato.common.odb.model import ChannelAMQP

def _get_edit_create_message(params: Any, prefix: Any = ...) -> None: ...

def _edit_create_response(client: Any, verb: Any, id: Any, name: Any) -> None: ...

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
