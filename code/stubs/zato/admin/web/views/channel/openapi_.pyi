from typing import Any

import logging
import os
from json import dumps, loads
from traceback import format_exc
from django.http import HttpResponse, HttpResponseServerError
from zato.admin.web.forms.channel.openapi import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.api import CONNECTION, GENERIC, generic_attrs, URL_TYPE
from zato.common.util.openapi_.exporter import build_openapi_spec as _build_openapi_spec

def get_openapi_path_prefix() -> None: ...

def build_openapi_spec(req: Any, cluster_id: Any, channel_name: Any, rest_channel_list: Any) -> None: ...

class OpenAPIChannelConfigObject:
    _config_attrs: Any
    id: Any
    name: Any
    is_active: Any
    is_public: Any
    url_path: Any
    rest_channel_list: Any
    def __init__(self: Any) -> None: ...
    @property
    def rest_channel_list_json(self: Any) -> None: ...
    @property
    def channel_count(self: Any) -> None: ...

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
    def pre_process_input_dict(self: Any, input_dict: Any) -> None: ...
    def success_message(self: Any, item: Any) -> None: ...
    def post_process_return_data(self: Any, return_data: Any) -> None: ...

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

def generate_openapi(req: Any) -> None: ...

def get_rest_channels(req: Any) -> None: ...
