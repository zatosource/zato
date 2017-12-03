# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select, add_select
from zato.common import PUBSUB

# ################################################################################################################################

class CreateForm(forms.Form):

    # Common ones
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    endpoint_type = forms.ChoiceField(widget=forms.Select())
    is_internal = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    role = forms.ChoiceField(widget=forms.Select())
    topic_patterns = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:120px'}))

    # REST/SOAP
    security_id = forms.ChoiceField(widget=forms.Select())

    # Service
    service_id = forms.ChoiceField(widget=forms.Select())

    # WebSockets
    ws_channel_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, req, data_list, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['role'].choices = []
        self.fields['ws_channel_id'].choices = []

        add_security_select(self, data_list.security_list, field_name='security_id', needs_no_security=False, needs_rbac=False)
        add_select(self, 'service_id', data_list.service_list)
        add_select(self, 'ws_channel_id', data_list.ws_channel_list)
        add_select(self, 'role', PUBSUB.ROLE)
        add_select(self, 'endpoint_type', PUBSUB.ENDPOINT_TYPE, needs_initial_select=False)

        # Let's assume the default type of pub/sub endpoint will be REST clients
        self.initial['endpoint_type'] = PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id

# ################################################################################################################################

class EditForm(CreateForm):
    is_internal = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################

class EndpointQueueEditForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    active_status = forms.ChoiceField(widget=forms.Select())
    is_staging_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    has_gd = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    sub_key = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:70%'}))

    def __init__(self, *args, **kwargs):
        super(EndpointQueueEditForm, self).__init__(prefix='edit', *args, **kwargs)
        add_select(self, 'active_status', PUBSUB.QUEUE_ACTIVE_STATUS, False)

# ################################################################################################################################
