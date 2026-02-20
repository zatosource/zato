from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from ftplib import FTP_PORT
from django import forms


class CreateForm(forms.Form):
    name: Any
    is_active: Any
    host: Any
    port: Any
    user: Any
    acct: Any
    timeout: Any
    dircache: Any
    default_directory: Any
    def __init__(self: Any, prefix: Any = ..., post_data: Any = ...) -> None: ...

class EditForm(CreateForm):
    is_active: Any
    dircache: Any
