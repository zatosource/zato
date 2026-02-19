from typing import Any

from django import forms

class CreateForm(forms.Form):
    name: Any
    is_active: Any
    host: Any
    username: Any
    password: Any
    def __init__(self: Any, req: Any = ..., prefix: Any = ...) -> None: ...

class EditForm(CreateForm):
    is_active: Any
