# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# One loopback AS4 exchange, driven through the Dashboard - a channel and an outgoing connection
# pointed back at it, plus the pre-deployed service that sends over the pair from the IDE.

# stdlib
import logging
import time

# Zato
from as4_channel import create_as4_channel, delete_as4_channel
from as4_keys import new_test_parties
from as4_outconn import create_as4_outconn, delete_as4_outconn
from soap_outconn import invoke_service_in_ide

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# The pre-deployed fixture services an exchange is driven with and routed to
Invoker_Service  = 'test.as4.invoke'
Receiver_Service = 'test.as4.receiver'

# What the events of one exchange are called
Event_Message_Sent     = 'message-sent'
Event_Receipt_Received = 'receipt-received'
Event_Message_Received = 'message-received'
Event_Receipt_Sent     = 'receipt-sent'

# One complete exchange records four events - message-sent and receipt-received on the sending side,
# message-received and receipt-sent on the receiving side
Events_Per_Exchange = 4

# How long to keep retrying an invocation while a UI change propagates to the server
_Propagation_Timeout = 60

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# ################################################################################################################################
# ################################################################################################################################

def open_invoker_in_ide(page:'Page', base_url:'str') -> 'None':
    """ Opens the pre-deployed AS4 invoker service in the IDE and waits until the Invoke button
    is usable.
    """

    _ = page.goto(f'{base_url}/zato/service/ide/service/{Invoker_Service}/?cluster=1')
    _ = page.wait_for_selector('#invoke-service:not([disabled])', state='visible', timeout=15000)

# ################################################################################################################################

def wait_for_invoker_service(page:'Page', base_url:'str') -> 'None':
    """ Opens the invoker service in the IDE and keeps clicking Invoke with a readiness probe
    until the service responds, confirming it deployed during server boot.
    """

    open_invoker_in_ide(page, base_url)

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            response = invoke_service_in_ide(page, {'mode': 'ping'})
        except Exception as probe_error:
            last_error = probe_error
            time.sleep(_Propagation_Poll_Interval)
        else:
            if response.get('is_ready'):
                return
            time.sleep(_Propagation_Poll_Interval)

    raise Exception(f'Service `{Invoker_Service}` did not deploy within {_Propagation_Timeout}s, last: {last_error!r}')

# ################################################################################################################################

def send_with_retry(page:'Page', base_url:'str', connection_name:'str', payload:'str') -> 'anydict':
    """ Sends one AS4 message through the pre-deployed service, driven from the IDE in the browser,
    retrying while the pair configured a moment ago propagates to the server.
    """

    open_invoker_in_ide(page, base_url)

    request = {
        'mode': 'send',
        'connection': connection_name,
        'payload': payload,
    }

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            out = invoke_service_in_ide(page, request)
        except Exception as invoke_error:
            last_error = invoke_error
            time.sleep(_Propagation_Poll_Interval)
        else:
            # The service reports errors as a reply field, e.g. while the connection
            # or the channel it points back at is still propagating to the server.
            if error := out.get('error'):
                last_error = error
                time.sleep(_Propagation_Poll_Interval)
                continue

            return out

    raise Exception(f'Could not send over `{connection_name}` within {_Propagation_Timeout}s, last error: {last_error}')

# ################################################################################################################################

def new_exchange(
    page:'Page',
    base_url:'str',
    server_port:'int',
    name:'str',
    from_party:'str',
    to_party:'str',
    ) -> 'anydict':
    """ Creates one loopback pair through the Dashboard - a channel and an outgoing connection
    pointed back at it - and returns the ids of both, so the exchange can be driven and taken down.
    """

    url_path = '/' + name
    sender, receiver = new_test_parties()

    channel_id = create_as4_channel(page, base_url, name, url_path, {
        'as4_profile': 'edelivery1',
        'as4_from_party': from_party,
        'as4_to_party': to_party,
        'as4_service': 'urn:test:service',
        'as4_action': 'SubmitDocument',
        'as4_signing_key': receiver.key,
        'as4_signing_cert_chain': receiver.certificate,
        'as4_decryption_key': receiver.key,
        'as4_peer_signing_cert': sender.certificate,
        'service': Receiver_Service,
    })

    outconn_id = create_as4_outconn(page, base_url, name, f'http://127.0.0.1:{server_port}', {
        'as4_profile': 'edelivery1',
        'as4_from_party': from_party,
        'as4_to_party': to_party,
        'as4_service': 'urn:test:service',
        'as4_action': 'SubmitDocument',
        'url_path': url_path,
        'as4_signing_key': sender.key,
        'as4_signing_cert_chain': sender.certificate,
        'as4_peer_signing_cert': receiver.certificate,
        'as4_peer_encryption_cert': receiver.certificate,
    })

    out = {
        'channel_id': channel_id,
        'outconn_id': outconn_id,
    }

    return out

# ################################################################################################################################

def delete_exchange(page:'Page', exchange:'anydict') -> 'None':
    """ Takes down both sides of one loopback pair - both helpers find their own page first,
    so this works no matter where the browser was left.
    """

    delete_as4_outconn(page, exchange['outconn_id'])
    delete_as4_channel(page, exchange['channel_id'])

# ################################################################################################################################
# ################################################################################################################################
