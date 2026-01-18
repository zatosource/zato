# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select, add_select, add_services, \
    SearchForm as _ChooseClusterForm, DataFormatForm
from zato.common.api import DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, HTTP_SOAP, HTTP_SOAP_SERIALIZATION_TYPE, \
     MISC, PARAMS_PRIORITY, SIMPLE_IO, SOAP_VERSIONS, URL_PARAMS_PRIORITY

# ################################################################################################################################

params_priority = (
    (PARAMS_PRIORITY.CHANNEL_PARAMS_OVER_MSG, 'URL over message'),
    (PARAMS_PRIORITY.MSG_OVER_CHANNEL_PARAMS, 'Message over URL'),
)

# ################################################################################################################################

url_params_priority = (
    (URL_PARAMS_PRIORITY.QS_OVER_PATH, 'QS over path'),
    (URL_PARAMS_PRIORITY.PATH_OVER_QS, 'Path over QS'),
)

validate_tls_choices = (
    (True, 'Yes'),
    (False, 'No'),
)

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(DataFormatForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    host = forms.CharField(initial='http://', widget=forms.TextInput(attrs={'style':'width:100%'}))
    url_path = forms.CharField(initial='/', widget=forms.TextInput(attrs={'style':'width:100%'}))
    match_slash = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    merge_url_params_req = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    url_params_pri = forms.ChoiceField(widget=forms.Select())
    params_pri = forms.ChoiceField(widget=forms.Select())
    serialization_type = forms.CharField(widget=forms.HiddenInput(), initial='string')
    method = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    soap_action = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    soap_version = forms.ChoiceField(widget=forms.Select())
    service = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:100%'}))
    ping_method = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    pool_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}))
    timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}), initial=MISC.DEFAULT_HTTP_TIMEOUT)
    security = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    content_type = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    connection = forms.CharField(widget=forms.HiddenInput())
    transport = forms.CharField(widget=forms.HiddenInput())
    cache_id = forms.ChoiceField(widget=forms.Select())
    cache_expiry = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}), initial=0)
    content_encoding = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    data_formats_allowed = SIMPLE_IO.HTTP_SOAP_FORMAT
    http_accept = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=HTTP_SOAP.ACCEPT.ANY)
    validate_tls = forms.ChoiceField(widget=forms.Select())

    data_encoding = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, security_list=None, cache_list=None, soap_versions=SOAP_VERSIONS,
            prefix=None, post_data=None, req=None):

        security_list = security_list or []
        cache_list = cache_list or []

        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['url_params_pri'].choices = []
        for value, label in url_params_priority:
            self.fields['url_params_pri'].choices.append([value, label])

        self.fields['params_pri'].choices = []
        for value, label in params_priority:
            self.fields['params_pri'].choices.append([value, label])

        self.fields['serialization_type'].initial = 'string'

        self.fields['soap_version'].choices = []
        for name in sorted(soap_versions):
            self.fields['soap_version'].choices.append([name, name])

        self.fields['validate_tls'].choices = []
        for value, label in validate_tls_choices:
            self.fields['validate_tls'].choices.append([value, label])

        self.fields['ping_method'].initial = DEFAULT_HTTP_PING_METHOD
        self.fields['pool_size'].initial = DEFAULT_HTTP_POOL_SIZE

        add_security_select(self, security_list)

        add_services(self, req)
        add_select(self, 'cache_id', cache_list)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    merge_url_params_req = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    match_slash = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################

class SearchForm(_ChooseClusterForm):
    connection = forms.CharField(widget=forms.HiddenInput())
    transport = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, clusters, data=None):
        super(SearchForm, self).__init__(clusters, data)

        self.initial['connection'] = data.get('connection') or ''
        self.initial['transport'] = data.get('transport') or ''

# ################################################################################################################################
# ################################################################################################################################
