# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web import alerts_tab
from zato.common.api import FTP
from zato.common.file_transfer.api import Verify_How_Human, Verify_How_List

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:70%'}))
    port = forms.CharField(widget=forms.TextInput(attrs={'style':'width:12%'}), initial=FTP.DEFAULT.PORT)

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%', 'autocomplete':'off'}))
    secret = forms.CharField(required=False, strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))

    use_ssl = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    should_store_content = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    verify_how = forms.ChoiceField(widget=forms.Select())

    def __init__(self, prefix:'any_' = None, req:'any_' = None) -> 'None':
        super(CreateForm, self).__init__(prefix=prefix)

        # One choice per verification method.
        choices = []

        for item in Verify_How_List:
            label = Verify_How_Human[item]
            choices.append([item, label])

        self.fields['verify_how'].choices = choices

        # The Alerts tab - the file transfer thresholds, toggles and the email connection.
        alerts_tab.add_alerts_fields(self, alerts_tab.alert_type_file_transfer, req)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################

# What the shell starts with unless a link into it, e.g. from a schedule, says otherwise
_default_command = 'ls .'

class CommandShellForm(forms.Form):

    data = forms.CharField(widget=forms.Textarea())

    def __init__(self, initial_command:'str'=_default_command) -> 'None':
        super(CommandShellForm, self).__init__()
        self.fields['data'].initial = initial_command

# ################################################################################################################################
# ################################################################################################################################
