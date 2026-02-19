from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms
from zato.common.api import ODOO

class CreateForm(forms.Form):
    name: Any
    is_active: Any
    host: Any
    port: Any
    user: Any
    database: Any
    protocol: Any
    pool_size: Any
    def __init__(self: Any, prefix: Any = ..., post_data: Any = ...) -> None: ...

class EditForm(CreateForm):
    ...
