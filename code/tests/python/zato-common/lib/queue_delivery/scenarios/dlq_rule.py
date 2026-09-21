# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The DLQ rule, on every pub/sub backend.

# stdlib
import time

# Zato
from zato.common.api import HTTP_SOAP, PubSub, SCHEDULER
from zato.common.defaults import default_cluster_id
from zato.common.pubsub.dlq import Header_Rounds, Key_DLQ
from zato.common.pubsub.outgoing import Key_DLQ_Rounds

# Test support
from queue_delivery.client import edit_connection, get_client, get_connection, wait_for_queue_empty
from queue_delivery.dlq import DLQ_Run, get_dlq, Get_Job_By_Name, get_topic_messages, invoke, Retry_Message, run_dlq_rule, \
    send_to_dlq, subscribe_topic
from queue_delivery.scenarios.base import ScenarioBase
from queue_delivery.type_under_test import Attempts_Per_Round, Conn_DLQ_Discard, Conn_DLQ_Forward, Conn_DLQ_Keep, \
    Conn_DLQ_Retry, DLQ_Retry_Conn_Rounds, DLQ_Retry_Interval, Forward_Topic

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_dlq = HTTP_SOAP.DLQ

_past_interval_seconds = DLQ_Retry_Interval + 0.5

# An interval no test outlasts
_long_interval_seconds = 600

# Longer than one round of the connection
_return_timeout_seconds = PubSub.Outgoing.Retry_Round_Wait + 10.0
_poll_interval_seconds = 0.1

# ################################################################################################################################
# ################################################################################################################################

def wait_past_interval() -> 'None':
    """ Waits until a message that just moved to the DLQ is old enough for the rule to act on it.
    """
    time.sleep(_past_interval_seconds)

# ################################################################################################################################

def wait_for_rounds(client:'AdminClient', conn_name:'str', rounds:'int') -> 'anydict':
    """ Blocks until a connection's DLQ holds one message that the rule has put back that many times, then returns it.
    """
    deadline = time.monotonic() + _return_timeout_seconds

    while time.monotonic() < deadline:

        dlq = get_dlq(client, conn_name)
        messages = dlq['messages']

        if len(messages) == 1 and messages[0]['document'][Key_DLQ][Header_Rounds] == rounds:
            out = messages[0]
            return out

        time.sleep(_poll_interval_seconds)

    raise AssertionError(f'Timed out waiting for a DLQ message of `{conn_name}` with {rounds} rounds')

# ################################################################################################################################
# ################################################################################################################################

class DLQRuleScenarios(ScenarioBase):

    def test_the_rule_is_a_scheduler_job_that_runs_every_minute(self) -> 'None':
        """ The server declares the rule's job on startup.
        """
        client = get_client()

        job = invoke(client, Get_Job_By_Name, {'cluster_id': default_cluster_id, 'name': PubSub.Outgoing.DLQ_Job_Name})

        assert job['service_name'] == DLQ_Run
        assert job['job_type'] == SCHEDULER.JOB_TYPE.INTERVAL_BASED
        assert job['is_active'] is True
        assert job['minutes'] == PubSub.Outgoing.DLQ_Job_Interval_Minutes

# ################################################################################################################################

    def test_retry_puts_the_message_back_as_many_times_as_allowed_and_then_leaves_it(self) -> 'None':
        """ Under the retry action the rule puts a message back into the queue once its interval passed.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Retry)
        conn_name = self.conn(Conn_DLQ_Retry)

        receiver.refuse_all()

        try:
            message = send_to_dlq(client, conn_name, receiver, {'seq': 1})
            assert message['document'][Key_DLQ][Header_Rounds] == 0

            for rounds in range(1, DLQ_Retry_Conn_Rounds + 1):
                wait_past_interval()

                counts = run_dlq_rule(client)
                assert counts[conn_name] == 1, counts

                message = wait_for_rounds(client, conn_name, rounds)
                assert message['document'][Key_DLQ_Rounds] == rounds

            receiver.accept_all()
            wait_past_interval()

            counts = run_dlq_rule(client)
            assert conn_name not in counts, counts

            dlq = get_dlq(client, conn_name)
            assert len(dlq['messages']) == 1
            assert dlq['messages'][0]['msg_id'] == message['msg_id']

            before = len(receiver.wait_for_requests(0))
            _ = invoke(client, Retry_Message, {'sub_key': dlq['sub_key'], 'msg_id': message['msg_id']})

            requests = receiver.wait_for_requests(before + 1)
            assert self.t.body_of(requests[-1]) == {'seq': 1}

            _ = wait_for_queue_empty(client, conn_name)
            assert get_dlq(client, conn_name)['messages'] == []

        finally:
            receiver.accept_all()

# ################################################################################################################################

    def test_a_message_the_rule_put_back_arrives_when_the_endpoint_accepts_it(self) -> 'None':
        """ The rule's retry is a delivery like any other.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Retry)
        conn_name = self.conn(Conn_DLQ_Retry)

        _ = send_to_dlq(client, conn_name, receiver, {'seq': 7})
        wait_past_interval()

        counts = run_dlq_rule(client)
        assert counts[conn_name] == 1, counts

        requests = receiver.wait_for_requests(Attempts_Per_Round + 1)
        assert len(requests) == Attempts_Per_Round + 1
        assert self.t.body_of(requests[-1]) == {'seq': 7}

        _ = wait_for_queue_empty(client, conn_name)
        assert get_dlq(client, conn_name)['messages'] == []

# ################################################################################################################################

    def test_forward_publishes_the_message_to_the_connection_topic_with_its_header(self) -> 'None':
        """ Under the forward action the rule publishes a due message to the topic the connection names.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Forward)
        conn_name = self.conn(Conn_DLQ_Forward)

        subscribe_topic(client, Forward_Topic)
        _ = get_topic_messages(client, Forward_Topic)

        message = send_to_dlq(client, conn_name, receiver, {'seq': 1})
        wait_past_interval()

        counts = run_dlq_rule(client)
        assert counts[conn_name] == 1, counts

        forwarded = get_topic_messages(client, Forward_Topic)
        assert len(forwarded) == 1

        assert forwarded[0]['document'] == message['document']
        assert Key_DLQ in forwarded[0]['document']

        assert get_dlq(client, conn_name)['messages'] == []

# ################################################################################################################################

    def test_discard_empties_the_dlq(self) -> 'None':
        """ Under the discard action a due message is taken out of the DLQ and goes nowhere else.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Discard)
        conn_name = self.conn(Conn_DLQ_Discard)

        subscribe_topic(client, Forward_Topic)
        _ = get_topic_messages(client, Forward_Topic)

        _ = send_to_dlq(client, conn_name, receiver, {'seq': 1})
        wait_past_interval()

        counts = run_dlq_rule(client)
        assert counts[conn_name] == 1, counts

        assert get_dlq(client, conn_name)['messages'] == []
        assert get_topic_messages(client, Forward_Topic) == []

# ################################################################################################################################

    def test_keep_leaves_the_message_where_it_is(self) -> 'None':
        """ Under the keep action the rule does not touch the connection's DLQ at all.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        message = send_to_dlq(client, conn_name, receiver, {'seq': 1})
        wait_past_interval()

        counts = run_dlq_rule(client)
        assert conn_name not in counts, counts

        dlq = get_dlq(client, conn_name)
        assert len(dlq['messages']) == 1
        assert dlq['messages'][0]['msg_id'] == message['msg_id']

# ################################################################################################################################

    def test_a_message_too_recent_for_the_interval_waits_for_a_later_run(self) -> 'None':
        """ The rule acts on a message only once its last round is at least the connection's interval behind it.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Discard)
        conn_name = self.conn(Conn_DLQ_Discard)

        _ = edit_connection(client, conn_name, {_dlq.Field_Retry_Interval: _long_interval_seconds})

        try:
            after = get_connection(client, conn_name)
            assert after[_dlq.Field_Retry_Interval] == _long_interval_seconds

            _ = send_to_dlq(client, conn_name, receiver, {'seq': 1})
            wait_past_interval()

            counts = run_dlq_rule(client)
            assert conn_name not in counts, counts
            assert len(get_dlq(client, conn_name)['messages']) == 1

        finally:
            _ = edit_connection(client, conn_name, {_dlq.Field_Retry_Interval: DLQ_Retry_Interval})

        counts = run_dlq_rule(client)
        assert counts[conn_name] == 1, counts
        assert get_dlq(client, conn_name)['messages'] == []

# ################################################################################################################################

    def test_an_edit_of_the_action_applies_to_the_next_run(self) -> 'None':
        """ An action changed through the server's edit service is what the very next run of the rule carries out.
        """
        client = get_client()
        receiver = self.receiver(Conn_DLQ_Keep)
        conn_name = self.conn(Conn_DLQ_Keep)

        _ = send_to_dlq(client, conn_name, receiver, {'seq': 1})
        _ = edit_connection(client, conn_name, {
            _dlq.Field_Action: _dlq.Action.Discard,
            _dlq.Field_Retry_Interval: DLQ_Retry_Interval,
        })

        try:
            after = get_connection(client, conn_name)
            assert after[_dlq.Field_Action] == _dlq.Action.Discard

            wait_past_interval()

            counts = run_dlq_rule(client)
            assert counts[conn_name] == 1, counts
            assert get_dlq(client, conn_name)['messages'] == []

        finally:
            _ = edit_connection(client, conn_name, {
                _dlq.Field_Action: _dlq.Action.Keep,
                _dlq.Field_Retry_Interval: _dlq.Default_Retry_Interval,
            })

# ################################################################################################################################
# ################################################################################################################################
