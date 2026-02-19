from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from smtplib import SMTP_PORT
from django import forms
from zato.common.api import EMAIL

class CreateForm(forms.Form):
    id: Any
    name: Any
    is_active: Any
    host: Any
    port: Any
    timeout: Any
    is_debug: Any
    username: Any
    mode: Any
    ping_address: Any
    def __init__(self: Any, prefix: Any = ..., post_data: Any = ...) -> None: ...

class EditForm(CreateForm):
    is_active: Any
    is_debug: Any
