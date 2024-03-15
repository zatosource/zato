# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_services, DataFormatForm
from zato.common.api import ZMQ

class CreateForm(DataFormatForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    socket_type = forms.ChoiceField(widget=forms.Select())
    socket_method = forms.ChoiceField(widget=forms.Select())
    service = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    sub_key = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    pool_strategy = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:20%'}))
    service_source = forms.ChoiceField(widget=forms.Select())

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self._add_field('socket_type', ZMQ.CHANNEL)
        self._add_field('socket_method', ZMQ.METHOD)
        self._add_field('pool_strategy', ZMQ.POOL_STRATEGY)
        self._add_field('service_source', ZMQ.SERVICE_SOURCE)

        add_services(self, req)

    def _add_field(self, field_name, source):
        self.fields[field_name].choices = []
        for code, name in source.items():
            self.fields[field_name].choices.append([code, name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
