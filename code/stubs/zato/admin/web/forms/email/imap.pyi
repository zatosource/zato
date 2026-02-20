from typing import Any, TYPE_CHECKING

from imaplib import IMAP4_SSL_PORT
from django import forms
from zato.common.api import EMAIL


class CreateForm(forms.Form):
    id: Any
    name: Any
    is_active: Any
    server_type: Any
    host: Any
    port: Any
    timeout: Any
    debug_level: Any
    username: Any
    mode: Any
    get_criteria: Any
    tenant_id: Any
    client_id: Any
    filter_criteria: Any
    def __init__(self: Any, prefix: Any = ..., post_data: Any = ...) -> None: ...

class EditForm(CreateForm):
    is_active: Any
