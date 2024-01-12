# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

class AuthenticationForm(forms.Form):
    """ A form to log a user in.
    """
    username = forms.CharField(max_length=254)
    password = forms.CharField(strip=False, widget=forms.PasswordInput)
    totp_code = forms.CharField(widget=forms.TextInput())
