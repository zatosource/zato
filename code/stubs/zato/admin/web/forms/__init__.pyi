from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms
from zato.common.ext.future.utils import iteritems
from zato.common.py23_.past.builtins import basestring
from zato.common.api import SIMPLE_IO, ZATO_NONE

INITIAL_CHOICES = list[Any]

def add_initial_select(form: Any, field_name: Any) -> None: ...

def add_select(form: Any, field_name: Any, elems: Any, needs_initial_select: Any = ..., skip: Any = ...) -> None: ...

def add_security_select(form: Any, security_list: Any, needs_no_security: Any = ..., field_name: Any = ...) -> None: ...

def add_http_soap_select(form: Any, field_name: Any, req: Any, connection: Any, transport: Any, needs_initial_select: Any = ..., skip: Any = ...) -> None: ...

def add_services(form: Any, req: Any, by_id: Any = ..., initial_service: Any = ..., api_name: Any = ..., has_name_filter: Any = ..., should_include_scheduler: Any = ...) -> None: ...

def add_select_from_service(form: Any, req: Any, service_name: Any, field_names: Any, by_id: Any = ..., service_extra: Any = ...) -> None: ...

class SearchForm(forms.Form):
    cluster: Any
    query: Any
    zato_auto_submit: Any
    def __init__(self: Any, clusters: Any, data: Any = ...) -> None: ...

class ChangePasswordForm(forms.Form):
    password1: Any
    password2: Any

class DataFormatForm(forms.Form):
    data_format: Any
    data_formats_allowed: Any
    def __init__(self: Any, *args: Any, **kwargs: Any) -> None: ...

class UploadForm(forms.Form):
    file: Any
