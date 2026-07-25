# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Sending an AS2 message, spread over one module per concern.

- common - the documents a message carries and what comes back of one delivery
- payload - the innermost MIME entity, one document or a multipart/related of several
- message - compression, signing, encryption and the AS2 headers around the result
- transport - how the request is framed and authenticated on its way out
- send - the delivery itself and the reconciliation of a synchronous receipt
- report - the JSON-friendly report every reader of a send outcome reads
"""

# Zato
from zato.common.as2.outbound.common import bytesgen, payload_item_list, PayloadItem, send_payload, SendResult
from zato.common.as2.outbound.message import build_message
from zato.common.as2.outbound.report import describe_send_result, new_send_report
from zato.common.as2.outbound.send import send

# ################################################################################################################################
# ################################################################################################################################

__all__ = (
    'build_message',
    'bytesgen',
    'describe_send_result',
    'new_send_report',
    'payload_item_list',
    'send',
    'send_payload',
    'PayloadItem',
    'SendResult',
)

# ################################################################################################################################
# ################################################################################################################################
