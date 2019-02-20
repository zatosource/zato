# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

class AuthenticationForm(forms.Form):
    """ A form to log a user in.
    """
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.TextInput())
    totp_code = forms.CharField(widget=forms.TextInput())

