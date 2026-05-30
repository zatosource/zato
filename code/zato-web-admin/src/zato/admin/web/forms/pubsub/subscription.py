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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    from zato.common.typing_ import any_, strnone

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def get_rest_endpoint_choices(request:'HttpRequest') -> 'list':
    """ Returns a list of REST outgoing connections as form choices.
    """
    # Invoke the service ..
    response = request.zato.client.invoke('zato.http-soap.get-list', {
        'cluster_id': request.zato.cluster_id,
        'connection': 'outgoing',
        'transport': 'plain_http'
    })

    # .. build the choices list ..
    out = [('', '---')]

    for item in response.data:
        out.append((item.id, item.name))

    # .. and return the result.
    return out

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    """ Form for creating a pub/sub subscription.
    """
    is_delivery_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    is_pub_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    topic_id = forms.MultipleChoiceField(widget=forms.SelectMultiple())
    sec_base_id = forms.ChoiceField(widget=forms.Select())
    delivery_type = forms.ChoiceField(
        choices=[
            (PubSub.Delivery_Type.Pull, 'Pull'),
            (PubSub.Delivery_Type.Push, 'Push')
        ],
        initial=PubSub.Delivery_Type.Pull,
        widget=forms.Select()
    )
    push_type = forms.ChoiceField(
        choices=[
            (PubSub.Push_Type.REST, 'REST'),
            (PubSub.Push_Type.Service, 'Service')
        ],
        initial=PubSub.Push_Type.REST,
        widget=forms.Select()
    )
    rest_push_endpoint_id = forms.ChoiceField(
        required=False,
        widget=forms.Select()
    )
    push_service_name = forms.ChoiceField(
        required=False,
        widget=forms.Select()
    )

    def __init__(self, prefix:'strnone'=None, post_data:'any_'=None, req:'any_'=None) -> 'None':
        super().__init__(post_data, prefix=prefix)
        if req:

            # Topics will be populated dynamically via AJAX
            self.fields['topic_id'].choices = []

            # Use filtered security definitions for PubSub clients with empty first option
            choices = [('', 'Select a security definition')] + get_pubsub_security_choices(req, 'create', 'subscription')
            self.fields['sec_base_id'].choices = choices

            # Set default option for REST endpoints
            self.fields['rest_push_endpoint_id'].choices = [('', 'Select a REST endpoint')]

            # Set default option for service select
            self.fields['push_service_name'].choices = [('', 'Select a service')]

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    """ Form for editing a pub/sub subscription.
    """
    is_delivery_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_pub_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    def __init__(self, prefix:'strnone'=None, post_data:'any_'=None, req:'any_'=None) -> 'None':
        super().__init__(prefix, post_data, req)

        if req:
            # Topics will be populated dynamically via AJAX
            self.fields['topic_id'].choices = []

            # Use filtered security definitions for edit (allows all available ones) with empty first option
            choices = [('', 'Select a security definition')] + get_pubsub_security_choices(req, 'edit', 'subscription')

            self.fields['sec_base_id'].choices = choices

            # Set default option for REST endpoints (will be populated via AJAX)
            self.fields['rest_push_endpoint_id'].choices = [('', 'Select a REST endpoint')]

# ################################################################################################################################
# ################################################################################################################################
