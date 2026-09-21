# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The harness itself holds - the server runs on the backend of the session, the connections carry what the template
# gave them, the endpoints record and answer as told and an edit goes through the server.

# SQLAlchemy
from sqlalchemy import func, select

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.sql.schema import message_table

# Test support
from queue_delivery.client import edit_connection, get_client, get_connection, get_pubsub_backend, get_pubsub_db_engine, \
    read, send, send_many
from queue_delivery.scenarios.base import ScenarioBase
from queue_delivery.type_under_test import Conn_DLQ_Forward, Conn_DLQ_Keep, Conn_No_DLQ, Conn_Orders, Conn_Plain, \
    DLQ_Conn_Max_Retries, DLQ_Retry_Interval, Forward_Topic, Orders_Max_Retries, Orders_Sleep_Time, TestConfig

# ################################################################################################################################
# ################################################################################################################################

_retry = HTTP_SOAP.Retry
_queue = HTTP_SOAP.Queue
_dlq = HTTP_SOAP.DLQ

# ################################################################################################################################
# ################################################################################################################################

class HarnessScenarios(ScenarioBase):

    def test_the_server_runs_on_the_backend_of_this_session(self) -> 'None':
        """ The server's pub/sub database is the one the session fixture started, and it can be reached from the test.
        """
        client = get_client()
        backend = TestConfig.backend

        server_side = get_pubsub_backend(client)

        assert server_side['type'] == backend.details['type']
        assert server_side['name'] == backend.details['name']

        engine = get_pubsub_db_engine()

        assert engine.url.get_backend_name() == backend.details['type']

        with engine.connect() as connection:
            _ = connection.execute(select(func.count()).select_from(message_table)).scalar()

# ################################################################################################################################

    def test_the_connections_carry_their_delivery_settings(self) -> 'None':
        """ Every connection of the template is in the server with the queue, retry and DLQ settings it was declared with.
        """
        client = get_client()

        plain = get_connection(client, self.conn(Conn_Plain))

        assert plain[_queue.Field_Use_Queue] is False
        assert plain[_dlq.Field_Use_DLQ] is _dlq.Default_Use_DLQ
        assert plain[_dlq.Field_Action] == _dlq.Default_Action

        orders = get_connection(client, self.conn(Conn_Orders))

        assert orders[_queue.Field_Use_Queue] is True
        assert orders[_retry.Field_Max_Retries] == Orders_Max_Retries
        assert orders[_retry.Field_Sleep_Time] == Orders_Sleep_Time
        assert orders[_dlq.Field_Use_DLQ] is False

        dlq_keep = get_connection(client, self.conn(Conn_DLQ_Keep))

        assert dlq_keep[_queue.Field_Use_Queue] is True
        assert dlq_keep[_retry.Field_Max_Retries] == DLQ_Conn_Max_Retries
        assert dlq_keep[_dlq.Field_Use_DLQ] is True
        assert dlq_keep[_dlq.Field_Action] == _dlq.Action.Keep

        no_dlq = get_connection(client, self.conn(Conn_No_DLQ))

        assert no_dlq[_queue.Field_Use_Queue] is True
        assert no_dlq[_dlq.Field_Use_DLQ] is False

        dlq_forward = get_connection(client, self.conn(Conn_DLQ_Forward))

        assert dlq_forward[_dlq.Field_Action] == _dlq.Action.Forward
        assert dlq_forward[_dlq.Field_Forward_To] == Forward_Topic
        assert dlq_forward[_dlq.Field_Retry_Interval] == DLQ_Retry_Interval

# ################################################################################################################################

    def test_a_send_reaches_the_endpoint(self) -> 'None':
        """ A send through a connection arrives at that connection's endpoint and at no other.
        """
        client = get_client()

        result = send(client, self.conn(Conn_Plain), {'order_id': 'abc-1'})

        assert result['is_ok'] is True

        requests = self.receiver(Conn_Plain).wait_for_requests(1)

        assert len(requests) == 1
        assert requests[0].is_read is False
        assert self.t.body_of(requests[0]) == {'order_id': 'abc-1'}

        assert self.receiver(Conn_Orders).requests == []

# ################################################################################################################################

    def test_sends_arrive_in_the_order_they_were_made(self) -> 'None':
        """ Messages sent one after another through one connection arrive at its endpoint in that order.
        """
        client = get_client()

        data_list = [{'seq': index} for index in range(5)]
        results = send_many(client, self.conn(Conn_Plain), data_list)

        assert len(results) == 5

        for result in results:
            assert result['is_ok'] is True

        requests = self.receiver(Conn_Plain).wait_for_requests(5)

        assert self.bodies(requests) == data_list

# ################################################################################################################################

    def test_a_read_goes_through_the_connection_too(self) -> 'None':
        """ A read through a connection arrives as one.
        """
        client = get_client()

        result = read(client, self.conn(Conn_Plain))

        assert result['is_ok'] is True

        requests = self.receiver(Conn_Plain).wait_for_requests(1)

        assert len(requests) == 1
        assert requests[0].is_read is True

# ################################################################################################################################

    def test_the_endpoint_answers_the_way_it_was_scripted(self) -> 'None':
        """ A run of scripted outcomes is handed out one per request, in order.
        """
        client = get_client()
        receiver = self.receiver(Conn_Plain)

        receiver.refuse_then_accept(1)

        first = send(client, self.conn(Conn_Plain), {'attempt': 1})
        second = send(client, self.conn(Conn_Plain), {'attempt': 2})
        third = send(client, self.conn(Conn_Plain), {'attempt': 3})

        assert first['is_ok'] is False
        assert second['is_ok'] is True
        assert third['is_ok'] is True

        assert receiver.acceptance() == [False, True, True]
        assert len(receiver.accepted()) == 2

# ################################################################################################################################

    def test_the_endpoint_refuses_and_accepts_again(self) -> 'None':
        """ An endpoint told to refuse rejects everything until it is told to accept again.
        """
        client = get_client()
        receiver = self.receiver(Conn_Plain)

        receiver.refuse_all()

        refused = send(client, self.conn(Conn_Plain), {'while': 'refusing'})

        assert refused['is_ok'] is False

        receiver.accept_all()

        accepted = send(client, self.conn(Conn_Plain), {'while': 'accepting'})

        assert accepted['is_ok'] is True

        assert len(receiver.requests) == 2
        assert len(receiver.accepted()) == 1

# ################################################################################################################################

    def test_an_edit_goes_through_the_server_and_keeps_the_rest(self) -> 'None':
        """ Changing one delivery field through the server's own edit service changes that field only.
        """
        client = get_client()
        conn_name = self.conn(Conn_Orders)

        before = get_connection(client, conn_name)

        _ = edit_connection(client, conn_name, {_retry.Field_Max_Retries: 5})

        after = get_connection(client, conn_name)

        assert after[_retry.Field_Max_Retries] == 5
        assert after[_queue.Field_Use_Queue] is True
        assert after[_retry.Field_Sleep_Time] == before[_retry.Field_Sleep_Time]
        assert after[_dlq.Field_Use_DLQ] is before[_dlq.Field_Use_DLQ]

        for field_name, value in before.items():
            if field_name != _retry.Field_Max_Retries:
                assert after[field_name] == value, field_name

        _ = edit_connection(client, conn_name, {_retry.Field_Max_Retries: before[_retry.Field_Max_Retries]})

        restored = get_connection(client, conn_name)

        assert restored[_retry.Field_Max_Retries] == before[_retry.Field_Max_Retries]

# ################################################################################################################################
# ################################################################################################################################
