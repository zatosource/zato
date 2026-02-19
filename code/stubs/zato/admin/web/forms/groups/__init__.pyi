from typing import Any

from django import forms

class CreateForm(forms.Form):
    id: Any
    name: Any

class EditForm(CreateForm):
    ...
