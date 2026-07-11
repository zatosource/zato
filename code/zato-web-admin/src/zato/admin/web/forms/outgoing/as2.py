# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import AS2
from zato.common.as2.common import Default, DigestAlgorithm, EncryptionAlgorithm, MDNMode, TransferMode

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

_sign_algorithm_choices = [
    (DigestAlgorithm.SHA256, 'SHA-256'),
    (DigestAlgorithm.SHA384, 'SHA-384'),
    (DigestAlgorithm.SHA512, 'SHA-512'),
    (DigestAlgorithm.SHA1,   'SHA-1'),
]

_encryption_algorithm_choices = [
    (EncryptionAlgorithm.AES_256_CBC,  'AES-256-CBC'),
    (EncryptionAlgorithm.AES_128_CBC,  'AES-128-CBC'),
    (EncryptionAlgorithm.AES_256_GCM,  'AES-256-GCM'),
    (EncryptionAlgorithm.AES_128_GCM,  'AES-128-GCM'),
    (EncryptionAlgorithm.DES_EDE3_CBC, '3DES-CBC'),
]

_mdn_mode_choices = [
    (MDNMode.Sync,  'Synchronous'),
    (MDNMode.Async, 'Asynchronous'),
    (MDNMode.None_, 'None'),
]

_content_type_choices = [
    ('application/edi-x12',      'X12'),
    ('application/edifact',      'EDIFACT'),
    ('application/xml',          'XML'),
    ('application/octet-stream', 'Binary'),
]

_as2_version_choices = [
    ('1.2', '1.2'),
    ('1.1', '1.1'),
    ('1.3', '1.3'),
]

_content_transfer_encoding_choices = [
    ('binary', 'Binary'),
    ('base64', 'Base64'),
]

_http_transfer_mode_choices = [
    (TransferMode.Content_Length, 'Content-Length'),
    (TransferMode.Chunked,        'Chunked'),
    (TransferMode.Threshold,      'Chunked above threshold'),
]

# The select fields and their choice lists, applied in __init__.
_select_choices = {
    'sign_algorithm':            _sign_algorithm_choices,
    'encryption_algorithm':      _encryption_algorithm_choices,
    'mdn_mode':                  _mdn_mode_choices,
    'content_type':              _content_type_choices,
    'as2_version':               _as2_version_choices,
    'content_transfer_encoding': _content_transfer_encoding_choices,
    'http_transfer_mode':        _http_transfer_mode_choices,
}

_text_attrs = {'style':'width:100%'}
_number_attrs = {'style':'width:20%'}
_pem_attrs = {'style':'width:100%', 'rows':3, 'class':'pem-input'}

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    # Main
    name = forms.CharField(widget=forms.TextInput(attrs=_text_attrs))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    endpoint_url = forms.CharField(initial='https://', widget=forms.TextInput(attrs=_text_attrs))
    as2_from = forms.CharField(widget=forms.TextInput(attrs=_text_attrs))
    as2_to = forms.CharField(widget=forms.TextInput(attrs=_text_attrs))
    subject = forms.CharField(required=False, widget=forms.TextInput(attrs=_text_attrs))

    # EDI
    isa_qualifier = forms.CharField(required=False, widget=forms.TextInput(attrs=_text_attrs))
    isa_id = forms.CharField(required=False, widget=forms.TextInput(attrs=_text_attrs))
    gs_id = forms.CharField(required=False, widget=forms.TextInput(attrs=_text_attrs))
    unb_id = forms.CharField(required=False, widget=forms.TextInput(attrs=_text_attrs))
    content_type = forms.ChoiceField(initial=Default.Content_Type, widget=forms.Select())
    inbound_topic = forms.CharField(required=False, widget=forms.TextInput(attrs=_text_attrs))
    inbound_service = forms.CharField(required=False, widget=forms.TextInput(attrs=_text_attrs))

    # Security
    sign = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    sign_algorithm = forms.ChoiceField(initial=Default.Digest_Algorithm, widget=forms.Select())
    encrypt = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    encryption_algorithm = forms.ChoiceField(initial=Default.Encryption_Algorithm, widget=forms.Select())
    compress = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    compress_before_signing = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    mdn_mode = forms.ChoiceField(initial=MDNMode.Sync, widget=forms.Select())
    mdn_signed = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    async_mdn_url = forms.CharField(required=False, widget=forms.TextInput(attrs=_text_attrs))

    # Certificates - everything is pasted PEM, the private keys are encrypted at rest
    as2_partner_cert = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as2_partner_next_cert = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as2_partner_next_cert_from = forms.CharField(required=False, widget=forms.TextInput(attrs=_number_attrs))
    as2_signing_key = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as2_signing_cert_chain = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as2_decryption_key = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as2_next_decryption_key = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as2_next_decryption_cert = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as2_peer_signing_cert = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as2_peer_encryption_cert = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))
    as2_trust_anchors = forms.CharField(required=False, widget=forms.Textarea(attrs=_pem_attrs))

    # Delivery
    verify_tls = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    username = forms.CharField(required=False, widget=forms.TextInput(attrs=_text_attrs))
    http_timeout_seconds = forms.CharField(required=False, initial=0, widget=forms.TextInput(attrs=_number_attrs))
    http_transfer_mode = forms.ChoiceField(initial=TransferMode.Content_Length, widget=forms.Select())
    chunked_threshold_bytes = forms.CharField(required=False, initial=0, widget=forms.TextInput(attrs=_number_attrs))
    preserve_filename = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    ack_overdue_after = forms.CharField(required=False, initial=0, widget=forms.TextInput(attrs=_number_attrs))
    resend_max_retries = forms.CharField(required=False, initial=0, widget=forms.TextInput(attrs=_number_attrs))
    alerting_opt_out = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    ship_notice_window_hours = forms.CharField(required=False, initial=0, widget=forms.TextInput(attrs=_number_attrs))

    # More
    as2_version = forms.ChoiceField(initial=Default.AS2_Version, widget=forms.Select())
    content_transfer_encoding = forms.ChoiceField(initial='binary', widget=forms.Select())
    force_base64 = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    prevent_canonicalization = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    warn_on_duplicate_filename = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    pool_size = forms.CharField(initial=AS2.Default.Pool_Size, widget=forms.TextInput(attrs=_number_attrs))

    def __init__(self, prefix:'any_'=None, post_data:'any_'=None, req:'any_'=None) -> 'None':
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        for name, choices in _select_choices.items():
            self.fields[name].choices = []
            for value, label in choices:
                self.fields[name].choices.append([value, label])

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
