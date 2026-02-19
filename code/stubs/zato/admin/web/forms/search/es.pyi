from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms
from zato.common.api import SEARCH

class CreateForm(forms.Form):
    id: Any
    name: Any
    is_active: Any
    hosts: Any
    timeout: Any
    body_as: Any

class EditForm(CreateForm):
    is_active: Any
