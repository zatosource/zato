# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web import delivery_tab, sms_tab
from zato.admin.web.forms import add_select, add_services
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

    name = forms.CharField(widget=forms.TextInput(attrs={'class':'sms-tab-name'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'class':'alerts-tab-select'}))
    receive_mode = forms.ChoiceField(widget=forms.Select())
    scheduler_run_every = forms.CharField(required=False, initial=_scheduler.Default_Run_Every, widget=forms.TextInput())
    scheduler_run_unit = forms.ChoiceField(required=False, choices=sms_tab.poll_unit_choices,
        initial=sms_tab.poll_unit_for_form(_scheduler.Default_Run_Unit), widget=forms.Select())

    # The outgoing connection of the channel, created and edited along with it
    outconn_name = forms.CharField(required=False, widget=forms.HiddenInput())
    outconn_id = forms.CharField(required=False, widget=forms.HiddenInput())

    # Retry config - the Delivery tab's micro-form edits these, the queue and DLQ fields join them in __init__
    max_retries = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Max_Retries)
    retry_sleep_time = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Sleep_Time)
    retry_backoff_threshold = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Backoff_Threshold)
    retry_backoff_multiplier = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Backoff_Multiplier)

    def __init__(self, req:'any_', prefix:'strnone'=None) -> 'None':
        super().__init__(prefix=prefix)

        add_services(self, req)
        add_select(self, 'receive_mode', _receive_mode_choices, needs_initial_select=False)

        # The Provider section's fields, edited in its popover
        sms_tab.add_provider_fields(self)

        # The Delivery tab's fields, all of them hidden behind the tab's popovers
        delivery_tab.add_delivery_fields(self, self.is_edit_form)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_edit_form = True
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
