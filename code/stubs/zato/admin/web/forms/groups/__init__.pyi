from typing import Any, TYPE_CHECKING

from django import forms


class CreateForm(forms.Form):
    id: Any
    name: Any

class EditForm(CreateForm):
    ...
