# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import AS4, MISC

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_validate_tls_choices = [
    (True, 'Yes'),
    (False, 'No'),
]

profile_choices = [
    (AS4.Profile.EDelivery1, 'eDelivery AS4 1.x'),
    (AS4.Profile.EDelivery2, 'eDelivery AS4 2.0'),
    (AS4.Profile.Peppol,     'Peppol'),
    (AS4.Profile.ICS2,       'ICS2'),
]

token_type_choices = [
    ('',                    'Profile default'),
    (AS4.TokenType.X509v3,  'X.509 certificate'),
    (AS4.TokenType.PKIPath, 'X.509 certificate chain'),
    (AS4.TokenType.SAML20,  'SAML 2.0 assertion'),
]

_pem_attrs = {'style':'width:100%', 'rows':4, 'class':'pem-input'}

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    # Main
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    is_audit_log_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    as4_profile = forms.ChoiceField(widget=forms.Select())
    as4_from_party = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_to_party = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_service = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_action = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_agreement = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    # Delivery
    host = forms.CharField(initial='https://', widget=forms.TextInput(attrs={'style':'width:100%'}))
    url_path = forms.CharField(required=False, initial='/', widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_use_discovery = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    as4_sml_domain = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_mpc = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    timeout = forms.CharField(initial=MISC.DEFAULT_HTTP_TIMEOUT, widget=forms.TextInput(attrs={'style':'width:10%'}))
    validate_tls = forms.ChoiceField(widget=forms.Select())

    # Security - the certificates and keys are pasted PEM, the private keys and the password
    # are encrypted at rest
    as4_token_type = forms.ChoiceField(required=False, widget=forms.Select())
    as4_username = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'style':'width:100%'},
        render_value=True))
    as4_signing_key = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as4_signing_cert_chain = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as4_decryption_key = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as4_saml_assertion = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as4_peer_signing_cert = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as4_peer_encryption_cert = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as4_trust_anchors = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))

    # Reliability - the reception awareness parameters, each empty unless the profile's own
    # value is to be overridden
    as4_retry_max_attempts = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:10%'}))
    as4_retry_interval = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:10%'}))
    as4_missing_receipt_after = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:10%'}))

    # More
    as4_original_sender = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_final_recipient = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    as4_extra_pmodes = forms.CharField(required=False, widget=forms.Textarea(attrs={'style':'width:100%', 'rows':4}))

    def __init__(self, prefix:'any_'=None, post_data:'any_'=None, req:'any_'=None) -> 'None':
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['as4_profile'].choices = []
        for value, label in profile_choices:
            self.fields['as4_profile'].choices.append([value, label])

        self.fields['validate_tls'].choices = []
        for value, label in _validate_tls_choices:
            self.fields['validate_tls'].choices.append([value, label])

        self.fields['as4_token_type'].choices = []
        for value, label in token_type_choices:
            self.fields['as4_token_type'].choices.append([value, label])

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_audit_log_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
