from typing import Any

import logging
from json import dumps
from operator import attrgetter
from traceback import format_exc
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse
from zato.admin.web.forms.groups import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, get_group_list as common_get_group_list, get_security_name_link, Index as _Index, method_allowed
from zato.common.api import Groups, SEC_DEF_TYPE_NAME
from zato.common.model.groups import GroupObject
from zato.common.typing_ import any_, anylist, strdict, strlist, strnone

class Index(_Index):
    method_allowed: Any
    url_name: Any
    template: Any
    service_name: Any
    output_class: Any
    paginate: Any
    def get_initial_input(self: Any) -> strdict: ...
    def handle_return_data(self: Any, return_data: strdict) -> strdict: ...
    def handle(self: Any) -> None: ...

class _CreateEdit(CreateEdit):
    method_allowed: Any
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

def _extract_items_from_response(req: any_, response: any_) -> anylist: ...

def _get_security_list(req: any_, sec_type: strnone | strlist = ..., query: strnone = ...) -> anylist: ...

def _get_member_list(req: any_, group_type: str, group_id: int) -> anylist: ...

def _filter_out_members_from_security_list(security_list: anylist, member_list: anylist) -> anylist: ...

def get_security_list(req: any_) -> HttpResponse: ...

def get_member_list(req: any_) -> HttpResponse: ...

def manage_group_members(req: any_, group_type: str, group_id: str | int) -> HttpResponse: ...

def members_action(req: any_, action: str, group_id: str, member_id_list: str) -> HttpResponse: ...

def get_group_list(req: any_, group_type: str) -> HttpResponse: ...
