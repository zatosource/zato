# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# How a channel's queue delivers to its service - the retries of a round, the rounds, the DLQ and what its rule does,
# and that a restart loses nothing, read through the browse service and the audit log as the outgoing scenarios do.

# stdlib
import time

# Zato
from zato.common.api import HTTP_SOAP, PubSub
from zato.common.audit_log.common import AuditEvent
from zato.common.pubsub.dlq import Header_Attempts, Header_Error, Header_Reason, Header_Rounds, Header_Source_Msg_ID, \
    Header_Source_Topic, Key_DLQ
from zato.common.pubsub.outgoing import get_outgoing_topic_name, Key_CID, Key_Conn_Name, Key_Data, Key_DLQ_Rounds, \
    Key_Msg_ID, Key_Request

# Test support
from queue_delivery.channel.client import accept_all, get_gaps, get_received, Refuse_Everything, set_behaviour, \
    wait_for_accepted, wait_for_received
from queue_delivery.channel.type_under_test import Attempts_Per_Round, Channel_DLQ_Discard, Channel_DLQ_Forward, \
    Channel_DLQ_Keep, Channel_DLQ_Retry, Channel_No_DLQ, Channel_No_Retries, Channel_Orders, DLQ_Retry_Channel_Rounds, \
    DLQ_Retry_Interval, Forward_Topic, Orders_Max_Retries, Orders_Sleep_Time, Refused_Error_Text
from queue_delivery.channel_scenarios.base import acceptance_of, ChannelScenarioBase, order, sequences_of
from queue_delivery.client import get_client, get_queue, is_broker_backend, restart_server, wait_for_audit_events, \
    wait_for_queue_empty
from queue_delivery.dlq import get_dlq, get_topic_messages, invoke, Retry_Message, run_dlq_rule, subscribe_topic, \
    wait_for_dlq_count

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry
_round_wait = PubSub.Delivery.Retry_Round_Wait

# Timing allowances for sleeps that are not exact
_slack = 0.3

# A message that waits for its next round arrives within this long
_round_timeout = _round_wait + 10.0

# How long a message with the DLQ off is watched staying at the head of its queue
_stay_seconds = _round_wait + 4

# The rule acts on a message once its interval passed
_past_interval_seconds = DLQ_Retry_Interval + 0.5

# ################################################################################################################################
# ################################################################################################################################

def wait_past_interval() -> 'None':
    """ Lets the retry interval of the DLQ channels pass.
    """
    time.sleep(_past_interval_seconds)

# ################################################################################################################################
# ################################################################################################################################

class DeliveryScenarios(ChannelScenarioBase):

    def _send_to_dlq(self, client:'AdminClient', key:'str', document:'anydict') -> 'anydict':
        """ Sends a request the target turns down until its attempts ran out and returns the DLQ message it became.
        """
        set_behaviour(client, Attempts_Per_Round)

        _ = self.ack_of(self.call(key, document))

        dlq = wait_for_dlq_count(client, self.conn(key), 1)
        assert len(dlq['messages']) == 1, dlq

        # The message lands in the DLQ a moment before its queue entry is acked
        queue = wait_for_queue_empty(client, self.conn(key))
        assert queue['depth'] == 0, queue

        out = dlq['messages'][0]
        return out

# ################################################################################################################################

    def test_the_retries_run_out_and_the_request_arrives_in_the_next_round(self) -> 'None':
        """ Two retries a second apart, then the round waits and the next one delivers.
        """
        client = get_client()
        set_behaviour(client, Orders_Max_Retries + 1)

        _ = self.ack_of(self.call(Channel_Orders, order(1)))

        accepted = wait_for_accepted(client, 1, timeout=_round_timeout)
        assert len(accepted) == 1

        received = get_received(client)
        assert acceptance_of(received) == [False, False, False, True], received

        gaps = get_gaps(received)

        assert gaps[0] >= Orders_Sleep_Time - _slack, gaps
        assert gaps[0] < _round_wait, gaps

        assert gaps[1] >= Orders_Sleep_Time - _slack, gaps
        assert gaps[1] < _round_wait, gaps

        # A queued request was never attempted on its way in, so each round opens with an attempt straight away
        assert gaps[2] >= _round_wait - _slack, gaps
        assert gaps[2] < _round_wait + Orders_Sleep_Time, gaps

        _ = wait_for_queue_empty(client, self.conn(Channel_Orders))

# ################################################################################################################################

    def test_no_retries_means_one_attempt_per_round(self) -> 'None':
        """ A channel that allows no retries still runs a waiting request once per round.
        """
        client = get_client()
        set_behaviour(client, 2)

        _ = self.ack_of(self.call(Channel_No_Retries, order(1)))

        accepted = wait_for_accepted(client, 1, timeout=_round_timeout * 2)
        assert len(accepted) == 1

        received = get_received(client)
        assert acceptance_of(received) == [False, False, True], received

        # Each round is the one attempt, a round's wait apart from the one before it
        gaps = get_gaps(received)
        assert gaps[0] >= _round_wait - _slack, gaps
        assert gaps[1] >= _round_wait - _slack, gaps

        _ = wait_for_queue_empty(client, self.conn(Channel_No_Retries))

# ################################################################################################################################

    def test_a_request_whose_attempts_ran_out_moves_to_the_dlq_and_the_next_one_gets_its_turn(self) -> 'None':
        """ Two requests, the first turned down for good - it moves to the DLQ with its header and the second is delivered.
        """
        client = get_client()
        conn_name = self.conn(Channel_DLQ_Keep)

        set_behaviour(client, Attempts_Per_Round)

        first = self.ack_of(self.call(Channel_DLQ_Keep, order(1)))
        second = self.ack_of(self.call(Channel_DLQ_Keep, order(2)))

        assert first['cid'] != second['cid']

        dlq = wait_for_dlq_count(client, conn_name, 1)
        assert len(dlq['messages']) == 1, dlq

        document = dlq['messages'][0]['document']
        header = document[Key_DLQ]

        assert header[Header_Reason] == PubSub.Outgoing.DLQ_Reason_Retries_Exhausted
        assert Refused_Error_Text in header[Header_Error], header[Header_Error]
        assert header[Header_Attempts] == Attempts_Per_Round
        assert header[Header_Rounds] == 0
        assert header[Header_Source_Topic] == get_outgoing_topic_name(self.t.conn_type, conn_name)

        # The DLQ message is a new one, the header names the queue message it was moved from
        assert header[Header_Source_Msg_ID] == document[Key_Msg_ID]
        assert header[Header_Source_Msg_ID] != dlq['messages'][0]['msg_id']

        assert document[Key_Conn_Name] == conn_name
        assert document[Key_DLQ_Rounds] == 0
        assert self.t.body_of_envelope_data(document[Key_Request][Key_Data]) == order(1)

        # The document carries the full cid of the first request, the ack quoted its public form
        cid = document[Key_CID]
        assert cid.startswith(first['cid']), (cid, first)

        # The move to the DLQ is in the audit log under that cid, with the error that caused it
        events = wait_for_audit_events(cid, AuditEvent.DLQ, 1)
        assert len(events) == 1
        assert events[0]['sub_key'] == dlq['sub_key']
        assert events[0]['msg_id'] == dlq['messages'][0]['msg_id']
        assert events[0]['endpoint'] == conn_name
        assert Refused_Error_Text in events[0]['status'], events[0]['status']

        accepted = wait_for_accepted(client, 1)
        assert sequences_of(accepted) == [2]

        assert len(get_received(client)) == Attempts_Per_Round + 1

        queue = wait_for_queue_empty(client, conn_name)
        assert queue['depth'] == 0

        # The DLQ is in the pub/sub database whichever backend the queue has
        if is_broker_backend():
            assert queue['messages'] == []
            assert len(get_dlq(client, conn_name)['messages']) == 1

# ################################################################################################################################

    def test_with_the_dlq_off_the_request_stays_at_the_head_and_nothing_overtakes_it(self) -> 'None':
        """ With the DLQ switch off a request whose attempts ran out stays where it is and the one behind it waits.
        """
        client = get_client()
        conn_name = self.conn(Channel_No_DLQ)

        set_behaviour(client, Refuse_Everything)

        try:
            _ = self.ack_of(self.call(Channel_No_DLQ, order(1)))
            _ = self.ack_of(self.call(Channel_No_DLQ, order(2)))

            received = wait_for_received(client, 3, timeout=_stay_seconds)
            assert len(received) >= 3

            for seq in sequences_of(received):
                assert seq == 1, received

            assert get_dlq(client, conn_name)['messages'] == []

            queue = get_queue(client, conn_name)
            assert queue['depth'] == 2, queue

        finally:
            accept_all(client)

        accepted = wait_for_accepted(client, 2, timeout=_round_timeout)
        assert sequences_of(accepted) == [1, 2]

        queue = wait_for_queue_empty(client, conn_name)
        assert queue['depth'] == 0

# ################################################################################################################################

    def test_the_rule_retries_a_dlq_message_as_many_times_as_allowed_and_then_leaves_it(self) -> 'None':
        """ Under the retry action the rule puts a message back into the queue once its interval passed, and after
        the allowed rounds it leaves the message alone until someone retries it by hand.
        """
        client = get_client()
        conn_name = self.conn(Channel_DLQ_Retry)

        message = self._send_to_dlq(client, Channel_DLQ_Retry, order(1))
        assert message['document'][Key_DLQ][Header_Rounds] == 0

        set_behaviour(client, Refuse_Everything)

        try:
            for rounds in range(1, DLQ_Retry_Channel_Rounds + 1):
                wait_past_interval()

                counts = run_dlq_rule(client)
                assert counts[conn_name] == 1, counts

                dlq = wait_for_dlq_count(client, conn_name, 1)
                message = dlq['messages'][0]
                assert message['document'][Key_DLQ_Rounds] == rounds, message

                _ = wait_for_queue_empty(client, conn_name)

            accept_all(client)
            wait_past_interval()

            counts = run_dlq_rule(client)
            assert conn_name not in counts, counts

            dlq = get_dlq(client, conn_name)
            assert len(dlq['messages']) == 1
            assert dlq['messages'][0]['msg_id'] == message['msg_id']

            before = len(get_received(client))
            _ = invoke(client, Retry_Message, {'sub_key': dlq['sub_key'], 'msg_id': message['msg_id']})

            received = wait_for_received(client, before + 1)
            assert received[-1]['is_accepted'] is True
            assert sequences_of(received[-1:]) == [1]

        finally:
            accept_all(client)

        _ = wait_for_queue_empty(client, conn_name)
        assert get_dlq(client, conn_name)['messages'] == []

# ################################################################################################################################

    def test_the_rule_forwards_a_dlq_message_to_the_topic_with_its_header(self) -> 'None':
        """ Under the forward action the rule publishes a due message to the topic the channel names.
        """
        client = get_client()
        conn_name = self.conn(Channel_DLQ_Forward)

        subscribe_topic(client, Forward_Topic)
        _ = get_topic_messages(client, Forward_Topic)

        message = self._send_to_dlq(client, Channel_DLQ_Forward, order(1))
        wait_past_interval()

        counts = run_dlq_rule(client)
        assert counts[conn_name] == 1, counts

        forwarded = get_topic_messages(client, Forward_Topic)
        assert len(forwarded) == 1

        assert forwarded[0]['document'] == message['document']
        assert Key_DLQ in forwarded[0]['document']

        assert get_dlq(client, conn_name)['messages'] == []

# ################################################################################################################################

    def test_the_rule_discards_a_dlq_message(self) -> 'None':
        """ Under the discard action a due message is taken out of the DLQ and goes nowhere else.
        """
        client = get_client()
        conn_name = self.conn(Channel_DLQ_Discard)

        subscribe_topic(client, Forward_Topic)
        _ = get_topic_messages(client, Forward_Topic)

        _ = self._send_to_dlq(client, Channel_DLQ_Discard, order(1))
        wait_past_interval()

        counts = run_dlq_rule(client)
        assert counts[conn_name] == 1, counts

        assert get_dlq(client, conn_name)['messages'] == []
        assert get_topic_messages(client, Forward_Topic) == []

# ################################################################################################################################

    def test_the_rule_leaves_a_kept_dlq_message_where_it_is(self) -> 'None':
        """ Under the keep action the rule does not touch the channel's DLQ at all.
        """
        client = get_client()
        conn_name = self.conn(Channel_DLQ_Keep)

        message = self._send_to_dlq(client, Channel_DLQ_Keep, order(1))
        wait_past_interval()

        counts = run_dlq_rule(client)
        assert conn_name not in counts, counts

        dlq = get_dlq(client, conn_name)
        assert len(dlq['messages']) == 1
        assert dlq['messages'][0]['msg_id'] == message['msg_id']

# ################################################################################################################################

    def test_a_request_queued_while_the_target_refuses_is_delivered_after_a_restart(self) -> 'None':
        """ A message in the queue survives the server's restart and arrives once the target accepts.
        """
        client = get_client()
        conn_name = self.conn(Channel_Orders)

        set_behaviour(client, Refuse_Everything)

        _ = self.ack_of(self.call(Channel_Orders, order(1)))

        # The first attempt was refused, so the message is in the queue when the server goes down
        received = wait_for_received(client, 1)
        assert received[0]['is_accepted'] is False

        restart_server()

        # A restart starts the services afresh, accepting
        accepted = wait_for_accepted(client, 1, timeout=_round_timeout)
        assert sequences_of(accepted) == [1]

        queue = wait_for_queue_empty(client, conn_name)
        assert queue['depth'] == 0

# ################################################################################################################################
# ################################################################################################################################
