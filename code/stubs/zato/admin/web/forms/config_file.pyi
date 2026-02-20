from typing import Any, TYPE_CHECKING

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms


class CreateForm(forms.Form):
    name: Any
    data: Any

class EditForm(CreateForm):
    ...
