# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web import delivery_tab
from zato.admin.web.forms import add_select, add_services
from zato.admin.web.forms.http_soap import scheduler_run_unit_choices
from zato.common.api import HTTP_SOAP, SMS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry
_scheduler = SMS.Scheduler

# The receive mode select lists both modes under their human-readable names
_receive_mode_choices = []

for _receive_mode in SMS.Receive_Mode_List:
    _receive_mode_choices.append({'id': _receive_mode, 'name': SMS.Receive_Mode_Human[_receive_mode]})

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    is_edit_form = False

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    outconn_name = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    receive_mode = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    scheduler_run_every = forms.CharField(required=False, initial=_scheduler.Default_Run_Every,
        widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:20%'}))
    scheduler_run_unit = forms.ChoiceField(required=False, choices=scheduler_run_unit_choices,
        initial=_scheduler.Default_Run_Unit, widget=forms.Select())
    webhook_url = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%', 'readonly':'readonly'}))

    # Retry config - the Delivery tab's micro-form edits these, the queue and DLQ fields join them in __init__
    max_retries = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Max_Retries)
    retry_sleep_time = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Sleep_Time)
    retry_backoff_threshold = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Backoff_Threshold)
    retry_backoff_multiplier = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Backoff_Multiplier)

    def __init__(self, req:'any_', prefix:'strnone'=None) -> 'None':
        super().__init__(prefix=prefix)

        add_services(self, req)
        add_select(self, 'receive_mode', _receive_mode_choices, needs_initial_select=False)

        # The outgoing connection select is filled in by the view, which knows the outgoing SMS connections that exist
        self.fields['outconn_name'].choices = []

        # The Delivery tab's fields, all of them hidden behind the tab's popovers
        delivery_tab.add_delivery_fields(self, self.is_edit_form)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_edit_form = True
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
