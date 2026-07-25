# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

One complete AS2 message in the making - compress, sign and encrypt in the order the partnership
configures, then the AS2 headers around the result.
"""

# Zato
from zato.common.as2.common import AS2Exception, Default, MDNMode
from zato.common.as2.mdn import new_message_id
from zato.common.as2.outbound.payload import build_payload_part
from zato.common.as2.partnership import quote_as2_identifier, select_encryption_certificate
from zato.common.as2.smime import compress, compute_mic, encrypt, select_mic_algorithm, sign

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from zato.common.as2.outbound.common import send_payload
    from zato.common.as2.partnership import Partnership
    from zato.common.as2.smime import SMIMEPart
    from zato.common.typing_ import anytuple, strnone, strstrdict
    from zato.common.util.xml_.keystore import Keystore
    anytuple = anytuple
    send_payload = send_payload
    strnone = strnone
    strstrdict = strstrdict
    Certificate = Certificate
    Keystore = Keystore
    Partnership = Partnership
    SMIMEPart = SMIMEPart

# ################################################################################################################################
# ################################################################################################################################

def _get_encryption_certificate(partnership:'Partnership', keystore:'Keystore') -> 'Certificate':
    """ Returns what an outgoing message is encrypted to. The partner's rotation list decides -
    during a migration window the most recently activated certificate wins - while a partnership
    without one uses the certificate pinned in the keystore.
    """
    out = select_encryption_certificate(partnership)

    if not out:
        out = keystore.peer_encryption_certificate

    if not out:
        raise AS2Exception(f'No encryption certificate for partner `{partnership.as2_to}`')

    return out

# ################################################################################################################################

def _build_secured_part(partnership:'Partnership', keystore:'Keystore', payload:'send_payload', filename:'strnone') \
    -> 'anytuple':
    """ Applies compression, signing and encryption to the payload entity in the configured order.
    Returns the outermost entity and the MIC computed at send time, which is what a returned
    MDN reconciles against.
    """
    prevent_canonicalization = partnership.prevent_canonicalization
    current = build_payload_part(partnership, payload, filename)

    # Compression before signing makes the signature cover the compressed bytes ..
    if partnership.compress:
        if partnership.compress_before_signing:
            current = compress(current, prevent_canonicalization)

    # .. the MIC of a signed message covers exactly what gets signed,
    # while an unsigned one is digested only once all its wrapping is done ..
    if partnership.sign:
        options = {
            'is_signed': True,
            'is_encrypted': partnership.encrypt,
            'prevent_canonicalization': prevent_canonicalization,
        }
        mic = compute_mic(current, partnership.sign_algorithm, **options)
        current = sign(current, keystore, partnership.sign_algorithm, prevent_canonicalization)
    else:
        mic = ''

    # .. compression after signing wraps the signed structure whole ..
    if partnership.compress:
        if not partnership.compress_before_signing:
            current = compress(current, prevent_canonicalization)

    # .. an unsigned message digests whatever is about to hit the wire or get encrypted,
    # with the MIC algorithm taken from the partnership's own preference list.
    if not mic:
        mic_algorithm = select_mic_algorithm(partnership.mdn_mic_algorithms)
        options = {
            'is_signed': False,
            'is_encrypted': partnership.encrypt,
            'prevent_canonicalization': prevent_canonicalization,
        }
        mic = compute_mic(current, mic_algorithm, **options)

    # .. and encryption comes last, so that only ciphertext travels over the wire.
    if partnership.encrypt:
        encryption_certificate = _get_encryption_certificate(partnership, keystore)

        current = encrypt(
            current,
            encryption_certificate,
            partnership.encryption_algorithm,
            partnership.force_base64,
            prevent_canonicalization,
        )

    out = (current, mic)
    return out

# ################################################################################################################################

def _build_headers(partnership:'Partnership', part:'SMIMEPart', message_id:'str') -> 'strstrdict':
    """ Builds the HTTP headers one message travels under - the outermost entity's MIME headers,
    the AS2 identities and the MDN request, when one is asked for.
    """

    # Our response to produce
    out:'strstrdict' = {}

    out['Content-Type'] = part.content_type
    out['Content-Transfer-Encoding'] = part.content_transfer_encoding

    if part.content_disposition:
        out['Content-Disposition'] = part.content_disposition

    out['MIME-Version'] = '1.0'
    out['Message-ID'] = message_id
    out['Subject'] = partnership.subject
    out['AS2-Version'] = partnership.as2_version
    out['AS2-From'] = quote_as2_identifier(partnership.as2_from)
    out['AS2-To'] = quote_as2_identifier(partnership.as2_to)
    out['EDIINT-Features'] = Default.EDIINT_Features

    # The MDN request headers - the notification address is informational
    # and never used for routing, so our own identifier serves as one.
    if partnership.mdn_mode != MDNMode.Not_Requested:

        out['Disposition-Notification-To'] = partnership.as2_from

        if partnership.mdn_signed:
            algorithms = ', '.join(partnership.mdn_mic_algorithms)
            out['Disposition-Notification-Options'] = \
                f'signed-receipt-protocol=required, pkcs7-signature; signed-receipt-micalg=required, {algorithms}'

        if partnership.mdn_mode == MDNMode.Async:
            out['Receipt-Delivery-Option'] = partnership.async_mdn_url

    return out

# ################################################################################################################################

def build_message(
    partnership:'Partnership',
    keystore:'Keystore',
    payload:'send_payload',
    filename:'strnone' = None,
    message_id:'strnone' = None,
    ) -> 'anytuple':
    """ Builds one complete AS2 message - compress, sign and encrypt in the configured order,
    then the AS2 headers around the result. Returns the body bytes, the HTTP headers,
    the Message-ID and the MIC computed at send time.
    """
    # A fresh Message-ID unless the caller resends earlier content under the original one.
    if not message_id:
        message_id = new_message_id()

    part, mic = _build_secured_part(partnership, keystore, payload, filename)
    headers = _build_headers(partnership, part, message_id)

    out = (part.data, headers, message_id, mic)
    return out

# ################################################################################################################################
# ################################################################################################################################
