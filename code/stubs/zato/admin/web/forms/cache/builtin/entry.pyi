from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms
from zato.common.api import CACHE
from zato.admin.web.forms import add_select


class CreateForm(forms.Form):
    id: Any
    key: Any
    value: Any
    expiry: Any
    replace_existing: Any
    cache_id: Any
    key_data_type: Any
    value_data_type: Any
    def __init__(self: Any, post_data: Any = ..., req: Any = ...) -> None: ...

class EditForm(CreateForm):
    replace_existing: Any
    old_key: Any
