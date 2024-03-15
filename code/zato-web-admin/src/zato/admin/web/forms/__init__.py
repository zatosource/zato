# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Python 2/3 compatibility
from zato.common.ext.future.utils import iteritems
from zato.common.py23_.past.builtins import basestring

# Zato
from zato.common.api import AuditLog, DELEGATED_TO_RBAC, RATE_LIMIT, SIMPLE_IO, TLS, ZATO_DEFAULT, ZATO_NONE, ZATO_SEC_USE_RBAC

# ################################################################################################################################

INITIAL_CHOICES_DICT = {'': '----------'}
Initial_Choices_Dict_Attrs = {'id':'', 'name':'----------'}
INITIAL_CHOICES = list(iteritems(INITIAL_CHOICES_DICT))[0]

# ################################################################################################################################

SELECT_SERVICE_FIELDS = [
    'hook_service_id',
    'hook_service_name',
    'on_close_service_name',
    'on_connect_service_name',
    'on_message_service_name',
    'service',
    'service_id',
    'service_list',
    'service_name',
]

# ################################################################################################################################

SELECT_TOPICS_FIELDS = [
    'topic_list',
    'topic_name',
]

# ################################################################################################################################

def add_initial_select(form, field_name):
    form.fields[field_name].choices = []
    form.fields[field_name].choices.append(INITIAL_CHOICES)

# ################################################################################################################################

def add_select(form, field_name, elems, needs_initial_select=True, skip=None):
    skip = skip or []
    if not isinstance(skip, (list, tuple)):
        skip = [skip]

    if needs_initial_select:
        add_initial_select(form, field_name)
    else:
        form.fields[field_name].choices = []

    for elem in elems:

        if isinstance(elem, basestring):
            id = elem
            name = elem
        else:
            id = getattr(elem, 'id', None) or elem['id']
            name = getattr(elem, 'name', None) or elem['name']

        if id in skip:
            continue

        form.fields[field_name].choices.append([id, name])

# ################################################################################################################################

def add_security_select(form, security_list, needs_no_security=True, field_name='security', needs_rbac=True):
    form.fields[field_name].choices = []
    form.fields[field_name].choices.append(INITIAL_CHOICES)

    if needs_no_security:
        form.fields[field_name].choices.append([ZATO_NONE, 'No security definition'])

    if needs_rbac:
        form.fields[field_name].choices.append([ZATO_SEC_USE_RBAC, DELEGATED_TO_RBAC])

    for value, label in security_list:
        form.fields[field_name].choices.append([value, label])

# ################################################################################################################################

def add_sec_tls_ca_cert_id_select(req, form):

    from zato.admin.web.views import get_tls_ca_cert_list

    tls_ca_cert_list = get_tls_ca_cert_list(req.zato.client, req.zato.cluster)

    form.fields['sec_tls_ca_cert_id'].choices = []
    form.fields['sec_tls_ca_cert_id'].choices.append([ZATO_DEFAULT, 'Default bundle'])
    form.fields['sec_tls_ca_cert_id'].choices.append([ZATO_NONE, 'Skip validation'])

    for value, label in tls_ca_cert_list.items():
        form.fields['sec_tls_ca_cert_id'].choices.append([value, label])

# ################################################################################################################################

def add_http_soap_select(form, field_name, req, connection, transport, needs_initial_select=True, skip=None):

    skip = skip or []
    if not isinstance(skip, (list, tuple)):
        skip = [skip]

    if needs_initial_select:
        add_initial_select(form, field_name)
    else:
        form.fields[field_name].choices = []

    field = form.fields[field_name]

    if req.zato.cluster_id:

        response = req.zato.client.invoke('zato.http-soap.get-list', {
            'cluster_id': req.zato.cluster_id,
            'connection': connection,
            'transport': transport,
        })

        for item in response.data:
            field.choices.append([item.id, item.name])

# ################################################################################################################################

def add_services(form, req, by_id=False, initial_service=None, api_name='zato.service.get-list', has_name_filter=True,
    should_include_scheduler=False):

    if req.zato.cluster_id:

        fields = {}

        for name in SELECT_SERVICE_FIELDS:
            field = form.fields.get(name)
            if field:
                fields[name] = field

        if not fields:
            raise ValueError('Could not find any service field (tried: `{}` in `{}`)'.format(
                SELECT_SERVICE_FIELDS, form.fields))

        for field_name, field in fields.items():

            field.choices = []
            field.choices.append(INITIAL_CHOICES)

            request = {
                'cluster_id': req.zato.cluster_id,
                'name_filter':'*',
                'should_include_scheduler': should_include_scheduler,
            }

            if has_name_filter:
                request['name_filter'] = '*'

            response = req.zato.client.invoke(api_name, request)
            data = response.data

            for service in data:

                # Older parts of web-admin use service names only but newer ones prefer service ID
                id_attr = service.id if by_id else service.name
                field.choices.append([id_attr, service.name])

            if initial_service:
                form.initial[field_name] = initial_service

# ################################################################################################################################

def add_pubsub_services(form, req, by_id=False, initial_service=None):
    return add_services(form, req, by_id, initial_service, 'zato.pubsub.hook.get-hook-service-list', False)

# ################################################################################################################################

def add_topics(form, req, by_id=True):
    return add_select_from_service(form, req, 'zato.pubsub.topic.get-list', SELECT_TOPICS_FIELDS, by_id=by_id)

# ################################################################################################################################

def add_select_from_service(form, req, service_name, field_names, by_id=True, service_extra=None):
    if req.zato.cluster_id:

        field_names = field_names if isinstance(field_names, list) else [field_names]

        field = None
        for name in field_names:
            field = form.fields.get(name)
            if field:
                break

        field.choices = []
        field.choices.append(INITIAL_CHOICES)

        service_request = {'cluster_id': req.zato.cluster_id}
        service_request.update(service_extra or {})

        response = req.zato.client.invoke(service_name, service_request)
        response = response.data if isinstance(response.data, list) else response.data.response

        for item in response:
            id_attr = item.id if by_id else item.name
            field.choices.append([id_attr, item.name])

# ################################################################################################################################
# ################################################################################################################################

class SearchForm(forms.Form):

    cluster = forms.ChoiceField(widget=forms.Select())
    query = forms.CharField(widget=forms.TextInput(
        attrs={'style':'width:40%', 'class':'required', 'placeholder':'Enter search terms'}))

    def __init__(self, clusters, data=None):

        data = data or {}

        #
        # https://github.com/zatosource/zato/issues/361
        #
        # If the length is 1 it we have only one cluster defined in ODB.
        # This means we can make use that only one straightaway to display anything that is needed.
        #

        if len(clusters) == 1:
            initial = dict(iteritems(data))
            initial.update({'cluster':clusters[0].id})
            self.zato_auto_submit = True
        else:
            initial = {'query': data.get('query', '')}
            self.zato_auto_submit = False

        super(SearchForm, self).__init__(initial)

        self.fields['cluster'].choices = [INITIAL_CHOICES]
        for cluster in clusters:
            server_info = '{0} - http://{1}:{2}'.format(cluster.name, cluster.lb_host, cluster.lb_port)
            self.fields['cluster'].choices.append([cluster.id, server_info])

        self.initial['cluster'] = (data.get('cluster') or [''])[0]

# ################################################################################################################################
# ################################################################################################################################

class ChangePasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class':'required', 'style':'width:100%'}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class':'required validate-password-confirm', 'style':'width:100%'}))

# ################################################################################################################################
# ################################################################################################################################

class DataFormatForm(forms.Form):
    data_format = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100px'}))
    data_formats_allowed = None

    def __init__(self, *args, **kwargs):
        super(DataFormatForm, self).__init__(*args, **kwargs)
        self.fields['data_format'].choices = []
        self.fields['data_format'].choices.append(INITIAL_CHOICES)

        for code, name in iteritems(self.data_formats_allowed or SIMPLE_IO.COMMON_FORMAT):
            self.fields['data_format'].choices.append([code, name])

# ################################################################################################################################
# ################################################################################################################################

class UploadForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'size':'70'}))

# ################################################################################################################################
# ################################################################################################################################

class WithTLSForm(forms.Form):

    is_tls_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    tls_private_key_file = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_cert_file = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_ca_certs_file = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_crl_file = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_version = forms.ChoiceField(widget=forms.Select(), initial=TLS.DEFAULT.VERSION)
    tls_validate = forms.ChoiceField(widget=forms.Select(), initial=TLS.CERT_VALIDATE.CERT_REQUIRED.id)
    tls_pem_passphrase = forms.CharField(widget=forms.PasswordInput(attrs={'style':'width:100%'}))
    is_tls_match_hostname_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    tls_ciphers = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=TLS.DEFAULT.CIPHERS)

    def __init__(self, prefix=None, post_data=None):
        super(WithTLSForm, self).__init__(post_data, prefix=prefix)

        add_select(self, 'tls_version', TLS.VERSION(), needs_initial_select=False)
        add_select(self, 'tls_validate', TLS.CERT_VALIDATE(), needs_initial_select=False)

# ################################################################################################################################
# ################################################################################################################################

class WithJSONSchema(forms.Form):
    is_json_schema_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    needs_json_schema_err_details = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################

class WithRateLimiting(forms.Form):
    rate_limit_type = forms.ChoiceField(widget=forms.Select(), initial=RATE_LIMIT.TYPE.APPROXIMATE)
    rate_limit_def = forms.CharField(widget=forms.Textarea(
        attrs={'style':'overflow:auto; width:100%; white-space: pre-wrap;height:100px'}))

    def __init__(self, *args, **kwargs):
        super(WithRateLimiting, self).__init__(*args, **kwargs)

        add_select(self, 'rate_limit_type', RATE_LIMIT.TYPE(), needs_initial_select=False)

# ################################################################################################################################
# ################################################################################################################################

class WithAuditLog(forms.Form):
    is_audit_log_sent_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_audit_log_received_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    max_len_messages_sent = forms.CharField(
        initial=AuditLog.Default.max_len_messages, widget=forms.TextInput(attrs={'style':'width:10%'}))

    max_len_messages_received = forms.CharField(
        initial=AuditLog.Default.max_len_messages, widget=forms.TextInput(attrs={'style':'width:10%'}))

    max_bytes_per_message_sent = forms.CharField(
        initial=AuditLog.Default.max_data_stored_per_message, widget=forms.TextInput(attrs={'style':'width:13%'}))

    max_bytes_per_message_received = forms.CharField(
        initial=AuditLog.Default.max_data_stored_per_message, widget=forms.TextInput(attrs={'style':'width:13%'}))

# ################################################################################################################################
# ################################################################################################################################
