# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

MDN reconciliation - a small state tracker persisting the Message-ID, the expected MIC and the
asynchronous delivery URL of each sent message, and matching incoming MDNs against them, so a
missing MDN is detectable.

- common - what one sent message is described by and what matching a receipt against it yields
- store - what was sent, which receipts arrived, and everything still waiting for one
- incoming - an asynchronously delivered receipt on its way in
"""

# Zato
from zato.common.as2.reconcile.common import Default_Server_Name, Max_Outstanding, MDNMatchResult, pair_key, \
    pending_mdn_list, PendingMDN, ReconcileAttr
from zato.common.as2.reconcile.incoming import process_incoming_mdn
from zato.common.as2.reconcile.store import MDNReconciler

# ################################################################################################################################
# ################################################################################################################################

__all__ = (
    'pair_key',
    'pending_mdn_list',
    'process_incoming_mdn',
    'Default_Server_Name',
    'Max_Outstanding',
    'MDNMatchResult',
    'MDNReconciler',
    'PendingMDN',
    'ReconcileAttr',
)

# ################################################################################################################################
# ################################################################################################################################
