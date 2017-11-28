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
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    endpoint_type = forms.ChoiceField(widget=forms.Select())
    endpoint_id = forms.ChoiceField(widget=forms.Select())
    topic_list_text = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:120px'}))
    topic_list_json = forms.CharField(widget=forms.Textarea(attrs={'display':'none'}))

    # REST/SOAP
    security_id = forms.ChoiceField(widget=forms.Select())

    # Service
    service_id = forms.ChoiceField(widget=forms.Select())

    # WebSockets
    ws_channel_id = forms.ChoiceField(widget=forms.Select())

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
