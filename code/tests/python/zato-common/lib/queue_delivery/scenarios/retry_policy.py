# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The queue retries as the connection's retry fields say, on every pub/sub backend.

# Zato
from zato.common.api import HTTP_SOAP, PubSub

# Test support
from queue_delivery.client import edit_connection, get_client, get_connection, send, wait_for_queue_empty
from queue_delivery.scenarios.base import ScenarioBase
from queue_delivery.type_under_test import Conn_No_Retries, Conn_Orders, Orders_Backoff_Multiplier, \
    Orders_Backoff_Threshold, Orders_Max_Retries, Orders_Sleep_Time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from queue_delivery.receiver import RecordingReceiver

    floatlist = list[float]

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry

_round_wait = PubSub.Outgoing.Retry_Round_Wait

# Scheduling slack of a measured wait
_slack = 0.2

# ################################################################################################################################
# ################################################################################################################################

def get_gaps(receiver:'RecordingReceiver') -> 'floatlist':
    """ How long passed between each request and the one before it, in the order the endpoint saw them.
    """
    out = []
    requests = receiver.requests

    for index in range(1, len(requests)):
        gap = requests[index].received_at - requests[index - 1].received_at
        out.append(gap)

    return out

# ################################################################################################################################

def restore_orders(client:'AdminClient', conn_name:'str') -> 'None':
    """ Puts the orders connection's retry fields back to what the template gave it.
    """
    _ = edit_connection(client, conn_name, {
        _retry.Field_Max_Retries: Orders_Max_Retries,
        _retry.Field_Sleep_Time: Orders_Sleep_Time,
        _retry.Field_Backoff_Threshold: Orders_Backoff_Threshold,
        _retry.Field_Backoff_Multiplier: Orders_Backoff_Multiplier,
    })

# ################################################################################################################################
# ################################################################################################################################

class RetryPolicyScenarios(ScenarioBase):

    def test_the_attempts_run_out_and_the_message_arrives_in_the_next_round(self) -> 'None':
        """ Two retries and an endpoint that turns down three attempts.
        """
        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        receiver.refuse_then_accept(3)

        result = send(client, conn_name, {'order_id': 'three-then-ok'})
        assert result['is_in_queue'] is True

        accepted = receiver.wait_for_accepted(1)
        assert len(accepted) == 1

        assert receiver.acceptance() == [False, False, False, True]

        gaps = get_gaps(receiver)

        assert gaps[0] >= Orders_Sleep_Time - _slack, gaps
        assert gaps[0] < _round_wait, gaps

        assert gaps[1] >= Orders_Sleep_Time - _slack, gaps
        assert gaps[1] < _round_wait, gaps

        assert gaps[2] >= _round_wait + Orders_Sleep_Time - _slack, gaps

        queue = wait_for_queue_empty(client, conn_name)
        assert queue['depth'] == 0

# ################################################################################################################################

    def test_no_retries_means_one_attempt_from_the_queue_per_round(self) -> 'None':
        """ A connection that allows no retries still tries a waiting message once per round.
        """
        client = get_client()
        receiver = self.receiver(Conn_No_Retries)
        conn_name = self.conn(Conn_No_Retries)

        receiver.refuse_then_accept(2)

        result = send(client, conn_name, {'order_id': 'no-retries'})
        assert result['is_in_queue'] is True

        accepted = receiver.wait_for_accepted(1)
        assert len(accepted) == 1

        assert receiver.acceptance() == [False, False, True]

        gaps = get_gaps(receiver)
        assert gaps[0] >= _retry.Default_Sleep_Time - _slack, gaps
        assert gaps[1] >= _round_wait + _retry.Default_Sleep_Time - _slack, gaps

        queue = wait_for_queue_empty(client, conn_name)
        assert queue['depth'] == 0

# ################################################################################################################################

    def test_the_multiplier_grows_the_sleep_and_the_threshold_ends_the_round(self) -> 'None':
        """ With a multiplier of two the second sleep is twice the first.
        """
        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        _ = edit_connection(client, conn_name, {
            _retry.Field_Max_Retries: 5,
            _retry.Field_Sleep_Time: 1,
            _retry.Field_Backoff_Threshold: 3,
            _retry.Field_Backoff_Multiplier: 2,
        })

        try:
            receiver.refuse_then_accept(3)

            result = send(client, conn_name, {'order_id': 'capped'})
            assert result['is_in_queue'] is True

            accepted = receiver.wait_for_accepted(1)
            assert len(accepted) == 1

            assert receiver.acceptance() == [False, False, False, True]

            gaps = get_gaps(receiver)

            assert gaps[0] >= 1 - _slack, gaps
            assert gaps[0] < 2, gaps

            assert gaps[1] >= 2 - _slack, gaps
            assert gaps[1] < _round_wait, gaps

            assert gaps[2] >= _round_wait + 1 - _slack, gaps

            queue = wait_for_queue_empty(client, conn_name)
            assert queue['depth'] == 0

        finally:
            restore_orders(client, conn_name)

# ################################################################################################################################

    def test_an_edit_of_the_retries_applies_to_the_next_message(self) -> 'None':
        """ Turning the retries off through the server's own edit service changes how the very next message is retried.
        """
        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        _ = edit_connection(client, conn_name, {_retry.Field_Max_Retries: 0})

        try:
            after = get_connection(client, conn_name)
            assert after[_retry.Field_Max_Retries] == 0

            receiver.refuse_then_accept(2)

            result = send(client, conn_name, {'order_id': 'edited'})
            assert result['is_in_queue'] is True

            accepted = receiver.wait_for_accepted(1)
            assert len(accepted) == 1

            assert receiver.acceptance() == [False, False, True]

            gaps = get_gaps(receiver)
            assert gaps[1] >= _round_wait + Orders_Sleep_Time - _slack, gaps

            queue = wait_for_queue_empty(client, conn_name)
            assert queue['depth'] == 0

        finally:
            restore_orders(client, conn_name)

# ################################################################################################################################
# ################################################################################################################################
