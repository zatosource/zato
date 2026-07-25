# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

Receiving an AS2 message, spread over one module per stage of the path a request travels.

- common - the result object, the delivered documents and the ceilings the path is held to
- layers - reversing compression, signing and encryption, and the security policy check
- payloads - the innermost entity turned into the documents that are handed on
- receipt - the MDN placed on the response or queued for asynchronous delivery
- pipeline - the entry point tying the stages together
"""

# Zato
from zato.common.as2.inbound.common import InboundPayload, InboundResult, payload_list, PendingAsyncMDN, StoredMDN
from zato.common.as2.inbound.pipeline import handle

# ################################################################################################################################
# ################################################################################################################################

__all__ = (
    'handle',
    'payload_list',
    'InboundPayload',
    'InboundResult',
    'PendingAsyncMDN',
    'StoredMDN',
)

# ################################################################################################################################
# ################################################################################################################################
