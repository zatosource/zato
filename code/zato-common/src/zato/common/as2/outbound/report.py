# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

What a delivery is reported as - the JSON-friendly shape a completed delivery and a failed attempt
share, so that everything reading a send outcome reads the same keys.
"""

# Zato
from zato.common.as2.common import is_digest_equal
from zato.common.as2.mdn import describe_disposition

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.outbound.common import SendResult
    from zato.common.typing_ import stranydict
    stranydict = stranydict
    SendResult = SendResult

# ################################################################################################################################
# ################################################################################################################################

def new_send_report() -> 'stranydict':
    """ Returns an empty delivery report - the JSON-friendly shape a completed delivery
    and a failed attempt share, so callers always read the same keys.
    """
    out:'stranydict' = {
        'is_ok': False,
        'message_id': '',
        'http_status': 0,
        'has_mdn': False,
        'mdn_signed': False,
        'disposition': '',
        'mic_matched': None,

        # Why the receipt did not acknowledge the message, one of the SendError reasons.
        'mdn_error': '',

        # Why the message never left at all, the description of the exception raised.
        'error': '',
    }

    return out

# ################################################################################################################################

def describe_send_result(result:'SendResult') -> 'stranydict':
    """ Turns one delivery result into a JSON-friendly report of the MDN outcome -
    whether the receipt arrived signed, what its disposition says and whether
    its Received-Content-MIC agrees with the one computed at send time.
    """

    # Our response to produce
    out = new_send_report()

    out['is_ok'] = result.is_ok
    out['message_id'] = result.message_id
    out['http_status'] = result.http_status
    out['mdn_error'] = result.mdn_error

    mdn = result.mdn

    # With no MDN on the response, the transport details are everything there is to report.
    if not mdn:
        return out

    out['has_mdn'] = True
    out['mdn_signed'] = mdn.is_signed
    out['disposition'] = describe_disposition(mdn.disposition, mdn.modifier_kind, mdn.modifier)

    # The Received-Content-MIC is compared with the one computed at send time,
    # both the digest and the algorithm - an MDN without one leaves the comparison undecided.
    if mdn.mic:
        sent_digest, _, sent_algorithm = result.mic.partition(', ')

        if not is_digest_equal(mdn.mic, sent_digest):
            out['mic_matched'] = False
        elif mdn.mic_algorithm != sent_algorithm:
            out['mic_matched'] = False
        else:
            out['mic_matched'] = True

    return out

# ################################################################################################################################
# ################################################################################################################################
