# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import WithAuditLog
from zato.common.api import Microsoft365 as Microsoft365Common

# ################################################################################################################################
# ################################################################################################################################

_default = Microsoft365Common.Default

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(WithAuditLog):

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    tenant_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    client_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    secret_value = forms.CharField(widget=forms.PasswordInput(attrs={'style':'width:100%'}))

    scopes = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}), initial='\n'.join(_default.Scopes))

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
