# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The message integrity check a receipt carries back to the sender - which digest algorithm a
partner asked for, and which bytes the digest covers for each combination of security layers.
"""

# stdlib
from base64 import b64encode

# cryptography
from cryptography.hazmat.primitives.hashes import Hash

# Zato
from zato.common.as2.common import AS2ProtocolException, Default, Failure
from zato.common.as2.smime.algorithms import Digest_By_Name, Micalg_Spelling
from zato.common.as2.smime.part import canonicalize_content, serialize_part

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.smime.part import SMIMEPart
    from zato.common.typing_ import strlist
    strlist = strlist
    SMIMEPart = SMIMEPart

# ################################################################################################################################
# ################################################################################################################################

def normalize_micalg(value:'str') -> 'str':
    """ Accepts any known spelling of a MIC algorithm name, case-insensitively,
    and returns the RFC 5751 spelling always used on output.
    """
    stripped = value.strip()
    lowered = stripped.lower()

    if spelling := Micalg_Spelling.get(lowered):
        out = spelling
        return out

    # .. anything else is an algorithm this implementation does not support.
    else:
        raise AS2ProtocolException(Failure.Unsupported_MIC_Algorithms, f'Unsupported MIC algorithm `{value}`')

# ################################################################################################################################

def select_mic_algorithm(requested:'strlist') -> 'str':
    """ Picks the first supported algorithm from a signed-receipt-micalg list,
    honoring the sender's order of preference left to right.
    """
    for value in requested:
        stripped = value.strip()
        lowered = stripped.lower()
        if spelling := Micalg_Spelling.get(lowered):
            out = spelling
            break
    else:
        joined = ', '.join(requested)
        raise AS2ProtocolException(Failure.Unsupported_MIC_Algorithms, f'No supported MIC algorithm among `{joined}`')

    return out

# ################################################################################################################################

def compute_mic_over(covered:'bytes', algorithm:'str' = Default.Digest_Algorithm) -> 'str':
    """ Digests the exact bytes given and returns the MIC in its wire form -
    the base64 digest with the RFC 5751 algorithm name appended after a comma.
    """
    normalized = normalize_micalg(algorithm)
    hash_class = Digest_By_Name[normalized]
    hash_algorithm = hash_class()

    digest = Hash(hash_algorithm)
    digest.update(covered)
    digest_bytes = digest.finalize()

    encoded_bytes = b64encode(digest_bytes)
    encoded = encoded_bytes.decode('ascii')

    out = f'{encoded}, {normalized}'
    return out

# ################################################################################################################################

def compute_mic(
    part:'SMIMEPart',
    algorithm:'str' = Default.Digest_Algorithm,
    *,
    is_signed:'bool',
    is_encrypted:'bool',
    prevent_canonicalization:'bool' = False,
    ) -> 'str':
    """ Computes the Received-Content-MIC per RFC 4130 section 7.3.1. For signed messages the digest
    covers the canonicalized MIME headers plus content of the signed part, for encrypted unsigned
    messages the decrypted canonicalized MIME headers plus content, and for unsigned unencrypted
    messages the content alone, without any headers.
    """
    # Signed and encrypted messages digest the complete MIME entity ..
    include_headers = is_signed
    if is_encrypted:
        include_headers = True

    if include_headers:
        covered = serialize_part(part, prevent_canonicalization)

    # .. plain content travels bare and is digested alone.
    else:
        covered = canonicalize_content(part, prevent_canonicalization)

    out = compute_mic_over(covered, algorithm)
    return out

# ################################################################################################################################
# ################################################################################################################################
