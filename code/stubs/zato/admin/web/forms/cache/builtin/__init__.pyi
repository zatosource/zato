from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms
from zato.common.api import CACHE
from zato.admin.web.forms import add_select

class CreateForm(forms.Form):
    id: Any
    name: Any
    is_active: Any
    is_default: Any
    max_size: Any
    max_item_size: Any
    extend_expiry_on_get: Any
    extend_expiry_on_set: Any
    sync_method: Any
    persistent_storage: Any
    id: Any
    def __init__(self: Any, prefix: Any = ..., post_data: Any = ..., req: Any = ...) -> None: ...

class EditForm(CreateForm):
    is_active: Any
    is_default: Any
    extend_expiry_on_get: Any
    extend_expiry_on_set: Any
