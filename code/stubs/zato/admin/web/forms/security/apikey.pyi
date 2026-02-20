from typing import Any, TYPE_CHECKING

from django import forms
from zato.common.api import API_Key


class CreateForm(forms.Form):
    id: Any
    name: Any
    is_active: Any
    username: Any

class EditForm(CreateForm):
    is_active: Any
