# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import Discord

# ################################################################################################################################
# ################################################################################################################################

_default = Discord.Default

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    token = forms.CharField(widget=forms.PasswordInput(attrs={'style':'width:100%'}))
    default_channel_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.Address)
    ready_timeout = forms.IntegerField(widget=forms.TextInput(attrs={'style':'width:15%'}), initial=_default.Ready_Timeout)
    timeout = forms.IntegerField(widget=forms.TextInput(attrs={'style':'width:15%'}), initial=_default.Timeout)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    token = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))

# ################################################################################################################################
# ################################################################################################################################
