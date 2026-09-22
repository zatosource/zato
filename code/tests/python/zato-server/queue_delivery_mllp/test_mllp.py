# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What is outgoing MLLP connections' own on top of the shared scenarios - acknowledgments and their codes, a ping
# that is never a delivery and the retries a direct send makes with the switch off when no acknowledgment comes back.

# Zato
from zato.common.api import HTTP_SOAP
from zato.common.audit_log.api import AuditEvent
from zato.common.pubsub.outgoing import Body_Mode_HL7, Key_Data, Key_Request

# Test support
from queue_delivery.client import edit_connection, get_client, get_queue, get_receiver, read, send, wait_for_audit_events, \
    wait_for_queue_depth
from queue_delivery.dlq import invoke, wait_for_dlq_count
from queue_delivery.scenarios.browse import Get_Message, Kind_DLQ
from queue_delivery.scenarios.retry_policy import get_gaps
from queue_delivery.type_under_test import Attempts_Per_Round, Conn_DLQ_Keep, Conn_Orders, Conn_Plain, Orders_Max_Retries, \
    Orders_Sleep_Time
from _receiver import Accept_Code, Drop_Outcome, Ping_Outcome, Refuse_Code
from _services import control_id_of_message
from _type import Connections, Destination_Prefix, mllp_type

# ################################################################################################################################
# ################################################################################################################################

_queue = HTTP_SOAP.Queue

_orders_conn = Connections[Conn_Orders]
_plain_conn = Connections[Conn_Plain]
_dlq_conn = Connections[Conn_DLQ_Keep]

# The segment an acknowledgment answers with and the field of its code
_msa_prefix = 'MSA|'

# Scheduling slack of a measured wait
_slack = 0.2

# ################################################################################################################################
# ################################################################################################################################

def _msa_of(ack_text:'str') -> 'list[str]':
    """ The fields of the MSA segment of an acknowledgment.
    """
    for segment in ack_text.split('\r'):
        if segment.startswith(_msa_prefix):
            out = segment.split('|')
            return out

    raise ValueError(f'No MSA segment in `{ack_text!r}`')

# ################################################################################################################################
# ################################################################################################################################

def test_a_send_comes_back_with_the_acknowledgment() -> 'None':
    """ A send with the switch off comes back with the acknowledgment as the connection read it - its code, that it was
    accepted and the ER7 text, whose MSA names the control id of the message sent.
    """
    client = get_client()

    result = send(client, _plain_conn, {'order_id': 'abc-1'})

    assert result['is_ok'] is True
    assert result['is_send_result'] is False

    ack = result['response']
    assert ack['ack_code'] == Accept_Code
    assert ack['is_accepted'] is True
    assert ack['error_text'] == ''

    requests = get_receiver(Conn_Plain).wait_for_requests(1)
    assert requests[0].ack_code == Accept_Code

    msa = _msa_of(ack['ack_text'])
    assert msa[1] == Accept_Code
    assert msa[2] == control_id_of_message(requests[0].body)

# ################################################################################################################################

def test_a_negative_acknowledgment_is_a_rejection_and_the_message_arrives_later() -> 'None':
    """ An AE turns a send down - the message goes to the queue with the code as its error and the acknowledgment as the
    response, and it arrives once the receiving system accepts again.
    """
    client = get_client()
    receiver = get_receiver(Conn_Orders)

    receiver.refuse_next(1)

    result = send(client, _orders_conn, {'order_id': 'nack-1'})

    assert result['is_ok'] is False
    assert result['is_in_queue'] is True
    assert result['error'].startswith(Refuse_Code), result['error']

    ack = result['response']
    assert ack['ack_code'] == Refuse_Code
    assert ack['is_accepted'] is False

    accepted = receiver.wait_for_accepted(1)
    assert mllp_type.body_of(accepted[0]) == {'order_id': 'nack-1'}

    assert receiver.outcomes() == [Refuse_Code, Accept_Code]

    queue = wait_for_queue_depth(client, _orders_conn, 0)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_the_switch_off_answers_with_the_negative_acknowledgment() -> 'None':
    """ With the switch off a negative acknowledgment is the receiving system's answer to the caller, not something queued.
    """
    client = get_client()
    receiver = get_receiver(Conn_Plain)

    receiver.refuse_next(1)

    result = send(client, _plain_conn, {'order_id': 'plain-1'})

    assert result['raised'] == ''
    assert result['is_send_result'] is False
    assert result['is_ok'] is False
    assert result['response']['ack_code'] == Refuse_Code

    queue = get_queue(client, _plain_conn)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_the_switch_off_retries_a_direct_send_under_the_connections_policy() -> 'None':
    """ A connection dropped before an acknowledgment arrives is tried again as many times as the policy allows, with the
    policy's sleep between the attempts, and the send comes back with the acknowledgment of the attempt that went through.
    """
    client = get_client()
    receiver = get_receiver(Conn_Orders)

    # The orders connection carries the retries, its switch goes off for this one test
    _ = edit_connection(client, _orders_conn, {_queue.Field_Use_Queue: False})

    try:
        receiver.answer_next([Drop_Outcome] * Orders_Max_Retries + [Accept_Code])

        result = send(client, _orders_conn, {'order_id': 'direct-retry-1'})

        assert result['raised'] == ''
        assert result['is_send_result'] is False
        assert result['is_ok'] is True
        assert result['response']['ack_code'] == Accept_Code

        requests = receiver.wait_for_requests(Orders_Max_Retries + 1)
        assert receiver.outcomes() == [Drop_Outcome] * Orders_Max_Retries + [Accept_Code]

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

def test_a_negative_acknowledgment_is_not_retried_directly() -> 'None':
    """ With the switch off only a send that no acknowledgment came back from is tried again - an AE is the receiving
    system's answer and goes to the caller as it is, however many retries the connection has.
    """
    client = get_client()
    receiver = get_receiver(Conn_Orders)

    _ = edit_connection(client, _orders_conn, {_queue.Field_Use_Queue: False})

    try:
        receiver.refuse_next(1)

        result = send(client, _orders_conn, {'order_id': 'direct-nack-1'})

        assert result['raised'] == ''
        assert result['is_send_result'] is False
        assert result['is_ok'] is False
        assert result['response']['ack_code'] == Refuse_Code

        requests = receiver.wait_for_requests(1)
        assert len(requests) == 1
        assert receiver.outcomes() == [Refuse_Code]

    finally:
        _ = edit_connection(client, _orders_conn, {_queue.Field_Use_Queue: True})

# ################################################################################################################################

def test_no_retries_means_one_direct_attempt() -> 'None':
    """ A connection with no retries makes its one attempt and, with no acknowledgment back, raises to the caller.
    """
    client = get_client()
    receiver = get_receiver(Conn_Plain)

    receiver.answer_next([Drop_Outcome, Accept_Code])

    result = send(client, _plain_conn, {'order_id': 'no-retries-1'})

    assert result['raised'] != ''
    assert 'is_ok' not in result

    requests = receiver.wait_for_requests(1)
    assert len(requests) == 1
    assert receiver.outcomes() == [Drop_Outcome]

# ################################################################################################################################

def test_the_audit_log_records_the_code_of_each_acknowledgment() -> 'None':
    """ Each acknowledgment received from the queue is recorded with its code, a negative one carrying the code as its
    application outcome.
    """
    client = get_client()
    receiver = get_receiver(Conn_Orders)

    receiver.refuse_next(2)

    result = send(client, _orders_conn, {'order_id': 'audit-1'})
    assert result['is_in_queue'] is True

    _ = receiver.wait_for_accepted(1)

    sent_events = wait_for_audit_events(result['cid'], AuditEvent.Message_Sent, 3)
    assert len(sent_events) == 3

    received_events = wait_for_audit_events(result['cid'], AuditEvent.Ack_Received, 3)
    assert len(received_events) == 3

    received_outcomes = [event['application_outcome'] for event in received_events]
    assert received_outcomes == [Refuse_Code, Refuse_Code, '']

    queue = wait_for_queue_depth(client, _orders_conn, 0)
    assert queue['depth'] == 0

# ################################################################################################################################

def test_a_ping_goes_to_the_wire_while_the_queue_holds_messages() -> 'None':
    """ A ping is a connection opened and closed again, nothing the queue has a say in - it reaches the receiving system
    while a message waits in the queue and is recorded as a read, not a delivery.
    """
    client = get_client()
    receiver = get_receiver(Conn_Orders)

    receiver.refuse_all()

    queued = send(client, _orders_conn, {'order_id': 'waiting-1'})
    assert queued['is_in_queue'] is True

    result = read(client, _orders_conn)

    assert result['is_send_result'] is False
    assert result['is_ok'] is True
    assert result['response'] is None

    reads = receiver.reads()
    assert len(reads) == 1
    assert reads[0].outcome == Ping_Outcome
    assert reads[0].body == ''

    receiver.accept_all()

    queue = wait_for_queue_depth(client, _orders_conn, 0)
    assert queue['depth'] == 0

    # The ping consumed nothing of what the endpoint had to say about messages
    assert receiver.acceptance() == [False, True, True]

# ################################################################################################################################

def test_a_ping_of_a_system_that_is_not_there_fails() -> 'None':
    """ A ping raises to the caller when nothing listens on the port.
    """
    client = get_client()
    receiver = get_receiver(Conn_Plain)

    receiver.stop()

    try:
        result = read(client, _plain_conn)
    finally:
        receiver.start()

    assert result['is_ok'] is False
    assert mllp_type.down_error_text in result['response']['text']

# ################################################################################################################################

def test_the_destination_is_the_protocol_and_the_address() -> 'None':
    """ The delivery page shows a message as MLLP and the address it goes to, with the ER7 text as its body, no facts
    and no invoke dialog.
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
        'conn_type': mllp_type.conn_type,
        'conn_id': conn_id,
        'kind': Kind_DLQ,
        'msg_id': message['msg_id'],
    })

    assert response['destination'] == f'{Destination_Prefix} 127.0.0.1:{receiver.port}'
    assert response['facts'] == []
    assert response['body_mode'] == Body_Mode_HL7
    assert response['document'] == message['document']
    assert response['invoker'] is None

    assert mllp_type.body_of_envelope_data(response['document'][Key_Request][Key_Data]) == data

# ################################################################################################################################
# ################################################################################################################################
