# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads
from time import monotonic, sleep
from urllib.parse import quote

# pytest
import pytest

# Zato
from zato.common.api import AS2
from zato.common.as2.mdn import normalize_message_id
from zato.common.as2.reconcile import MDNReconciler
from zato.common.as2.resubmit import record_message_received
from zato.common.audit_log.api import AuditLog
from zato.common.crypto.api import CryptoManager
from as2_outconn import create_as2_outconn, delete_as2_outconn
from as4_keys import new_party

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anylist
    from client import ZatoClient

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.audit.resubmit.' + CryptoManager.generate_hex_string(32) + '.'

_Audit_Log_Url_Prefix = '/zato/audit-log/'

# The endpoint of the Dashboard view the row action talks to
_Resubmit_Url_Path = '/zato/audit-log/resubmit/'

# The services managing the inbound channel's keystore
_Service_Get  = 'zato.channel.as2.keystore.get'
_Service_Edit = 'zato.channel.as2.keystore.edit'

# How long to keep retrying while the connections and the keystore propagate to the server
_Propagation_Timeout = 60

# How long to wait between retries
_Retry_Sleep = 2

# How long one click may take - a resend blocks while the connection pool is still being built
_Response_Timeout_Ms = 60000

# AS2 column indexes: Time, CID, Event, Partner, Message id, Disposition, MIC, Size, Data preview, Actions
_Column_Msg_ID = 4
_Column_Action = 9

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def channel_keystore(api_client:'ZatoClient') -> 'any_':
    """ Points the inbound AS2 channel's keystore at a receiving party for the duration
    of this module, restoring whatever was stored before once the module is done.
    """
    original = api_client.invoke(_Service_Get)

    receiver = new_party('audit-resubmit-receiver')

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

def _goto_audit_log(page:'Page', base_url:'str', object_name:'str') -> 'None':
    """ Navigates to the AS2 audit log page of one identity pair and waits
    for the first page of events to load.
    """
    encoded_name = quote(object_name)
    url = f'{base_url}{_Audit_Log_Url_Prefix}?source=as2&object_name={encoded_name}&cluster=1'

    _ = page.goto(url)
    _wait_for_table(page)

# ################################################################################################################################

def _wait_for_table(page:'Page') -> 'None':
    """ Waits until the audit log table has finished loading its current page of events.
    """
    _ = page.wait_for_function(
        '''() => {
            let body = document.querySelector('#audit-log-table-body');
            if (!body) return false;
            let rows = body.querySelectorAll('tr');
            if (!rows.length) return false;
            return !body.querySelector('tr.detail-loading-row');
        }''',
        timeout=10000)

# ################################################################################################################################

def _is_resubmit_response(response:'any_') -> 'bool':
    """ Matches the response of the resubmit view.
    """
    out = _Resubmit_Url_Path in response.url
    return out

# ################################################################################################################################

def _row_selector(message_id:'str') -> 'str':
    """ Returns the selector of the audit log row showing the given message id.
    """
    out = f'#audit-log-table-body tr:has(td:text-is("{message_id}"))'
    return out

# ################################################################################################################################

def _click_resubmit(page:'Page', message_id:'str') -> 'anydict | None':
    """ Clicks the resubmit link of one row and returns the parsed report,
    or None if the endpoint did not answer with one.
    """
    selector = _row_selector(message_id) + ' a.audit-log-resubmit-link'

    with page.expect_response(_is_resubmit_response, timeout=_Response_Timeout_Ms) as response_info:
        page.click(selector)

    response = response_info.value

    # A non-2xx response means the invocation itself failed, e.g. the service
    # has not deployed yet - the retry loop treats it the same as a failed report.
    if response.status != 200:
        return None

    out = loads(response.text())
    return out

# ################################################################################################################################

def _resubmit_until(page:'Page', message_id:'str', is_done_func:'any_') -> 'anydict':
    """ Clicks the resubmit link until the report satisfies the given condition,
    retrying while the connections propagate to the server.
    """
    deadline = monotonic() + _Propagation_Timeout

    while True:
        out = _click_resubmit(page, message_id)

        if out is not None:
            if is_done_func(out):
                break

        if monotonic() > deadline:
            pytest.fail(f'Resubmit did not reach the expected outcome in time, the last report was: {out}')

        sleep(_Retry_Sleep)

        # The report handler refreshes the table after each attempt, so wait for it
        # to settle and close the previous attempt's tooltip before clicking again.
        _wait_for_table(page)
        page.keyboard.press('Escape')

    return out

# ################################################################################################################################

def _wait_for_marker(page:'Page', message_id:'str') -> 'None':
    """ Waits until the row of the original event shows the resubmitted marker -
    the table refreshes itself once the report arrives.
    """
    selector = _row_selector(message_id) + ' .audit-log-resubmitted-marker'
    _ = page.wait_for_selector(selector, state='visible', timeout=10000)

# ################################################################################################################################

def _get_rows(page:'Page') -> 'anylist':
    """ Returns all rows currently shown in the audit log table.
    """
    out = page.query_selector_all('#audit-log-table-body tr')
    return out

# ################################################################################################################################

def _is_report_ok(report:'anydict') -> 'bool':
    out = report['is_ok']
    return out

# ################################################################################################################################

def _is_reprocessed_to_service(report:'anydict') -> 'bool':
    """ Tells whether a reprocess landed on the partner's own service - until the connection
    propagates to the server, it lands on the default shared topic instead.
    """
    out = report['is_ok'] and report['target_name'] == 'demo.ping'
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAuditLogResubmit:
    """ The resubmit action of the AS2 audit log - resend on outbound rows,
    reprocess on inbound ones, both landing as new events linked to the original
    by CID, with a marker on the already-resubmitted row.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors('AS2 delivery not confirmed', 'AS2 request rejected')
    def test_resend_of_an_outbound_row(
        self, logged_in_page:'Page', zato_dashboard:'anydict', channel_keystore:'any_') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        receiver = channel_keystore
        sender = new_party('audit-resubmit-sender')

        # The identities are unique per run so the exchange reconciles against itself only.
        suffix = CryptoManager.generate_hex_string()
        sender_identity = f'ZatoRetail.{suffix}'
        receiver_identity = f'PartnerCorp.{suffix}'
        pair = f'{sender_identity}:{receiver_identity}'

        original_id = f'{suffix}-original@zato.test'

        sender_name = _Test_Name_Prefix + 'sender'
        receiver_name = _Test_Name_Prefix + 'receiver'

        # The resent message goes to this server's own inbound AS2 channel.
        endpoint_url = f'http://127.0.0.1:{server_port}{AS2.Default.Channel_URL_Path}'

        # The sending side of the exchange - the connection the resend goes back through ..
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

            # The original delivery, stored with its clear payload the way
            # the outgoing connection records each send.
            reconciler = MDNReconciler()

            reconciler.record_message_sent(
                sender_identity, receiver_identity, original_id,
                cid='cid-original-' + suffix,
                payload='Test payload of an 850 order',
                filename='orders-850.edi',
            )

            # The row of an outbound event carries the resend action ..
            _goto_audit_log(page, base_url, pair)

            link_text = page.inner_text(_row_selector(original_id) + ' a.audit-log-resubmit-link')
            assert link_text == 'Resend', f'Expected a Resend link, got: "{link_text}"'

            # .. clicking it sends the stored payload out again through the real pipeline,
            # retrying while the connections propagate to the server ..
            report = _resubmit_until(page, original_id, _is_report_ok)

            # .. the report carries the complete outcome of the new delivery ..
            assert report['action'] == 'resend'
            assert report['message_id']
            assert report['has_mdn'] is True
            assert report['disposition'] == 'processed'
            assert report['mic_matched'] is True
            assert report['error'] == ''
            assert report['cid']

            # .. the original row shows the resubmitted marker once the table refreshes ..
            _wait_for_marker(page, original_id)

            # .. and the new attempt is its own row, under a fresh Message-ID - the resend
            # went through this server's own inbound channel, so the pair also collected
            # the inbound and MDN evidence of the exchange, each as its own row.
            resent_id = normalize_message_id(report['message_id'])
            resent_row = page.query_selector(_row_selector(resent_id))
            assert resent_row, f'Expected a row for the resent message `{resent_id}`'

        finally:
            delete_as2_outconn(page, sender_id)
            delete_as2_outconn(page, receiver_id)

# ################################################################################################################################

    def test_reprocess_of_an_inbound_row(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        sender = new_party('audit-reprocess-sender')
        receiver = new_party('audit-reprocess-receiver')

        # The identities are unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string()
        our_identity = f'ZatoRetail.{suffix}'
        partner_identity = f'PartnerCorp.{suffix}'

        # An inbound message arrives with the partner first, which is also
        # how its audit events are named.
        pair = f'{partner_identity}:{our_identity}'

        original_id = f'{suffix}-inbound@zato.test'

        connection_name = _Test_Name_Prefix + 'reprocess'

        # The partnership carries the routing override a reprocess follows -
        # the partner's documents go directly to this service.
        outconn_id = create_as2_outconn(page, base_url, connection_name, 'https://as2.example.com/exchange', {
            'as2_from': our_identity,
            'as2_to': partner_identity,
            'as2_partner_cert': sender.certificate,
            'as2_signing_key': receiver.key,
            'as2_signing_cert_chain': receiver.certificate,
            'as2_decryption_key': receiver.key,
            'inbound_service': 'demo.ping',
        })

        try:

            # The original arrival, stored with its clear payload the way
            # the inbound channel records each accepted message.
            audit_log = AuditLog('playwright-test')

            record_message_received(
                audit_log,
                partner_identity, our_identity, original_id,
                payload='Test payload of an 810 invoice',
                filename='invoice-810.edi',
                content_type='application/edi-x12',
                cid='cid-inbound-' + suffix,
            )

            # The row of an inbound event carries the reprocess action ..
            _goto_audit_log(page, base_url, pair)

            link_text = page.inner_text(_row_selector(original_id) + ' a.audit-log-resubmit-link')
            assert link_text == 'Reprocess', f'Expected a Reprocess link, got: "{link_text}"'

            # .. clicking it re-publishes the stored payload to the partner's routing target,
            # retrying while the connection propagates to the server - until it has,
            # a reprocess lands on the default shared topic rather than the partner's service ..
            report = _resubmit_until(page, original_id, _is_reprocessed_to_service)

            # .. the report says where the payload went ..
            assert report['action'] == 'reprocess'
            assert report['target_kind'] == 'service'
            assert report['error'] == ''
            assert report['cid']

            # .. the original row shows the resubmitted marker once the table refreshes ..
            _wait_for_marker(page, original_id)

            # .. and each new attempt is its own row under the same Message-ID,
            # so the pair now has more events than the one it started with.
            rows = _get_rows(page)
            row_count = len(rows)
            assert row_count >= 2, f'Expected at least 2 audit log rows, got {row_count}'

        finally:
            delete_as2_outconn(page, outconn_id)

# ################################################################################################################################
# ################################################################################################################################
