from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms
from zato.admin.web.forms import UploadForm

class CreateForm(forms.Form):
    is_active: Any
    slow_threshold: Any

class EditForm(CreateForm):
    is_active: Any

class WSDLUploadForm(UploadForm):
    ...
