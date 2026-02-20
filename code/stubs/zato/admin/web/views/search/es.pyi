from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
import logging
from zato.admin.web.forms.search.es import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.api import SEARCH
from zato.common.odb.model import ElasticSearch


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
