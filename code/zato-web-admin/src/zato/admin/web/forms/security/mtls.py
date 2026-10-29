# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import MTLS

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    use_for = forms.ChoiceField(widget=forms.Select(), choices=MTLS.Use_For_Choices, initial=MTLS.Use_For.Default)
    cert_path = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    key_path = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ca_certs_path = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    client_cert_fingerprint = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    client_cert_subject_dn = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

class EditForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    use_for = forms.ChoiceField(widget=forms.Select(), choices=MTLS.Use_For_Choices, initial=MTLS.Use_For.Default)
    cert_path = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    key_path = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ca_certs_path = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    client_cert_fingerprint = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    client_cert_subject_dn = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
