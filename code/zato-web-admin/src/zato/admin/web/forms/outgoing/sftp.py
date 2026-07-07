# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select
from zato.common.api import SFTP

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    secret = forms.CharField(required=False, strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))

    private_key = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    strict_host_key_checking = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    def __init__(self, prefix=None, req=None):
        super(CreateForm, self).__init__(prefix=prefix)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    strict_host_key_checking = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################

class CommandShellForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:70px'}), initial='ls .')
    stdout = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:170px'}))
    stderr = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:270px'}))
    log_level = forms.ChoiceField(widget=forms.Select())

    def __init__(self):
        super(CommandShellForm, self).__init__()
        add_select(self, 'log_level', SFTP.LOG_LEVEL(), needs_initial_select=False)

# ################################################################################################################################
# ################################################################################################################################
