# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web import alerts_tab, delivery_tab, sms_tab
from zato.common.alerting.object_config import alert_type_sms_outgoing
from zato.common.api import HTTP_SOAP, SMS

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    is_edit_form = False

    name = forms.CharField(widget=forms.TextInput(attrs={'class':'sms-tab-name'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    channel_name = forms.ChoiceField(required=False, widget=forms.Select())
    pool_size = forms.CharField(widget=forms.TextInput(), initial=SMS.Default_Pool_Size)

    # Retry config - the Delivery tab's micro-form edits these, the queue and DLQ fields join them in __init__
    max_retries = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Max_Retries)
    retry_sleep_time = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Sleep_Time)
    retry_backoff_threshold = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Backoff_Threshold)
    retry_backoff_multiplier = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Backoff_Multiplier)

    def __init__(self, req:'any_', prefix:'strnone'=None) -> 'None':
        super().__init__(prefix=prefix)

        # The Config tab's fields, edited in its popovers
        sms_tab.add_provider_fields(self)
        sms_tab.add_timeout_fields(self)

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
