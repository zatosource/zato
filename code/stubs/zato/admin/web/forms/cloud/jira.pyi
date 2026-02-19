from typing import Any

from django import forms
from zato.common.api import Atlassian as AtlassianCommon

class CreateForm(forms.Form):
    name: Any
    is_active: Any
    is_cloud: Any
    api_version: Any
    address: Any
    username: Any
    password: Any

class EditForm(CreateForm):
    is_active: Any
    is_cloud: Any
