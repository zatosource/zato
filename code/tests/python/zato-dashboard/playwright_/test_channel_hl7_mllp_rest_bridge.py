# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from http.client import HTTPConnection

# pytest
import pytest

# Zato
from hl7_client.mllp_receiver import MLLPReceiver
from mllp_channel import create_channel, delete_channel, save_channel, send_with_both_clients, wait_for_item, \
    wait_for_port, wait_until_accepted, Host
from mllp_outconn import create_outgoing_connection, delete_outgoing_connection
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.mllp.rest.' + CryptoManager.generate_hex_string(32) + '.'

# The service every channel here invokes - it answers with an acknowledgment naming the channel in MSA-3
_Test_Service = 'test.hl7.mllp.wire.ack-identity'

# The sender the channel's routing criterion is about
_Bridge_App = 'BRIDGE_SENDER'

# How long a REST request to the bridge waits for its answer
_Rest_Timeout = 10

# How long the bridge is given to answer after a save, and how often it is asked
_Bridge_Timeout = 30
_Poll_Interval = 0.5

# The status a REST request to a path no channel listens on receives
_Not_Found = 404

# ################################################################################################################################
# ################################################################################################################################

def _build_message(control_id:'str') -> 'bytes':
    message = (
        f'MSH|^~\\&|{_Bridge_App}|BRIDGE_FAC|ZatoRecv|ZatoFac|20260507120000||ADT^A01|{control_id}|P|2.5\r'
        f'EVN|A01|20260507120000\r'
        f'PID|||12345^^^MRN||Doe^John||19800101|M'
    )

    out = message.encode('utf-8')
    return out

# ################################################################################################################################

def _post_to_bridge(port:'int', url_path:'str', message:'bytes') -> 'tuple[int, str]':
    """ One HL7 message over the REST bridge, as a sender without MLLP sends it - a POST
    with the message as its body and no credentials, the bridge having no security assigned.
    """
    connection = HTTPConnection(Host, port, timeout=_Rest_Timeout)
    connection.request('POST', url_path, body=message, headers={'Content-Type': 'application/hl7-v2'})

    response = connection.getresponse()
    body = response.read().decode('utf-8')
    connection.close()

    out = (response.status, body)
    return out

# ################################################################################################################################

def _wait_until_bridge_answers(port:'int', url_path:'str') -> 'None':
    """ Waits until the REST bridge answers a message, which it does once the channel's
    save has reached the server and the path is active.
    """
    deadline = time.monotonic() + _Bridge_Timeout

    while time.monotonic() < deadline:
        control_id = 'probe.' + CryptoManager.generate_hex_string()
        status, _ = _post_to_bridge(port, url_path, _build_message(control_id))

        if status == 200:
            return

        time.sleep(_Poll_Interval)

    raise Exception(f'The REST bridge at {url_path} did not answer within {_Bridge_Timeout}s')

# ################################################################################################################################

def _text_has(control_id:'str') -> 'any_':
    def _predicate(item:'any_') -> 'bool':
        out = control_id in item.text
        return out

    return _predicate

# ################################################################################################################################
# ################################################################################################################################

class TestChannelHL7MLLPRestBridge:
    """ A channel with the REST bridge on receives the same message over MLLP and over REST - the same
    service answers, the same destination receives the message - and the bridge remains after the channel
    is saved again through the wizard. Deleting the channel deletes the bridge.
    """

    # Deleting the bridge removes a REST endpoint, which the OpenAPI console notes as a breaking change
    @pytest.mark.expect_log_errors('No matching MLLP channel for message', 'OpenAPI breaking change: endpoint removed')
    def test_the_bridge_receives_what_mllp_does_and_survives_an_edit(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        ) -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        mllp_port = zato_dashboard['mllp_port']
        server_port = zato_dashboard['server_port']

        channel_name = _Test_Name_Prefix + 'channel'
        outconn_name = _Test_Name_Prefix + 'outconn'
        rest_url_path = '/' + _Test_Name_Prefix.replace('.', '/') + 'bridge'

        # The receiver the channel's destination delivers to
        receiver = MLLPReceiver()
        receiver.start()

        try:
            create_outgoing_connection(page, base_url, outconn_name, f'{Host}:{receiver.port}')

            destinations = [{'connection': outconn_name, 'type': 'hl7-mllp', 'is_active': True, 'options': {}}]

            create_channel(page, base_url, channel_name,
                service=_Test_Service,
                criteria={'msh3_sending_app': _Bridge_App},
                destinations=destinations,
                rest_url_path=rest_url_path)

            wait_for_port(mllp_port)
            _ = wait_until_accepted(mllp_port, _Bridge_App)
            _wait_until_bridge_answers(server_port, rest_url_path)

            # Both transports reach the same service and the same destination ..
            self._check_both_transports(mllp_port, server_port, rest_url_path, channel_name, receiver)

            # .. and they still do once the channel has been saved again with nothing changed - an edit
            # that deleted the bridge would leave the REST path without a channel.
            save_channel(page, base_url, channel_name)
            _ = wait_until_accepted(mllp_port, _Bridge_App)
            _wait_until_bridge_answers(server_port, rest_url_path)

            self._check_both_transports(mllp_port, server_port, rest_url_path, channel_name, receiver)

        finally:
            delete_channel(page, base_url, channel_name)
            delete_outgoing_connection(page, base_url, outconn_name)
            receiver.stop()

        # The bridge is deleted with the channel
        self._check_bridge_is_gone(server_port, rest_url_path)

# ################################################################################################################################

    def _check_both_transports(
        self,
        mllp_port:'int',
        server_port:'int',
        rest_url_path:'str',
        channel_name:'str',
        receiver:'MLLPReceiver',
        ) -> 'None':

        # Over MLLP, the acknowledgment names the channel and the destination receives the message ..
        for control_id, result in send_with_both_clients(mllp_port, _Bridge_App):
            assert result.msa_1 == 'AA', f'Expected AA, got: {result}'
            assert result.msa_3 == channel_name, f'Expected `{channel_name}` in MSA-3, got: {result}'

            _ = wait_for_item(receiver.deliveries, _text_has(control_id), f'MLLP delivery of {control_id}')

        # .. and over REST, the same service answers and the same destination receives the message.
        control_id = 'rest.' + CryptoManager.generate_hex_string()
        status, body = _post_to_bridge(server_port, rest_url_path, _build_message(control_id))

        assert status == 200, f'Expected 200 from the bridge, got: {status} {body}'
        assert 'MSA|AA|' + control_id in body, f'Expected an AA acknowledgment of {control_id}, got: {body}'

        _ = wait_for_item(receiver.deliveries, _text_has(control_id), f'MLLP delivery of {control_id} received over REST')

# ################################################################################################################################

    def _check_bridge_is_gone(self, server_port:'int', rest_url_path:'str') -> 'None':

        deadline = time.monotonic() + _Bridge_Timeout

        while time.monotonic() < deadline:
            control_id = 'gone.' + CryptoManager.generate_hex_string()
            status, _ = _post_to_bridge(server_port, rest_url_path, _build_message(control_id))

            if status == _Not_Found:
                return

            time.sleep(_Poll_Interval)

        raise Exception(f'The REST bridge at {rest_url_path} still answers {_Bridge_Timeout}s after the channel was deleted')

# ################################################################################################################################
# ################################################################################################################################
