from typing import Any

from django import forms

class CreateForm(forms.Form):
    name: Any
    url_path: Any
    is_active: Any
    is_public: Any

class EditForm(CreateForm):
    is_active: Any
    is_public: Any
