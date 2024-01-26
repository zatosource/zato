# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select, add_services, WithAuditLog
from zato.common.api import HL7

# ################################################################################################################################
# ################################################################################################################################

_default = HL7.Default
_address = f'{_default.channel_host}:{_default.channel_port}'

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(WithAuditLog):
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

    def __init__(self, prefix=None, post_data=None, req=None):
        super(WithAuditLog, self).__init__(post_data, prefix=prefix)
        add_select(self, 'hl7_version', HL7.Const.Version(), needs_initial_select=False)
        add_select(self, 'logging_level', HL7.Const.LoggingLevel(), needs_initial_select=False)
        add_services(self, req)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
