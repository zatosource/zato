# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django import forms

# Zato
from zato.admin.web.util import get_pubsub_security_choices
from zato.common.api import PubSub

logger = logging.getLogger()

def get_rest_endpoint_choices(req):
    response = req.zato.client.invoke('zato.http-soap.get-list', {
        'cluster_id': req.zato.cluster_id,
        'connection': 'outgoing',
        'transport': 'plain_http'
    })
    choices = [('', '---')]
    for item in response.data:
        choices.append((item.id, item.name))
    return choices

class CreateForm(forms.Form):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    topic_id = forms.ChoiceField(widget=forms.Select())
    sec_base_id = forms.ChoiceField(widget=forms.Select())
    delivery_type = forms.ChoiceField(
        choices=[
            (PubSub.Delivery_Type.Pull, 'Pull'),
            (PubSub.Delivery_Type.Push, 'Push')
        ],
        initial=PubSub.Delivery_Type.Pull,
        widget=forms.Select()
    )
    rest_push_endpoint_id = forms.ChoiceField(
        required=False,
        widget=forms.Select()
    )

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        if req:
            # Topics will be populated dynamically via AJAX
            self.fields['topic_id'].choices = []
            # Use filtered security definitions for PubSub clients
            logger.info('FORM CreateForm: calling get_pubsub_security_choices with form_type=create, context=subscription')
            security_choices = get_pubsub_security_choices(req, 'create', 'subscription')
            logger.info('FORM CreateForm: get_pubsub_security_choices returned %d choices: %s', len(security_choices), security_choices)
            self.fields['sec_base_id'].choices = security_choices
            # Populate REST endpoints
            self.fields['rest_push_endpoint_id'].choices = get_rest_endpoint_choices(req)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    def __init__(self, prefix=None, post_data=None, req=None):
        super(EditForm, self).__init__(prefix, post_data, req)
        if req:
            # Topics will be populated dynamically via AJAX
            self.fields['topic_id'].choices = []
            # Use filtered security definitions for edit (allows all available ones)
            logger.info('FORM EditForm: calling get_pubsub_security_choices with form_type=edit, context=subscription')
            security_choices = get_pubsub_security_choices(req, 'edit', 'subscription')
            logger.info('FORM EditForm: get_pubsub_security_choices returned %d choices: %s', len(security_choices), security_choices)
            self.fields['sec_base_id'].choices = security_choices
            # REST endpoints will be populated dynamically via AJAX
            self.fields['rest_push_endpoint_id'].choices = []
