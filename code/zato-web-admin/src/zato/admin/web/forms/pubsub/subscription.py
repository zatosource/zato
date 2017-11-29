# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common import PUBSUB
from zato.admin.web.forms import add_security_select, add_select

# ################################################################################################################################

class CreateForm(forms.Form):

    id = forms.CharField(widget=forms.HiddenInput())
    endpoint_type = forms.ChoiceField(widget=forms.Select())
    endpoint_id = forms.ChoiceField(widget=forms.Select())

    active_status = forms.ChoiceField(widget=forms.Select())
    is_staging_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    delivery_batch_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:15%'}))
    wrap_one_msg_in_list = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    delivery_max_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:15%'}))

    delivery_max_retry = forms.CharField(widget=forms.TextInput(attrs={'style':'width:15%'}))
    delivery_err_should_block = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    wait_sock_err = forms.CharField(widget=forms.TextInput(attrs={'style':'width:15%'}))
    wait_non_sock_err = forms.CharField(widget=forms.TextInput(attrs={'style':'width:15%'}))

    delivery_method = forms.ChoiceField(widget=forms.Select())
    delivery_data_format = forms.ChoiceField(widget=forms.Select())

    delivery_endpoint = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    out_http_soap_id = forms.ChoiceField(widget=forms.Select())
    out_amqp_id = forms.ChoiceField(widget=forms.Select())

    hook_service_id = forms.ChoiceField(widget=forms.Select())

    # REST/SOAP
    security_id = forms.ChoiceField(widget=forms.Select())

    # Service
    service_id = forms.ChoiceField(widget=forms.Select())

    # WebSockets
    ws_channel_id = forms.ChoiceField(widget=forms.Select())

    topic_list_text = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:120px'}))
    topic_list_json = forms.CharField(widget=forms.Textarea(attrs={'display':'none'}))

    def __init__(self, req, data_list, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)

        add_security_select(self, data_list.security_list, field_name='security_id', needs_no_security=False, needs_rbac=False)
        add_select(self, 'endpoint_type', PUBSUB.ENDPOINT_TYPE, needs_initial_select=False,
            skip=PUBSUB.ENDPOINT_TYPE.WEB_SOCKETS.id)
        add_select(self, 'service_id', data_list.service_list)

        # Let's assume the default type of pub/sub endpoint will be REST clients
        self.initial['endpoint_type'] = PUBSUB.ENDPOINT_TYPE.REST.id

# ################################################################################################################################

class EditForm(CreateForm):
    pass

# ################################################################################################################################
