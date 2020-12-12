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
from zato.common.api import DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, HTTP_SOAP, HTTP_SOAP_SERIALIZATION_TYPE, \
     MISC, PARAMS_PRIORITY, RATE_LIMIT, SIMPLE_IO, SOAP_VERSIONS, URL_PARAMS_PRIORITY, ZATO_NONE

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(DataFormatForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    hl7_version = forms.ChoiceField(widget=forms.Select())
    host = forms.CharField(initial='http://', widget=forms.TextInput(attrs={'style':'width:100%'}))
    url_path = forms.CharField(initial='/', widget=forms.TextInput(attrs={'style':'width:70%'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:100%'}))
    security = forms.ChoiceField(widget=forms.Select())

    def __init__(self, security_list=[], prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        add_security_select(self, security_list, needs_rbac=False)
        add_services(self, req)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
