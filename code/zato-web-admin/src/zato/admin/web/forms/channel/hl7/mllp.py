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

_max_msg_size_unit_choices = [
    ('kb', 'kB'),
    ('mb', 'MB'),
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
    service = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:100%'}))

    logging_level = forms.ChoiceField(widget=forms.Select())

    max_msg_size = forms.CharField(initial='2', widget=forms.TextInput(attrs={'style':'width:8%'}))
    max_msg_size_unit = forms.ChoiceField(
        choices=_max_msg_size_unit_choices,
        initial='mb',
        widget=forms.Select(attrs={'style':'width:60px'}),
    )
    read_buffer_size = forms.CharField(initial=_default.read_buffer_size, widget=forms.TextInput(attrs={'style':'width:10%'}))
    recv_timeout = forms.CharField(initial=_default.recv_timeout, widget=forms.TextInput(attrs={'style':'width:8%'}))
    start_seq = forms.CharField(initial=_default.start_seq, widget=forms.TextInput(attrs={'style':'width:15%'}))
    end_seq = forms.CharField(initial=_default.end_seq, widget=forms.TextInput(attrs={'style':'width:15%'}))

    # Routing fields
    msh3_sending_app        = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:50%'}))
    msh4_sending_facility   = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:50%'}))
    msh5_receiving_app      = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:50%'}))
    msh6_receiving_facility = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:50%'}))
    msh9_message_type       = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:30%'}))
    msh9_trigger_event      = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:30%'}))
    msh11_processing_id     = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:15%'}))
    msh12_version_id        = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:15%'}))
    is_default              = forms.BooleanField(required=False, widget=forms.CheckboxInput())

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
