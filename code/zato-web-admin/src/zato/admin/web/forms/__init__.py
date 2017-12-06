# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common import DELEGATED_TO_RBAC, SIMPLE_IO, ZATO_NONE, ZATO_SEC_USE_RBAC

INITIAL_CHOICES_DICT = {'': '----------'}
INITIAL_CHOICES = INITIAL_CHOICES_DICT.items()[0]

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
        id = getattr(elem, 'id', None) or elem['id']
        if id in skip:
            continue
        name = getattr(elem, 'name', None) or elem['name']
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

def add_services(form, req, by_id=False, initial_service=None, api_name='zato.service.get-list', has_name_filter=True):
    if req.zato.cluster_id:

        service_fields = ['service_name', 'service_id', 'service', 'hook_service_id', 'hook_service_name']

        for name in service_fields:
            field = form.fields.get(name)
            if field:
                field_name = name
                break
        else:
            raise ValueError('Could not find any service field (tried: `{}` in `{}`)'.format(
                service_fields, form.fields))

        field.choices = []
        field.choices.append(INITIAL_CHOICES)

        request = {'cluster_id': req.zato.cluster_id, 'name_filter':'*'}
        if has_name_filter:
            request['name_filter'] = '*'

        for service in req.zato.client.invoke(api_name, request).data:

            # Older parts of web-admin use service names only but newer ones prefer service ID
            id_attr = service.id if by_id else service.name
            field.choices.append([id_attr, service.name])

        if initial_service:
            form.initial[field_name] = initial_service

# ################################################################################################################################

def add_pubsub_services(form, req, by_id=False, initial_service=None):
    return add_services(form, req, by_id, initial_service, 'zato.pubsub.hook.get-hook-service-list', False)

# ################################################################################################################################

def add_select_from_service(form, req, service_name, field_names, by_id=True):
    if req.zato.cluster_id:

        field_names = field_names if isinstance(field_names, list) else [field_names]

        field = None
        for name in field_names:
            field = form.fields.get(name)
            if field:
                break

        field.choices = []
        field.choices.append(INITIAL_CHOICES)

        for item in req.zato.client.invoke(service_name, {'cluster_id': req.zato.cluster_id, }).data:
            id_attr = item.id if by_id else item.name
            field.choices.append([id_attr, item.name])

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
            initial = dict(data.iteritems())
            initial.update({'cluster':clusters[0].id})
            self.zato_auto_submit = True
        else:
            initial = None
            self.zato_auto_submit = False

        super(SearchForm, self).__init__(initial)

        self.fields['cluster'].choices = [INITIAL_CHOICES]
        for cluster in clusters:
            server_info = '{0} - http://{1}:{2}'.format(cluster.name, cluster.lb_host, cluster.lb_port)
            self.fields['cluster'].choices.append([cluster.id, server_info])

        self.initial['cluster'] = (data.get('cluster') or [''])[0]

# ################################################################################################################################

class ChangePasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'required'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'required validate-password-confirm'}))

# ################################################################################################################################

class DataFormatForm(forms.Form):
    data_format = forms.ChoiceField(widget=forms.Select())
    data_formats_allowed = None

    def __init__(self, *args, **kwargs):
        super(DataFormatForm, self).__init__(*args, **kwargs)
        self.fields['data_format'].choices = []
        self.fields['data_format'].choices.append(INITIAL_CHOICES)

        for code, name in (self.data_formats_allowed or SIMPLE_IO.COMMON_FORMAT).iteritems():
            self.fields['data_format'].choices.append([code, name])

# ################################################################################################################################

class UploadForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'size':'70'}))

# ################################################################################################################################
