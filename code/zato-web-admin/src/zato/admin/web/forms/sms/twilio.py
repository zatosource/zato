# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    account_sid = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    auth_token = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    default_from = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    default_to = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
