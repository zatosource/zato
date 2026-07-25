# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta

# pytest
import pytest

# Zato
from zato.common.as4.audit import decode_payload_documents
from zato.common.as4.common import AS4Exception, Default, EbMSError, serves_channel
from zato.common.as4.mpc import claim_next, complete, count_waiting, PullState, queue_message, requeue_stale
from zato.common.as4.outbound import new_part
from zato.common.audit_log.api import AuditEvent, get_audit_engine
from zato.common.audit_log.common import as4_pull_queue_table
from zato.common.json_internal import loads
from zato.common.util.api import utcnow

from .test_audit import audit_db, _by_event_type, _read_events
from .test_server_connection import _connect, _make_channel, _make_wrapper, Payload, Test_CID

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist
    from .conftest import TestParties
    any_ = any_
    anylist = anylist
    TestParties = TestParties

# ################################################################################################################################
# ################################################################################################################################

# The channel the test messages wait on, plus a sub-channel of it.
Test_MPC = 'urn:test:mpc:eori:pl:1234'
Test_Sub_MPC = Test_MPC + '/priority'

# The two ends of a pull exchange - the message travels from the responder to the party pulling it.
_Own_Party = 'party-b'
_Partner_Party = 'party-a'

# The business information the test messages are queued under, which is what the loopback channel
# and connection are configured for.
_Service = 'urn:test:service'
_Action = 'SubmitInvoice'

Other_Payload = b'<Invoice xmlns="urn:test"><Total>200</Total></Invoice>'

# ################################################################################################################################
# ################################################################################################################################

# Keeps the imported fixture reachable under the name pytest resolves it by.
audit_db = audit_db

# ################################################################################################################################
# ################################################################################################################################

def _queue(data:'bytes'=Payload, mpc:'str'=Test_MPC) -> 'str':
    """ Queues one message on a channel the way a connection queues what a partner is to pull.
    """
    part = new_part(data)

    out = queue_message(mpc, _Own_Party, _Partner_Party, _Service, _Action, [part])
    return out

# ################################################################################################################################

def _find_row(message_id:'str') -> 'any_':
    """ Returns the queue row of one message, or None once the channel is done with it, so a test
    reads the state the store left it in.
    """
    engine = get_audit_engine()

    statement = as4_pull_queue_table.select()
    statement = statement.where(as4_pull_queue_table.c.message_id == message_id)

    with engine.connect() as connection:
        result = connection.execute(statement)
        row = result.first()

    if row is None:
        out = None
    else:
        out = row._asdict()

    return out

# ################################################################################################################################

def _read_row(message_id:'str') -> 'any_':
    """ Returns the queue row of one message, which the caller expects to still be there.
    """
    out = _find_row(message_id)

    assert out is not None
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestChannelNames:
    """ Which channel a request for one of them is served by.
    """

    def test_a_channel_serves_itself(self) -> 'None':
        assert serves_channel(Test_MPC, Test_MPC)

# ################################################################################################################################

    def test_a_channel_serves_its_sub_channels(self) -> 'None':
        assert serves_channel(Test_MPC, Test_Sub_MPC)

# ################################################################################################################################

    def test_a_channel_serves_no_other_channel(self) -> 'None':
        assert not serves_channel(Test_MPC, 'urn:test:mpc:eori:pl:9999')

# ################################################################################################################################

    def test_a_name_that_merely_starts_the_same_is_another_channel(self) -> 'None':
        assert not serves_channel(Test_MPC, Test_MPC + '-other')

# ################################################################################################################################

    def test_an_endpoint_with_no_channel_serves_none(self) -> 'None':
        assert not serves_channel('', Test_MPC)

# ################################################################################################################################
# ################################################################################################################################

class TestPullQueue:
    """ The store the responder side hands its messages over from.
    """

    def test_a_queued_message_waits_on_its_channel(self, audit_db:'any_') -> 'None':
        message_id = _queue()

        assert message_id
        assert count_waiting(Test_MPC) == 1

        row = _read_row(message_id)

        assert row['state'] == PullState.Waiting
        assert row['mpc'] == Test_MPC
        assert row['from_party'] == _Own_Party
        assert row['to_party'] == _Partner_Party
        assert row['pull_count'] == 0

# ################################################################################################################################

    def test_a_message_is_queued_under_its_own_conversation(self, audit_db:'any_') -> 'None':
        message_id = _queue()
        row = _read_row(message_id)

        # A message queued without a conversation of its own opens one, which is its own id.
        assert row['conversation_id'] == message_id

# ################################################################################################################################

    def test_an_empty_channel_hands_over_nothing(self, audit_db:'any_') -> 'None':
        assert claim_next(Test_MPC) is None

# ################################################################################################################################

    def test_a_claim_takes_the_message_that_waited_longest(self, audit_db:'any_') -> 'None':
        first = _queue()
        second = _queue(Other_Payload)

        claimed = claim_next(Test_MPC)

        assert claimed is not None
        assert claimed.message_id == first
        assert claimed.message_id != second
        assert claimed.pull_count == 1

# ################################################################################################################################

    def test_a_claimed_message_is_not_claimed_again(self, audit_db:'any_') -> 'None':
        first = _queue()
        second = _queue(Other_Payload)

        first_claimed = claim_next(Test_MPC)
        second_claimed = claim_next(Test_MPC)

        assert first_claimed is not None
        assert second_claimed is not None

        assert first_claimed.message_id == first
        assert second_claimed.message_id == second

        # Both are in flight now, so a third pull of the channel finds nothing.
        assert claim_next(Test_MPC) is None
        assert count_waiting(Test_MPC) == 0

# ################################################################################################################################

    def test_the_payloads_survive_the_queue(self, audit_db:'any_') -> 'None':
        _ = _queue()

        claimed = claim_next(Test_MPC)
        assert claimed is not None

        data, content_type, content_id = claimed.documents[0]

        assert data == Payload
        assert content_type == 'application/xml'
        assert content_id

# ################################################################################################################################

    def test_the_business_information_survives_the_queue(self, audit_db:'any_') -> 'None':
        _ = _queue()

        claimed = claim_next(Test_MPC)
        assert claimed is not None

        assert claimed.service == _Service
        assert claimed.action == _Action

# ################################################################################################################################

    def test_a_receipt_closes_the_row(self, audit_db:'any_') -> 'None':
        message_id = _queue()

        claimed = claim_next(Test_MPC)
        assert claimed is not None

        assert complete(message_id)

        # An acknowledged message leaves the channel altogether, its evidence being what remains.
        assert _find_row(message_id) is None
        assert claim_next(Test_MPC) is None

# ################################################################################################################################

    def test_a_receipt_for_a_pushed_message_closes_no_row(self, audit_db:'any_') -> 'None':
        _ = _queue()

        assert not complete('pushed-message@test')

# ################################################################################################################################

    def test_a_repeated_receipt_closes_nothing_a_second_time(self, audit_db:'any_') -> 'None':
        message_id = _queue()

        claimed = claim_next(Test_MPC)
        assert claimed is not None

        assert complete(message_id)
        assert not complete(message_id)

# ################################################################################################################################

    def test_an_unacknowledged_message_goes_back_on_its_channel(self, audit_db:'any_') -> 'None':
        message_id = _queue()

        claimed = claim_next(Test_MPC)
        assert claimed is not None
        assert count_waiting(Test_MPC) == 0

        # Well past the window the hand-over was given to be acknowledged in.
        later = utcnow() + timedelta(seconds=Default.Pull_Receipt_Seconds * 2)

        assert requeue_stale(later, Default.Pull_Receipt_Seconds) == 1
        assert count_waiting(Test_MPC) == 1

        # The partner asks again and receives the message it already had, under its own id.
        again = claim_next(Test_MPC)

        assert again is not None
        assert again.message_id == message_id
        assert again.pull_count == 2

# ################################################################################################################################

    def test_a_message_still_inside_its_window_stays_in_flight(self, audit_db:'any_') -> 'None':
        _ = _queue()

        claimed = claim_next(Test_MPC)
        assert claimed is not None

        assert requeue_stale(utcnow(), Default.Pull_Receipt_Seconds) == 0
        assert count_waiting(Test_MPC) == 0

# ################################################################################################################################

    def test_an_acknowledged_message_never_goes_back(self, audit_db:'any_') -> 'None':
        message_id = _queue()

        claimed = claim_next(Test_MPC)
        assert claimed is not None

        assert complete(message_id)

        later = utcnow() + timedelta(seconds=Default.Pull_Receipt_Seconds * 2)

        assert requeue_stale(later, Default.Pull_Receipt_Seconds) == 0
        assert count_waiting(Test_MPC) == 0

# ################################################################################################################################

    def test_each_channel_holds_its_own_messages(self, audit_db:'any_') -> 'None':
        _ = _queue()
        _ = _queue(Other_Payload, Test_Sub_MPC)

        assert count_waiting(Test_MPC) == 1
        assert count_waiting(Test_Sub_MPC) == 1

        claimed = claim_next(Test_Sub_MPC)

        assert claimed is not None
        assert claimed.documents[0][0] == Other_Payload

# ################################################################################################################################
# ################################################################################################################################

class TestQueueForPull:
    """ How a connection puts a message on its channel.
    """

    def test_the_message_lands_on_the_connection_channel(self, audit_db:'any_', rsa_parties:'TestParties') -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)

        message_id = wrapper.queue_for_pull(Test_CID, Payload)

        assert message_id
        assert count_waiting(Test_MPC) == 1

        row = _read_row(message_id)

        # The message goes out from the connection's own party to the partner that pulls it.
        assert row['from_party'] == 'party-a'
        assert row['to_party'] == 'party-b'
        assert row['service'] == _Service
        assert row['action'] == _Action

# ################################################################################################################################

    def test_a_named_channel_overrides_the_connection_one(self, audit_db:'any_', rsa_parties:'TestParties') -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)

        _ = wrapper.queue_for_pull(Test_CID, Payload, mpc=Test_Sub_MPC)

        assert count_waiting(Test_MPC) == 0
        assert count_waiting(Test_Sub_MPC) == 1

# ################################################################################################################################

    def test_queueing_over_an_inactive_connection_is_rejected(
        self,
        audit_db:'any_',
        rsa_parties:'TestParties',
        ) -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)
        wrapper.config['is_active'] = False

        with pytest.raises(AS4Exception) as exception_info:
            _ = wrapper.queue_for_pull(Test_CID, Payload)

        assert 'not active' in str(exception_info.value)

# ################################################################################################################################
# ################################################################################################################################

class TestPullResponder:
    """ The responder half of One-Way/Pull - a real pull request answered by a real channel over
    a loopback transport.
    """

    def test_a_pull_receives_the_queued_message(self, audit_db:'any_', rsa_parties:'TestParties') -> 'None':
        message_id = _queue()

        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)
        channel = _make_channel(rsa_parties, 'edelivery1', mpc=Test_MPC)
        _connect(wrapper, channel)

        result = wrapper.pull(Test_CID)

        assert result.is_ok
        assert result.has_message

        assert result.user_message is not None
        assert result.user_message.message_id == message_id
        assert result.user_message.service == _Service
        assert result.user_message.action == _Action

        # The message travelled from the responder to the party that asked for it.
        assert result.user_message.from_party == _Own_Party
        assert result.user_message.to_party == _Partner_Party

        # The payload is the one that was queued, decrypted and decompressed on the way in.
        assert result.payloads[0].data == Payload

# ################################################################################################################################

    def test_the_receipt_for_a_pulled_message_closes_its_row(
        self,
        audit_db:'any_',
        rsa_parties:'TestParties',
        ) -> 'None':
        message_id = _queue()

        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)
        channel = _make_channel(rsa_parties, 'edelivery1', mpc=Test_MPC)
        _connect(wrapper, channel)

        result = wrapper.pull(Test_CID)

        assert result.receipt_sent

        # The receipt travelled back to the same endpoint, and the channel that took it in
        # closed the row of the message it answers.
        assert _find_row(message_id) is None
        assert count_waiting(Test_MPC) == 0

# ################################################################################################################################

    def test_a_pull_of_an_empty_channel_is_answered_not_failed(
        self,
        audit_db:'any_',
        rsa_parties:'TestParties',
        ) -> 'None':
        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)
        channel = _make_channel(rsa_parties, 'edelivery1', mpc=Test_MPC)
        _connect(wrapper, channel)

        result = wrapper.pull(Test_CID)

        assert result.is_ok
        assert not result.has_message
        assert result.is_empty_channel
        assert result.payloads == []

        # The warning ebMS 3.0 defines for an empty channel is what said so.
        assert result.errors[0].error_code == EbMSError.Empty_Message_Partition

# ################################################################################################################################

    def test_a_second_pull_of_the_same_channel_finds_it_empty(
        self,
        audit_db:'any_',
        rsa_parties:'TestParties',
        ) -> 'None':
        _ = _queue()

        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)
        channel = _make_channel(rsa_parties, 'edelivery1', mpc=Test_MPC)
        _connect(wrapper, channel)

        first = wrapper.pull(Test_CID)
        second = wrapper.pull(Test_CID)

        assert first.has_message
        assert not second.has_message
        assert second.is_empty_channel

# ################################################################################################################################

    def test_a_pull_reaches_a_sub_channel_of_the_configured_one(
        self,
        audit_db:'any_',
        rsa_parties:'TestParties',
        ) -> 'None':
        _ = _queue(Other_Payload, Test_Sub_MPC)

        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)
        channel = _make_channel(rsa_parties, 'edelivery1', mpc=Test_MPC)
        _connect(wrapper, channel)

        result = wrapper.pull(Test_CID, mpc=Test_Sub_MPC)

        assert result.has_message
        assert result.payloads[0].data == Other_Payload

# ################################################################################################################################

    def test_a_channel_without_one_of_its_own_serves_no_pulls(
        self,
        audit_db:'any_',
        rsa_parties:'TestParties',
        ) -> 'None':
        _ = _queue()

        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)
        channel = _make_channel(rsa_parties, 'edelivery1')
        _connect(wrapper, channel)

        with pytest.raises(AS4Exception) as exception_info:
            _ = wrapper.pull(Test_CID)

        assert EbMSError.Feature_Not_Supported in str(exception_info.value)

        # Nothing was handed over, so the message is still waiting.
        assert count_waiting(Test_MPC) == 1

# ################################################################################################################################

    def test_a_pull_of_an_unknown_channel_is_refused(self, audit_db:'any_', rsa_parties:'TestParties') -> 'None':
        _ = _queue()

        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)
        channel = _make_channel(rsa_parties, 'edelivery1', mpc=Test_MPC)
        _connect(wrapper, channel)

        with pytest.raises(AS4Exception) as exception_info:
            _ = wrapper.pull(Test_CID, mpc='urn:test:mpc:eori:pl:9999')

        assert EbMSError.Value_Not_Recognized in str(exception_info.value)
        assert count_waiting(Test_MPC) == 1

# ################################################################################################################################
# ################################################################################################################################

class TestHandOverEvidence:
    """ What one hand-over leaves behind, which is what a dispute over a pulled message is settled
    from and what keeps the push retries away from a message the partner is to ask for.
    """

    def test_the_hand_over_is_recorded_as_a_message_that_went_out(
        self,
        audit_db:'any_',
        rsa_parties:'TestParties',
        ) -> 'None':
        message_id = _queue()

        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)
        channel = _make_channel(rsa_parties, 'edelivery1', is_audit_log_active=True, mpc=Test_MPC)
        _connect(wrapper, channel)

        result = wrapper.pull(Test_CID)
        assert result.has_message

        events = _by_event_type(_read_events())
        sent = events[AuditEvent.Message_Sent]

        assert sent['msg_id'] == message_id
        assert sent['object_name'] == f'{_Own_Party}:{_Partner_Party}'

        details = loads(sent['data'])

        assert details['service'] == _Service
        assert details['action'] == _Action

        # The payload is stored as it was submitted for pulling, not as the wire carried it.
        documents = decode_payload_documents(details)
        assert documents[0][0] == Payload

# ################################################################################################################################

    def test_the_hand_over_says_it_was_a_pull(self, audit_db:'any_', rsa_parties:'TestParties') -> 'None':
        _ = _queue()

        wrapper = _make_wrapper(rsa_parties, 'edelivery1', mpc=Test_MPC)
        channel = _make_channel(rsa_parties, 'edelivery1', is_audit_log_active=True, mpc=Test_MPC)
        _connect(wrapper, channel)

        _ = wrapper.pull(Test_CID)

        events = _by_event_type(_read_events())
        details = loads(events[AuditEvent.Message_Sent]['data'])

        # This is what tells the reception awareness retries to leave the message alone - an
        # unacknowledged pull message goes back on its channel rather than out through a connection.
        assert details['is_pull'] is True

# ################################################################################################################################
# ################################################################################################################################
