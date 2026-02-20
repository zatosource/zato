from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms
from zato.admin.web.forms import add_select_from_service


class CreateForm(forms.Form):
    name: Any
    is_active: Any
    engine: Any
    host: Any
    port: Any
    db_name: Any
    username: Any
    pool_size: Any
    extra: Any
    def __init__(self: Any, req: Any, prefix: Any = ..., post_data: Any = ...) -> None: ...

class EditForm(CreateForm):
    is_active: Any
