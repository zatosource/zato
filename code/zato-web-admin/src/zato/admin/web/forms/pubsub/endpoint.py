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

    def __init__(self, req, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)

# ################################################################################################################################

class EditForm(CreateForm):
    is_internal = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
