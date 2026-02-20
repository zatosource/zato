from typing import Any, TYPE_CHECKING

import logging
from collections import namedtuple
from http import HTTPStatus
from json import dumps, loads
from traceback import format_exc
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.template.response import TemplateResponse
from zato.admin.web import from_utc_to_user
from zato.admin.web.forms.service import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed, upload_to_server
from zato.admin.middleware import HeadersEnrichedException
from zato.common.ext.validate_ import is_boolean
from zato.common.odb.model import Service
from zato.common.typing_ import any_, anylist
import json


def _get_channels(client: any_, cluster: any_, id: str, channel_type: str) -> anylist: ...

class Index(_Index):
    method_allowed: Any
    url_name: Any
    template: Any
    service_name: Any
    output_class: Any
    paginate: Any
    def handle(self: Any) -> None: ...
    def handle_return_data(self: Any, return_data: any_) -> any_: ...

def create(req: any_) -> None: ...

class Edit(CreateEdit):
    method_allowed: Any
    url_name: Any
    form_prefix: Any
    service_name: Any
    def success_message(self: Any, item: any_) -> str: ...

def overview(req: HttpRequest, service_name: str) -> TemplateResponse: ...

class Delete(_Delete):
    url_name: Any
    error_message: Any
    service_name: Any

def upload(req: HttpRequest) -> any_: ...

def invoke(req: HttpRequest, name: str, cluster_id: str) -> HttpResponse: ...

def enmasse_export(req: Any) -> None: ...

def enmasse_import(req: Any) -> None: ...

def import_test_config(req: Any) -> None: ...

def download_openapi(req: Any) -> None: ...
