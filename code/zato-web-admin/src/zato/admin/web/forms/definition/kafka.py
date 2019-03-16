# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import WithTLSForm
from zato.common import KAFKA

default = KAFKA.DEFAULT
timeout = default.TIMEOUT

class CreateForm(WithTLSForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    should_use_zookeeper = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    should_exclude_internal_topics = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    socket_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:7%'}), initial=timeout.SOCKET)
    offset_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:7%'}), initial=timeout.OFFSETS)

    source_address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:19%'}))
    broker_version = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}), initial=default.BROKER_VERSION)

    server_list = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:70px'}), initial=default.SERVER_LIST)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    should_use_zookeeper = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    should_exclude_internal_topics = forms.BooleanField(required=False, widget=forms.CheckboxInput())
