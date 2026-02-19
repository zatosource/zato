from typing import Any

from django import forms

class CreateForm(forms.Form):
    id: Any
    name: Any
    is_active: Any
    description: Any

class EditForm(CreateForm):
    is_active: Any
