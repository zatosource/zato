# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The shared ground of the formal-document conformance suite. Every expected value in the
# suite is typed out literally from the governing documents - the AS2 header grammar and
# disposition strings of RFC 4130 sections 6 and 7, the disposition report layout of RFC 8098,
# the micalg names of RFC 5751 and the CMS object identifiers of RFC 5652 - never imported
# from the code under test. Every cryptographic value is recomputed independently: the MIC
# with hashlib over a literally typed entity, SignedData after an independent DER parse,
# EnvelopedData with cryptography primitives only, and the openssl CLI stands in as the
# third-party oracle in both directions.

# stdlib
from base64 import b64encode
from hashlib import sha256

# Zato
from zato.common.as2.partnership import new_partnership
from zato.common.as2.smime import new_part
from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

Sender_Identifier   = 'ZatoRetail'
Receiver_Identifier = 'PartnerCorp'

# The endpoint the sending side delivers to.
Endpoint_URL = 'https://partnercorp.example.com/as2'

# A small X12 purchase order interchange used as the payload throughout.
EDI_Payload = b'ISA*00*          *00*          *ZZ*SENDERID       *ZZ*RECEIVERID     ' + \
    b'*260709*1200*U*00401*000000001*0*P*>~GS*PO*SENDERID*RECEIVERID*20260709*1200*1*X*004010~' + \
    b'ST*850*0001~BEG*00*SA*PO-2026-001**20260709~SE*3*0001~GE*1*1~IEA*1*000000001~'

EDI_Content_Type = 'application/edi-x12'

# The complete MIME entity around the payload, typed out byte by byte - what a signed
# or encrypted message covers per RFC 4130 section 7.3.1.
EDI_Entity = b'Content-Type: application/edi-x12\r\nContent-Transfer-Encoding: binary\r\n\r\n' + EDI_Payload

# ################################################################################################################################
# ################################################################################################################################

def edi_part() -> 'any_':
    """ The payload wrapped in the MIME part the S/MIME layer operates on.
    """
    out = new_part(EDI_Payload, EDI_Content_Type)
    return out

# ################################################################################################################################

def make_sender_partnership() -> 'any_':
    """ The relationship as our own, sending side sees it.
    """
    out = new_partnership()

    out.as2_from = Sender_Identifier
    out.as2_to = Receiver_Identifier
    out.endpoint_url = Endpoint_URL

    return out

# ################################################################################################################################

def make_receiver_partnership() -> 'any_':
    """ The same relationship as the partner's, receiving side sees it - the identities swap places.
    """
    out = new_partnership()

    out.as2_from = Receiver_Identifier
    out.as2_to = Sender_Identifier

    return out

# ################################################################################################################################

def boundary_of(content_type:'str') -> 'bytes':
    """ Reads the boundary parameter out of a multipart content type with plain string
    operations - independent of any MIME parser in the code under test.
    """
    _, _, after = content_type.partition('boundary="')
    boundary, _, _ = after.partition('"')

    out = boundary.encode('ascii')
    return out

# ################################################################################################################################

def split_multipart(data:'bytes', boundary:'bytes') -> 'anylist':
    """ Splits a multipart body into its parts with plain byte operations - each part
    is everything between the CRLF after one boundary delimiter and the CRLF
    before the next one, exactly as RFC 2046 frames it.
    """

    # Our response to produce
    out:'anylist' = []

    delimiter = b'--' + boundary
    sections = data.split(delimiter)

    # The first section is the preamble and the last one is the closing '--',
    # everything in between is one part framed by CRLF on both sides.
    for section in sections[1:-1]:
        part = section.removeprefix(b'\r\n')
        part = part.removesuffix(b'\r\n')
        out.append(part)

    return out

# ################################################################################################################################

def mic_over(covered:'bytes') -> 'str':
    """ Recomputes an SHA-256 MIC with hashlib alone, in the base64-comma-algorithm
    form of RFC 4130 section 7.4.3.
    """
    digest = sha256(covered).digest()
    encoded_bytes = b64encode(digest)
    encoded = encoded_bytes.decode('ascii')

    out = f'{encoded}, sha-256'
    return out

# ################################################################################################################################
# ################################################################################################################################
