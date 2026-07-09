# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
from base64 import b64decode

# Zato
from containers import ModuleCtx as ContainerCtx
from mq_client import build_rfh2, ModuleCtx as MQClientCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from certificates import CertificatePaths
    from containers import MQServer
    from harness import QueueBridgeHarness
    from mq_client import MQTestClient
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

# The service every test channel points to
_service_name = 'demo.ibm-mq.test'

# ################################################################################################################################
# ################################################################################################################################

def channel_config(mq_server:'MQServer', *, name:'str', queue:'str', remove_jms_headers:'bool') -> 'anydict':
    """ Builds a channel connection config the bridge accepts in a reload command.
    """
    out = {
        'name': name,
        'type_': 'channel-ibm-mq',
        'address': mq_server.address,
        'service': _service_name,
        'queue_manager': ContainerCtx.Queue_Manager,
        'mq_channel_name': ContainerCtx.MQ_Channel_Name,
        'queue': queue,
        'username': ContainerCtx.Username,
        'password': ContainerCtx.Password,
        'remove_jms_headers': remove_jms_headers,
        'ssl': False,
        'ssl_ca_file': None,
        'ssl_cert_file': None,
        'ssl_key_file': None,
    }

    return out

# ################################################################################################################################

def outgoing_config(mq_server:'MQServer', *, name:'str', queue:'str') -> 'anydict':
    """ Builds an outgoing connection config the bridge accepts in a reload command.
    """
    out = {
        'name': name,
        'type_': 'outconn-ibm-mq',
        'address': mq_server.address,
        'queue_manager': ContainerCtx.Queue_Manager,
        'mq_channel_name': ContainerCtx.MQ_Channel_Name,
        'queue': queue,
        'username': ContainerCtx.Username,
        'password': ContainerCtx.Password,
        'ssl': False,
        'ssl_ca_file': None,
        'ssl_cert_file': None,
        'ssl_key_file': None,
    }

    return out

# ################################################################################################################################

def with_ssl(config:'anydict', certificates:'CertificatePaths') -> 'anydict':
    """ Turns a plain connection config into one that connects over TLS.
    """
    config['ssl'] = True
    config['cipher_spec'] = ContainerCtx.Cipher_Spec
    config['ssl_ca_file'] = certificates.ca_cert

    return config

# ################################################################################################################################

def run_send_and_consume_scenario(harness:'QueueBridgeHarness', channel_name:'str') -> 'None':
    """ Sends a message through the outgoing connection and asserts the channel consumes it,
    publishing a recv event complete with MQMD headers.
    """

    # Send a message through the outgoing connection ..
    message = b'{"invoice_id": "INV-2026-001", "status": "paid"}'
    reply = harness.send_message('test.ibm-mq.publisher', message)
    assert reply['status'] == 'ok', f'Send failed: {reply}'

    # .. the channel consumes it and publishes a recv event ..
    event = harness.wait_for_recv_event()

    assert event['channel_name'] == channel_name
    assert event['service'] == _service_name
    assert event['topic'] == ContainerCtx.Request_Queue
    assert b64decode(event['payload']) == message

    # .. whose headers carry the MQMD fields of the incoming message.
    headers = json.loads(event['headers'])

    assert headers['mqmd.format'] == 'MQSTR'
    assert len(headers['mqmd.message_id']) == 48
    assert headers['mqmd.put_date_time']

    # A message sent through the outgoing connection has no reply-to queue,
    # while the queue manager fills in its own name for the reply-to queue manager.
    assert event['reply_to_queue'] == ''
    assert event['reply_to_queue_manager'] == ContainerCtx.Queue_Manager

# ################################################################################################################################

def run_reply_scenario(harness:'QueueBridgeHarness', client:'MQTestClient', channel_name:'str') -> 'None':
    """ Puts a request message with a reply-to queue on the channel's queue and asserts
    the send_reply path delivers a correlated reply to that queue.
    """

    # Put a request message that names a reply-to queue ..
    request = b'{"account_id": "ACC-77"}'
    request_message_id = client.put(
        ContainerCtx.Request_Queue,
        request,
        message_type=MQClientCtx.MQMT_Request,
        reply_to_queue=ContainerCtx.Reply_Queue,
        reply_to_queue_manager=ContainerCtx.Queue_Manager,
    )

    # .. the channel consumes it and the recv event carries the reply-to details ..
    event = harness.wait_for_recv_event()

    assert b64decode(event['payload']) == request
    assert event['reply_to_queue'] == ContainerCtx.Reply_Queue
    assert event['reply_to_queue_manager'] == ContainerCtx.Queue_Manager
    assert event['message_id'] == request_message_id.hex()

    # .. send a reply the way the server does when a service sets self.response.payload ..
    response = b'{"account_id": "ACC-77", "balance": 512.25}'
    reply = harness.send_reply(
        channel_name,
        event['reply_to_queue'],
        event['reply_to_queue_manager'],
        event['message_id'],
        response,
    )
    assert reply['status'] == 'ok', f'Reply failed: {reply}'

    # .. and the reply arrives on the reply-to queue, correlated with the request's message ID.
    received = client.get(ContainerCtx.Reply_Queue, wait_ms=15000, correlation_id=request_message_id)
    assert received is not None, 'No reply arrived on the reply-to queue'

    payload, fields = received
    assert payload == response
    assert fields['correlation_id'] == request_message_id

# ################################################################################################################################

def run_rfh2_scenario(
    harness:'QueueBridgeHarness',
    client:'MQTestClient',
    *,
    queue:'str',
    remove_jms_headers:'bool',
    ) -> 'None':
    """ Puts a message with an MQRFH2 header on a queue and asserts the flattened headers
    are exposed while the payload is stripped or kept according to the channel config.
    """

    # Craft a message the way the IBM MQ classes for JMS do ..
    jms_folder = '<jms><Dst>queue:///' + queue + '</Dst><Dlv>2</Dlv></jms>'
    usr_folder = '<usr><tenant>acme</tenant><order_type>standard</order_type></usr>'
    body = b'{"order_id": 123}'

    message = build_rfh2([jms_folder, usr_folder], body)
    _ = client.put(queue, message, format=MQClientCtx.Format_RFH2)

    # .. the channel consumes it and exposes the flattened MQRFH2 headers either way ..
    event = harness.wait_for_recv_event()
    headers = json.loads(event['headers'])

    assert headers['jms.Dst'] == 'queue:///' + queue
    assert headers['jms.Dlv'] == '2'
    assert headers['usr.tenant'] == 'acme'
    assert headers['usr.order_type'] == 'standard'
    assert headers['mqmd.format'] == 'MQHRF2'

    # .. while the payload depends on whether the channel removes JMS headers.
    payload = b64decode(event['payload'])

    if remove_jms_headers:
        assert payload == body
    else:
        assert payload == message

# ################################################################################################################################
# ################################################################################################################################
