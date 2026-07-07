# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from imaplib import IMAP4_SSL_PORT

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_services
from zato.common.api import EMAIL

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    server_type = forms.ChoiceField(widget=forms.Select())
    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    port = forms.CharField(initial=IMAP4_SSL_PORT, widget=forms.TextInput(attrs={'style':'width:10%'}))
    timeout = forms.CharField(initial=EMAIL.DEFAULT.TIMEOUT, widget=forms.TextInput(attrs={'style':'width:6%'}))
    debug_level = forms.CharField(initial=EMAIL.DEFAULT.IMAP_DEBUG_LEVEL, widget=forms.TextInput(attrs={'style':'width:7%'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    mode = forms.ChoiceField(widget=forms.Select())
    get_criteria = forms.CharField(
        initial=EMAIL.DEFAULT.GET_CRITERIA,
        widget=forms.Textarea(attrs={'style':'width:100%; height:4rem'}
    ))

    tenant_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    client_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    filter_criteria = forms.CharField(
        initial=EMAIL.DEFAULT.FILTER_CRITERIA,
        widget=forms.Textarea(attrs={'style':'width:100%; height:4rem'}
    ))

    scheduler_run_every = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:12%'}))
    scheduler_run_unit = forms.ChoiceField(required=False, widget=forms.Select())
    scheduler_start_date = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:50%; height:19px'}))
    scheduler_service = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))
    scheduler_invoke_with = forms.ChoiceField(required=False, widget=forms.Select())
    scheduler_job_id = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        add_services(self, req)
        self.fields['mode'].choices = ((item, item) for item in EMAIL.IMAP.MODE())

        self.fields['server_type'].choices = []
        for key, value in EMAIL.IMAP.ServerTypeHuman.items():
            self.fields['server_type'].choices.append([key, value])

        self.fields['scheduler_run_unit'].choices = []
        for item in EMAIL.IMAP.Scheduler.UnitList:
            self.fields['scheduler_run_unit'].choices.append([item, item])

        self.fields['scheduler_invoke_with'].choices = []
        for key, value in EMAIL.IMAP.Scheduler.InvokeWithHuman.items():
            self.fields['scheduler_invoke_with'].choices.append([key, value])

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
