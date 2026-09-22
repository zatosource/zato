# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What is outgoing REST connections' own on top of the shared scenarios - HTTP statuses, headers, paths and query strings.

# stdlib
from http.client import INTERNAL_SERVER_ERROR, OK, UNAUTHORIZED
from urllib.parse import urlencode

# Zato
from zato.common.audit_log.api import AuditEvent
from zato.common.pubsub.outgoing import Key_Headers, Key_Request

# Test support
from queue_delivery.client import as_dict, get_client, get_queue, get_receiver, read, send, wait_for_audit_events, \
    wait_for_queue_depth, wait_for_queue_empty
from queue_delivery.dlq import invoke, wait_for_dlq_count
from queue_delivery.scenarios.browse import Get_Message, Kind_DLQ
from queue_delivery.scenarios.retry_policy import get_gaps
from queue_delivery.type_under_test import Attempts_Per_Round, Conn_DLQ_Keep, Conn_Orders, Conn_Plain, Orders_Sleep_Time
from _type import Connections, Request_Method, URL_Paths

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.client import AdminClient
    from zato.common.typing_ import anydict, strdict

# ################################################################################################################################
# ################################################################################################################################

_orders_conn = Connections[Conn_Orders]
_plain_conn = Connections[Conn_Plain]
_dlq_conn = Connections[Conn_DLQ_Keep]

# The receiver records header names in lower case
_test_header = 'X-Test-Source'
_test_header_value = 'billing'
_recorded_test_header = _test_header.lower()
_recorded_cid_header = 'x-zato-cid'

_send_service = 'test.queue-delivery.send'

# Scheduling slack of a measured wait
_slack = 0.2

# ################################################################################################################################
# ################################################################################################################################

def test_a_send_is_a_post_to_the_connection_path() -> 'None':
    """ A send arrives as the method and the path the template declares.
    """
    client = get_client()

    result = send(client, _plain_conn, {'order_id': 'abc-1'})

    assert result['is_ok'] is True
    assert result['response']['status_code'] == OK

    requests = get_receiver(Conn_Plain).wait_for_requests(1)

    assert requests[0].method == Request_Method
    assert requests[0].path == URL_Paths[Conn_Plain]

# ################################################################################################################################

def test_a_read_is_a_get() -> 'None':
    """ A read arrives as a GET.
    """
    client = get_client()

    result = read(client, _plain_conn)

    assert result['is_ok'] is True
    assert result['response']['status_code'] == OK

    requests = get_receiver(Conn_Plain).wait_for_requests(1)

    assert requests[0].method == 'GET'

# ################################################################################################################################

def test_a_rejected_send_carries_the_status_and_the_headers_travel_with_the_message() -> 'None':
    """ The endpoint answers 500, the send says so, and the headers of the send arrive with the message from the queue.
    """
    client = get_client()
    receiver = get_receiver(Conn_Orders)

    receiver.answer_next([INTERNAL_SERVER_ERROR])

    headers = {_test_header: _test_header_value}
    result = send(client, _orders_conn, {'order_id': 'rejected-1'}, headers)

    assert result['is_in_queue'] is True
    assert result['error'].startswith(f'HTTP {INTERNAL_SERVER_ERROR}')
    assert result['response']['status_code'] == INTERNAL_SERVER_ERROR

    cid = result['cid']

    queue = get_queue(client, _orders_conn)

    if queue['messages']:
        request = queue['messages'][0]['envelope'][Key_Request]
        assert request[Key_Headers] == headers

    accepted = receiver.wait_for_accepted(1)
    assert len(accepted) == 1
    assert accepted[0].headers[_recorded_test_header] == _test_header_value
    assert accepted[0].headers[_recorded_cid_header] == cid

    assert receiver.outcomes() == [INTERNAL_SERVER_ERROR, OK]

    queue = wait_for_queue_empty(client, _orders_conn)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_the_switch_off_answers_with_the_status() -> 'None':
    """ With the switch off a 500 comes back as the response.
    """
    client = get_client()
    receiver = get_receiver(Conn_Plain)

    receiver.answer_next([INTERNAL_SERVER_ERROR])

    result = send(client, _plain_conn, {'order_id': 'plain-1'})

    assert result['is_send_result'] is False
    assert result['is_ok'] is False
    assert result['response']['status_code'] == INTERNAL_SERVER_ERROR

# ################################################################################################################################

def test_every_failure_counts_whatever_its_status() -> 'None':
    """ An endpoint that answers 401 is one failed attempt like any other.
    """
    client = get_client()
    receiver = get_receiver(Conn_Orders)

    receiver.answer_next([UNAUTHORIZED, OK])

    result = send(client, _orders_conn, {'order_id': 'unauthorized-once'})
    assert result['is_in_queue'] is True
    assert result['error'].startswith(f'HTTP {UNAUTHORIZED}')

    accepted = receiver.wait_for_accepted(1)
    assert len(accepted) == 1

    assert receiver.outcomes() == [UNAUTHORIZED, OK]

    gaps = get_gaps(receiver)
    assert gaps[0] >= Orders_Sleep_Time - _slack, gaps

    queue = wait_for_queue_depth(client, _orders_conn, 0)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_the_audit_log_records_the_status_of_each_attempt() -> 'None':
    """ Each response received from the queue carries its HTTP status in the audit log.
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

    queue = wait_for_queue_depth(client, _orders_conn, 0)
    assert queue['depth'] == 0

# ################################################################################################################################

def _send_with_params(client:'AdminClient', conn_name:'str', data:'anydict', params:'strdict') -> 'anydict':
    """ Sends one message with a query string, which is REST's own.
    """
    request = {
        'conn_name': conn_name,
        'data': data,
        'headers': {},
        'params': params,
    }

    out = as_dict(client.invoke(_send_service, request))
    return out

# ################################################################################################################################

def test_the_destination_is_the_method_and_the_address_with_the_query_string() -> 'None':
    """ The delivery page shows a message as the request it will make, the message's own query string included.
    """
    client = get_client()
    receiver = get_receiver(Conn_DLQ_Keep)

    receiver.refuse_next(Attempts_Per_Round)

    params = {'abc': '123', 'source': 'billing'}
    result = _send_with_params(client, _dlq_conn, {'seq': 1}, params)
    assert result['is_in_queue'] is True

    dlq = wait_for_dlq_count(client, _dlq_conn, 1)
    message = dlq['messages'][0]

    assert receiver.requests[0].query_string == urlencode(params)

    conn_id = get_queue(client, _dlq_conn)['conn_id']

    response = invoke(client, Get_Message, {
        'conn_type': 'rest',
        'conn_id': conn_id,
        'kind': Kind_DLQ,
        'msg_id': message['msg_id'],
    })

    address = f'http://127.0.0.1:{receiver.port}{URL_Paths[Conn_DLQ_Keep]}'
    assert response['destination'] == f'{Request_Method} {address}?{urlencode(params)}'

    facts = {fact['label']: fact['value'] for fact in response['facts']}
    assert facts['Method'] == Request_Method
    assert facts['Query string'] == params

    assert response['document'] == message['document']

# ################################################################################################################################
# ################################################################################################################################
