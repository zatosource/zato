from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms
from zato.common.api import SAP


class CreateForm(forms.Form):
    name: Any
    is_active: Any
    host: Any
    sysnr: Any
    sysid: Any
    user: Any
    client: Any
    router: Any
    pool_size: Any
    def __init__(self: Any, prefix: Any = ..., post_data: Any = ...) -> None: ...

class EditForm(CreateForm):
    is_active: Any
