# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common import SIMPLE_IO, ZATO_NONE

INITIAL_CHOICES_DICT = {'': '----------'}
INITIAL_CHOICES = INITIAL_CHOICES_DICT.items()[0]

# ################################################################################################################################

def add_security_select(form, security_list, needs_no_security=True, field_name='security'):
    form.fields[field_name].choices = []
    form.fields[field_name].choices.append(INITIAL_CHOICES)

    if needs_no_security:
        form.fields[field_name].choices.append([ZATO_NONE, 'No security definition'])

    for value, label in security_list:
        form.fields[field_name].choices.append([value, label])

# ################################################################################################################################

def add_services(form, req):
    if req.zato.cluster_id:

        # Either must exist
        field = form.fields.get('service_name') or form.fields['service']
        field.choices[:] = []
        field.choices.append(INITIAL_CHOICES)

        for service in req.zato.client.invoke(
            'zato.service.get-list', {'cluster_id': req.zato.cluster_id, 'name_filter':'*'}).data:
            field.choices.append([service.name, service.name])

# ################################################################################################################################

class ChooseClusterForm(forms.Form):

    cluster = forms.ChoiceField(widget=forms.Select())
    name_filter = forms.CharField(widget=forms.TextInput(
        attrs={'style':'width:30%', 'class':'required', 'placeholder':"Enter * or part of a service's name, e.g. http json"}))

    def __init__(self, clusters, data=None):

        data = data or {}

        #
        # https://github.com/zatosource/zato/issues/361
        #
        # If the length is 1 it we have a single cluster only defined in ODB.
        # This means we can make use that only one straightaway to display anything that is needed.
        #

        if len(clusters) == 1:
            initial = dict(data.iteritems())
            initial.update({'cluster':clusters[0].id})
            self.zato_auto_submit = True
        else:
            initial = None
            self.zato_auto_submit = False

        super(ChooseClusterForm, self).__init__(initial)

        self.fields['cluster'].choices = [INITIAL_CHOICES]
        for cluster in clusters:
            server_info = '{0} - http://{1}:{2}'.format(cluster.name, cluster.lb_host, cluster.lb_port)
            self.fields['cluster'].choices.append([cluster.id, server_info])

# ################################################################################################################################

class ChangePasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'required'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'required validate-password-confirm'}))

# ################################################################################################################################

class DataFormatForm(forms.Form):
    data_format = forms.ChoiceField(widget=forms.Select())
    
    def __init__(self, *args, **kwargs):
        super(DataFormatForm, self).__init__(*args, **kwargs)
        self.fields['data_format'].choices = []
        self.fields['data_format'].choices.append(INITIAL_CHOICES)
        for name in sorted(dir(SIMPLE_IO.FORMAT)):
            if name.upper() == name:
                self.fields['data_format'].choices.append([name.lower(), name])

# ################################################################################################################################

class UploadForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'size':'70'}))

# ################################################################################################################################
