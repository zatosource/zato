# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import WithRateLimiting
from zato.common.api import API_Key

class CreateForm(WithRateLimiting):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class':'required', 'style':'width:100%', 'disabled':True}),
        initial=API_Key.Default_Header,
    )
    is_rate_limit_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    rate_limit_check_parent_def = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
