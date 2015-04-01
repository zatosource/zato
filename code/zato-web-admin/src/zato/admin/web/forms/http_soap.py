# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select, add_services, ChooseClusterForm as _ChooseClusterForm, DataFormatForm, \
     INITIAL_CHOICES
from zato.common import BATCH_DEFAULTS, DEFAULT_HTTP_PING_METHOD, DEFAULT_HTTP_POOL_SIZE, HTTP_SOAP_SERIALIZATION_TYPE, \
     MISC, MSG_PATTERN_TYPE, PARAMS_PRIORITY, SOAP_VERSIONS, URL_PARAMS_PRIORITY, ZATO_NONE

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
    serialization_type = forms.ChoiceField(widget=forms.Select())
    sec_tls_ca_cert_id = forms.ChoiceField(widget=forms.Select())
    method = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    soap_action = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    soap_version = forms.ChoiceField(widget=forms.Select())
    service = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:100%'}))
    ping_method = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    pool_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}))
    timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}), initial=MISC.DEFAULT_HTTP_TIMEOUT)
    security = forms.ChoiceField(widget=forms.Select())
    has_rbac = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    connection = forms.CharField(widget=forms.HiddenInput())
    transport = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, security_list=[], sec_tls_ca_cert_list={}, soap_versions=SOAP_VERSIONS,
            prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['url_params_pri'].choices = []
        for value, label in url_params_priority:
            self.fields['url_params_pri'].choices.append([value, label])

        self.fields['params_pri'].choices = []
        for value, label in params_priority:
            self.fields['params_pri'].choices.append([value, label])

        self.fields['serialization_type'].choices = []
        for item in HTTP_SOAP_SERIALIZATION_TYPE:
            self.fields['serialization_type'].choices.append([item.id, item.name])

        self.fields['soap_version'].choices = []
        for name in sorted(soap_versions):
            self.fields['soap_version'].choices.append([name, name])

        self.fields['sec_tls_ca_cert_id'].choices = []
        self.fields['sec_tls_ca_cert_id'].choices.append(INITIAL_CHOICES)
        self.fields['sec_tls_ca_cert_id'].choices.append([ZATO_NONE, 'Skip validation'])

        for value, label in sec_tls_ca_cert_list.items():
            self.fields['sec_tls_ca_cert_id'].choices.append([value, label])

        self.fields['ping_method'].initial = DEFAULT_HTTP_PING_METHOD
        self.fields['pool_size'].initial = DEFAULT_HTTP_POOL_SIZE

        add_security_select(self, security_list)
        add_services(self, req)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    merge_url_params_req = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    has_rbac = forms.BooleanField(required=False, widget=forms.CheckboxInput())

class ChooseClusterForm(_ChooseClusterForm):
    connection = forms.CharField(widget=forms.HiddenInput())
    transport = forms.CharField(widget=forms.HiddenInput())

class ReplacePatternsForm(forms.Form):
    audit_repl_patt_type = forms.ChoiceField(widget=forms.Select())
    pattern_list = forms.CharField(widget=forms.Textarea(attrs={'rows':13, 'cols':70}), required=False)
    audit_max_payload = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))

    def __init__(self, initial=None):
        super(ReplacePatternsForm, self).__init__(initial=initial)

        self.fields['audit_repl_patt_type'].choices = []
        self.fields['audit_repl_patt_type'].choices.append(['', '----------'])

        for item in MSG_PATTERN_TYPE:
            self.fields['audit_repl_patt_type'].choices.append([item.id, item.name])

class AuditLogEntryList(forms.Form):
    """ List of audit log entries for a given HTTP/SOAP object.
    """
    start = forms.CharField(widget=forms.TextInput(attrs={'style':'width:150px; height:19px'}))
    stop = forms.CharField(widget=forms.TextInput(attrs={'style':'width:150px; height:19px'}))
    current_batch = forms.CharField(initial=BATCH_DEFAULTS.PAGE_NO, widget=forms.TextInput(attrs={'style':'width:50px; height:19px'}))
    batch_size = forms.CharField(initial=BATCH_DEFAULTS.SIZE, widget=forms.TextInput(attrs={'style':'width:50px; height:19px'}))
