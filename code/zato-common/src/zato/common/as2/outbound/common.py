# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

What goes out - the documents a message carries - and what comes back of one delivery.
"""

# stdlib
from dataclasses import dataclass
from typing import Generator, NamedTuple

# typing-extensions
from typing_extensions import TypeAlias

# ################################################################################################################################
# ################################################################################################################################

if 0:
    import httpx
    from zato.common.as2.mdn import MDNDetails
    httpx = httpx
    MDNDetails = MDNDetails

# ################################################################################################################################
# ################################################################################################################################

#  Type aliases
payload_item_list = list['PayloadItem']
bytesgen          = Generator[bytes, None, None]

send_payload:TypeAlias = 'bytes | payload_item_list'

# ################################################################################################################################
# ################################################################################################################################

class PayloadItem(NamedTuple):
    """ One document of a multi-document payload - its bytes, content type and filename.
    """
    data: bytes
    content_type: str
    filename: str

# ################################################################################################################################
# ################################################################################################################################

CRLF = b'\r\n'

# How many bytes of the body each chunk of a chunked request carries.
Chunk_Size = 64 * 1024

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SendResult:
    """ The outcome of delivering one AS2 message.
    """
    is_ok: bool = False

    # The Message-ID the message went out with.
    message_id: str = ''

    # The MIC computed at send time, in its wire form - the returned MDN reconciles against it.
    mic: str = ''

    # The parsed and verified MDN, when a synchronous one arrived.
    mdn: 'MDNDetails | None' = None

    # The complete raw MIME body that went over the wire, kept as delivery evidence.
    request_body: bytes = b''

    # The raw HTTP response, kept for audit purposes.
    http_status: int = 0
    response_body: bytes = b''

    # Why a delivery that left successfully is still unacknowledged - one of the SendError
    # reasons when a synchronous MDN was requested and did not confirm the message,
    # empty when the message is acknowledged or when there is nothing to reconcile. This is
    # separate from a transport-level exception, which never gets this far.
    mdn_error: str = ''

# ################################################################################################################################
# ################################################################################################################################
