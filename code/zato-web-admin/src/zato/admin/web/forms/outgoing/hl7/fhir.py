# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web import alerts_tab, delivery_tab
from zato.admin.web.forms import add_health_check_fields, add_select, add_security_select
from zato.common.alerting.object_config import alert_type_fhir
from zato.common.api import HL7, HTTP_SOAP

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    # Add dummy assignments to satisfy type checkers
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_const = HL7.Const
_default = HL7.Default
_retry = HTTP_SOAP.Retry

# What a checkbox that starts out ticked renders with.
_checked_attrs = {'checked':'checked'}

# ################################################################################################################################

def _new_checkbox_field(is_checked:'bool'=False) -> 'any_':
    """ Returns a checkbox, ticked by default or not.
    """
    if is_checked:
        attrs = dict(_checked_attrs)
    else:
        attrs = {}

    widget = forms.CheckboxInput(attrs=attrs)

    out = forms.BooleanField(required=False, widget=widget)
    return out

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    is_edit_form = False

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = _new_checkbox_field(is_checked=True)
    is_audit_log_active = _new_checkbox_field(is_checked=True)
    pool_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}), initial=_default.pool_size)

    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.address_fhir)
    auth_type = forms.ChoiceField(widget=forms.Select())

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%', 'autocomplete':'off'}))
    password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))

    security_id = forms.ChoiceField(widget=forms.Select())

    extra = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:60px'}), required=False)

    # Retry config - the Delivery tab's micro-form edits these, the queue and DLQ fields join them in __init__
    max_retries = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Max_Retries)
    retry_sleep_time = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Sleep_Time)
    retry_backoff_threshold = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Backoff_Threshold)
    retry_backoff_multiplier = forms.CharField(widget=forms.TextInput(), initial=_retry.Default_Backoff_Multiplier)

    def __init__(self, req:'any_', security_list:'any_', prefix:'any_'=None) -> 'None':
        super().__init__(prefix=prefix)
        add_select(self, 'auth_type', _const.FHIR_Auth_Type(), needs_initial_select=True)
        add_security_select(self, security_list, field_name='security_id')

        # The Alerts tab - the thresholds, the operation outcomes, the toggles and the email connection,
        # with the health check schedule the tab edits as fields of this form
        alerts_tab.add_alerts_fields(self, alert_type_fhir, req)
        add_health_check_fields(self)

        delivery_tab.add_delivery_fields(self, self.is_edit_form)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_edit_form = True
    is_active = _new_checkbox_field()

    # An existing connection with the audit log off opens with the box unticked.
    is_audit_log_active = _new_checkbox_field()

# ################################################################################################################################
# ################################################################################################################################
