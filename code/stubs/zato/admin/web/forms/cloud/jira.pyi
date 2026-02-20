from typing import Any, TYPE_CHECKING

from django import forms
from zato.common.api import Atlassian as AtlassianCommon

_default = AtlassianCommon.Default

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
