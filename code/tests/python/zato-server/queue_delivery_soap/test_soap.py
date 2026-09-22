# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What is outgoing SOAP connections' own on top of the shared scenarios - operations, envelopes, faults and pings.

# stdlib
from http.client import INTERNAL_SERVER_ERROR, OK

# Zato
from zato.common.audit_log.api import AuditEvent
from zato.common.pubsub.outgoing import Body_Mode_XML, Key_Data, Key_Request
from zato.common.soap.common import FaultCode

# Test support
from queue_delivery.client import get_client, get_queue, get_receiver, read, send, wait_for_audit_events, \
    wait_for_queue_depth, wait_for_queue_empty
from queue_delivery.dlq import invoke, wait_for_dlq_count
from queue_delivery.scenarios.browse import Get_Message, Kind_DLQ
from queue_delivery.type_under_test import Attempts_Per_Round, Conn_DLQ_Keep, Conn_Orders, Conn_Plain
from _receiver import Fault_Reason
from _type import Connections, document_from_xml, Request_Operation, Request_SOAP_Version, soap_type, URL_Paths

# ################################################################################################################################
# ################################################################################################################################

_orders_conn = Connections[Conn_Orders]
_plain_conn = Connections[Conn_Plain]
_dlq_conn = Connections[Conn_DLQ_Keep]

# What a send arrives as and what a ping arrives as
_delivery_method = 'POST'
_ping_method = 'HEAD'

# The details window of a SOAP message and the field of the invoke dialog its operation goes into
_fact_operation = 'Operation'
_fact_soap_headers = 'SOAP headers'
_operation_field = 'operation'

# ################################################################################################################################
# ################################################################################################################################

def test_a_send_is_the_operation_posted_to_the_connection_path() -> 'None':
    """ A send arrives as a POST whose envelope carries the operation, in the version the template declares.
    """
    client = get_client()

    result = send(client, _plain_conn, {'order_id': 'abc-1'})

    assert result['is_ok'] is True
    assert result['response']['is_fault'] is False

    requests = get_receiver(Conn_Plain).wait_for_requests(1)

    assert requests[0].method == _delivery_method
    assert requests[0].path == URL_Paths[Conn_Plain]
    assert requests[0].operation == Request_Operation
    assert requests[0].soap_version == Request_SOAP_Version
    assert requests[0].status_code == OK

# ################################################################################################################################

def test_a_read_is_a_ping() -> 'None':
    """ A read arrives as the connection's ping, which carries no envelope.
    """
    client = get_client()

    result = read(client, _plain_conn)

    assert result['is_ok'] is True
    assert result['response']['status_code'] == OK

    requests = get_receiver(Conn_Plain).wait_for_requests(1)

    assert requests[0].method == _ping_method
    assert requests[0].operation == ''
    assert requests[0].body == ''

# ################################################################################################################################

def test_a_fault_is_a_rejection_and_the_message_arrives_later() -> 'None':
    """ The endpoint answers with a fault, the send says which one, and the same operation arrives from the queue.
    """
    client = get_client()
    receiver = get_receiver(Conn_Orders)

    receiver.refuse_next(1)

    data = {'order_id': 'faulted-1'}
    result = send(client, _orders_conn, data)

    assert result['is_in_queue'] is True
    assert result['error'] == f'{FaultCode.Receiver} {Fault_Reason}'
    assert result['response']['is_fault'] is True

    accepted = receiver.wait_for_accepted(1)
    assert len(accepted) == 1
    assert accepted[0].operation == Request_Operation
    assert soap_type.body_of(accepted[0]) == data

    assert receiver.outcomes() == [INTERNAL_SERVER_ERROR, OK]

    queue = wait_for_queue_empty(client, _orders_conn)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_the_switch_off_answers_with_the_fault() -> 'None':
    """ With the switch off a fault is the endpoint's answer to the caller, not something queued.
    """
    client = get_client()
    receiver = get_receiver(Conn_Plain)

    receiver.refuse_next(1)

    result = send(client, _plain_conn, {'order_id': 'plain-1'})

    assert result['raised'] == ''
    assert result['is_send_result'] is False
    assert result['is_ok'] is False
    assert result['response']['is_fault'] is True
    assert result['response']['text'] == f'{FaultCode.Receiver} {Fault_Reason}'

# ################################################################################################################################

def test_the_audit_log_records_the_fault_of_each_attempt() -> 'None':
    """ Each response received from the queue carries its HTTP status and, for a fault, the fault's code.
    """
    client = get_client()
    receiver = get_receiver(Conn_Orders)

    receiver.answer_next([INTERNAL_SERVER_ERROR, INTERNAL_SERVER_ERROR])

    result = send(client, _orders_conn, {'order_id': 'audit-1'})
    assert result['is_in_queue'] is True

    _ = receiver.wait_for_accepted(1)

    received_events = wait_for_audit_events(result['cid'], AuditEvent.Response_Received, 3)
    assert len(received_events) == 3

    received_statuses = [event['status'].split(' ')[0] for event in received_events]
    assert received_statuses == [str(INTERNAL_SERVER_ERROR), str(INTERNAL_SERVER_ERROR), str(OK)]

    received_outcomes = [event['application_outcome'] for event in received_events]
    assert received_outcomes == [FaultCode.Receiver, FaultCode.Receiver, '']

    queue = wait_for_queue_depth(client, _orders_conn, 0)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_the_destination_is_the_operation_and_the_address() -> 'None':
    """ The delivery page shows a message as the operation it will invoke and where, with the XML of the operation element
    as its body, and the invoke dialog opens with the operation filled in.
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
        'conn_type': soap_type.conn_type,
        'conn_id': conn_id,
        'kind': Kind_DLQ,
        'msg_id': message['msg_id'],
    })

    address = f'http://127.0.0.1:{receiver.port}{URL_Paths[Conn_DLQ_Keep]}'
    assert response['destination'] == f'{Request_Operation} {address}'

    facts = {fact['label']: fact['value'] for fact in response['facts']}
    assert facts[_fact_operation] == Request_Operation
    assert facts[_fact_soap_headers] == {}

    assert response['body_mode'] == Body_Mode_XML
    assert response['document'] == message['document']

    assert document_from_xml(response['document'][Key_Request][Key_Data]) == data

    fields = response['invoker']['options']['fields']
    assert fields == [{'name': _operation_field, 'label': _fact_operation, 'value': Request_Operation}]

# ################################################################################################################################
# ################################################################################################################################
