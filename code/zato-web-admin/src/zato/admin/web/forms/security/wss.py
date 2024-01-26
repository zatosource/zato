# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:90%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:90%'}))
    reject_empty_nonce_creat = forms.BooleanField(widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    reject_stale_tokens = forms.BooleanField(widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    reject_expiry_limit = forms.IntegerField(widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:20%'}))
    nonce_freshness_time = forms.IntegerField(widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:20%'}))

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    reject_empty_nonce_creat = forms.BooleanField(widget=forms.CheckboxInput())
    reject_stale_tokens = forms.BooleanField(widget=forms.CheckboxInput())
