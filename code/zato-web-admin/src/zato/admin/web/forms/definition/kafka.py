# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_services, WithTLSForm
from zato.common.api import Kafka

default = Kafka.Default
timeout = default.Timeout

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(WithTLSForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    should_use_zookeeper = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    should_exclude_internal_topics = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    socket_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:7%'}), initial=timeout.Socket)
    offset_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:7%'}), initial=timeout.Offsets)

    source_address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:44%'}))
    broker_version = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}), initial=default.Broker_Version)

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=default.Username)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'style':'width:100%'}))

    server_list = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:40px'}), initial=default.Server_List)

    topic_list = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:40px'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))

    def __init__(self, prefix:'any_'=None, post_data:'any_'=None, req:'any_'=None):
        super().__init__(post_data=post_data, prefix=prefix)
        add_services(self, req)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    should_use_zookeeper = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    should_exclude_internal_topics = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
