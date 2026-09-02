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
from zato.common.test.playwright_pubsub import close_dialog_via_jquery, open_create_dialog
from as4_channel import edit_as4_channel, open_as4_channel_page
from as4_exchange import delete_exchange, new_exchange, send_with_retry, wait_for_invoker_service, Events_Per_Exchange
from as4_keys import new_test_parties
from as4_outconn import create_as4_outconn, delete_as4_outconn, edit_as4_outconn, open_as4_outconn_page, \
    open_edit_dialog, wait_for_as4_outconn_row
from audit_log_ui import get_details_value, get_pane_cid, get_row_event, get_row_outcome, get_row_time_text, get_rows, \
    open_details
from audit_toggle import assert_checkbox_exists, get_audit_row_count, get_checkbox_state, wait_for_table

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as4.audit.' + CryptoManager.generate_hex_string(32) + '.'

_Audit_Source = 'as4'

_Audit_Log_Url_Prefix = '/zato/audit-log/'

# The section title for the AS4 source, compared lowercase because the heading is styled with CSS
_AS4_Title = 'as4 audit log'

# What the four events of one exchange show as, by the labels their role tags carry
_Event_Message_Sent     = 'Message sent'
_Event_Receipt_Received = 'Receipt received'
_Event_Message_Received = 'Message received'
_Event_Receipt_Sent     = 'Receipt sent'

# What an event that went through says
_Outcome_Ok = 'ok'

# How long an edit needs before the channel runtime and the outgoing wrapper are rebuilt
_Rebuild_Delay = 5.0

# Log lines this suite's propagation retries can produce on the server
_AS4_Log_Patterns = ('AS4 request rejected',)

# ################################################################################################################################
# ################################################################################################################################

def _get_events_by_type(page:'Page') -> 'anydict':
    """ Returns every row currently shown, keyed by the on-screen event label of the row.
    """

    # Our response to produce
    out:'anydict' = {}

    for row in get_rows(page):
        out[get_row_event(row)] = row

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestAS4AuditLog:
    """ The audit log page as the AS4 transaction monitor - one live loopback exchange
    writes the four events of a complete AS4 conversation, they render under the AS4
    columns of the page, each connection row links to the log of its own party pair
    and the per-connection toggle gates whether anything is recorded at all.
    """

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_AS4_Log_Patterns)
    def test_exchange_events_render_with_their_columns(
        self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_invoker_service(page, base_url)

        # The parties are unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string()
        from_party = f'party-a-{suffix}'
        to_party = f'party-b-{suffix}'
        pair = f'{from_party}:{to_party}'

        name = _Test_Name_Prefix + 'columns'
        exchange = new_exchange(page, base_url, server_port, name, from_party, to_party)

        try:
            payload = '<Document xmlns="urn:test"><Value>' + CryptoManager.generate_hex_string() + '</Value></Document>'
            result = send_with_retry(page, base_url, name, payload)
            assert result['is_ok'], f'Expected a verified receipt, got: {result}'

            # The page pre-filtered to this party pair ..
            row_count = get_audit_row_count(page, base_url, _Audit_Source, pair)

            # .. shows all four events of the exchange, both halves of both sides ..
            assert row_count == Events_Per_Exchange, \
                f'Expected {Events_Per_Exchange} audit log rows, got {row_count}'

            # .. under a title naming the source, compared case-insensitively because of CSS styling ..
            title_text = page.inner_text('#detail-section-title')
            title_text = title_text.lower()
            assert title_text.startswith(_AS4_Title), \
                f'Expected the title to start with "{_AS4_Title}", got: "{title_text}"'

            # .. with the party pair in the title pill.
            pill_text = page.inner_text('#detail-section-title .detail-component-pill')
            pill_text = pill_text.lower()
            assert pill_text == pair.lower(), f'Expected pair "{pair}" in the pill, got: "{pill_text}"'

            events = _get_events_by_type(page)

            expected_events = {
                _Event_Message_Sent,
                _Event_Receipt_Received,
                _Event_Message_Received,
                _Event_Receipt_Sent,
            }

            assert set(events) == expected_events, f'Expected the four events of one exchange, got: {sorted(events)}'

            # Every event is filed under the pair and names the message it belongs to,
            # all of which the pane's Details tab says ..
            conversation_ids = {} # type: anydict

            for event_label, row in events.items():

                # The times are shown in the browser's locale format, not as raw ISO strings.
                time_text = get_row_time_text(row)
                assert time_text != '', f'Expected a non-empty event time on {event_label}'
                assert '+00:00' not in time_text, \
                    f'Expected a locale-formatted time on {event_label}, got: "{time_text}"'

                outcome = get_row_outcome(page, row)
                assert outcome == _Outcome_Ok, f'Expected outcome "{_Outcome_Ok}" on {event_label}, got: "{outcome}"'

                open_details(page, row)

                partner = get_details_value(page, 'Partner')
                assert partner == pair, f'Expected partner "{pair}" on {event_label}, got: "{partner}"'

                msg_id = get_details_value(page, 'Message id')
                assert msg_id == result['message_id'], \
                    f'Expected message id "{result["message_id"]}" on {event_label}, got: "{msg_id}"'

                cid = get_pane_cid(page)
                assert cid != '', f'Expected a correlation id on {event_label}'

                conversation_ids[event_label] = get_details_value(page, 'Conversation id')

            # .. and the user message events carry the conversation their exchange belongs to.
            sent_conversation_id = conversation_ids[_Event_Message_Sent]
            received_conversation_id = conversation_ids[_Event_Message_Received]

            assert sent_conversation_id != '', 'Expected a conversation id on the sent message'
            assert sent_conversation_id == received_conversation_id, \
                'Expected both sides of the exchange to record the same conversation id'

        finally:
            delete_exchange(page, exchange)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_AS4_Log_Patterns)
    def test_link_from_connection_list(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_invoker_service(page, base_url)

        suffix = CryptoManager.generate_hex_string()
        from_party = f'party-a-{suffix}'
        to_party = f'party-b-{suffix}'
        pair = f'{from_party}:{to_party}'

        name = _Test_Name_Prefix + 'link'
        exchange = new_exchange(page, base_url, server_port, name, from_party, to_party)

        try:
            payload = '<Document xmlns="urn:test"><Value>linked</Value></Document>'
            result = send_with_retry(page, base_url, name, payload)
            assert result['is_ok'], f'Expected a verified receipt, got: {result}'

            # Reload so the row carries the link the server built out of the stored parties ..
            open_as4_outconn_page(page, base_url, query=name)
            _ = wait_for_as4_outconn_row(page, name)

            # .. click the audit log link in this connection's row ..
            row_selector = f'#data-table tbody tr:has(td:text-is("{name}"))'
            page.click(f'{row_selector} a:text-is("Audit log")')

            # .. wait for the audit log page to load ..
            page.wait_for_url(f'**{_Audit_Log_Url_Prefix}**')
            wait_for_table(page)

            # .. the URL points to the AS4 audit log pre-filtered to this party pair ..
            assert 'source=as4' in page.url, f'Expected source=as4 in the URL, got: "{page.url}"'

            pill_text = page.inner_text('#detail-section-title .detail-component-pill')
            pill_text = pill_text.lower()
            assert pill_text == pair.lower(), f'Expected pair "{pair}" in the pill, got: "{pill_text}"'

            # .. and the events of the exchange are shown.
            events = _get_events_by_type(page)
            assert _Event_Message_Sent in events, f'Expected a sent message, got: {sorted(events)}'

            open_details(page, events[_Event_Message_Sent])

            msg_id = get_details_value(page, 'Message id')
            assert msg_id == result['message_id'], \
                f'Expected message id "{result["message_id"]}", got: "{msg_id}"'

        finally:
            delete_exchange(page, exchange)

# ################################################################################################################################

    def test_checkbox_defaults(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # The create dialog of an outgoing connection has the checkbox and it is on by default ..
        open_as4_outconn_page(page, base_url)
        open_create_dialog(page)

        assert_checkbox_exists(page, '#id_is_audit_log_active')
        assert get_checkbox_state(page, '#id_is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on by default in the create dialog of a connection'

        close_dialog_via_jquery(page, 'create-div')

        # .. so does the create dialog of a channel ..
        open_as4_channel_page(page, base_url)
        open_create_dialog(page)

        assert_checkbox_exists(page, '#id_is_audit_log_active')
        assert get_checkbox_state(page, '#id_is_audit_log_active') is True, \
            'Expected the audit log checkbox to be on by default in the create dialog of a channel'

        close_dialog_via_jquery(page, 'create-div')

        # .. and a connection created with the default carries it into the edit dialog.
        name = _Test_Name_Prefix + 'defaults'
        sender, receiver = new_test_parties()

        outconn_id = create_as4_outconn(page, base_url, name, 'https://ap.example.com', {
            'as4_profile': 'edelivery1',
            'url_path': '/as4',
            'as4_signing_key': sender.key,
            'as4_signing_cert_chain': sender.certificate,
            'as4_peer_signing_cert': receiver.certificate,
            'as4_peer_encryption_cert': receiver.certificate,
        })

        try:
            open_edit_dialog(page, outconn_id)

            assert_checkbox_exists(page, '#id_edit-is_audit_log_active')
            assert get_checkbox_state(page, '#id_edit-is_audit_log_active') is True, \
                'Expected the audit log checkbox to be on in the edit dialog of a default connection'

            close_dialog_via_jquery(page, 'edit-div')

        finally:
            delete_as4_outconn(page, outconn_id)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_AS4_Log_Patterns)
    def test_toggle_gates_events(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_invoker_service(page, base_url)

        suffix = CryptoManager.generate_hex_string()
        from_party = f'party-a-{suffix}'
        to_party = f'party-b-{suffix}'
        pair = f'{from_party}:{to_party}'

        name = _Test_Name_Prefix + 'toggle'
        exchange = new_exchange(page, base_url, server_port, name, from_party, to_party)

        channel_id = exchange['channel_id']
        outconn_id = exchange['outconn_id']

        try:
            # One exchange with the toggle on, which is what a new pair starts with ..
            payload = '<Document xmlns="urn:test"><Value>toggle-on</Value></Document>'
            result = send_with_retry(page, base_url, name, payload)
            assert result['is_ok'], f'Expected a verified receipt with the toggle on, got: {result}'

            baseline = get_audit_row_count(page, base_url, _Audit_Source, pair)
            assert baseline == Events_Per_Exchange, \
                f'Expected {Events_Per_Exchange} audit log rows with the toggle on, got {baseline}'

            # .. then turn the toggle off on both sides of the exchange and let the change reach the server ..
            open_as4_outconn_page(page, base_url, query=name)
            edit_as4_outconn(page, outconn_id, {'is_audit_log_active': False})

            open_as4_channel_page(page, base_url, query=name)
            edit_as4_channel(page, channel_id, {'is_audit_log_active': False})

            time.sleep(_Rebuild_Delay)

            # .. the message still travels end to end but nothing new is recorded ..
            result = send_with_retry(page, base_url, name, payload)
            assert result['is_ok'], f'Expected a verified receipt with the toggle off, got: {result}'

            row_count = get_audit_row_count(page, base_url, _Audit_Source, pair)
            assert row_count == baseline, \
                f'Expected still {baseline} audit log rows with the toggle off, got {row_count}'

            # .. and turning it back on records the four events of one more exchange.
            open_as4_outconn_page(page, base_url, query=name)
            edit_as4_outconn(page, outconn_id, {'is_audit_log_active': True})

            open_as4_channel_page(page, base_url, query=name)
            edit_as4_channel(page, channel_id, {'is_audit_log_active': True})

            time.sleep(_Rebuild_Delay)

            result = send_with_retry(page, base_url, name, payload)
            assert result['is_ok'], f'Expected a verified receipt with the toggle back on, got: {result}'

            row_count = get_audit_row_count(page, base_url, _Audit_Source, pair)
            expected = baseline + Events_Per_Exchange
            assert row_count == expected, \
                f'Expected {expected} audit log rows after turning the toggle back on, got {row_count}'

        finally:
            delete_exchange(page, exchange)

# ################################################################################################################################
# ################################################################################################################################
