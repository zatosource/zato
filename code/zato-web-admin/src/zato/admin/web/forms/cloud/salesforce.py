# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import WithAuditLog
from zato.common.api import SALESFORCE

# ################################################################################################################################
# ################################################################################################################################

_default = SALESFORCE.Default

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(WithAuditLog):

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    api_version = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}), initial=_default.API_Version)
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.Address)
    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))
    consumer_key = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))
    consumer_secret = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
