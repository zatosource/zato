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
from zato.common import DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, \
     PARAMS_PRIORITY, SOAP_VERSIONS, URL_PARAMS_PRIORITY, ZATO_NONE

params_priority = (
    (PARAMS_PRIORITY.CHANNEL_PARAMS_OVER_MSG, 'URL over message'),
    (PARAMS_PRIORITY.MSG_OVER_CHANNEL_PARAMS, 'Message over URL'),
)

url_params_priority = (
    (URL_PARAMS_PRIORITY.QS_OVER_PATH, 'QS over path'),
    (URL_PARAMS_PRIORITY.PATH_OVER_QS, 'Path over QS'),
)

class CreateForm(DataFormatForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    host = forms.CharField(initial='http://', widget=forms.TextInput(attrs={'style':'width:100%'}))
    url_path = forms.CharField(initial='/', widget=forms.TextInput(attrs={'style':'width:100%'}))
    merge_url_params_req = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    url_params_pri = forms.ChoiceField(widget=forms.Select())
    params_pri = forms.ChoiceField(widget=forms.Select())
    method = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    soap_action = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    soap_version = forms.ChoiceField(widget=forms.Select())
    service = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    ping_method = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    pool_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    security = forms.ChoiceField(widget=forms.Select())
    connection = forms.CharField(widget=forms.HiddenInput())
    transport = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, security_list=[], soap_versions=SOAP_VERSIONS, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        
        self.fields['url_params_pri'].choices = []
        for value, label in url_params_priority:
            self.fields['url_params_pri'].choices.append([value, label])
            
        self.fields['params_pri'].choices = []
        for value, label in params_priority:
            self.fields['params_pri'].choices.append([value, label])

        self.fields['soap_version'].choices = []
        for name in sorted(soap_versions):
            self.fields['soap_version'].choices.append([name, name])
            
        self.fields['security'].choices = []
        self.fields['security'].choices.append(['', '----------'])
        self.fields['security'].choices.append([ZATO_NONE, 'No security'])
        
        for value, label in security_list:
            self.fields['security'].choices.append([value, label])
            
        self.fields['ping_method'].initial = DEFAULT_HTTP_PING_METHOD
        self.fields['pool_size'].initial = DEFAULT_HTTP_POOL_SIZE

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    merge_url_params_req = forms.BooleanField(required=False, widget=forms.CheckboxInput())

class ChooseClusterForm(_ChooseClusterForm):
    connection = forms.CharField(widget=forms.HiddenInput())
    transport = forms.CharField(widget=forms.HiddenInput())
