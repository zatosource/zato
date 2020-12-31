# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select, add_services, WithAuditLog
from zato.common.api import HL7

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(WithAuditLog):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    should_parse_on_input = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    should_validate = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    should_return_errors = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    hl7_version = forms.ChoiceField(widget=forms.Select())
    data_encoding = forms.CharField(widget=forms.TextInput(attrs={'style':'width:30%'}))
    address = forms.CharField(initial=HL7.Default.address, widget=forms.TextInput(attrs={'style':'width:13%'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:100%'}))

    def __init__(self, prefix=None, post_data=None, req=None):
        super(WithAuditLog, self).__init__(post_data, prefix=prefix)
        add_select(self, 'hl7_version', HL7.Const.Version(), needs_initial_select=False)
        add_services(self, req)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
