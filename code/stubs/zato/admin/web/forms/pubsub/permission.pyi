from typing import Any

from django import forms

class CreateForm(forms.Form):
    sec_base_id: Any
    access_type: Any
    def __init__(self: Any, sec_base_choices: Any = ..., *args: Any, **kwargs: Any) -> None: ...

class EditForm(CreateForm):
    id: Any
    def __init__(self: Any, sec_base_choices: Any = ..., *args: Any, **kwargs: Any) -> None: ...
