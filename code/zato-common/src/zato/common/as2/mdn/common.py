# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

What an MDN is made of - the disposition it carries, what the sender of a message asked for,
what signing one requires and what parsing one yields.
"""

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.as2.common import Default
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from zato.common.typing_ import strlist
    from zato.common.util.xml_.keystore import Keystore
    Certificate = Certificate
    Keystore = Keystore
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

CRLF = b'\r\n'

# The disposition mode of an MDN produced without human intervention (RFC 4130 section 7.5.2).
Automatic_Mode = 'automatic-action/MDN-sent-automatically'

# What this implementation announces in the Reporting-UA field of every MDN.
Reporting_UA = 'Zato'

# The address type prefix of the recipient fields (RFC 8098 section 3.2.3).
Address_Type = 'rfc822'

# The one signed receipt protocol AS2 defines (RFC 4130 section 7.3) - a request
# for any other protocol makes an unsigned MDN the legitimate answer.
Supported_Receipt_Protocol = 'pkcs7-signature'

# ################################################################################################################################
# ################################################################################################################################

class DispositionType:
    """ The two disposition types AS2 uses (RFC 4130 section 7.5) - "processed" also covers errors
    and warnings through its modifier, while "failed" is reserved for problems with the MDN request itself.
    """
    Processed = 'processed'
    Failed    = 'failed'

# ################################################################################################################################
# ################################################################################################################################

class ModifierKind:
    """ The three disposition modifier kinds of RFC 4130 section 7.5 and RFC 8098 section 3.2.6.
    """
    Error   = 'error'
    Warning = 'warning'
    Failure = 'failure'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Disposition:
    """ One parsed or to-be-emitted Disposition field of an MDN.
    """
    # The action mode pair before the semicolon, e.g. automatic-action/MDN-sent-automatically.
    mode: str = Automatic_Mode

    # The disposition type - processed or failed.
    disposition_type: str = DispositionType.Processed

    # The modifier kind - error, warning or failure - or an empty string for a clean disposition.
    modifier_kind: str = ''

    # The modifier text after the kind, e.g. decryption-failed - never split on a comma,
    # so a value like "authentication-failed, processing continued" stays whole.
    modifier: str = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MDNRequest:
    """ What the sender of a message asked for in terms of its MDN - parsed out of the AS2 headers.
    """
    # The Message-ID of the message the MDN will answer, exactly as received.
    message_id: str = ''

    # The AS2 identities of the exchange - as2_from is the message's sender, who receives the MDN.
    as2_from: str = ''
    as2_to: str = ''

    # Whether an MDN was requested at all - the Disposition-Notification-To field indicates it
    # by its mere presence, its value is never used for routing.
    requests_mdn: bool = False

    # Whether a signed receipt was requested, and with which protocol.
    requests_signed_mdn: bool = False
    signed_receipt_protocol: str = ''

    # The signed-receipt-micalg preference list, in the sender's order -
    # assigned by parse_mdn_request.
    mic_algorithms: 'strlist'

    # The Receipt-Delivery-Option URL for an asynchronous MDN - empty means a synchronous one.
    async_mdn_url: str = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MDNSigningConfig:
    """ What signing an MDN requires - our keystore and the digest algorithm to prefer
    when the request does not name any.
    """
    keystore: 'Keystore'
    digest_algorithm: str = Default.Digest_Algorithm

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class MDNDetails:
    """ What parsing an MDN yields.
    """
    # The Original-Message-ID field - which message this MDN answers.
    original_message_id: str = ''

    # The parsed pieces of the Disposition field.
    mode: str = ''
    disposition: str = ''
    modifier_kind: str = ''
    modifier: str = ''

    # The Received-Content-MIC - the base64 digest and the algorithm name.
    mic: str = ''
    mic_algorithm: str = ''

    # Whether the MDN arrived signed and, if so, who signed it.
    is_signed: bool = False
    signer_certificate: 'Certificate | None' = None

    # The human-readable first part of the report.
    text: str = ''

# ################################################################################################################################
# ################################################################################################################################

def new_message_id() -> 'str':
    """ Returns a fresh Message-ID for an outgoing message or MDN.
    """
    suffix = CryptoManager.generate_hex_string()

    out = f'<{suffix}@zato>'
    return out

# ################################################################################################################################

def normalize_message_id(value:'str') -> 'str':
    """ Strips the angle brackets off a Message-ID - the comparison stays case-sensitive
    on the full addr-spec underneath, so nothing else is touched.
    """
    out = value.strip()

    if out.startswith('<'):
        out = out[1:]

    if out.endswith('>'):
        out = out[:-1]

    return out

# ################################################################################################################################
# ################################################################################################################################
