# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

What the inbound pipeline produces - the documents it delivers, the receipt it sends back and the
result object tying the two together, along with the ceilings every quantity on the path is held to.
"""

# stdlib
from dataclasses import dataclass
from http.client import OK

# Zato
from zato.common.as2.common import Default

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from cryptography.x509 import Certificate
    from zato.common.as2.mdn import Disposition
    from zato.common.as2.partnership import Partnership
    from zato.common.typing_ import strnone, strstrdict
    from zato.common.util.xml_.keystore import Keystore
    Certificate = Certificate
    Disposition = Disposition
    Keystore = Keystore
    Partnership = Partnership
    strnone = strnone
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
payload_list = list['InboundPayload']

# ################################################################################################################################
# ################################################################################################################################

CRLF = b'\r\n'

# The transfer encoding assumed when an incoming request does not declare one.
Default_Transfer_Encoding = 'binary'

# How many security layers one message may be wrapped in. Real messages use at most
# compression, signing and encryption together, so this leaves generous room while still
# denying a peer the ability to stack layers without limit.
Max_Layer_Depth = 8

# How large an incoming request body may be. Processing one message holds the body, its base64
# form and the decoded payload at once, so peak memory is a multiple of this rather than equal
# to it, which is why the ceiling sits well below what a single process can hold.
Max_Inbound_Bytes = 256 * 1024 * 1024

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class InboundPayload:
    """ One delivered document - what the inbound topic or service receives.
    """
    data: bytes = b''
    content_type: str = ''
    filename: str = ''

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class StoredMDN:
    """ The MDN response of an earlier delivery, kept by the duplicate store so that a replay
    of the same message gets the exact same bytes back, never a recomputed answer.
    """
    status_code: int = OK
    body: bytes = b''
    headers: 'strstrdict'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PendingAsyncMDN:
    """ An MDN the caller is to deliver asynchronously to the URL the sender named -
    already checked against the partnership, so the caller delivers it as it stands.
    """
    url: str = ''
    body: bytes = b''
    headers: 'strstrdict'

    # How the delivery is to be made, carried here so that the transport does not need
    # the partnership - an outgoing request with no ceiling on it would hold a worker
    # for as long as the destination cared to keep the connection open.
    verify_tls: bool = True
    timeout_seconds: int = Default.HTTP_Timeout_Seconds

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class InboundResult:
    """ What the transport should send back and what the application receives.
    """
    # The HTTP response - an MDN on the body for synchronous receipts,
    # empty for asynchronous ones and when no MDN was requested at all.
    status_code:  int = OK
    content_type: str = ''
    body:         bytes = b''
    headers:      'strstrdict'

    # The identities of the exchange, unquoted, and the Message-ID without its angle brackets.
    as2_from:   str = ''
    as2_to:     str = ''
    message_id: str = ''

    # What the peer advertised in its EDIINT-Features header - logged for onboarding,
    # never driving behavior.
    ediint_features: str = ''

    # The partnership the message matched.
    partnership: 'Partnership | None' = None

    # The MIC computed over the received content, in its wire form.
    mic: str = ''

    # The delivered documents - empty on a duplicate or an error.
    payloads: 'payload_list'

    # The certificate that signed the message, when it arrived signed.
    signer_certificate: 'Certificate | None' = None

    # Whether the message was recognized as a replay - the stored MDN is re-transmitted
    # as it is and the payloads are not delivered a second time.
    is_duplicate: bool = False

    # Whether processing failed and the body carries an MDN with an error disposition.
    is_error: bool = False
    error_modifier: 'strnone' = None

    # The disposition the MDN was built with - clean processing or the matching error,
    # kept on the result so the caller can record it as delivery evidence.
    disposition: 'Disposition | None' = None

    # The MDN to deliver asynchronously, when the sender asked for one.
    pending_async_mdn: 'PendingAsyncMDN | None' = None

# ################################################################################################################################
# ################################################################################################################################
