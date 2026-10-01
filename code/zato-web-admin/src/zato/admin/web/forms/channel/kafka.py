# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web import delivery_tab, kafka_consumer_tab
from zato.admin.web.forms import add_security_select, add_select, add_services
from zato.common.api import HTTP_SOAP, KAFKA

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.admin.web.views import SecurityList
    from zato.common.typing_ import any_, strnone

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    is_edit_form = False

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=KAFKA.Default.Address)
    group_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    security_id = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    sasl_mechanism = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    ssl = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    ssl_ca_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssl_cert_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssl_key_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssl_key_password = forms.CharField(
        required=False, strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%', 'autocomplete':'new-password'}))

    # Retry config
    max_retries = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Max_Retries)
    retry_sleep_time = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Sleep_Time)
    retry_backoff_threshold = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Backoff_Threshold)
    retry_backoff_multiplier = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Backoff_Multiplier)

    def __init__(
        self,
        req:'any_',
        security_list:'SecurityList',
        prefix:'strnone' = None,
        post_data:'any_' = None,
    ) -> 'None':
        super().__init__(post_data, prefix=prefix)
        sasl_mechanisms = KAFKA.SASL_MECHANISM()

        add_services(self, req)
        add_security_select(self, security_list, field_name='security_id')
        add_select(self, 'sasl_mechanism', sasl_mechanisms, needs_initial_select=True)

        # The Consumer, Routing and Delivery tabs' fields
        kafka_consumer_tab.add_consumer_fields(self, self.is_edit_form)
        kafka_consumer_tab.copy_service_choices(self)
        delivery_tab.add_delivery_fields(self, self.is_edit_form)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_edit_form = True
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
