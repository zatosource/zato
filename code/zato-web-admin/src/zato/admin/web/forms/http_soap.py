# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import ChooseClusterForm as _ChooseClusterForm
from zato.admin.web.forms import DataFormatForm
from zato.common import DEFAULT_HTTP_PING_METHOD, SOAP_VERSIONS, ZATO_NONE

class CreateForm(DataFormatForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    host = forms.CharField(initial='http://', widget=forms.TextInput(attrs={'style':'width:100%'}))
    url_path = forms.CharField(initial='/', widget=forms.TextInput(attrs={'style':'width:100%'}))
    method = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    soap_action = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    soap_version = forms.ChoiceField(widget=forms.Select())
    service = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    ping_method = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    security = forms.ChoiceField(widget=forms.Select())
    connection = forms.CharField(widget=forms.HiddenInput())
    transport = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, security_list=[], soap_versions=SOAP_VERSIONS, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['soap_version'].choices = []
        for name in sorted(soap_versions):
            self.fields['soap_version'].choices.append([name, name])
            
        self.fields['security'].choices = []
        self.fields['security'].choices.append(['', '----------'])
        self.fields['security'].choices.append([ZATO_NONE, 'No security'])
        
        for value, label in security_list:
            self.fields['security'].choices.append([value, label])
            
        self.fields['ping_method'].initial = DEFAULT_HTTP_PING_METHOD

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

class ChooseClusterForm(_ChooseClusterForm):
    connection = forms.CharField(widget=forms.HiddenInput())
    transport = forms.CharField(widget=forms.HiddenInput())