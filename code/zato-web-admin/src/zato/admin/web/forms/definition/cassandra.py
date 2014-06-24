# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common import CASSANDRA

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    contact_points = forms.CharField(initial=CASSANDRA.DEFAULT.CONTACT_POINTS.value, widget=forms.Textarea(attrs={'style':'width:100%'}))
    port = forms.CharField(initial=CASSANDRA.DEFAULT.PORT.value, widget=forms.TextInput(attrs={'class':'required', 'style':'width:15%'}))
    exec_size = forms.CharField(initial=CASSANDRA.DEFAULT.EXEC_SIZE.value, widget=forms.TextInput(attrs={'class':'required', 'style':'width:15%'}))
    proto_version = forms.CharField(initial=CASSANDRA.DEFAULT.PROTOCOL_VERSION.value, widget=forms.TextInput(attrs={'class':'required', 'style':'width:15%'}))
    cql_version = forms.CharField(initial=CASSANDRA.DEFAULT.CQL_VERSION.value, widget=forms.TextInput(attrs={'class':'required', 'style':'width:15%'}))
    default_keyspace = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:50%'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:50%'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'required', 'style':'width:50%'}))

class EditForm(CreateForm):
    pass
