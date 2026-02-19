from typing import Any

from django import forms
from zato.common.api import Microsoft365 as Microsoft365Common

class CreateForm(forms.Form):
    name: Any
    is_active: Any
    tenant_id: Any
    client_id: Any
    secret_value: Any
    scopes: Any

class EditForm(CreateForm):
    is_active: Any
