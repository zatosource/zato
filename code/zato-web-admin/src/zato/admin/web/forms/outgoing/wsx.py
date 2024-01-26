# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select, add_services, DataFormatForm
from zato.common.api import WEB_SOCKET

class CreateForm(DataFormatForm):
    data_format = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:60px'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    is_zato = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    has_auto_reconnect = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%', 'placeholder':'wss://'}))
    address_masked = forms.CharField(widget=forms.HiddenInput())

    ping_interval = forms.CharField(initial=WEB_SOCKET.DEFAULT.PING_INTERVAL,
        widget=forms.TextInput(attrs={'style':'width:10%'}))

    pings_missed_threshold = forms.CharField(initial=WEB_SOCKET.DEFAULT.PINGS_MISSED_THRESHOLD_OUTGOING,
        widget=forms.TextInput(attrs={'style':'width:10%', 'disabled':'disabled'}))

    socket_read_timeout = forms.CharField(initial=WEB_SOCKET.DEFAULT.Socket_Read_Timeout,
        widget=forms.TextInput(attrs={'style':'width:10%'}))

    socket_write_timeout = forms.CharField(initial=WEB_SOCKET.DEFAULT.Socket_Write_Timeout,
        widget=forms.TextInput(attrs={'style':'width:10%', 'disabled':'disabled'}))

    on_connect_service_name = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    on_message_service_name = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    on_close_service_name = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    security_def = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    subscription_list = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:60px'}))

    def __init__(self, security_list=None, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        add_services(self, req, by_id=False)
        add_security_select(self, security_list, field_name='security_def', needs_rbac=False)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_zato = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    has_auto_reconnect = forms.BooleanField(required=False, widget=forms.CheckboxInput())
