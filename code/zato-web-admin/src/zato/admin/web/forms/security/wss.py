# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# ################################################################################################################################
# ################################################################################################################################

# The modes a definition can be in, in the order the mode selector shows them.
_mode_choices = [
    ('username_token', 'Username token'),
    ('x509', 'X.509'),
    ('saml', 'SAML'),
]

# The PEM fields share one widget shape - a small monospace textarea.
_pem_widget = forms.Textarea(attrs={'style':'width:100%; font-family:monospace; font-size:11px', 'rows':4})

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    # Main
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    mode = forms.ChoiceField(widget=forms.Select(), choices=_mode_choices)
    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    # Username token
    use_digest = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    # SAML
    issuer = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    subject = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    audience = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    # Crypto material
    sign = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    encrypt = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    signing_key = forms.CharField(required=False, widget=_pem_widget)
    signing_certificate_chain = forms.CharField(required=False, widget=_pem_widget)
    decryption_key = forms.CharField(required=False, widget=_pem_widget)
    peer_certificate = forms.CharField(required=False, widget=_pem_widget)
    trust_anchors = forms.CharField(required=False, widget=_pem_widget)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
