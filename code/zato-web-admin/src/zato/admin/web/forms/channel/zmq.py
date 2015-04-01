# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_services, DataFormatForm
from zato.common import ZMQ_CHANNEL_TYPES

class CreateForm(DataFormatForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    socket_type = forms.ChoiceField(widget=forms.Select())
    service = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    sub_key = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        
        self.fields['socket_type'].choices = []
        for name in sorted(ZMQ_CHANNEL_TYPES):
            self.fields['socket_type'].choices.append([name, name])

        add_services(self, req)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
