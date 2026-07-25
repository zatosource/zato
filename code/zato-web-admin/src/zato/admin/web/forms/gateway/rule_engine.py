# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.util.rule_engine_api import default_rule_engine_api_url_path

# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    url_path = forms.CharField(initial=default_rule_engine_api_url_path,
        widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))

    # The grants: exact names, subtrees or everything, comma-separated
    rulesets = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'style':'width:100%', 'placeholder':'payments.discounts, payments.*, *'}))

# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
