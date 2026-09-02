# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select
from zato.common.api import HL7

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    # Add dummy assignments to satisfy type checkers
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_default = HL7.Default

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
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = _new_checkbox_field(is_checked=True)
    should_log_messages = _new_checkbox_field()
    is_audit_log_active = _new_checkbox_field(is_checked=True)
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    pool_size = forms.CharField(initial=_default.pool_size, widget=forms.TextInput(attrs={'style':'width:11%'}))
    logging_level = forms.ChoiceField(widget=forms.Select())
    max_wait_time = forms.CharField(initial=_default.max_wait_time, widget=forms.TextInput(attrs={'style':'width:25%'}))
    max_msg_size = forms.CharField(initial=_default.max_msg_size, widget=forms.TextInput(attrs={'style':'width:30%'}))
    read_buffer_size = forms.CharField(initial=_default.read_buffer_size, widget=forms.TextInput(attrs={'style':'width:15%'}))
    recv_timeout = forms.CharField(initial=_default.recv_timeout, widget=forms.TextInput(attrs={'style':'width:8%'}))
    start_seq = forms.CharField(initial=_default.start_seq, widget=forms.TextInput(attrs={'style':'width:35%'}))
    end_seq = forms.CharField(initial=_default.end_seq, widget=forms.TextInput(attrs={'style':'width:26%'}))

    # Retry engine
    max_retries = forms.CharField(
        initial=_default.max_retries,
        widget=forms.TextInput(attrs={'style':'width:8%'}),
    )
    backoff_base_seconds = forms.CharField(
        initial=_default.backoff_base_seconds,
        widget=forms.TextInput(attrs={'style':'width:8%'}),
    )
    backoff_cap_seconds = forms.CharField(
        initial=_default.backoff_cap_seconds,
        widget=forms.TextInput(attrs={'style':'width:10%'}),
    )
    backoff_jitter_percent = forms.CharField(
        initial=_default.backoff_jitter_percent,
        widget=forms.TextInput(attrs={'style':'width:8%'}),
    )

    # Circuit breaker
    circuit_breaker_threshold_percent = forms.CharField(
        initial=_default.circuit_breaker_threshold_percent,
        widget=forms.TextInput(attrs={'style':'width:8%'}),
    )
    circuit_breaker_window_seconds = forms.CharField(
        initial=_default.circuit_breaker_window_seconds,
        widget=forms.TextInput(attrs={'style':'width:10%'}),
    )
    circuit_breaker_reset_seconds = forms.CharField(
        initial=_default.circuit_breaker_reset_seconds,
        widget=forms.TextInput(attrs={'style':'width:10%'}),
    )

    # TLS
    tls_cert_path = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_key_path  = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_ca_path   = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    def __init__(self, prefix:'any_'=None, post_data:'any_'=None) -> 'None':
        super().__init__(post_data, prefix=prefix)
        add_select(self, 'logging_level', HL7.Const.LoggingLevel(), needs_initial_select=False)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = _new_checkbox_field()

    # An existing connection with the audit log off opens with the box unticked.
    is_audit_log_active = _new_checkbox_field()

# ################################################################################################################################
# ################################################################################################################################
