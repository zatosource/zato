# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select, add_select
from zato.common.api import PUBSUB, skip_endpoint_types

# ################################################################################################################################

class CreateForm(forms.Form):

    # Common ones
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    endpoint_type = forms.ChoiceField(widget=forms.Select())
    is_internal = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    role = forms.ChoiceField(widget=forms.Select())
    topic_patterns = forms.CharField(widget=forms.Textarea(attrs={
        'style':'width:100%; height:120px',
        'placeholder':'pub=/*\nsub=/*',
    }))

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
        add_select(self, 'role', PUBSUB.ROLE())
        add_select(self, 'endpoint_type', PUBSUB.ENDPOINT_TYPE().get_pub_types(),
            needs_initial_select=False, skip=skip_endpoint_types)

        # Let's assume the default type of pub/sub endpoint will be REST clients
        self.initial['endpoint_type'] = PUBSUB.ENDPOINT_TYPE.REST.id

# ################################################################################################################################

class EditForm(CreateForm):
    is_internal = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
