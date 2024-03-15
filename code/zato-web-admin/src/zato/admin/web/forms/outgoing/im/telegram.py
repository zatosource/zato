# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common.api import TELEGRAM

default = TELEGRAM.DEFAULT
timeout = TELEGRAM.TIMEOUT

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=default.ADDRESS)

    connect_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=timeout.CONNECT)
    invoke_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=timeout.INVOKE)

    http_proxy_list = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    https_proxy_list = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
