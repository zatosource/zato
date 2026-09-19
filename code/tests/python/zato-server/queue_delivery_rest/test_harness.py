# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import INTERNAL_SERVER_ERROR, OK
from json import loads

# sqlalchemy
from sqlalchemy import func, select

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.pubsub.sql.schema import message_table

# local
from _helpers import Connections, edit_connection, get_client, get_connection, get_pubsub_backend, get_pubsub_db_engine, \
    get_receiver, read, send, send_many, TestConfig

# ################################################################################################################################
# ################################################################################################################################

_queue = HTTP_SOAP.Queue
_dlq = HTTP_SOAP.DLQ
_retry = HTTP_SOAP.Retry

# ################################################################################################################################
# ################################################################################################################################

def test_the_server_runs_its_pubsub_on_the_backend_under_test() -> 'None':
    """ The server's pub/sub backend runs on the database it was started against.
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

def test_the_connections_carry_their_delivery_settings() -> 'None':
    """ Every connection of the template is in the server with the queue, retry and DLQ settings it was declared with.
    """
    client = get_client()

    plain = get_connection(client, Connections['plain'])

    assert plain[_queue.Field_Use_Queue] is False
    assert plain[_dlq.Field_Use_DLQ] is _dlq.Default_Use_DLQ
    assert plain[_dlq.Field_Action] == _dlq.Default_Action

    orders = get_connection(client, Connections['orders'])

    assert orders[_queue.Field_Use_Queue] is True
    assert orders[_retry.Field_Max_Retries] == 2
    assert orders[_retry.Field_Sleep_Time] == 1
    assert orders[_dlq.Field_Use_DLQ] is False

    dlq_keep = get_connection(client, Connections['dlq_keep'])

    assert dlq_keep[_queue.Field_Use_Queue] is True
    assert dlq_keep[_retry.Field_Max_Retries] == 1
    assert dlq_keep[_dlq.Field_Use_DLQ] is True
    assert dlq_keep[_dlq.Field_Action] == _dlq.Action.Keep

    no_dlq = get_connection(client, Connections['no_dlq'])

    assert no_dlq[_queue.Field_Use_Queue] is True
    assert no_dlq[_dlq.Field_Use_DLQ] is False

    dlq_forward = get_connection(client, Connections['dlq_forward'])

    assert dlq_forward[_dlq.Field_Action] == _dlq.Action.Forward
    assert dlq_forward[_dlq.Field_Forward_To] == 'test.queue-delivery.forwarded'
    assert dlq_forward[_dlq.Field_Retry_Interval] == 1

# ################################################################################################################################

def test_a_send_reaches_the_endpoint() -> 'None':
    """ A send through a connection arrives at that connection's endpoint.
    """
    client = get_client()

    result = send(client, Connections['plain'], {'order_id': 'abc-1'})

    assert result['is_ok'] is True
    assert result['response']['status_code'] == OK

    requests = get_receiver('plain').wait_for_requests(1)

    assert len(requests) == 1
    assert requests[0].method == 'POST'
    assert requests[0].path == '/api/plain'
    assert loads(requests[0].body) == {'order_id': 'abc-1'}

    assert get_receiver('orders').requests == []

# ################################################################################################################################

def test_sends_arrive_in_the_order_they_were_made() -> 'None':
    """ Messages sent one after another through one connection arrive at its endpoint in that order.
    """
    client = get_client()

    data_list = [{'seq': index} for index in range(5)]
    results = send_many(client, Connections['plain'], data_list)

    assert len(results) == 5

    for result in results:
        assert result['is_ok'] is True

    requests = get_receiver('plain').wait_for_requests(5)

    bodies = [loads(request.body) for request in requests]

    assert bodies == data_list

# ################################################################################################################################

def test_a_read_goes_through_the_connection_too() -> 'None':
    """ A GET through a connection arrives as one.
    """
    client = get_client()

    result = read(client, Connections['plain'])

    assert result['is_ok'] is True

    requests = get_receiver('plain').wait_for_requests(1)

    assert len(requests) == 1
    assert requests[0].method == 'GET'

# ################################################################################################################################

def test_the_endpoint_answers_the_way_it_was_scripted() -> 'None':
    """ A run of scripted statuses is handed out one per request, in order.
    """
    client = get_client()
    receiver = get_receiver('plain')

    receiver.answer_next([INTERNAL_SERVER_ERROR, OK])

    first = send(client, Connections['plain'], {'attempt': 1})
    second = send(client, Connections['plain'], {'attempt': 2})
    third = send(client, Connections['plain'], {'attempt': 3})

    assert first['is_ok'] is False
    assert first['response']['status_code'] == INTERNAL_SERVER_ERROR

    assert second['is_ok'] is True
    assert third['is_ok'] is True

    statuses = [request.status_code for request in receiver.requests]

    assert statuses == [INTERNAL_SERVER_ERROR, OK, OK]
    assert len(receiver.accepted()) == 2

# ################################################################################################################################

def test_the_endpoint_refuses_and_accepts_again() -> 'None':
    """ An endpoint told to refuse rejects everything until it is told to accept again.
    """
    client = get_client()
    receiver = get_receiver('plain')

    receiver.refuse_all()

    refused = send(client, Connections['plain'], {'while': 'refusing'})

    assert refused['is_ok'] is False

    receiver.accept_all()

    accepted = send(client, Connections['plain'], {'while': 'accepting'})

    assert accepted['is_ok'] is True

    assert len(receiver.requests) == 2
    assert len(receiver.accepted()) == 1

# ################################################################################################################################

def test_an_edit_goes_through_the_server_and_keeps_the_rest() -> 'None':
    """ Changing one delivery field through the server's own edit service changes that field only.
    """
    client = get_client()
    conn_name = Connections['orders']

    before = get_connection(client, conn_name)

    _ = edit_connection(client, conn_name, {_retry.Field_Max_Retries: 5})

    after = get_connection(client, conn_name)

    assert after[_retry.Field_Max_Retries] == 5
    assert after[_queue.Field_Use_Queue] is True
    assert after[_retry.Field_Sleep_Time] == before[_retry.Field_Sleep_Time]
    assert after[_dlq.Field_Use_DLQ] is before[_dlq.Field_Use_DLQ]
    assert after['host'] == before['host']
    assert after['url_path'] == before['url_path']

    _ = edit_connection(client, conn_name, {_retry.Field_Max_Retries: before[_retry.Field_Max_Retries]})

    restored = get_connection(client, conn_name)

    assert restored[_retry.Field_Max_Retries] == before[_retry.Field_Max_Retries]

# ################################################################################################################################
# ################################################################################################################################
