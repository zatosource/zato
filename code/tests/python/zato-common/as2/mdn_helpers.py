# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.as2.mdn import MDNRequest, MDNSigningConfig
from zato.common.as2.smime import compute_mic, new_part

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, byteslist
    from .conftest import TestParties
    byteslist = byteslist
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

Message_ID = '<20260709100000.12345@sender.example.com>'

# ################################################################################################################################
# ################################################################################################################################

def make_request(
    requests_signed_mdn:'any_' = False,
    signed_receipt_protocol:'any_' = '',
    mic_algorithms:'any_' = None,
    async_mdn_url:'any_' = '',
    ) -> 'any_':
    """ Returns an MDN request the way the inbound pipeline would have parsed it.
    """
    out = MDNRequest()

    out.message_id = Message_ID
    out.as2_from = 'PartnerCorp'
    out.as2_to = 'ZatoRetail'
    out.requests_mdn = True
    out.requests_signed_mdn = requests_signed_mdn
    out.signed_receipt_protocol = signed_receipt_protocol

    if mic_algorithms:
        out.mic_algorithms = mic_algorithms

    out.async_mdn_url = async_mdn_url

    return out

# ################################################################################################################################

def make_signing_config(parties:'TestParties') -> 'any_':
    """ Returns the signing material the receiving side signs its MDNs with.
    """
    out = MDNSigningConfig()
    out.keystore = parties.receiver

    return out

# ################################################################################################################################

def sample_mic() -> 'any_':
    """ A MIC over a sample payload, the way the inbound pipeline would have computed it.
    """
    part = new_part(b'ISA*00*          *00*          *', 'application/edi-x12', 'binary')

    out = compute_mic(part, is_signed=True, is_encrypted=False)
    return out

# ################################################################################################################################

def crlf_join(lines:'any_') -> 'any_':
    """ Joins wire-format lines with CRLF, the way an AS2 peer would have sent them.
    """
    encoded:'byteslist' = []

    for line in lines:
        encoded_line = line.encode('utf-8')
        encoded.append(encoded_line)

    out = b'\r\n'.join(encoded)
    return out

# ################################################################################################################################
# ################################################################################################################################
