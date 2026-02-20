from typing import Any, TYPE_CHECKING

from django import forms
from zato.common.api import OAuth as OAuthCommon, SIMPLE_IO
from zato.admin.web.forms import add_select

_default = OAuthCommon.Default

class CreateForm(forms.Form):
    id: Any
    name: Any
    username: Any
    auth_server_url: Any
    scopes: Any
    client_id_field: Any
    client_secret_field: Any
    grant_type: Any
    extra_fields: Any
    data_format: Any
    def __init__(self: Any, prefix: Any = ..., post_data: Any = ...) -> None: ...

class EditForm(CreateForm):
    is_active: Any
