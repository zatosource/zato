from typing import Any

from django import forms
from zato.common.api import SALESFORCE

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
