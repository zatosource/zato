# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads
from time import monotonic, sleep

# pytest
import pytest

# Zato
from zato.common.api import AS2
from zato.common.crypto.api import CryptoManager
from as2_outconn import create_as2_outconn, delete_as2_outconn, open_as2_outconn_page, wait_for_as2_outconn_row
from as4_keys import new_party

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict
    from client import ZatoClient

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as2.send.' + CryptoManager.generate_hex_string(32) + '.'

# The endpoint of the Dashboard view the row action talks to
_Send_Test_Url_Path = '/zato/outgoing/as2/send-test-message/'

# The services managing the inbound channel's keystore
_Service_Get  = 'zato.channel.as2.keystore.get'
_Service_Edit = 'zato.channel.as2.keystore.edit'

# How long to keep retrying while the connections and the keystore propagate to the server
_Propagation_Timeout = 60

# How long to wait between retries
_Retry_Sleep = 2

# How long one click may take - the send blocks while the connection pool is still being built
_Response_Timeout_Ms = 60000

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def channel_keystore(api_client:'ZatoClient') -> 'any_':
    """ Points the inbound AS2 channel's keystore at a receiving party for the duration
    of this module, restoring whatever was stored before once the module is done.
    """
    original = api_client.invoke(_Service_Get)

    receiver = new_party('as2-test-receiver')

    _ = api_client.invoke(_Service_Edit, {
        'as2_signing_key': receiver.key,
        'as2_signing_cert_chain': receiver.certificate,
        'as2_decryption_key': receiver.key,
        'as2_next_decryption_key': '',
        'as2_next_decryption_cert': '',
    })

    yield receiver

    # The keystore get service returns only the certificates - the private keys never
    # leave the server, so the restore puts the certificates back while the empty
    # key fields keep the stored keys in place.
    _ = api_client.invoke(_Service_Edit, {
        'as2_signing_key': '',
        'as2_signing_cert_chain': original['as2_signing_cert_chain'],
        'as2_decryption_key': '',
        'as2_next_decryption_key': '',
        'as2_next_decryption_cert': original['as2_next_decryption_cert'],
    })

# ################################################################################################################################
# ################################################################################################################################

def _is_send_test_response(response:'any_') -> 'bool':
    """ Matches the response of the send-test-message view.
    """
    out = _Send_Test_Url_Path in response.url
    return out

# ################################################################################################################################

def _click_send_test(page:'Page', name:'str') -> 'anydict':
    """ Clicks the Send test link of one connection's row and returns the parsed report.
    """
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    with page.expect_response(_is_send_test_response, timeout=_Response_Timeout_Ms) as response_info:
        page.click(f'{row_selector} a.send-test-link')

    response = response_info.value

    out = loads(response.text())
    return out

# ################################################################################################################################

def _send_until(page:'Page', name:'str', is_done_func:'any_') -> 'anydict':
    """ Clicks the Send test link until the report satisfies the given condition,
    retrying while the connections and the keystore are still propagating.
    """
    deadline = monotonic() + _Propagation_Timeout

    while True:
        out = _click_send_test(page, name)

        if is_done_func(out):
            break

        if monotonic() > deadline:
            pytest.fail(f'Send test did not reach the expected outcome in time, the last report was: {out}')

        sleep(_Retry_Sleep)

    return out

# ################################################################################################################################

def _is_report_ok(report:'anydict') -> 'bool':
    out = report['is_ok']
    return out

# ################################################################################################################################

def _report_has_mdn(report:'anydict') -> 'bool':
    out = report['has_mdn']
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAS2SendTestMessage:
    """ The Send test row action of the outgoing AS2 connections list - a small identified
    test payload travels through the real pipeline against this server's own inbound
    AS2 channel and the MDN outcome comes back inline.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors('AS2 delivery not confirmed', 'AS2 request rejected')
    def test_send_test_message_reports_the_mdn_outcome(
        self, logged_in_page:'Page', zato_dashboard:'anydict', channel_keystore:'any_') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        receiver = channel_keystore
        sender = new_party('as2-test-sender')

        # The identities are unique per run so the exchange reconciles against itself only.
        suffix = CryptoManager.generate_hex_string()
        sender_identity = f'ZatoRetail.{suffix}'
        receiver_identity = f'PartnerCorp.{suffix}'

        sender_name = _Test_Name_Prefix + 'sender'
        receiver_name = _Test_Name_Prefix + 'receiver'

        # The message goes to this server's own inbound AS2 channel.
        endpoint_url = f'http://127.0.0.1:{server_port}{AS2.Default.Channel_URL_Path}'

        # The sending side of the exchange ..
        sender_id = create_as2_outconn(page, base_url, sender_name, endpoint_url, {
            'as2_from': sender_identity,
            'as2_to': receiver_identity,
            'as2_partner_cert': receiver.certificate,
            'as2_signing_key': sender.key,
            'as2_signing_cert_chain': sender.certificate,
            'as2_decryption_key': sender.key,
        })

        # .. and the receiving side - the inbound channel matches the reversed identity pair
        # against this connection and routes the payload to its inbound service.
        receiver_id = create_as2_outconn(page, base_url, receiver_name, 'https://as2.example.com/exchange', {
            'as2_from': receiver_identity,
            'as2_to': sender_identity,
            'as2_partner_cert': sender.certificate,
            'as2_signing_key': receiver.key,
            'as2_signing_cert_chain': receiver.certificate,
            'as2_decryption_key': receiver.key,
            'inbound_service': 'demo.ping',
        })

        try:

            # Reload so the rows carry their action links ..
            open_as2_outconn_page(page, base_url, query=_Test_Name_Prefix)
            _ = wait_for_as2_outconn_row(page, sender_name)

            # .. send the test message, retrying while everything propagates ..
            report = _send_until(page, sender_name, _is_report_ok)

            # .. and the report carries the complete MDN outcome.
            assert report['is_ok'] is True
            assert report['message_id']
            assert report['has_mdn'] is True
            assert report['mdn_signed'] is True
            assert report['disposition'] == 'processed'
            assert report['mic_matched'] is True
            assert report['error'] == ''

        finally:
            delete_as2_outconn(page, sender_id)
            delete_as2_outconn(page, receiver_id)

# ################################################################################################################################

    @pytest.mark.expect_log_errors('AS2 delivery not confirmed', 'AS2 request rejected')
    def test_send_test_message_reports_an_unknown_partner(
        self, logged_in_page:'Page', zato_dashboard:'anydict', channel_keystore:'any_') -> 'None':
        """ With no reverse connection configured, the channel answers with an error MDN
        and the report says why the delivery was not accepted.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        receiver = channel_keystore
        sender = new_party('as2-unknown-sender')

        suffix = CryptoManager.generate_hex_string()
        sender_name = _Test_Name_Prefix + 'unknown'

        endpoint_url = f'http://127.0.0.1:{server_port}{AS2.Default.Channel_URL_Path}'

        sender_id = create_as2_outconn(page, base_url, sender_name, endpoint_url, {
            'as2_from': f'ZatoRetail.unknown.{suffix}',
            'as2_to': f'PartnerCorp.unknown.{suffix}',
            'as2_partner_cert': receiver.certificate,
            'as2_signing_key': sender.key,
            'as2_signing_cert_chain': sender.certificate,
            'as2_decryption_key': sender.key,
        })

        try:

            open_as2_outconn_page(page, base_url, query=sender_name)
            _ = wait_for_as2_outconn_row(page, sender_name)

            # The channel knows no reverse partnership for this pair, so it answers
            # with an unsigned explanatory MDN.
            report = _send_until(page, sender_name, _report_has_mdn)

            assert report['is_ok'] is False
            assert report['mdn_signed'] is False
            assert 'unknown-trading-relationship' in report['disposition']

        finally:
            delete_as2_outconn(page, sender_id)

# ################################################################################################################################
# ################################################################################################################################
