from typing import Any, TYPE_CHECKING

from django import forms
from zato.common.api import SALESFORCE

_default = SALESFORCE.Default

class CreateForm(forms.Form):
    name: Any
    is_active: Any
    api_version: Any
    address: Any
    username: Any
    password: Any
    consumer_key: Any
    consumer_secret: Any

class EditForm(CreateForm):
    is_active: Any
