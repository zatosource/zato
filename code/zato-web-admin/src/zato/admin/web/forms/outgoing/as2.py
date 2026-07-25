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
    any_ = any_

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
    (MDNMode.Not_Requested, 'None'),
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
_checked_attrs = {'checked':'checked'}

# ################################################################################################################################
# ################################################################################################################################

def _new_text_field(required:'bool' = True, initial:'any_' = None) -> 'any_':
    """ Returns a full-width single-line text field.
    """
    attrs = dict(_text_attrs)
    widget = forms.TextInput(attrs=attrs)

    out = forms.CharField(required=required, initial=initial, widget=widget)
    return out

# ################################################################################################################################

def _new_number_field(required:'bool' = False, initial:'any_' = 0) -> 'any_':
    """ Returns a narrow text field for a numeric value - the Dashboard sends numbers as text
    and the service layer is what turns them into numbers.
    """
    attrs = dict(_number_attrs)
    widget = forms.TextInput(attrs=attrs)

    out = forms.CharField(required=required, initial=initial, widget=widget)
    return out

# ################################################################################################################################

def _new_pem_field() -> 'any_':
    """ Returns a text area for pasted PEM material.
    """
    attrs = dict(_pem_attrs)
    widget = forms.Textarea(attrs=attrs)

    out = forms.CharField(required=False, widget=widget)
    return out

# ################################################################################################################################

def _new_checkbox_field(is_checked:'bool' = False) -> 'any_':
    """ Returns a checkbox, ticked by default or not.
    """
    if is_checked:
        attrs = dict(_checked_attrs)
    else:
        attrs = {}

    widget = forms.CheckboxInput(attrs=attrs)

    out = forms.BooleanField(required=False, widget=widget)
    return out

# ################################################################################################################################

def _new_choice_field(initial:'any_') -> 'any_':
    """ Returns a select field - its choices are filled in by the form's own __init__.
    """
    widget = forms.Select()

    out = forms.ChoiceField(initial=initial, widget=widget)
    return out


# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    # Main
    name = _new_text_field()
    is_active = _new_checkbox_field(is_checked=True)
    is_audit_log_active = _new_checkbox_field(is_checked=True)
    endpoint_url = _new_text_field(initial='https://')
    as2_from = _new_text_field()
    as2_to = _new_text_field()
    subject = _new_text_field(required=False)

    # EDI
    isa_qualifier = _new_text_field(required=False)
    isa_id = _new_text_field(required=False)
    gs_id = _new_text_field(required=False)
    unb_id = _new_text_field(required=False)
    content_type = _new_choice_field(Default.Content_Type)
    inbound_topic = _new_text_field(required=False)
    inbound_service = _new_text_field(required=False)

    # Security
    sign = _new_checkbox_field(is_checked=True)
    sign_algorithm = _new_choice_field(Default.Digest_Algorithm)
    encrypt = _new_checkbox_field(is_checked=True)
    encryption_algorithm = _new_choice_field(Default.Encryption_Algorithm)
    compress = _new_checkbox_field()
    compress_before_signing = _new_checkbox_field(is_checked=True)
    mdn_mode = _new_choice_field(MDNMode.Sync)
    mdn_signed = _new_checkbox_field(is_checked=True)
    async_mdn_url = _new_text_field(required=False)

    # Certificates - everything is pasted PEM, the private keys are encrypted at rest
    as2_partner_cert = _new_pem_field()
    as2_partner_next_cert = _new_pem_field()
    as2_partner_next_cert_from = _new_number_field(initial=None)
    as2_signing_key = _new_pem_field()
    as2_signing_cert_chain = _new_pem_field()
    as2_decryption_key = _new_pem_field()
    as2_next_decryption_key = _new_pem_field()
    as2_next_decryption_cert = _new_pem_field()
    as2_peer_signing_cert = _new_pem_field()
    as2_peer_encryption_cert = _new_pem_field()
    as2_trust_anchors = _new_pem_field()

    # Delivery
    verify_tls = _new_checkbox_field(is_checked=True)
    username = _new_text_field(required=False)
    http_timeout_seconds = _new_number_field()
    http_transfer_mode = _new_choice_field(TransferMode.Content_Length)
    chunked_threshold_bytes = _new_number_field()
    preserve_filename = _new_checkbox_field()
    ack_overdue_after = _new_number_field()
    resend_max_retries = _new_number_field()
    alerting_opt_out = _new_checkbox_field()
    ship_notice_window_hours = _new_number_field()

    # More
    as2_version = _new_choice_field(Default.AS2_Version)
    content_transfer_encoding = _new_choice_field('binary')
    force_base64 = _new_checkbox_field()
    prevent_canonicalization = _new_checkbox_field()
    warn_on_duplicate_filename = _new_checkbox_field()
    pool_size = _new_number_field(required=True, initial=AS2.Default.Pool_Size)

    def __init__(self, prefix:'any_' = None, post_data:'any_' = None, req:'any_' = None) -> 'None':
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        for name, choices in _select_choices.items():
            field = self.fields[name]
            field.choices = []

            for value, label in choices:
                field.choices.append([value, label])

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = _new_checkbox_field()
    is_audit_log_active = _new_checkbox_field()

# ################################################################################################################################
# ################################################################################################################################
