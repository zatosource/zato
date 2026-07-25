# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# lxml
from lxml import etree

# Zato
from zato.common.as4.audit import record_errors_received, record_message_sent, record_receipt_received
from zato.common.as4.ebms import build_envelope, build_receipt, ErrorDetails, SignalDetails
from zato.common.as4.outbound import new_part, SendResult
from zato.common.as4.profiles import new_edelivery1_pmode
from zato.common.as4.reconcile import ReceiptReconciler
from zato.common.as4.security.sign import sign_envelope
from zato.common.audit_log.api import AuditLog
from zato.common.json_internal import loads
from zato.common.util.api import utcnow

from .test_audit import _read_events, audit_db
from .test_server_connection import _make_channel, Payload

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from .conftest import TestParties
    TestParties = TestParties

# The fixture is imported for its side effect of pointing the audit log at a database of its own.
audit_db = audit_db

# ################################################################################################################################
# ################################################################################################################################

_From_Party = 'party-a'
_To_Party = 'party-b'

_Service = 'urn:test:service'
_Action = 'SubmitDocument'

# ################################################################################################################################
# ################################################################################################################################

def _new_reconciler() -> 'ReceiptReconciler':
    """ Returns a store reading the database the audit_db fixture set up.
    """
    out = ReceiptReconciler('test-as4-reconciler')
    return out

# ################################################################################################################################

def _record_send(message_id:'str', conversation_id:'str'='') -> 'None':
    """ Records one push of a message with the given id, the way a wrapper records a send
    whose receipt is to arrive later.
    """
    if not conversation_id:
        conversation_id = message_id

    result = SendResult()
    result.errors = []
    result.is_ok = True
    result.message_id = message_id
    result.conversation_id = conversation_id
    result.request_body = b'<Envelope/>'

    audit_log = AuditLog('test-as4-sender')

    record_message_sent(audit_log, _From_Party, _To_Party, result,
        payloads=[new_part(Payload)], service=_Service, action=_Action, cid='cid-' + message_id)

# ################################################################################################################################

def _record_receipt(message_id:'str') -> 'None':
    """ Records the arrival of a receipt for the message of the given id.
    """
    receipt = SignalDetails()
    receipt.errors = []
    receipt.receipt_references = []
    receipt.is_receipt = True
    receipt.message_id = 'receipt-' + message_id
    receipt.ref_to_message_id = message_id

    audit_log = AuditLog('test-as4-sender')

    record_receipt_received(audit_log, _From_Party, _To_Party, receipt, ref_to_message_id=message_id)

# ################################################################################################################################

def _record_errors(message_id:'str') -> 'None':
    """ Records the arrival of error signals for the message of the given id, which is the other
    way an exchange can end.
    """
    error = ErrorDetails()
    error.error_code = 'EBMS:0004'
    error.severity = 'failure'
    error.short_description = 'Other'
    error.detail = 'Refused'

    audit_log = AuditLog('test-as4-sender')

    record_errors_received(audit_log, _From_Party, _To_Party, ref_to_message_id=message_id, errors=[error])

# ################################################################################################################################

def _future_cutoff() -> 'any_':
    """ A moment every event recorded by a test is older than.
    """
    out = utcnow() + timedelta(seconds=1)
    return out

# ################################################################################################################################

def _past_cutoff() -> 'any_':
    """ A moment no event recorded by a test is older than.
    """
    out = utcnow() - timedelta(hours=1)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestMatch:
    """ Resolving the message one receipt refers to, which is all an asynchronous receipt
    carries to identify what it answers.
    """

    def test_a_sent_message_is_matched_by_the_id_a_receipt_echoes(self, audit_db:'any_') -> 'None':
        _record_send('message-1@test')

        pending = _new_reconciler().match('message-1@test')

        assert pending
        assert pending.message_id == 'message-1@test'
        assert pending.from_party == _From_Party
        assert pending.to_party == _To_Party
        assert pending.service == _Service
        assert pending.action == _Action
        assert pending.conversation_id == 'message-1@test'
        assert pending.cid == 'cid-message-1@test'
        assert pending.sent_time_iso

# ################################################################################################################################

    def test_a_message_whose_receipt_arrived_is_no_longer_matched(self, audit_db:'any_') -> 'None':
        _record_send('message-1@test')
        _record_receipt('message-1@test')

        pending = _new_reconciler().match('message-1@test')
        assert pending is None

# ################################################################################################################################

    def test_a_message_the_partner_refused_is_no_longer_matched(self, audit_db:'any_') -> 'None':
        """ Error signals close the exchange the same way a receipt does - what is open is
        a message nothing at all has answered.
        """
        _record_send('message-1@test')
        _record_errors('message-1@test')

        pending = _new_reconciler().match('message-1@test')
        assert pending is None

# ################################################################################################################################

    def test_a_message_id_never_sent_matches_nothing(self, audit_db:'any_') -> 'None':
        _record_send('message-1@test')

        pending = _new_reconciler().match('message-2@test')
        assert pending is None

# ################################################################################################################################

    def test_a_signal_that_echoed_no_message_id_matches_nothing(self, audit_db:'any_') -> 'None':
        _record_send('message-1@test')

        pending = _new_reconciler().match('')
        assert pending is None

# ################################################################################################################################

    def test_only_the_conversation_of_its_own_send_is_returned(self, audit_db:'any_') -> 'None':
        """ One conversation spans several messages, so the conversation a receipt belongs to
        is the one of the message it refers to, not the one of the newest message sent.
        """
        _record_send('message-1@test', conversation_id='conversation-1')
        _record_send('message-2@test', conversation_id='conversation-2')

        pending = _new_reconciler().match('message-1@test')

        assert pending
        assert pending.conversation_id == 'conversation-1'

# ################################################################################################################################
# ################################################################################################################################

class TestOutstanding:
    """ Everything still waiting for a receipt, which is what a missing receipt timer runs on.
    """

    def test_a_message_without_a_receipt_is_outstanding(self, audit_db:'any_') -> 'None':
        _record_send('message-1@test')

        pending_list = _new_reconciler().outstanding(_future_cutoff())

        assert len(pending_list) == 1
        assert pending_list[0].message_id == 'message-1@test'

# ################################################################################################################################

    def test_a_message_with_a_receipt_is_not_outstanding(self, audit_db:'any_') -> 'None':
        _record_send('message-1@test')
        _record_send('message-2@test')
        _record_receipt('message-1@test')

        pending_list = _new_reconciler().outstanding(_future_cutoff())

        assert len(pending_list) == 1
        assert pending_list[0].message_id == 'message-2@test'

# ################################################################################################################################

    def test_a_message_newer_than_the_cutoff_is_not_reported(self, audit_db:'any_') -> 'None':
        """ The cutoff is what gives a receipt time to arrive before the message counts as late.
        """
        _record_send('message-1@test')

        pending_list = _new_reconciler().outstanding(_past_cutoff())
        assert pending_list == []

# ################################################################################################################################

    def test_one_message_is_one_entry_however_many_attempts_it_took(self, audit_db:'any_') -> 'None':
        """ Every attempt at one message records its own send under the same message id, so an
        entry per attempt would mean an alert per attempt and a further resend per attempt.
        """
        _record_send('message-1@test')
        _record_send('message-1@test')
        _record_send('message-1@test')

        pending_list = _new_reconciler().outstanding(_future_cutoff())

        assert len(pending_list) == 1
        assert pending_list[0].message_id == 'message-1@test'

# ################################################################################################################################

    def test_the_oldest_messages_come_first(self, audit_db:'any_') -> 'None':
        _record_send('message-1@test')
        _record_send('message-2@test')
        _record_send('message-3@test')

        pending_list = _new_reconciler().outstanding(_future_cutoff())

        message_ids = [item.message_id for item in pending_list]
        assert message_ids == ['message-1@test', 'message-2@test', 'message-3@test']

# ################################################################################################################################

    def test_the_batch_is_bounded(self, audit_db:'any_') -> 'None':
        """ A partner outage over a weekend must not be read into memory in one go.
        """
        _record_send('message-1@test')
        _record_send('message-2@test')
        _record_send('message-3@test')

        pending_list = _new_reconciler().outstanding(_future_cutoff(), limit=2)

        message_ids = [item.message_id for item in pending_list]
        assert message_ids == ['message-1@test', 'message-2@test']

# ################################################################################################################################

    def test_nothing_sent_means_nothing_outstanding(self, audit_db:'any_') -> 'None':
        pending_list = _new_reconciler().outstanding(_future_cutoff())
        assert pending_list == []

# ################################################################################################################################
# ################################################################################################################################

class TestAsyncCorrelation:
    """ A receipt that arrives on its own, on whichever channel the partner posts it to, is filed
    under the exchange it closes rather than under the channel it came in on.
    """

    def _deliver_receipt(self, rsa_parties:'TestParties', ref_to_message_id:'str') -> 'any_':
        """ Posts one standalone signed receipt to a channel, the way a partner delivers
        an asynchronous receipt for a message pushed earlier.
        """
        channel = _make_channel(rsa_parties, 'edelivery1', is_audit_log_active=True)

        pmode = new_edelivery1_pmode()

        envelope = build_envelope()
        _ = build_receipt(envelope, ref_to_message_id, [])
        _ = sign_envelope(envelope, [], rsa_parties.sender, pmode.security)

        body = etree.tostring(envelope, xml_declaration=True, encoding='UTF-8')

        out = channel.handle('cid-async', body, 'application/soap+xml')
        return out

# ################################################################################################################################

    def test_a_receipt_lands_on_the_pair_of_its_own_send(
        self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':

        # The message went out first, under the pair of the sending direction ..
        _record_send('message-1@test')

        result = self._deliver_receipt(rsa_parties, 'message-1@test')
        assert len(result.signals) == 1

        events = _read_events()
        assert len(events) == 2

        receipt_event = events[1]

        # .. and the receipt that answered it is filed under that same pair, which is what
        # makes the two halves one exchange even though the receipt arrived on its own.
        assert receipt_event['object_name'] == f'{_From_Party}:{_To_Party}'
        assert receipt_event['msg_id'] == 'message-1@test'

        details = loads(receipt_event['data'])
        assert details['is_matched'] is True

        # The exchange is closed, so nothing is waiting for a receipt any more.
        pending_list = _new_reconciler().outstanding(_future_cutoff())
        assert pending_list == []

# ################################################################################################################################

    def test_a_receipt_answering_nothing_falls_back_to_the_channel_pair(
        self, rsa_parties:'TestParties', audit_db:'any_') -> 'None':
        """ A repeated or misdirected receipt is recorded, never errored - the channel it arrived
        on is what places it, and the event says it matched nothing.
        """
        result = self._deliver_receipt(rsa_parties, 'never-sent@test')
        assert len(result.signals) == 1

        events = _read_events()
        assert len(events) == 1

        receipt_event = events[0]

        # On a channel the responder is this access point, so the fallback pair reads
        # in the direction a message sent from here would have travelled.
        assert receipt_event['object_name'] == f'{_To_Party}:{_From_Party}'
        assert receipt_event['msg_id'] == 'never-sent@test'

        details = loads(receipt_event['data'])
        assert details['is_matched'] is False

# ################################################################################################################################
# ################################################################################################################################
