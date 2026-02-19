from typing import Any

from __future__ import absolute_import, division, print_function, unicode_literals
from django import forms

class AuthenticationForm(forms.Form):
    username: Any
    password: Any
    totp_code: Any
