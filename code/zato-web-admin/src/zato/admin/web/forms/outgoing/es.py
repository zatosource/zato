# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import ES

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    address_list = forms.CharField(
        widget=forms.Textarea(attrs={'style':'width:100%; height:70px'}), initial=ES.Default.Address_List)

    username = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    secret = forms.CharField(required=False, strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))

    timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:12%'}), initial=ES.Default.Timeout)

    is_tls_validation_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    tls_ca_certs_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_cert_key_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    def __init__(self, prefix=None, req=None):
        super(CreateForm, self).__init__(prefix=prefix)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_tls_validation_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
