# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web import alerts_tab, delivery_tab
from zato.admin.web.forms import add_select
from zato.common.alerting.object_config import alert_type_sms_outgoing
from zato.common.api import HTTP_SOAP, SMS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

# The provider select lists every provider under its human-readable name
_provider_choices = []

for _provider_name in SMS.ProviderList:
    _provider_choices.append({'id': _provider_name, 'name': SMS.ProviderHuman[_provider_name]})

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    is_edit_form = False

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    provider = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    host = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}),
        initial=SMS.Default_Host[SMS.Provider.Twilio])
    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    secret = forms.CharField(
        required=False, strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%', 'autocomplete':'new-password'}))
    sender = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    signature_secret = forms.CharField(
        required=False, strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%', 'autocomplete':'new-password'}))
    channel_name = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))
    pool_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}), initial=SMS.Default_Pool_Size)
    timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}), initial=SMS.Default_Timeout)

    # Retry config - the Delivery tab's micro-form edits these, the queue and DLQ fields join them in __init__
    max_retries = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Max_Retries)
    retry_sleep_time = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Sleep_Time)
    retry_backoff_threshold = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Backoff_Threshold)
    retry_backoff_multiplier = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Backoff_Multiplier)

    def __init__(self, req:'any_', prefix:'strnone'=None) -> 'None':
        super().__init__(prefix=prefix)

        add_select(self, 'provider', _provider_choices, needs_initial_select=False)

        # The channel select is filled in by the view, which knows the SMS channels that exist
        self.fields['channel_name'].choices = []

        # The Delivery and Alerts tabs' fields, all of them hidden behind the tabs' popovers
        delivery_tab.add_delivery_fields(self, self.is_edit_form)
        alerts_tab.add_alerts_fields(self, alert_type_sms_outgoing, req)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_edit_form = True
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
