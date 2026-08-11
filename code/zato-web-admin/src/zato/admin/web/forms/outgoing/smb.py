# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import SMB

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:70%'}))
    port = forms.CharField(widget=forms.TextInput(attrs={'style':'width:12%'}), initial=SMB.DEFAULT.PORT)

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%', 'autocomplete':'off'}))
    secret = forms.CharField(required=False, strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))

    # Off by default - the audit log records every transfer either way,
    # this flag additionally keeps the bytes of the files moved.
    should_store_content = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    def __init__(self, prefix=None, req=None):
        super(CreateForm, self).__init__(prefix=prefix)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
