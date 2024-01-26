# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import WithAuditLog
from zato.common.api import HL7

# ################################################################################################################################
# ################################################################################################################################

_default = HL7.Default

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(WithAuditLog):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    should_log_messages = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    pool_size = forms.CharField(initial=_default.pool_size, widget=forms.TextInput(attrs={'style':'width:11%'}))
    logging_level = forms.ChoiceField(widget=forms.Select())
    max_wait_time = forms.CharField(initial=_default.max_wait_time, widget=forms.TextInput(attrs={'style':'width:25%'}))
    max_msg_size = forms.CharField(initial=_default.max_msg_size, widget=forms.TextInput(attrs={'style':'width:30%'}))
    read_buffer_size = forms.CharField(initial=_default.read_buffer_size, widget=forms.TextInput(attrs={'style':'width:15%'}))
    start_seq = forms.CharField(initial=_default.start_seq, widget=forms.TextInput(attrs={'style':'width:35%'}))
    end_seq = forms.CharField(initial=_default.end_seq, widget=forms.TextInput(attrs={'style':'width:26%'}))

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
