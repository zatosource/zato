from typing import Any

import logging
import os
from operator import itemgetter
from traceback import format_exc
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template.response import TemplateResponse
from zato.admin.web.forms.http_soap import SearchForm, CreateForm, EditForm
from zato.admin.web.views import get_group_list as common_get_group_list, get_http_channel_security_id, get_security_id_from_select, get_security_groups_from_checkbox_list, id_only_service, method_allowed, parse_response_data, SecurityList
from zato.common.api import CACHE, DATA_FORMAT, DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, generic_attrs, Groups, HTTP_SOAP_SERIALIZATION_TYPE, MISC, PARAMS_PRIORITY, SEC_DEF_TYPE, SOAP_CHANNEL_VERSIONS, SOAP_VERSIONS, URL_PARAMS_PRIORITY, URL_TYPE
from zato.common.exception import ZatoException
from zato.common.json_internal import dumps
from zato.common.odb.model import HTTPSOAP
from zato.common.util import openapi_ as openapi_module

def _get_edit_create_message(params: Any, prefix: Any = ...) -> None: ...

def _edit_create_response(req: Any, id: Any, verb: Any, transport: Any, connection: Any, name: Any) -> None: ...

def index(req: Any) -> None: ...

def create(req: Any) -> None: ...

def edit(req: Any) -> None: ...

def delete(req: Any, id: Any, cluster_id: Any) -> None: ...

def ping(req: Any, id: Any, cluster_id: Any) -> None: ...

def reload_wsdl(req: Any, id: Any, cluster_id: Any) -> None: ...
