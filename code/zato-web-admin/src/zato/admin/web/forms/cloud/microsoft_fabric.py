# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import MicrosoftFabric as MicrosoftFabricCommon

# ################################################################################################################################
# ################################################################################################################################

_default = MicrosoftFabricCommon.Default

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.Address)
    tenant_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    client_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    client_secret = forms.CharField(widget=forms.PasswordInput(attrs={'style':'width:100%'}))

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
