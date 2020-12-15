# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select, add_select, add_services, SearchForm as _ChooseClusterForm, \
     DataFormatForm, INITIAL_CHOICES
from zato.common.api import HL7

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(DataFormatForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    should_parse_on_input = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    should_validate = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    should_return_errors = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    hl7_version = forms.ChoiceField(widget=forms.Select())
    data_encoding = forms.CharField(widget=forms.TextInput(attrs={'style':'width:30%'}))
    json_path = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    url_path = forms.CharField(initial='/', widget=forms.TextInput(attrs={'style':'width:100%'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:100%'}))
    security_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, security_list=[], prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        add_security_select(self, security_list, field_name='security_id', needs_rbac=False)
        add_select(self, 'hl7_version', HL7.Const.Version(), needs_initial_select=False)
        add_services(self, req)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
