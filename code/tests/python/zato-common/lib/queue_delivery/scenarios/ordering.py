# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# A message never overtakes the ones waiting before it, on every pub/sub backend.

# pytest
import pytest

# Zato
from zato.common.pubsub.outgoing import Attempts_Direct, Attempts_None, Key_Attempts, Key_Data, Key_Request

# Test support
from queue_delivery.client import get_client, get_queue, is_broker_backend, restart_server, send, send_many, \
    wait_for_queue_depth
from queue_delivery.scenarios.base import ScenarioBase
from queue_delivery.type_under_test import Conn_Orders

# ################################################################################################################################
# ################################################################################################################################

_restart_skip_reason = 'The depth of a queue in a broker is not read back at startup'

# ################################################################################################################################
# ################################################################################################################################

class OrderingScenarios(ScenarioBase):

    def test_a_send_behind_a_waiting_message_does_not_touch_the_wire(self) -> 'None':
        """ The first message is turned down and waits, the second is sent while it does.
        """
        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        receiver.refuse_all()

        first = send(client, conn_name, {'seq': 1})

        assert first['is_in_queue'] is True

        second = send(client, conn_name, {'seq': 2})

        assert second['is_ok'] is False
        assert second['is_in_queue'] is True
        assert second['error'] == ''
        assert second['response'] is None

        for body in self.bodies(receiver.requests):
            assert body == {'seq': 1}

        queue = get_queue(client, conn_name)
        assert queue['depth'] == 2

        if not is_broker_backend():

            attempts = {}
            for message in queue['messages']:
                envelope = message['envelope']
                body = self.t.body_of_envelope_data(envelope[Key_Request][Key_Data])
                attempts[body['seq']] = envelope[Key_Attempts]

            assert attempts == {1: Attempts_Direct, 2: Attempts_None}

        receiver.accept_all()

        accepted = receiver.wait_for_accepted(2)
        assert self.bodies(accepted) == [{'seq': 1}, {'seq': 2}]

        queue = wait_for_queue_depth(client, conn_name, 0)
        assert queue['depth'] == 0

# ################################################################################################################################

    def test_many_sends_behind_a_waiting_message_arrive_in_order(self) -> 'None':
        """ A run of sends while the queue holds a message all go to the queue and all arrive in the order they were made.
        """
        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        receiver.refuse_all()

        first = send(client, conn_name, {'seq': 0})
        assert first['is_in_queue'] is True

        data_list = [{'seq': index} for index in range(1, 6)]
        results = send_many(client, conn_name, data_list)

        for result in results:
            assert result['is_ok'] is False
            assert result['is_in_queue'] is True

        for body in self.bodies(receiver.requests):
            assert body == {'seq': 0}

        queue = get_queue(client, conn_name)
        assert queue['depth'] == 6

        receiver.accept_all()

        accepted = receiver.wait_for_accepted(6)
        assert self.bodies(accepted) == [{'seq': index} for index in range(6)]

        queue = wait_for_queue_depth(client, conn_name, 0)
        assert queue['depth'] == 0

# ################################################################################################################################

    def test_a_send_after_the_queue_drained_goes_to_the_wire_again(self) -> 'None':
        """ Once the queue is empty again, the next send is a direct one.
        """
        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        receiver.refuse_all()

        waiting = send(client, conn_name, {'seq': 'waiting'})
        assert waiting['is_in_queue'] is True

        receiver.accept_all()

        _ = receiver.wait_for_accepted(1)

        queue = wait_for_queue_depth(client, conn_name, 0)
        assert queue['depth'] == 0

        receiver.clear()

        direct = send(client, conn_name, {'seq': 'direct'})

        assert direct['is_ok'] is True
        assert direct['is_in_queue'] is False

        assert self.bodies(receiver.requests) == [{'seq': 'direct'}]

        queue = get_queue(client, conn_name)
        assert queue['depth'] == 0
        assert queue['messages'] == []

# ################################################################################################################################

    def test_a_restart_reads_the_depth_back_and_nothing_overtakes_the_waiting_messages(self) -> 'None':
        """ Two messages wait when the server stops.
        """
        if is_broker_backend():
            pytest.skip(_restart_skip_reason)

        client = get_client()
        receiver = self.receiver(Conn_Orders)
        conn_name = self.conn(Conn_Orders)

        receiver.refuse_all()

        first = send(client, conn_name, {'seq': 1})
        second = send(client, conn_name, {'seq': 2})

        assert first['is_in_queue'] is True
        assert second['is_in_queue'] is True

        queue = get_queue(client, conn_name)
        assert queue['depth'] == 2

        restart_server()

        client = get_client()

        queue = get_queue(client, conn_name)
        assert queue['depth'] == 2
        assert len(queue['messages']) == 2

        third = send(client, conn_name, {'seq': 3})

        assert third['is_ok'] is False
        assert third['is_in_queue'] is True

        for body in self.bodies(receiver.requests):
            assert body == {'seq': 1}

        queue = get_queue(client, conn_name)
        assert queue['depth'] == 3

        receiver.accept_all()

        accepted = receiver.wait_for_accepted(3)
        assert self.bodies(accepted) == [{'seq': 1}, {'seq': 2}, {'seq': 3}]

        queue = wait_for_queue_depth(client, conn_name, 0)
        assert queue['depth'] == 0

# ################################################################################################################################
# ################################################################################################################################
