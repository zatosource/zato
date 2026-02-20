from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms


class CreateForm(forms.Form):
    id: Any
    name: Any
    is_active: Any
    username: Any

class EditForm(CreateForm):
    is_active: Any
