from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
import logging
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.security.oauth import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.api import NONCE_STORE
from zato.common.odb.model import OAuth

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

def change_secret(req: Any) -> None: ...
