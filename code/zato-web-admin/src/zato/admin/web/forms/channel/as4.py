# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select
from zato.admin.web.forms.outgoing.as4 import profile_choices

# ################################################################################################################################
# ################################################################################################################################

_pem_attrs = {'style':'width:100%', 'rows':4, 'class':'pem-input'}

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    # Main
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    url_path = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    security_id = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    as4_profile = forms.ChoiceField(widget=forms.Select())
    as4_from_party = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_to_party = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_service = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_action = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_agreement = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_mpc = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_extra_pmodes = forms.CharField(required=False, widget=forms.Textarea(attrs={'style':'width:100%', 'rows':4}))

    # Security - everything is pasted PEM, the private keys are encrypted at rest
    as4_signing_key = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as4_signing_cert_chain = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as4_decryption_key = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as4_peer_signing_cert = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as4_peer_encryption_cert = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as4_trust_anchors = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))

    # Participants
    as4_serviced_participants = forms.CharField(required=False, widget=forms.Textarea(attrs={'style':'width:100%', 'rows':6}))

    # Routing
    service = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_inbound_topic = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    # More
    as4_original_sender = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_final_recipient = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    def __init__(self, security_list=None, prefix=None, post_data=None, req=None):
        if security_list is None:
            security_list = []
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['as4_profile'].choices = []
        for value, label in profile_choices:
            self.fields['as4_profile'].choices.append([value, label])

        add_security_select(self, security_list, field_name='security_id')

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
