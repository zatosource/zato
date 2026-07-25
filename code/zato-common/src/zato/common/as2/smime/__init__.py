# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The S/MIME primitives of RFC 8551 and the CMS structures of RFC 5652 that AS2 messages are built
out of, spread over one module per concern and gathered back here.

- der - DER tags, lengths and the BER re-encoding every structure is read through
- algorithms - the object identifiers, names and sizes of the algorithms this package speaks
- part - the MIME entity all of the below operate on, and its canonicalization
- mic - the message integrity check a receipt carries back
- signing, verification - the detached multipart/signed structure and the SignedData in it
- encryption, decryption - EnvelopedData and AuthEnvelopedData
- compression - CompressedData
"""

# Zato
from zato.common.as2.smime.compression import compress, decompress
from zato.common.as2.smime.decryption import decrypt
from zato.common.as2.smime.encryption import encrypt
from zato.common.as2.smime.mic import compute_mic, compute_mic_over, normalize_micalg, select_mic_algorithm
from zato.common.as2.smime.part import encode_base64_lines, new_part, parse_part, serialize_part, SMIMEPart
from zato.common.as2.smime.signing import sign
from zato.common.as2.smime.verification import verify, VerifyResult

# ################################################################################################################################
# ################################################################################################################################

__all__ = (
    'compress',
    'compute_mic',
    'compute_mic_over',
    'decompress',
    'decrypt',
    'encode_base64_lines',
    'encrypt',
    'new_part',
    'normalize_micalg',
    'parse_part',
    'select_mic_algorithm',
    'serialize_part',
    'sign',
    'verify',
    'SMIMEPart',
    'VerifyResult',
)

# ################################################################################################################################
# ################################################################################################################################
