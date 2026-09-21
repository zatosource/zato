# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What is outgoing FHIR connections' own on top of the shared scenarios - resources, paths, OperationOutcomes
# and the retries a direct save makes with the switch off.

# stdlib
from http.client import CREATED, TOO_MANY_REQUESTS, UNPROCESSABLE_ENTITY

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.audit_log.api import AuditEvent
from zato.common.pubsub.outgoing import Body_Mode_JSON, Key_Data, Key_Request

# Test support
from queue_delivery.client import edit_connection, get_client, get_queue, get_receiver, read, send, wait_for_audit_events, \
    wait_for_queue_depth, wait_for_queue_empty
from queue_delivery.dlq import invoke, wait_for_dlq_count
from queue_delivery.scenarios.browse import Get_Message, Kind_DLQ
from queue_delivery.scenarios.retry_policy import get_gaps
from queue_delivery.type_under_test import Attempts_Per_Round, Conn_DLQ_Keep, Conn_Orders, Conn_Plain, Orders_Max_Retries, \
    Orders_Sleep_Time
from _receiver import Outcome_Code, Outcome_Diagnostics
from _type import Connections, fhir_type, Request_Method, Request_Path, Resource_Type, Resource_Type_Key

# ################################################################################################################################
# ################################################################################################################################

_queue = HTTP_SOAP.Queue

_orders_conn = Connections[Conn_Orders]
_plain_conn = Connections[Conn_Plain]
_dlq_conn = Connections[Conn_DLQ_Keep]

# What a read arrives as and what it asks for - the test service reads this one resource
_read_method = 'GET'
_read_path = f'/{Resource_Type}/read-1'

# The id the endpoint gives the first resource it creates after a test starts
_first_created_id = 'created-1'

# The OperationOutcome a refused save is answered with
_operation_outcome_type = 'OperationOutcome'

# The details window of a FHIR message
_fact_method = 'Method'
_fact_path = 'Path'
_fact_content_type = 'Content type'
_fact_query_string = 'Query string'
_content_type = 'application/json'

# Scheduling slack of a measured wait
_slack = 0.2

# ################################################################################################################################
# ################################################################################################################################

def test_a_save_is_the_resource_posted_under_its_type() -> 'None':
    """ A save arrives as a POST under the path the resource's type names and comes back as the resource created.
    """
    client = get_client()

    result = send(client, _plain_conn, {'order_id': 'abc-1'})

    assert result['is_ok'] is True
    assert result['response'][Resource_Type_Key] == Resource_Type
    assert result['response']['id'] == _first_created_id
    assert result['response']['order_id'] == 'abc-1'

    requests = get_receiver(Conn_Plain).wait_for_requests(1)

    assert requests[0].method == Request_Method
    assert requests[0].path == '/' + Request_Path
    assert requests[0].status_code == CREATED

# ################################################################################################################################

def test_a_read_is_a_get_of_the_resource() -> 'None':
    """ A read arrives as a GET of the resource's own path and carries no body.
    """
    client = get_client()

    result = read(client, _plain_conn)

    assert result['is_ok'] is True
    assert result['response'][Resource_Type_Key] == Resource_Type

    requests = get_receiver(Conn_Plain).wait_for_requests(1)

    assert requests[0].method == _read_method
    assert requests[0].path == _read_path
    assert requests[0].body == ''

# ################################################################################################################################

def test_an_operation_outcome_is_a_rejection_and_the_resource_arrives_later() -> 'None':
    """ The endpoint answers with an OperationOutcome, the save says what it said, and the same resource arrives from the queue.
    """
    client = get_client()
    receiver = get_receiver(Conn_Orders)

    receiver.refuse_next(1)

    data = {'order_id': 'refused-1'}
    result = send(client, _orders_conn, data)

    assert result['is_in_queue'] is True
    assert result['error'] == f'HTTP {UNPROCESSABLE_ENTITY} {Outcome_Diagnostics}'
    assert result['response'][Resource_Type_Key] == _operation_outcome_type

    accepted = receiver.wait_for_accepted(1)
    assert len(accepted) == 1
    assert accepted[0].path == '/' + Request_Path
    assert fhir_type.body_of(accepted[0]) == data

    assert receiver.outcomes() == [UNPROCESSABLE_ENTITY, CREATED]

    queue = wait_for_queue_empty(client, _orders_conn)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_the_switch_off_answers_with_the_operation_outcome() -> 'None':
    """ With the switch off an OperationOutcome is the endpoint's answer to the caller, not something queued.
    """
    client = get_client()
    receiver = get_receiver(Conn_Plain)

    receiver.refuse_next(1)

    result = send(client, _plain_conn, {'order_id': 'plain-1'})

    assert result['raised'] == ''
    assert result['is_send_result'] is False
    assert result['is_ok'] is False
    assert Outcome_Diagnostics in result['response']['text']

    queue = get_queue(client, _plain_conn)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_the_switch_off_retries_a_direct_save_under_the_connections_policy() -> 'None':
    """ An endpoint that asks for the request to be made later is tried again as many times as the policy allows,
    with the policy's sleep between the attempts, and the save comes back with what the last attempt was answered with.
    """
    client = get_client()
    receiver = get_receiver(Conn_Orders)

    # The orders connection carries the retries, its switch goes off for this one test
    _ = edit_connection(client, _orders_conn, {_queue.Field_Use_Queue: False})

    try:
        receiver.answer_next([TOO_MANY_REQUESTS] * Orders_Max_Retries + [CREATED])

        result = send(client, _orders_conn, {'order_id': 'direct-retry-1'})

        assert result['raised'] == ''
        assert result['is_send_result'] is False
        assert result['is_ok'] is True
        assert result['response']['id'] == _first_created_id

        requests = receiver.wait_for_requests(Orders_Max_Retries + 1)
        assert receiver.outcomes() == [TOO_MANY_REQUESTS] * Orders_Max_Retries + [CREATED]

        gaps = get_gaps(receiver)
        assert len(gaps) == Orders_Max_Retries

        for gap in gaps:
            assert gap >= Orders_Sleep_Time - _slack, gaps

        assert len(requests) == Orders_Max_Retries + 1

    finally:
        _ = edit_connection(client, _orders_conn, {_queue.Field_Use_Queue: True})

    queue = get_queue(client, _orders_conn)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_no_retries_means_one_direct_attempt() -> 'None':
    """ A connection with no retries makes its one attempt and hands the answer to the caller.
    """
    client = get_client()
    receiver = get_receiver(Conn_Plain)

    receiver.answer_next([TOO_MANY_REQUESTS, CREATED])

    result = send(client, _plain_conn, {'order_id': 'no-retries-1'})

    assert result['raised'] == ''
    assert result['is_send_result'] is False
    assert result['is_ok'] is False

    requests = receiver.wait_for_requests(1)
    assert len(requests) == 1
    assert receiver.outcomes() == [TOO_MANY_REQUESTS]

# ################################################################################################################################

def test_the_audit_log_records_the_status_and_the_issue_code_of_each_attempt() -> 'None':
    """ Each response received from the queue carries its HTTP status and, for an OperationOutcome, the code of its issue.
    """
    client = get_client()
    receiver = get_receiver(Conn_Orders)

    receiver.answer_next([UNPROCESSABLE_ENTITY, UNPROCESSABLE_ENTITY])

    result = send(client, _orders_conn, {'order_id': 'audit-1'})
    assert result['is_in_queue'] is True

    _ = receiver.wait_for_accepted(1)

    received_events = wait_for_audit_events(result['cid'], AuditEvent.Response_Received, 3)
    assert len(received_events) == 3

    received_statuses = [event['status'].split(' ')[0] for event in received_events]
    assert received_statuses == [str(UNPROCESSABLE_ENTITY), str(UNPROCESSABLE_ENTITY), str(CREATED)]

    received_outcomes = [event['application_outcome'] for event in received_events]
    assert received_outcomes == [Outcome_Code, Outcome_Code, '']

    queue = wait_for_queue_depth(client, _orders_conn, 0)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_a_read_while_the_queue_holds_messages_is_answered_with_a_resource() -> 'None':
    """ A read goes to the wire and comes back with the resource read while a save waits in the queue.
    """
    client = get_client()
    receiver = get_receiver(Conn_Orders)

    receiver.refuse_all()

    queued = send(client, _orders_conn, {'order_id': 'waiting-1'})
    assert queued['is_in_queue'] is True

    receiver.accept_all()

    result = read(client, _orders_conn)

    assert result['is_ok'] is True
    assert result['response'][Resource_Type_Key] == Resource_Type
    assert result['response']['id'] == 'read-1'

    reads = receiver.reads()
    assert len(reads) == 1
    assert reads[0].is_accepted is True
    assert reads[0].path == _read_path

    queue = wait_for_queue_depth(client, _orders_conn, 0)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_the_destination_is_the_method_and_the_address_with_the_path() -> 'None':
    """ The delivery page shows a message as the method and the address its path is under, with the JSON of the resource
    as its body, its facts the four an HTTP request has and no invoke dialog, since the FHIR list page has none.
    """
    client = get_client()
    receiver = get_receiver(Conn_DLQ_Keep)

    receiver.refuse_next(Attempts_Per_Round)

    data = {'seq': 1}
    result = send(client, _dlq_conn, data)
    assert result['is_in_queue'] is True

    dlq = wait_for_dlq_count(client, _dlq_conn, 1)
    message = dlq['messages'][0]

    conn_id = get_queue(client, _dlq_conn)['conn_id']

    response = invoke(client, Get_Message, {
        'conn_type': fhir_type.conn_type,
        'conn_id': conn_id,
        'kind': Kind_DLQ,
        'msg_id': message['msg_id'],
    })

    address = f'http://127.0.0.1:{receiver.port}/{Request_Path}'
    assert response['destination'] == f'{Request_Method} {address}'

    facts = {fact['label']: fact['value'] for fact in response['facts']}
    assert facts[_fact_method] == Request_Method
    assert facts[_fact_path] == Request_Path
    assert facts[_fact_content_type] == _content_type
    assert facts[_fact_query_string] == {}

    assert response['body_mode'] == Body_Mode_JSON
    assert response['document'] == message['document']
    assert response['invoker'] is None

    assert fhir_type.body_of_envelope_data(response['document'][Key_Request][Key_Data]) == data

# ################################################################################################################################
# ################################################################################################################################
