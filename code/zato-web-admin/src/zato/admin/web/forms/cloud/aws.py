# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import AWS as AWSCommon

# ################################################################################################################################
# ################################################################################################################################

_default = AWSCommon.Default

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    region = forms.CharField(widget=forms.TextInput(attrs={'style':'width:30%'}), initial=_default.Region)
    access_key_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    endpoint_url = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
