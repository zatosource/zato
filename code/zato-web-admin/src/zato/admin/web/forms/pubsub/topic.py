# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import PubSub

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.http import HttpRequest
    from zato.common.typing_ import any_, anylist, strnone
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# This value marks the select option that takes the user to a page where the missing definition can be created.
Create_New_Value = 'zato-create-new'

# ################################################################################################################################
# ################################################################################################################################

def get_outconn_amqp_choices(req:'HttpRequest') -> 'anylist':
    """ Returns a list of outgoing AMQP connections as form choices.
    """
    # Invoke the service ..
    response = req.zato.client.invoke('zato.outgoing.amqp.get-list', {
        'cluster_id': req.zato.cluster_id,
    })

    # .. build the choices list ..
    out = [('', 'Select a connection')]

    for item in response.data:
        out.append((item.name, item.name))

    # .. with nothing to select, offer to create a connection ..
    has_items = len(out) > 1

    if not has_items:
        out.append((Create_New_Value, 'Create a new connection'))

    # .. and return the result.
    return out

# ################################################################################################################################
# ################################################################################################################################

def get_channel_amqp_choices(req:'HttpRequest') -> 'anylist':
    """ Returns a list of AMQP channels as form choices.
    """
    # Invoke the service ..
    response = req.zato.client.invoke('zato.channel.amqp.get-list', {
        'cluster_id': req.zato.cluster_id,
    })

    # .. build the choices list ..
    out = [('', 'Select a channel')]

    for item in response.data:
        out.append((item.name, item.name))

    # .. with nothing to select, offer to create a channel ..
    has_items = len(out) > 1

    if not has_items:
        out.append((Create_New_Value, 'Create a new channel'))

    # .. and return the result.
    return out

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    """ Form for creating a pub/sub topic.
    """
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:90%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    is_audit_log_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'style':'width:90%; height:80px'}), required=False)

    backend_type = forms.ChoiceField(
        choices=[
            (PubSub.Backend_Type.Builtin, 'Built-in'),
            (PubSub.Backend_Type.AMQP, 'AMQP'),
        ],
        initial=PubSub.Backend_Type.Builtin,
        widget=forms.Select()
    )
    amqp_outconn_name = forms.ChoiceField(required=False, widget=forms.Select())
    amqp_exchange = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:90%'}))
    amqp_routing_key = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:90%'}))
    amqp_channel_name = forms.ChoiceField(required=False, widget=forms.Select())

    def __init__(self, prefix:'strnone'=None, post_data:'any_'=None, req:'any_'=None) -> 'None':
        super().__init__(post_data, prefix=prefix)

        # Default choices when there is no request to invoke services with ..
        self.fields['amqp_outconn_name'].choices = [('', 'Select a connection')]
        self.fields['amqp_channel_name'].choices = [('', 'Select a channel')]

        # .. otherwise, populate the AMQP selects from what the cluster has.
        if req:
            self.fields['amqp_outconn_name'].choices = get_outconn_amqp_choices(req)
            self.fields['amqp_channel_name'].choices = get_channel_amqp_choices(req)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    """ Form for editing a pub/sub topic.
    """
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_audit_log_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
