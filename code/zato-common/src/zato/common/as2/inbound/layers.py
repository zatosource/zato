# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Reversing the security layers an incoming message arrived wrapped in, in whichever order they were
applied, and holding the peer to the layers the partnership requires rather than to the ones that
happened to arrive.
"""

# Zato
from zato.common.as2.common import AS2Error, AS2ProtocolException, Default
from zato.common.as2.inbound.common import Max_Layer_Depth
from zato.common.as2.partnership import active_verification_certificates
from zato.common.as2.smime import compute_mic, compute_mic_over, decompress, decrypt, select_mic_algorithm, \
    serialize_part, verify
from zato.common.util.xml_.mime_ import parse_header_parameters

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.inbound.common import InboundResult
    from zato.common.as2.partnership import Partnership
    from zato.common.as2.smime import SMIMEPart
    from zato.common.typing_ import strlist
    from zato.common.util.xml_.keystore import Keystore
    strlist = strlist
    InboundResult = InboundResult
    Keystore = Keystore
    Partnership = Partnership
    SMIMEPart = SMIMEPart

# ################################################################################################################################
# ################################################################################################################################

# The smime-type parameter values that mean an application/pkcs7-mime entity is encrypted.
_enveloped_smime_types = ('enveloped-data', 'authenveloped-data')

# The smime-type parameter value of a compressed entity.
_compressed_smime_type = 'compressed-data'

# ################################################################################################################################
# ################################################################################################################################

def _enforce_security_policy(partnership:'Partnership', is_signed:'bool', is_encrypted:'bool') -> 'None':
    """ Rejects a message that arrived with fewer security layers than the partnership requires.
    Without this check the layers that happened to arrive would be the only ones enforced, so a
    partnership configured for signing and encryption would accept an unsigned plaintext POST from
    anyone able to reach the channel URL and guess the AS2-From/AS2-To pair - and that pair is in
    every message the partner sends, so it is not a secret.
    """
    # The partnership's own signing and encryption settings describe the relationship,
    # not just what we send, so inbound holds the peer to the same terms.
    if partnership.sign:
        if not is_signed:
            raise AS2ProtocolException(
                AS2Error.Insufficient_Message_Security, 'The partnership requires a signed message')

    if partnership.encrypt:
        if not is_encrypted:
            raise AS2ProtocolException(
                AS2Error.Insufficient_Message_Security, 'The partnership requires an encrypted message')

# ################################################################################################################################

def process_layers(
    result:'InboundResult',
    part:'SMIMEPart',
    partnership:'Partnership',
    keystore:'Keystore',
    mic_request_algorithms:'strlist',
    ) -> 'SMIMEPart':
    """ Reverses the security layers in whichever order they actually arrived, detected from
    the content types, and captures what the MIC is to cover per RFC 4130 section 7.3.1 -
    the signed entity for signed messages, the decrypted entity for encrypted unsigned ones,
    the content alone for everything else.
    """
    signed_content = b''
    decrypted_content = b''
    compressed_content = b''

    # Which layers actually arrived, tracked apart from the captured bytes above because
    # a layer wrapping empty content is still a layer that arrived.
    is_signed = False
    is_encrypted = False

    # How many layers have been unwrapped so far - each iteration below removes one layer
    # and may reveal another, so without a ceiling a peer could stack them without limit
    # and multiply the work of every unwrapping step, all before any trust decision is made.
    depth = 0

    # The partner's rotation list - during an overlap window it holds more than one
    # certificate and a signature from any of them is accepted.
    accepted_certificates = active_verification_certificates(partnership)

    while True:

        # A well-formed message has at most a handful of layers, so crossing the ceiling
        # means the structure is hostile rather than merely unusual.
        if depth >= Max_Layer_Depth:
            raise AS2ProtocolException(
                AS2Error.Unexpected_Processing_Error, f'Too many security layers, the maximum is {Max_Layer_Depth}')

        parameters = parse_header_parameters(part.content_type)
        media_type = parameters['']

        # An encrypted or compressed entity - both ride in application/pkcs7-mime ..
        if media_type == 'application/pkcs7-mime':

            smime_type = parameters.get('smime-type')

            if smime_type is None:
                smime_type = ''

            # An absent smime-type parameter means an encrypted entity,
            # the one shape peers ship without the parameter.
            is_enveloped = smime_type in _enveloped_smime_types
            if not smime_type:
                is_enveloped = True

            if smime_type == _compressed_smime_type:
                if not compressed_content:
                    compressed_content = part.data
                part = decompress(part)

            # .. the encrypted entity is decrypted with our own key ..
            elif is_enveloped:
                part = decrypt(part, keystore)
                is_encrypted = True
                if not decrypted_content:
                    decrypted_content = serialize_part(part, partnership.prevent_canonicalization)

            # .. any other smime-type is not something this pipeline handles.
            else:
                raise AS2ProtocolException(
                    AS2Error.Unexpected_Processing_Error, f'Unsupported smime-type `{smime_type}`')

        # .. a signed entity is verified and unwrapped ..
        elif media_type == 'multipart/signed':
            verify_result = verify(part, keystore, accepted_certificates)
            is_signed = True

            if not signed_content:
                signed_content = verify_result.content

            result.signer_certificate = verify_result.signer_certificate
            part = verify_result.part

        # .. anything else is the payload itself.
        else:
            break

        depth += 1

    # The MIC algorithm honors the request's preference list when there is one.
    if mic_request_algorithms:
        algorithm = select_mic_algorithm(mic_request_algorithms)
    else:
        algorithm = Default.Digest_Algorithm

    # The 7.3.1 selection - signed wins over encrypted, encrypted over compressed,
    # and a bare payload digests its content alone, without any headers.
    if signed_content:
        result.mic = compute_mic_over(signed_content, algorithm)
    elif decrypted_content:
        result.mic = compute_mic_over(decrypted_content, algorithm)
    elif compressed_content:
        result.mic = compute_mic_over(compressed_content, algorithm)
    else:
        options = {
            'is_signed': False,
            'is_encrypted': False,
            'prevent_canonicalization': partnership.prevent_canonicalization,
        }
        result.mic = compute_mic(part, algorithm, **options)

    # The MIC is computed before the policy check so that a rejected message still reports
    # what arrived - the partner needs that value to tell which message we turned down.
    _enforce_security_policy(partnership, is_signed, is_encrypted)

    return part

# ################################################################################################################################
# ################################################################################################################################
