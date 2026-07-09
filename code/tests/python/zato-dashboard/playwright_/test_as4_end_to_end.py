# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from as4_channel import create_as4_channel, delete_as4_channel
from as4_keys import new_test_parties
from as4_outconn import create_as4_outconn, delete_as4_outconn, ping_as4_outconn
from soap_outconn import invoke_service_in_ide

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as4.live.' + CryptoManager.generate_hex_string(32) + '.'

# The pre-deployed fixture services this suite drives and routes to
_Invoker_Service  = 'test.as4.invoke'
_Receiver_Service = 'test.as4.receiver'

# How long to keep retrying an invocation while a UI change propagates to the server
_Propagation_Timeout = 60

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# Log lines this suite's propagation retries can produce on the server
_AS4_Log_Patterns = ('AS4 request rejected',)

# ################################################################################################################################
# ################################################################################################################################

def _open_invoker_in_ide(page:'Page', base_url:'str') -> 'None':
    """ Opens the pre-deployed AS4 invoker service in the IDE and waits until the Invoke button is usable.
    """

    _ = page.goto(f'{base_url}/zato/service/ide/service/{_Invoker_Service}/?cluster=1')
    _ = page.wait_for_selector('#invoke-service:not([disabled])', state='visible', timeout=15000)

# ################################################################################################################################

def _wait_for_invoker_service(page:'Page', base_url:'str') -> 'None':
    """ Opens the invoker service in the IDE and keeps clicking Invoke with a readiness
    probe until the service responds, confirming it deployed during server boot.
    """

    _open_invoker_in_ide(page, base_url)

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

    raise Exception(f'Service `{_Invoker_Service}` did not deploy within {_Propagation_Timeout}s, last: {last_error!r}')

# ################################################################################################################################

def _send_with_retry(page:'Page', base_url:'str', connection_name:'str', payload:'str') -> 'anydict':
    """ Sends one AS4 message through the pre-deployed service, driven from the IDE
    in the browser, retrying while the pair configured a moment ago propagates to the server.
    """

    _open_invoker_in_ide(page, base_url)

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

def _get_received(page:'Page', base_url:'str') -> 'list':
    """ Returns everything the receiver service recorded so far.
    """

    _open_invoker_in_ide(page, base_url)

    out = invoke_service_in_ide(page, {'mode': 'get-received'})
    return out['received']

# ################################################################################################################################

def _clear_received(page:'Page', base_url:'str') -> 'None':
    """ Starts a new exchange from a clean slate.
    """

    _open_invoker_in_ide(page, base_url)

    _ = invoke_service_in_ide(page, {'mode': 'clear-received'})

# ################################################################################################################################
# ################################################################################################################################

class TestAS4EndToEnd:
    """ The live end-to-end loopback - an AS4 channel and an outgoing AS4 connection,
    both created through the Dashboard, the connection pointed back at the channel
    of the same server. One send from a service then crosses the whole stack twice:
    build, sign and encrypt on the way out, decrypt, verify, receipt and routing
    on the way in - with the receipt verified by the sender and the payload
    received through the configured routing.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_AS4_Log_Patterns)
    def test_loopback_send_receipt_and_routing(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        _wait_for_invoker_service(page, base_url)
        _clear_received(page, base_url)

        name = _Test_Name_Prefix + 'loopback'
        url_path = '/' + name
        sender, receiver = new_test_parties()

        # The channel - it decrypts with the receiver's key, verifies against
        # the sender's pinned certificate, signs its receipts with the receiver's key
        # and routes accepted payloads to the pre-deployed receiver service ..
        channel_id = create_as4_channel(page, base_url, name, url_path, {
            'as4_profile': 'edelivery1',
            'as4_from_party': 'party-a',
            'as4_to_party': 'party-b',
            'as4_service': 'urn:test:service',
            'as4_action': 'SubmitDocument',
            'as4_signing_key': receiver.key,
            'as4_signing_cert_chain': receiver.certificate,
            'as4_decryption_key': receiver.key,
            'as4_peer_signing_cert': sender.certificate,
            'service': _Receiver_Service,
        })

        # .. and the outgoing connection pointed back at that channel over plain HTTP.
        outconn_id = create_as4_outconn(page, base_url, name, f'http://127.0.0.1:{server_port}', {
            'as4_profile': 'edelivery1',
            'as4_from_party': 'party-a',
            'as4_to_party': 'party-b',
            'as4_service': 'urn:test:service',
            'as4_action': 'SubmitDocument',
            'url_path': url_path,
            'as4_signing_key': sender.key,
            'as4_signing_cert_chain': sender.certificate,
            'as4_peer_signing_cert': receiver.certificate,
            'as4_peer_encryption_cert': receiver.certificate,
        })

        # One send now goes service -> outgoing connection -> channel -> receiver service.
        payload = '<Document xmlns="urn:test"><Value>' + CryptoManager.generate_hex_string() + '</Value></Document>'
        result = _send_with_retry(page, base_url, name, payload)

        # The sender verified the synchronous receipt - non-repudiation of receipt ..
        assert result['is_ok'], f'Expected a verified receipt, got: {result}'
        assert result['receipt_ref'] == result['message_id'], \
            f'Expected the receipt to reference the message, got: {result}'

        # .. and the payload arrived through the configured routing with its ebMS metadata.
        received = _get_received(page, base_url)
        assert len(received) == 1, f'Expected exactly one routed message, got: {received}'

        message = received[0]
        assert message['message_id'] == result['message_id'], f'Expected the message id, got: {message}'
        assert message['from_party'] == 'party-a', f'Expected the sender party, got: {message}'
        assert message['to_party'] == 'party-b', f'Expected the receiver party, got: {message}'
        assert message['service'] == 'urn:test:service', f'Expected the service, got: {message}'
        assert message['action'] == 'SubmitDocument', f'Expected the action, got: {message}'
        assert message['data'] == payload, f'Expected the payload, got: {message}'

        # The test-send button performs a signed ping exchange against the same channel.
        ping_result = ping_as4_outconn(page, name)
        assert ping_result['is_success'], f'Expected the test-send to succeed, got: {ping_result}'

        # Clean up.
        delete_as4_outconn(page, outconn_id)
        delete_as4_channel(page, channel_id)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_AS4_Log_Patterns)
    def test_duplicate_is_not_routed_twice(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Two sends are two distinct messages and both arrive - the duplicate detection
        keys on eb:MessageId, not on the payload, so an identical payload sent twice
        is still two deliveries.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        _wait_for_invoker_service(page, base_url)
        _clear_received(page, base_url)

        name = _Test_Name_Prefix + 'repeat'
        url_path = '/' + name
        sender, receiver = new_test_parties()

        channel_id = create_as4_channel(page, base_url, name, url_path, {
            'as4_profile': 'edelivery1',
            'as4_signing_key': receiver.key,
            'as4_signing_cert_chain': receiver.certificate,
            'as4_decryption_key': receiver.key,
            'as4_peer_signing_cert': sender.certificate,
            'service': _Receiver_Service,
        })

        outconn_id = create_as4_outconn(page, base_url, name, f'http://127.0.0.1:{server_port}', {
            'as4_profile': 'edelivery1',
            'url_path': url_path,
            'as4_signing_key': sender.key,
            'as4_signing_cert_chain': sender.certificate,
            'as4_peer_signing_cert': receiver.certificate,
            'as4_peer_encryption_cert': receiver.certificate,
        })

        payload = '<Document xmlns="urn:test"><Value>repeated</Value></Document>'

        first = _send_with_retry(page, base_url, name, payload)
        second = _send_with_retry(page, base_url, name, payload)

        # Each send is its own ebMS message with its own id ..
        assert first['message_id'] != second['message_id'], \
            f'Expected two distinct messages, got: {first} and {second}'

        # .. and both were routed, because duplicate detection keys on the message id.
        received = _get_received(page, base_url)
        message_ids = {message['message_id'] for message in received}

        assert message_ids == {first['message_id'], second['message_id']}, \
            f'Expected both messages routed, got: {received}'

        # Clean up.
        delete_as4_outconn(page, outconn_id)
        delete_as4_channel(page, channel_id)

# ################################################################################################################################
# ################################################################################################################################
