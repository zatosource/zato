# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_sec_tls_ca_cert_id_select, add_security_select, add_select, add_services, \
    SearchForm as _ChooseClusterForm, DataFormatForm, WithAuditLog
from zato.common.api import DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, HTTP_SOAP, HTTP_SOAP_SERIALIZATION_TYPE, \
     MISC, PARAMS_PRIORITY, RATE_LIMIT, SIMPLE_IO, SOAP_VERSIONS, URL_PARAMS_PRIORITY

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

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(DataFormatForm, WithAuditLog):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    host = forms.CharField(initial='http://', widget=forms.TextInput(attrs={'style':'width:100%'}))
    url_path = forms.CharField(initial='/', widget=forms.TextInput(attrs={'style':'width:100%'}))
    match_slash = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    merge_url_params_req = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    url_params_pri = forms.ChoiceField(widget=forms.Select())
    params_pri = forms.ChoiceField(widget=forms.Select())
    serialization_type = forms.ChoiceField(widget=forms.Select())
    sec_tls_ca_cert_id = forms.ChoiceField(widget=forms.Select())
    method = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    soap_action = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    soap_version = forms.ChoiceField(widget=forms.Select())
    service = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:100%'}))
    ping_method = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    pool_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}))
    timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}), initial=MISC.DEFAULT_HTTP_TIMEOUT)
    security = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    has_rbac = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    content_type = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    connection = forms.CharField(widget=forms.HiddenInput())
    transport = forms.CharField(widget=forms.HiddenInput())
    cache_id = forms.ChoiceField(widget=forms.Select())
    cache_expiry = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}), initial=0)
    content_encoding = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    data_formats_allowed = SIMPLE_IO.HTTP_SOAP_FORMAT
    http_accept = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=HTTP_SOAP.ACCEPT.ANY)

    is_rate_limit_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    rate_limit_check_parent_def = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    rate_limit_type = forms.ChoiceField(widget=forms.Select(), initial=RATE_LIMIT.TYPE.APPROXIMATE)
    rate_limit_def = forms.CharField(widget=forms.Textarea(
        attrs={'style':'overflow:auto; width:100%; white-space: pre-wrap;height:100px'}))

    hl7_version = forms.CharField(widget=forms.HiddenInput())
    json_path = forms.CharField(widget=forms.HiddenInput())
    data_encoding = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, security_list=None, sec_tls_ca_cert_list=None, cache_list=None, soap_versions=SOAP_VERSIONS,
            prefix=None, post_data=None, req=None):

        security_list = security_list or []
        sec_tls_ca_cert_list = sec_tls_ca_cert_list or {}
        cache_list = cache_list or []

        super(CreateForm, self).__init__(post_data, prefix=prefix)
        super(WithAuditLog).__init__()

        self.fields['url_params_pri'].choices = []
        for value, label in url_params_priority:
            self.fields['url_params_pri'].choices.append([value, label])

        self.fields['params_pri'].choices = []
        for value, label in params_priority:
            self.fields['params_pri'].choices.append([value, label])

        self.fields['serialization_type'].choices = []
        for item in HTTP_SOAP_SERIALIZATION_TYPE():
            self.fields['serialization_type'].choices.append([item.id, item.name])

        self.fields['soap_version'].choices = []
        for name in sorted(soap_versions):
            self.fields['soap_version'].choices.append([name, name])

        self.fields['ping_method'].initial = DEFAULT_HTTP_PING_METHOD
        self.fields['pool_size'].initial = DEFAULT_HTTP_POOL_SIZE

        add_security_select(self, security_list)
        add_sec_tls_ca_cert_id_select(req, self)

        add_services(self, req)
        add_select(self, 'cache_id', cache_list)
        add_select(self, 'rate_limit_type', RATE_LIMIT.TYPE(), needs_initial_select=False)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    merge_url_params_req = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    match_slash = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    has_rbac = forms.BooleanField(required=False, widget=forms.CheckboxInput())

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
