from typing import Any

from django import forms
from zato.admin.web.forms import add_security_select, add_select, add_services, SearchForm as _ChooseClusterForm, DataFormatForm
from zato.common.api import DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, HTTP_SOAP, HTTP_SOAP_SERIALIZATION_TYPE, MISC, PARAMS_PRIORITY, SIMPLE_IO, SOAP_VERSIONS, URL_PARAMS_PRIORITY

class CreateForm(DataFormatForm):
    name: Any
    is_active: Any
    host: Any
    url_path: Any
    match_slash: Any
    merge_url_params_req: Any
    url_params_pri: Any
    params_pri: Any
    serialization_type: Any
    method: Any
    soap_action: Any
    soap_version: Any
    service: Any
    ping_method: Any
    pool_size: Any
    timeout: Any
    security: Any
    content_type: Any
    connection: Any
    transport: Any
    cache_id: Any
    cache_expiry: Any
    content_encoding: Any
    data_formats_allowed: Any
    http_accept: Any
    validate_tls: Any
    data_encoding: Any
    def __init__(self: Any, security_list: Any = ..., cache_list: Any = ..., soap_versions: Any = ..., prefix: Any = ..., post_data: Any = ..., req: Any = ...) -> None: ...

class EditForm(CreateForm):
    is_active: Any
    merge_url_params_req: Any
    match_slash: Any

class SearchForm(_ChooseClusterForm):
    connection: Any
    transport: Any
    def __init__(self: Any, clusters: Any, data: Any = ...) -> None: ...
