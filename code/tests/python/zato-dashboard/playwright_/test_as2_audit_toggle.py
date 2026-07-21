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

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict
    from client import ZatoClient

# ################################################################################################################################
# ################################################################################################################################

from as2_outconn import create_as2_outconn, delete_as2_outconn, edit_as2_outconn, open_as2_outconn_page, \
    open_edit_dialog, wait_for_as2_outconn_row
from as4_keys import new_party
from audit_toggle import assert_checkbox_exists, get_audit_row_count, get_checkbox_state
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, open_create_dialog

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as2.audit.toggle.' + CryptoManager.generate_hex_string(32) + '.'

_Audit_Source = 'as2'

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

# How long an edit needs before both wrappers and the inbound partnership list are rebuilt
_Wrapper_Rebuild_Delay = 5.0

# One complete exchange records four events under one identity pair - message-sent
# and mdn-received on the sending side, message-received and mdn-sent on the inbound side
_Events_Per_Exchange = 4

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def channel_keystore(api_client:'ZatoClient') -> 'any_':
    """ Points the inbound AS2 channel's keystore at a receiving party for the duration
    of this module, restoring whatever was stored before once the module is done.
    """
    original = api_client.invoke(_Service_Get)

    receiver = new_party('as2-toggle-receiver')

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

def _click_send_test(page:'Page', name:'str') -> 'anydict':
    """ Clicks the Send test link of one connection's row and returns the parsed report.
    """
    row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'

    def _is_send_test_response(response:'any_') -> 'bool':
        out = _Send_Test_Url_Path in response.url
        return out

    with page.expect_response(_is_send_test_response, timeout=_Response_Timeout_Ms) as response_info:
        page.click(f'{row_selector} a.send-test-link')

    response = response_info.value

    out = loads(response.text())
    return out

# ################################################################################################################################

def _send_until_ok(page:'Page', name:'str') -> 'None':
    """ Clicks the Send test link until the exchange succeeds end to end,
    retrying while the connections and the keystore are still propagating.
    """
    deadline = monotonic() + _Propagation_Timeout

    while True:
        report = _click_send_test(page, name)

        if report['is_ok']:
            break

        if monotonic() > deadline:
            pytest.fail(f'Send test did not succeed in time, the last report was: {report}')

        sleep(_Retry_Sleep)

# ################################################################################################################################

def _open_page_with_rows(page:'Page', base_url:'str', sender_name:'str') -> 'None':
    """ Opens the outgoing AS2 connections page filtered to this run's rows
    and waits for the sender's row with its action links to appear.
    """
    open_as2_outconn_page(page, base_url, query=_Test_Name_Prefix)
    _ = wait_for_as2_outconn_row(page, sender_name)

# ################################################################################################################################

def _set_audit_flags(
    page:'Page',
    base_url:'str',
    sender_name:'str',
    sender_id:'str',
    receiver_id:'str',
    is_audit_log_active:'bool',
    ) -> 'None':
    """ Flips the audit log toggle of both sides of the exchange - the sender gates
    the message-sent and mdn-received events while the receiver's partnership gates
    the inbound channel's message-received and mdn-sent events. The wrappers
    and the inbound partnership list rebuild asynchronously, hence the fixed delay.
    """

    # Both edits run from the connections page ..
    _open_page_with_rows(page, base_url, sender_name)

    edit_as2_outconn(page, sender_id, {'is_audit_log_active': is_audit_log_active})
    edit_as2_outconn(page, receiver_id, {'is_audit_log_active': is_audit_log_active})

    # .. and the new configuration needs a moment to reach the server.
    sleep(_Wrapper_Rebuild_Delay)

# ################################################################################################################################
# ################################################################################################################################

class TestAS2AuditToggle:
    """ The per-connection audit log toggle of outgoing AS2 connections - the checkbox
    is on by default and turning it off stops audit events while exchanges continue.
    """

    def test_checkbox_defaults(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The create dialog has the checkbox and it is on by default ..
        open_as2_outconn_page(page, base_url)
        open_create_dialog(page)

        assert_checkbox_exists(page, '#id_is_audit_log_active')
        assert get_checkbox_state(page, '#id_is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on by default in the create dialog'

        close_dialog_via_jquery(page, 'create-div')

        # .. and a connection created with the default carries it into the edit dialog.
        sender = new_party('as2-toggle-defaults')

        name = _Test_Name_Prefix + 'defaults'
        suffix = CryptoManager.generate_hex_string()

        outconn_id = create_as2_outconn(page, base_url, name, 'https://as2.example.com/exchange', {
            'as2_from': f'ZatoRetail.defaults.{suffix}',
            'as2_to': f'PartnerCorp.defaults.{suffix}',
            'as2_partner_cert': sender.certificate,
            'as2_signing_key': sender.key,
            'as2_signing_cert_chain': sender.certificate,
            'as2_decryption_key': sender.key,
        })

        try:
            open_edit_dialog(page, outconn_id)

            assert_checkbox_exists(page, '#id_edit-is_audit_log_active')
            assert get_checkbox_state(page, '#id_edit-is_audit_log_active') is True, \
                'Expected the audit log checkbox to be on in the edit dialog of a default connection'

            close_dialog_via_jquery(page, 'edit-div')

        finally:
            delete_as2_outconn(page, outconn_id)

# ################################################################################################################################

    @pytest.mark.expect_log_errors('AS2 delivery not confirmed', 'AS2 request rejected')
    def test_toggle_gates_events(
        self, logged_in_page:'Page', zato_dashboard:'anydict', channel_keystore:'any_') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        receiver = channel_keystore
        sender = new_party('as2-toggle-sender')

        # The identities are unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string()
        sender_identity = f'ZatoRetail.{suffix}'
        receiver_identity = f'PartnerCorp.{suffix}'
        pair = f'{sender_identity}:{receiver_identity}'

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

            # Run one exchange with the toggle on, retrying while everything propagates -
            # failed attempts leave their own evidence events, so the baseline is whatever
            # the audit log shows after the first success rather than a fixed number ..
            _open_page_with_rows(page, base_url, sender_name)
            _send_until_ok(page, sender_name)

            baseline = get_audit_row_count(page, base_url, _Audit_Source, pair)
            assert baseline >= _Events_Per_Exchange, \
                f'Expected at least {_Events_Per_Exchange} audit log rows with the toggle on, got {baseline}'

            # .. turn the toggle off on both sides and run another exchange - the message
            # travels end to end but no new events are recorded ..
            _set_audit_flags(page, base_url, sender_name, sender_id, receiver_id, False)

            report = _click_send_test(page, sender_name)
            assert report['is_ok'] is True, f'Expected a successful exchange with the toggle off, got: {report}'

            row_count = get_audit_row_count(page, base_url, _Audit_Source, pair)
            assert row_count == baseline, \
                f'Expected still {baseline} audit log rows with the toggle off, got {row_count}'

            # .. turn the toggle back on and run one more exchange ..
            _set_audit_flags(page, base_url, sender_name, sender_id, receiver_id, True)

            report = _click_send_test(page, sender_name)
            assert report['is_ok'] is True, f'Expected a successful exchange with the toggle back on, got: {report}'

            # .. and all four of its events were recorded again.
            row_count = get_audit_row_count(page, base_url, _Audit_Source, pair)
            expected = baseline + _Events_Per_Exchange
            assert row_count == expected, \
                f'Expected {expected} audit log rows after turning the toggle back on, got {row_count}'

        finally:
            _open_page_with_rows(page, base_url, sender_name)
            delete_as2_outconn(page, sender_id)
            delete_as2_outconn(page, receiver_id)

# ################################################################################################################################
# ################################################################################################################################
