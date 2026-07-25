# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# Zato
from zato.common.api import AS4
from zato.common.as4.audit import decode_payload_documents, record_message_sent, record_receipt_received
from zato.common.as4.common import Default
from zato.common.as4.config import apply_reception_awareness
from zato.common.as4.ebms import SignalDetails
from zato.common.as4.outbound import new_part, SendResult
from zato.common.as4.profiles import new_edelivery1_pmode, new_peppol_pmode
from zato.common.as4.reconcile import ReceiptReconciler
from zato.common.as4.resend import collect_candidates, collect_missing_receipts, count_attempts, \
    get_reception_awareness, ResendCandidate
from zato.common.audit_log.api import AuditEvent, AuditLog
from zato.common.ext.bunch import Bunch
from zato.common.json_internal import loads
from zato.common.util.api import utcnow

from .test_audit import audit_db, _by_event_type, _read_events
from .test_server_connection import _connect, _make_channel, _make_wrapper, Payload, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    from .conftest import TestParties
    TestParties = TestParties

# The fixture is imported for its side effect of pointing the audit log at a database of its own.
audit_db = audit_db

# ################################################################################################################################
# ################################################################################################################################

# The store every test writes to and the resend collection reads from.
_Server_Name = 'test-as4-resend'

# Who the exchanges of these tests travel between.
_From_Party = 'party-a'
_To_Party = 'party-b'

# What the exchanges of these tests carry.
_Service = 'urn:test:service'
_Action = 'SubmitDocument'

# The document a repeat delivery sends again, and one that would not survive a text field, which
# is what makes the stored entries the thing a resend has to work from.
_Payload = b'<?xml version="1.0" encoding="UTF-8"?><Invoice><Id>1</Id></Invoice>'
_Binary_Payload = b'%PDF-1.7\x00\x80\xff\xfe bill of lading \x01\x02'

# The retry window every test connection uses, and a moment safely past it.
_Retry_Interval = 900
_Past_The_Window = _Retry_Interval + 100

# How long the test connections give an exchange before its receipt counts as missing.
_Missing_Receipt_After = 24 * 3600

# ################################################################################################################################
# ################################################################################################################################

def _new_config(**overrides:'any_') -> 'any_':
    """ One connection's configuration, the way the resend collection sees it.
    """
    out = Bunch()

    out['name'] = 'Partner AS4'
    out['as4_profile'] = AS4.Profile.EDelivery1
    out['as4_from_party'] = _From_Party
    out['as4_to_party'] = _To_Party
    out['as4_use_discovery'] = False
    out['as4_retry_max_attempts'] = 3
    out['as4_retry_interval'] = _Retry_Interval
    out['as4_missing_receipt_after'] = _Missing_Receipt_After

    out.update(overrides)

    return out

# ################################################################################################################################

def _record_send(message_id:'str', documents:'anylist') -> 'None':
    """ Records one delivery attempt the way an outgoing connection does.
    """
    result = SendResult()
    result.errors = []
    result.is_ok = False
    result.message_id = message_id
    result.conversation_id = 'conversation-' + message_id
    result.request_body = b'<Envelope/>'

    payloads:'anylist' = []

    for data, mime_type in documents:
        payloads.append(new_part(data, mime_type))

    audit_log = AuditLog(_Server_Name)

    record_message_sent(audit_log, _From_Party, _To_Party, result, payloads=payloads, service=_Service,
        action=_Action, final_recipient='0088:receiver', cid='cid-' + message_id)

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

    audit_log = AuditLog(_Server_Name)

    record_receipt_received(audit_log, _From_Party, _To_Party, receipt, ref_to_message_id=message_id)

# ################################################################################################################################

def _single_document() -> 'anylist':
    """ The payloads of a plain one-payload message.
    """
    out = [(_Payload, 'application/xml')]
    return out

# ################################################################################################################################

def _overdue_now() -> 'any_':
    """ A moment by which every attempt a test recorded is past its retry window.
    """
    out = utcnow() + timedelta(seconds=_Past_The_Window)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestReceptionAwarenessParameters:
    """ Which parameters one exchange is repeated under - the ones its network's profile prescribes,
    with whatever the connection itself configures on top.
    """

    def test_the_profile_prescribes_the_feature(self) -> 'None':

        pmode = new_edelivery1_pmode()
        awareness = pmode.reception_awareness

        assert awareness.is_enabled is True
        assert awareness.retry is True
        assert awareness.duplicate_detection is True

        assert awareness.retry_max_attempts == Default.Retry_Max_Attempts
        assert awareness.retry_interval_seconds == Default.Retry_Interval_Seconds
        assert awareness.missing_receipt_seconds == Default.Missing_Receipt_Seconds

# ################################################################################################################################

    def test_peppol_requires_duplicate_detection(self) -> 'None':

        pmode = new_peppol_pmode()
        awareness = pmode.reception_awareness

        assert awareness.is_enabled is True
        assert awareness.duplicate_detection is True

# ################################################################################################################################

    def test_the_connection_overrides_what_it_configures(self) -> 'None':

        config = _new_config(as4_retry_max_attempts=7, as4_retry_interval=60, as4_missing_receipt_after=3600)

        awareness = get_reception_awareness(config)

        assert awareness.retry_max_attempts == 7
        assert awareness.retry_interval_seconds == 60
        assert awareness.missing_receipt_seconds == 3600

# ################################################################################################################################

    def test_a_parameter_left_empty_keeps_the_profile_value(self) -> 'None':

        config = _new_config(as4_retry_max_attempts='', as4_retry_interval='', as4_missing_receipt_after='')

        awareness = get_reception_awareness(config)

        assert awareness.retry_max_attempts == Default.Retry_Max_Attempts
        assert awareness.retry_interval_seconds == Default.Retry_Interval_Seconds
        assert awareness.missing_receipt_seconds == Default.Missing_Receipt_Seconds

# ################################################################################################################################

    def test_a_connection_saved_without_the_parameters_keeps_the_profile_values(self) -> 'None':

        config = Bunch()
        config['name'] = 'Partner AS4'
        config['as4_profile'] = AS4.Profile.EDelivery1

        awareness = get_reception_awareness(config)

        assert awareness.retry is True
        assert awareness.retry_max_attempts == Default.Retry_Max_Attempts

# ################################################################################################################################

    def test_the_parameters_arrive_from_the_dashboard_as_text(self) -> 'None':

        config = _new_config(as4_retry_max_attempts='5', as4_retry_interval='120', as4_missing_receipt_after='7200')

        awareness = get_reception_awareness(config)

        assert awareness.retry_max_attempts == 5
        assert awareness.retry_interval_seconds == 120
        assert awareness.missing_receipt_seconds == 7200

# ################################################################################################################################

    def test_a_single_permitted_attempt_turns_the_repeats_off(self) -> 'None':

        config = _new_config(as4_retry_max_attempts=1)

        awareness = get_reception_awareness(config)

        assert awareness.retry is False

# ################################################################################################################################

    def test_the_parameters_reach_the_pmode_of_a_connection(self) -> 'None':

        pmode = new_edelivery1_pmode()
        config = _new_config(as4_retry_interval=45)

        apply_reception_awareness(pmode, config)

        assert pmode.reception_awareness.retry_interval_seconds == 45

# ################################################################################################################################
# ################################################################################################################################

class TestCollectCandidates:
    """ Which unanswered messages one run repeats the delivery of.
    """

    def test_an_unanswered_message_past_its_window_is_repeated(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())

        candidates = collect_candidates([_new_config()], _overdue_now(), _Server_Name)

        assert len(candidates) == 1

        candidate = candidates[0]

        assert candidate.connection_name == 'Partner AS4'
        assert candidate.from_party == _From_Party
        assert candidate.to_party == _To_Party
        assert candidate.message_id == 'msg-1'
        assert candidate.conversation_id == 'conversation-msg-1'
        assert candidate.service == _Service
        assert candidate.action == _Action
        assert candidate.final_recipient == '0088:receiver'
        assert candidate.attempt_count == 1

# ################################################################################################################################

    def test_a_message_inside_its_window_is_left_alone(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())

        candidates = collect_candidates([_new_config()], utcnow(), _Server_Name)

        assert candidates == []

# ################################################################################################################################

    def test_an_answered_message_is_not_repeated(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())
        _record_receipt('msg-1')

        candidates = collect_candidates([_new_config()], _overdue_now(), _Server_Name)

        assert candidates == []

# ################################################################################################################################

    def test_the_payloads_come_back_as_they_were_sent(self, audit_db:'None') -> 'None':

        documents = [(_Payload, 'application/xml'), (_Binary_Payload, 'application/pdf')]
        _record_send('msg-1', documents)

        candidates = collect_candidates([_new_config()], _overdue_now(), _Server_Name)
        candidate = candidates[0]

        assert len(candidate.documents) == 2

        first_data, first_content_type, _ = candidate.documents[0]
        second_data, second_content_type, _ = candidate.documents[1]

        assert first_data == _Payload
        assert first_content_type == 'application/xml'

        assert second_data == _Binary_Payload
        assert second_content_type == 'application/pdf'

# ################################################################################################################################

    def test_a_message_out_of_attempts_is_not_repeated(self, audit_db:'None') -> 'None':

        # Three attempts under a connection allowing three of them.
        _record_send('msg-1', _single_document())
        _record_send('msg-1', _single_document())
        _record_send('msg-1', _single_document())

        candidates = collect_candidates([_new_config()], _overdue_now(), _Server_Name)

        assert candidates == []

# ################################################################################################################################

    def test_every_attempt_is_counted(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())
        _record_send('msg-1', _single_document())

        reconciler = ReceiptReconciler(_Server_Name)

        assert count_attempts(reconciler, 'msg-1') == 2

# ################################################################################################################################

    def test_a_connection_with_the_repeats_off_repeats_nothing(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())

        config = _new_config(as4_retry_max_attempts=1)
        candidates = collect_candidates([config], _overdue_now(), _Server_Name)

        assert candidates == []

# ################################################################################################################################

    def test_a_message_with_no_connection_behind_it_is_left_to_the_operator(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())

        config = _new_config(as4_to_party='someone-else')
        candidates = collect_candidates([config], _overdue_now(), _Server_Name)

        assert candidates == []

# ################################################################################################################################

    def test_a_message_past_its_missing_receipt_window_is_no_longer_repeated(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())

        past_the_missing_receipt_window = utcnow() + timedelta(seconds=_Missing_Receipt_After + 100)
        candidates = collect_candidates([_new_config()], past_the_missing_receipt_window, _Server_Name)

        assert candidates == []

# ################################################################################################################################

    def test_one_run_repeats_at_most_one_batch(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())
        _record_send('msg-2', _single_document())
        _record_send('msg-3', _single_document())

        candidates = collect_candidates([_new_config()], _overdue_now(), _Server_Name, limit=2)

        assert len(candidates) == 2

# ################################################################################################################################
# ################################################################################################################################

class TestMissingReceipts:
    """ Which unanswered exchanges have stopped being a retry matter and become one to report.
    """

    def test_an_exchange_inside_its_window_is_not_reported(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())

        missing = collect_missing_receipts([_new_config()], _overdue_now(), _Server_Name)

        assert missing == []

# ################################################################################################################################

    def test_an_exchange_past_its_window_is_reported(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())

        past_the_window = utcnow() + timedelta(seconds=_Missing_Receipt_After + 100)
        missing = collect_missing_receipts([_new_config()], past_the_window, _Server_Name)

        assert len(missing) == 1

        pending = missing[0]

        assert pending.message_id == 'msg-1'
        assert pending.from_party == _From_Party
        assert pending.to_party == _To_Party
        assert pending.cid == 'cid-msg-1'

# ################################################################################################################################

    def test_an_answered_exchange_is_never_reported(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())
        _record_receipt('msg-1')

        past_the_window = utcnow() + timedelta(seconds=_Missing_Receipt_After + 100)
        missing = collect_missing_receipts([_new_config()], past_the_window, _Server_Name)

        assert missing == []

# ################################################################################################################################

    def test_an_exchange_whose_connection_is_gone_is_still_reported(self, audit_db:'None') -> 'None':

        _record_send('msg-1', _single_document())

        past_the_window = utcnow() + timedelta(seconds=Default.Missing_Receipt_Seconds + 100)
        missing = collect_missing_receipts([], past_the_window, _Server_Name)

        assert len(missing) == 1

# ################################################################################################################################
# ################################################################################################################################

class TestRepeatDelivery:
    """ What one repeat delivery is on the wire and what the receiving side makes of it.
    """

    def _new_candidate(self, result:'any_') -> 'any_':
        """ The repeat delivery of the message one send produced.
        """
        out = ResendCandidate()

        out.connection_name = 'Test Outgoing'
        out.from_party = _From_Party
        out.to_party = _To_Party
        out.message_id = result.message_id
        out.conversation_id = result.conversation_id
        out.service = 'urn:test:service'
        out.action = 'SubmitInvoice'
        out.attempt_count = 1
        out.documents = [(Payload, 'application/xml', 'payload-1')]

        return out

# ################################################################################################################################

    def test_the_repeat_goes_out_under_the_original_message_id(self, rsa_parties:'TestParties') -> 'None':

        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        channel = _make_channel(rsa_parties, 'edelivery1')
        _connect(wrapper, channel)

        first = wrapper.send(Test_CID, Payload)
        candidate = self._new_candidate(first)

        repeat = wrapper.resend(Test_CID, candidate)

        assert repeat.message_id == first.message_id
        assert repeat.conversation_id == first.conversation_id

# ################################################################################################################################

    def test_the_receiving_side_recognizes_the_repeat(self, rsa_parties:'TestParties') -> 'None':
        """ The repeat is the same message, so the receiving side delivers the payload once no matter
        how many attempts it took.
        """
        wrapper = _make_wrapper(rsa_parties, 'edelivery1')
        channel = _make_channel(rsa_parties, 'edelivery1')
        _connect(wrapper, channel)

        first = wrapper.send(Test_CID, Payload)
        candidate = self._new_candidate(first)

        _ = wrapper.resend(Test_CID, candidate)

        published = channel.server.pubsub_backend.published
        assert len(published) == 1

# ################################################################################################################################

    def test_the_repeat_is_recorded_as_an_attempt_of_its_own(self, rsa_parties:'TestParties', audit_db:'None') -> 'None':

        wrapper = _make_wrapper(rsa_parties, 'edelivery1', is_audit_log_active=True)
        channel = _make_channel(rsa_parties, 'edelivery1', is_audit_log_active=True)
        _connect(wrapper, channel)

        first = wrapper.send(Test_CID, Payload)
        candidate = self._new_candidate(first)

        _ = wrapper.resend(Test_CID, candidate)

        reconciler = ReceiptReconciler(wrapper.server.name)
        assert count_attempts(reconciler, first.message_id) == 2

# ################################################################################################################################

    def test_the_repeat_keeps_the_payload_of_the_attempt_it_repeats(self, rsa_parties:'TestParties',
        audit_db:'None') -> 'None':

        wrapper = _make_wrapper(rsa_parties, 'edelivery1', is_audit_log_active=True)
        channel = _make_channel(rsa_parties, 'edelivery1', is_audit_log_active=True)
        _connect(wrapper, channel)

        first = wrapper.send(Test_CID, Payload)
        candidate = self._new_candidate(first)

        _ = wrapper.resend(Test_CID, candidate)

        # The most recent message-sent event is the repeat, and what it stored is the payload
        # as it was submitted rather than the compressed bytes that went on the wire.
        events = _read_events()
        by_type = _by_event_type(events)

        details = loads(by_type[AuditEvent.Message_Sent]['data'])
        documents = decode_payload_documents(details)

        data, _, _ = documents[0]
        assert data == Payload

# ################################################################################################################################
# ################################################################################################################################
