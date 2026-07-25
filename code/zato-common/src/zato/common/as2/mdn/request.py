# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Reading what the sender of a message asked for in terms of its receipt out of the AS2 headers.
"""

# Zato
from zato.common.as2.mdn.common import MDNRequest

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strstrdict
    strlist = strlist
    strstrdict = strstrdict

# ################################################################################################################################
# ################################################################################################################################

def parse_mdn_request(headers:'strstrdict') -> 'MDNRequest':
    """ Reads what kind of MDN the sender of a message asked for out of its AS2 headers.
    Header names are expected in lowercase. Implementations must never reject a message
    based on the syntax of these fields, so everything here is lenient.
    """

    # Our response to produce
    out = MDNRequest()
    out.mic_algorithms = []

    if message_id := headers.get('message-id'):
        out.message_id = message_id

    if as2_from := headers.get('as2-from'):
        out.as2_from = as2_from

    if as2_to := headers.get('as2-to'):
        out.as2_to = as2_to

    # The mere presence of this field requests an MDN - its value is never used for routing.
    out.requests_mdn = 'disposition-notification-to' in headers

    # A synchronous MDN rides on the HTTP response, an asynchronous one is delivered to this URL.
    if async_mdn_url := headers.get('receipt-delivery-option'):
        out.async_mdn_url = async_mdn_url.strip()

    # The options field carries the signed receipt request - each option names its importance
    # first (required or optional) and its values after it.
    if options := headers.get('disposition-notification-options'):

        for option in options.split(';'):
            name, _, values_part = option.partition('=')
            name = name.strip()
            name = name.lower()

            values:'strlist' = []

            # The first comma-separated piece is the importance token, the rest are the values.
            value_pieces = values_part.split(',')

            for piece in value_pieces[1:]:
                piece = piece.strip()
                if piece:
                    values.append(piece)

            if name == 'signed-receipt-protocol':
                if values:
                    first_value = values[0]
                    out.signed_receipt_protocol = first_value.lower()
                    out.requests_signed_mdn = True

            elif name == 'signed-receipt-micalg':
                out.mic_algorithms = values

    return out

# ################################################################################################################################
# ################################################################################################################################
