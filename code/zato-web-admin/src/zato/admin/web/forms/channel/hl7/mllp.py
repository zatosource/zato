# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select, add_services
from zato.common.api import HL7

# ################################################################################################################################
# ################################################################################################################################

_default = HL7.Default
_address = f'{_default.channel_host}:{_default.channel_port}'

_dedup_ttl_unit_choices = [
    ('minutes', 'Minutes'),
    ('hours',   'Hours'),
    ('days',    'Days'),
]

_encoding_choices = [
    ('utf-8',        'UTF-8'),
    ('iso-8859-1',   'ISO-8859-1'),
    ('windows-1252', 'Windows-1252'),
    ('us-ascii',     'US-ASCII'),
]

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    should_parse_on_input = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    should_validate = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    should_return_errors = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    should_log_messages = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    hl7_version = forms.ChoiceField(widget=forms.Select())
    address = forms.CharField(initial=_address, widget=forms.TextInput(attrs={'style':'width:73%'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:100%'}))

    logging_level = forms.ChoiceField(widget=forms.Select())

    data_encoding = forms.CharField(initial=_default.data_encoding, widget=forms.TextInput(attrs={'style':'width:16%'}))
    max_msg_size = forms.CharField(initial=_default.max_msg_size, widget=forms.TextInput(attrs={'style':'width:30%'}))
    read_buffer_size = forms.CharField(initial=_default.read_buffer_size, widget=forms.TextInput(attrs={'style':'width:15%'}))
    recv_timeout = forms.CharField(initial=_default.recv_timeout, widget=forms.TextInput(attrs={'style':'width:8%'}))
    start_seq = forms.CharField(initial=_default.start_seq, widget=forms.TextInput(attrs={'style':'width:35%'}))
    end_seq = forms.CharField(initial=_default.end_seq, widget=forms.TextInput(attrs={'style':'width:26%'}))

    # TLS
    tls_cert_path = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_key_path  = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_ca_path   = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_verify    = forms.ChoiceField(
        required=False,
        choices=[('none', 'None'), ('optional', 'Optional'), ('required', 'Required')],
        initial='none',
        widget=forms.Select(attrs={'style':'width:20%'}),
    )

    # Dedup
    dedup_ttl_value = forms.CharField(
        initial=_default.dedup_ttl_value, required=False,
        widget=forms.TextInput(attrs={'style':'width:8%'}),
    )
    dedup_ttl_unit = forms.ChoiceField(
        required=False,
        choices=_dedup_ttl_unit_choices,
        initial=_default.dedup_ttl_unit,
        widget=forms.Select(attrs={'style':'width:15%'}),
    )

    # Default character encoding (when MSH-18 is missing or toggle is off)
    default_character_encoding = forms.ChoiceField(
        required=False,
        choices=_encoding_choices,
        initial='utf-8',
        widget=forms.Select(attrs={'style':'width:20%'}),
    )

    # Message tolerance toggles
    normalize_line_endings        = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    force_standard_delimiters     = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    repair_truncated_msh          = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    split_concatenated_messages   = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    use_msh18_encoding            = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        add_select(self, 'hl7_version', HL7.Const.Version(), needs_initial_select=False)
        add_select(self, 'logging_level', HL7.Const.LoggingLevel(), needs_initial_select=False)
        add_services(self, req)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
