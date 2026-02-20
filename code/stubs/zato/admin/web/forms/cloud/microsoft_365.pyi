from typing import Any, TYPE_CHECKING

from django import forms
from zato.common.api import Microsoft365 as Microsoft365Common

_default = Microsoft365Common.Default

class CreateForm(forms.Form):
    name: Any
    is_active: Any
    tenant_id: Any
    client_id: Any
    secret_value: Any
    scopes: Any

class EditForm(CreateForm):
    is_active: Any
