# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

An asynchronously delivered receipt on its way in - parsed, matched against what was sent, and
recorded either way, because the answer to an incoming MDN is always a plain 200.
"""

# stdlib
from logging import getLogger

# Zato
from zato.common.as2.audit import encode_raw_mime
from zato.common.as2.common import AS2Exception, is_digest_equal
from zato.common.as2.mdn import DispositionType, ModifierKind, normalize_message_id, parse_mdn
from zato.common.as2.reconcile.common import MDNMatchResult
from zato.common.audit_log.api import AuditOutcome
from zato.common.json_internal import dumps

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.as2.mdn import MDNDetails
    from zato.common.as2.reconcile.common import PendingMDN
    from zato.common.as2.reconcile.store import MDNReconciler
    from zato.common.util.xml_.keystore import certificate_list, Keystore
    certificate_list = certificate_list
    Keystore = Keystore
    MDNDetails = MDNDetails
    MDNReconciler = MDNReconciler
    PendingMDN = PendingMDN

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def _is_mdn_ok(mdn:'MDNDetails', pending:'PendingMDN') -> 'bool':
    """ Tells whether an MDN reports clean processing of the message it answers,
    with its Received-Content-MIC agreeing with the one computed at send time.
    """

    # The disposition must report clean processing - a warning still counts as processed ..
    if mdn.disposition != DispositionType.Processed:
        return False

    if mdn.modifier_kind == ModifierKind.Error:
        return False

    if mdn.modifier_kind == ModifierKind.Failure:
        return False

    # .. and the Received-Content-MIC must match what was computed at send time.
    if mdn.mic:
        sent_digest, _, sent_algorithm = pending.mic.partition(', ')

        if not is_digest_equal(mdn.mic, sent_digest):
            return False

        if mdn.mic_algorithm != sent_algorithm:
            return False

    return True

# ################################################################################################################################

def process_incoming_mdn(
    body:'bytes',
    content_type:'str',
    reconciler:'MDNReconciler',
    keystore:'Keystore | None' = None,
    cid:'str' = '',
    accepted_certificates:'certificate_list | None' = None,
    ) -> 'MDNMatchResult':
    """ Parses one asynchronously delivered MDN and reconciles it against the sent messages.
    Never raises - an unparseable body, an unknown Message-ID and an already-reconciled one
    are all accepted and logged, because the answer to an incoming MDN is always a plain 200.
    A non-empty accepted_certificates list is the trust decision for a signed MDN's signer.
    """

    # Our response to produce
    out = MDNMatchResult()

    # A body that does not parse and verify as an MDN is accepted and logged, nothing more.
    try:
        mdn = parse_mdn(body, content_type, keystore, accepted_certificates)
    except AS2Exception as e:
        logger.info('Incoming MDN did not parse, cid:`%s`, e:`%s`', cid, e)

        return out

    out.is_parsed = True
    out.mdn = mdn

    message_id = normalize_message_id(mdn.original_message_id)

    # What the MDN reported, kept alongside the arrival event - the raw MDN bytes
    # are the partner's signed receipt, which is the evidence half of non-repudiation.
    raw_mime = encode_raw_mime(body)

    mdn_details = {'disposition': mdn.disposition, 'modifier_kind': mdn.modifier_kind, 'modifier': mdn.modifier,
        'mic': mdn.mic, 'raw_mime': raw_mime}
    mdn_data = dumps(mdn_details)

    # An unknown or already-reconciled Message-ID is accepted and logged, never errored ..
    pending = reconciler.match(message_id)

    if not pending:
        logger.info('Incoming MDN matched no pending message, original id:`%s`, cid:`%s`', mdn.original_message_id, cid)
        reconciler.record_mdn_received_for(message_id, None, cid=cid, data=mdn_data)

        return out

    out.is_matched = True
    out.pending = pending

    # .. a matched one reconciles against the disposition and the MIC computed at send time.
    out.is_ok = _is_mdn_ok(mdn, pending)

    if out.is_ok:
        outcome = AuditOutcome.OK
    else:
        outcome = AuditOutcome.Error

    reconciler.record_mdn_received_for(message_id, pending, outcome=outcome, cid=cid, data=mdn_data)

    return out

# ################################################################################################################################
# ################################################################################################################################
