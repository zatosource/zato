from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from base64 import b64decode, b64encode
from bunch import Bunch, bunchify
from django.template.response import TemplateResponse
from zato.admin.web.views import invoke_service_with_json_response, method_allowed
from zato.admin.web.forms.cache.builtin.entry import CreateForm, EditForm
from zato.common.api import CACHE
from zato.common.py23_.past.builtins import unicode

def _create_edit(req: Any, action: Any, id: Any, cluster_id: Any, _KV_DATATYPE: Any = ...) -> None: ...

def create(req: Any, id: Any, cluster_id: Any) -> None: ...

def edit(req: Any, id: Any, cluster_id: Any) -> None: ...

def _create_edit_action_message(action: Any, post: Any, id: Any, cluster_id: Any) -> None: ...

def create_action(req: Any, id: Any, cluster_id: Any) -> None: ...

def edit_action(req: Any, id: Any, cluster_id: Any) -> None: ...
