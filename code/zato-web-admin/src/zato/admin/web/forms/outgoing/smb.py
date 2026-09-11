# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web import alerts_tab
from zato.common.api import SMB
from zato.common.file_transfer.api import Verify_How_Human, Verify_How_List

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

    verify_how = forms.ChoiceField(widget=forms.Select())

    def __init__(self, prefix=None, req=None):
        super(CreateForm, self).__init__(prefix=prefix)

        # One choice per verification method.
        choices = []

        for item in Verify_How_List:
            label = Verify_How_Human[item]
            choices.append([item, label])

        self.fields['verify_how'].choices = choices

        # The Alerts tab - the file transfer thresholds, toggles and the email connection
        alerts_tab.add_alerts_fields(self, alerts_tab.alert_type_file_transfer, req)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
