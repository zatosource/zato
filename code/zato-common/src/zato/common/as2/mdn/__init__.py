# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

The Message Disposition Notification of RFC 4130 section 7, spread over one module per concern.

- common - what an MDN is made of, and the Message-ID handling shared by messages and receipts
- disposition - the dispositions emitted and read back, and how each is written onto the wire
- request - what the sender of a message asked for, read out of its headers
- build - the multipart/report a received message is answered with
- parse - a receipt that arrived, read into the disposition, the MIC and the signer it reports
"""

# Zato
from zato.common.as2.mdn.build import build_mdn
from zato.common.as2.mdn.common import Disposition, DispositionType, MDNDetails, MDNRequest, MDNSigningConfig, \
    ModifierKind, new_message_id, normalize_message_id
from zato.common.as2.mdn.disposition import describe_disposition, disposition_from_exception, format_disposition, \
    is_known_modifier, new_error_disposition, new_failure_disposition, new_processed_disposition, \
    new_warning_disposition, parse_disposition
from zato.common.as2.mdn.parse import parse_mdn
from zato.common.as2.mdn.request import parse_mdn_request

# ################################################################################################################################
# ################################################################################################################################

__all__ = (
    'build_mdn',
    'describe_disposition',
    'disposition_from_exception',
    'format_disposition',
    'is_known_modifier',
    'new_error_disposition',
    'new_failure_disposition',
    'new_message_id',
    'new_processed_disposition',
    'new_warning_disposition',
    'normalize_message_id',
    'parse_disposition',
    'parse_mdn',
    'parse_mdn_request',
    'Disposition',
    'DispositionType',
    'MDNDetails',
    'MDNRequest',
    'MDNSigningConfig',
    'ModifierKind',
)

# ################################################################################################################################
# ################################################################################################################################
