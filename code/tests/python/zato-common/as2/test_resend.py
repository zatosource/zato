# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.api import AS2
from zato.common.as2.audit import encode_payload_document
from zato.common.as2.common import DeliveryKind
from zato.common.as2.reconcile import MDNReconciler
from zato.common.as2.resend import collect_candidates, count_attempts, get_max_retries
from zato.common.ext.bunch import Bunch
from zato.common.util.api import utcnow

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    any_ = any_
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

# The reconciliation store all the tests write to and the resend collection reads from.
_server_name = 'test-server'

# Who the exchanges of these tests travel between.
_as2_from = 'ZatoRetail'
_as2_to   = 'PartnerCorp'

# The overdue window every test partner uses, and a moment safely past it.
_overdue_seconds = 3600
_past_the_window = _overdue_seconds + 100

# The document a resend delivers again.
_edi = b'ISA*00*Test payload of an 850 order'

# An attachment that would not survive a text field, which is what makes the entries
# the thing a resend has to work from.
_pdf = b'%PDF-1.7\x00\x80\xff\xfe bill of lading \x01\x02'

# The HTTP status a partner that accepted the message answered with, and the one
# a delivery that never got there did not.
_http_accepted = 200
_http_never_sent = 0

# ################################################################################################################################
# ################################################################################################################################

def _new_config(**overrides:'any_') -> 'any_':
    """ One partner's connection configuration, the way the resend collection sees it.
    """
    out = Bunch()

    out['name'] = 'PartnerCorp AS2'
    out['as2_from'] = _as2_from
    out['as2_to'] = _as2_to
    out['ack_overdue_after'] = _overdue_seconds
    out['resend_max_retries'] = 0

    out.update(overrides)

    return out

# ################################################################################################################################

def _record_sent(
    reconciler:'MDNReconciler',
    message_id:'str',
    documents:'anylist',
    *,
    http_status:'int' = _http_accepted,
    delivery_kind:'str' = DeliveryKind.Original,
    ) -> 'None':
    """ Records one delivery attempt the way an outgoing connection does.
    """
    payloads:'anylist' = []

    for data, content_type, filename in documents:
        document = encode_payload_document(data, content_type, filename)
        payloads.append(document)

    first_data, _, first_filename = documents[0]
    first_text = first_data.decode('utf8', 'replace')

    sent_options = {
        'mic': 'abc, sha-256',
        'payload': first_text,
        'filename': first_filename,
        'payloads': payloads,
        'delivery_kind': delivery_kind,
        'http_status': http_status,
    }

    reconciler.record_message_sent(_as2_from, _as2_to, message_id, **sent_options)

# ################################################################################################################################

def _single_document() -> 'anylist':
    """ The stored documents of a plain one-document message.
    """
    out = [(_edi, 'application/edi-x12', 'order-850.edi')]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMaxRetries:
    """ How many resends a message gets is the partner's own setting, with the job's default
    standing in for the zero the Dashboard stores when the field is left alone.
    """

    def test_the_partners_own_setting_wins(self) -> 'None':

        config = _new_config(resend_max_retries=7)
        assert get_max_retries(config) == 7

# ################################################################################################################################

    def test_zero_means_the_default(self) -> 'None':

        config = _new_config(resend_max_retries=0)
        assert get_max_retries(config) == AS2.Resend.Default_Max_Retries

# ################################################################################################################################

    def test_no_partner_means_the_default(self) -> 'None':

        assert get_max_retries(None) == AS2.Resend.Default_Max_Retries

# ################################################################################################################################
# ################################################################################################################################

class TestCountAttempts:
    """ The attempts already made are the message-sent events under one Message-ID, which is
    what makes the count survive a restart without any bookkeeping of its own.
    """

    def test_one_delivery_counts_as_one_attempt(self) -> 'None':

        reconciler = MDNReconciler(_server_name)
        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents)

        assert count_attempts(reconciler, 'msg-1@zato') == 1

# ################################################################################################################################

    def test_each_resend_adds_an_attempt(self) -> 'None':

        reconciler = MDNReconciler(_server_name)

        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents)
        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents, delivery_kind=DeliveryKind.Resend)
        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents, delivery_kind=DeliveryKind.Resend)

        assert count_attempts(reconciler, 'msg-1@zato') == 3

        # Another message's attempts are its own.
        documents = _single_document()
        _record_sent(reconciler, 'msg-2@zato', documents)
        assert count_attempts(reconciler, 'msg-2@zato') == 1

# ################################################################################################################################
# ################################################################################################################################

class TestCollectCandidates:
    """ A message is resent when its receipt is overdue by the partner's own window and it has
    attempts left. Everything else - a receipt that arrived, a message still inside its window,
    a partner that is gone - is left alone.
    """

    def test_an_overdue_message_is_a_candidate(self) -> 'None':

        reconciler = MDNReconciler(_server_name)
        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents)

        now = utcnow() + timedelta(seconds=_past_the_window)
        candidates = collect_candidates([_new_config()], now, _server_name)

        candidate_count = len(candidates)
        assert candidate_count == 1

        candidate = candidates[0]

        # The content goes back out under the original Message-ID, which is what leaves it
        # to the receiver's duplicate detection to decide whether it is delivered twice.
        assert candidate.message_id == 'msg-1@zato'
        assert candidate.connection_name == 'PartnerCorp AS2'
        assert candidate.as2_from == _as2_from
        assert candidate.as2_to == _as2_to
        assert candidate.attempt_count == 1

        assert candidate.payload == _edi
        assert candidate.filename == 'order-850.edi'

# ################################################################################################################################

    def test_a_message_inside_its_window_is_left_alone(self) -> 'None':

        reconciler = MDNReconciler(_server_name)
        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents)

        # The window has not passed yet, so the receipt is merely pending.
        now = utcnow() + timedelta(seconds=_overdue_seconds - 100)
        candidates = collect_candidates([_new_config()], now, _server_name)

        candidate_count = len(candidates)
        assert candidate_count == 0

# ################################################################################################################################

    def test_a_message_whose_receipt_arrived_is_left_alone(self) -> 'None':

        reconciler = MDNReconciler(_server_name)
        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents)

        # The receipt closes the exchange, which takes the message out of the outstanding set
        # and with it out of the resend job's reach.
        reconciler.record_mdn_received('msg-1@zato')

        now = utcnow() + timedelta(seconds=_past_the_window)
        candidates = collect_candidates([_new_config()], now, _server_name)

        candidate_count = len(candidates)
        assert candidate_count == 0

# ################################################################################################################################

    def test_a_message_out_of_attempts_is_left_alone(self) -> 'None':

        reconciler = MDNReconciler(_server_name)

        # One original delivery plus two resends is three attempts, which is one more
        # than a partner allowing two resends gets.
        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents)
        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents, delivery_kind=DeliveryKind.Resend)
        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents, delivery_kind=DeliveryKind.Resend)

        now = utcnow() + timedelta(seconds=_past_the_window)

        config = _new_config(resend_max_retries=2)
        candidates = collect_candidates([config], now, _server_name)

        candidate_count = len(candidates)
        assert candidate_count == 0

        # A partner allowing one more resend still gets one.
        config = _new_config(resend_max_retries=3)
        candidates = collect_candidates([config], now, _server_name)

        candidate_count = len(candidates)
        assert candidate_count == 1

        candidate = candidates[0]
        assert candidate.attempt_count == 3

# ################################################################################################################################

    def test_a_message_whose_partner_is_gone_is_left_alone(self) -> 'None':

        reconciler = MDNReconciler(_server_name)
        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents)

        now = utcnow() + timedelta(seconds=_past_the_window)

        # The connection was deleted or renamed, so there is nothing to send through -
        # the operator resubmit is what remains for a message in that state.
        candidates = collect_candidates([], now, _server_name)

        candidate_count = len(candidates)
        assert candidate_count == 0

# ################################################################################################################################

    def test_a_message_with_no_stored_documents_is_left_alone(self) -> 'None':

        reconciler = MDNReconciler(_server_name)

        # A connection with its audit log turned off records the reconciliation entry
        # without any payload, so there is nothing to deliver again.
        reconciler.record_message_sent(_as2_from, _as2_to, 'msg-1@zato', mic='abc, sha-256')

        now = utcnow() + timedelta(seconds=_past_the_window)
        candidates = collect_candidates([_new_config()], now, _server_name)

        candidate_count = len(candidates)
        assert candidate_count == 0

# ################################################################################################################################

    def test_the_batch_bounds_one_run(self) -> 'None':

        reconciler = MDNReconciler(_server_name)

        message_number = 0

        while message_number < 5:
            message_number += 1
            documents = _single_document()
            _record_sent(reconciler, f'msg-{message_number}@zato', documents)

        now = utcnow() + timedelta(seconds=_past_the_window)

        # A partner outage must not turn one run into a burst of every message sent during it.
        candidates = collect_candidates([_new_config()], now, _server_name, limit=2)

        candidate_count = len(candidates)
        assert candidate_count == 2

# ################################################################################################################################
# ################################################################################################################################

class TestDeliveryKind:
    """ A repeat is a retry when the original attempt never reached the partner and a resend when
    it did - which is the difference between the transport failing and the receipt going missing.
    """

    def test_an_accepted_delivery_repeats_as_a_resend(self) -> 'None':

        reconciler = MDNReconciler(_server_name)
        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents, http_status=_http_accepted)

        now = utcnow() + timedelta(seconds=_past_the_window)
        candidates = collect_candidates([_new_config()], now, _server_name)

        candidate = candidates[0]
        assert candidate.delivery_kind == DeliveryKind.Resend

# ################################################################################################################################

    def test_a_delivery_that_never_arrived_repeats_as_a_retry(self) -> 'None':

        reconciler = MDNReconciler(_server_name)
        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents, http_status=_http_never_sent)

        now = utcnow() + timedelta(seconds=_past_the_window)
        candidates = collect_candidates([_new_config()], now, _server_name)

        candidate = candidates[0]
        assert candidate.delivery_kind == DeliveryKind.Retry

# ################################################################################################################################

    def test_a_refused_delivery_repeats_as_a_retry(self) -> 'None':

        reconciler = MDNReconciler(_server_name)
        documents = _single_document()
        _record_sent(reconciler, 'msg-1@zato', documents, http_status=500)

        now = utcnow() + timedelta(seconds=_past_the_window)
        candidates = collect_candidates([_new_config()], now, _server_name)

        candidate = candidates[0]
        assert candidate.delivery_kind == DeliveryKind.Retry

# ################################################################################################################################

    def test_an_event_from_before_the_kind_was_stored_repeats_as_a_retry(self) -> 'None':

        reconciler = MDNReconciler(_server_name)

        # Events already in the database carry neither the kind nor the status, which reads
        # as a transport outcome nobody knows - and a retry is the honest thing to call it.
        payload = _edi.decode('utf8')

        sent_options = {
            'mic': 'abc, sha-256',
            'payload': payload,
            'filename': 'order-850.edi',
        }

        reconciler.record_message_sent(_as2_from, _as2_to, 'msg-1@zato', **sent_options)

        now = utcnow() + timedelta(seconds=_past_the_window)
        candidates = collect_candidates([_new_config()], now, _server_name)

        candidate = candidates[0]
        assert candidate.delivery_kind == DeliveryKind.Retry

# ################################################################################################################################
# ################################################################################################################################

class TestMultipleAttachments:
    """ A resend delivers what the partner received the first time, which for a logistics partner
    means the EDI document and the attached PDF together, byte for byte.
    """

    def test_every_attachment_goes_back_out_together(self) -> 'None':

        reconciler = MDNReconciler(_server_name)

        documents = [
            (_edi, 'application/edi-x12', 'ship-notice-856.edi'),
            (_pdf, 'application/pdf', 'bill-of-lading.pdf'),
        ]

        _record_sent(reconciler, 'msg-1@zato', documents)

        now = utcnow() + timedelta(seconds=_past_the_window)
        candidates = collect_candidates([_new_config()], now, _server_name)

        candidate = candidates[0]

        item_count = len(candidate.payload)
        assert item_count == 2

        first, second = candidate.payload

        assert first.data == _edi
        assert first.content_type == 'application/edi-x12'
        assert first.filename == 'ship-notice-856.edi'

        # The attachment comes back unchanged, which the readable text field
        # could not have managed.
        assert second.data == _pdf
        assert second.content_type == 'application/pdf'
        assert second.filename == 'bill-of-lading.pdf'

        # A multi-document payload carries its filenames inside, so none travels separately.
        assert candidate.filename is None

# ################################################################################################################################
# ################################################################################################################################
