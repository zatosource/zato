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
from zato.common.file_transfer.api import Verify_How_Human, Verify_How_List

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%', 'autocomplete':'off'}))
    secret = forms.CharField(required=False, strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))

    private_key = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    # Off by default - a new connection reaches a host whose key is not in known_hosts yet,
    # so requiring it up front would reject the very first attempt.
    strict_host_key_checking = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    ignore_host_key_changes = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    # Off by default - the audit log records every transfer either way,
    # this flag additionally keeps the bytes of the files moved.
    should_store_content = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    verify_how = forms.ChoiceField(widget=forms.Select())

    def __init__(self, prefix=None, req=None):
        super(CreateForm, self).__init__(prefix=prefix)

        # One choice per verification method.
        choices = []

        for item in Verify_How_List:
            label = Verify_How_Human[item]
            choices.append([item, label])

        self.fields['verify_how'].choices = choices

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################

# What the shell starts with unless a link into it, e.g. from a schedule, says otherwise
_default_command = 'ls .'

class CommandShellForm(forms.Form):

    # Stdout and stderr are not fields - the command shell renders them as its own output panes.
    data = forms.CharField(widget=forms.Textarea())
    log_level = forms.ChoiceField(widget=forms.Select())

    def __init__(self, initial_command:'str'=_default_command) -> 'None':
        super(CommandShellForm, self).__init__()
        self.fields['data'].initial = initial_command
        add_select(self, 'log_level', SFTP.LOG_LEVEL(), needs_initial_select=False)

# ################################################################################################################################
# ################################################################################################################################
