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
from as4_channel import create_as4_channel, delete_as4_channel, edit_as4_channel, open_as4_channel_page
from as4_keys import new_test_parties
from as4_outconn import create_as4_outconn, delete_as4_outconn, edit_as4_outconn, open_as4_outconn_page, \
    open_edit_dialog, wait_for_as4_outconn_row
from audit_toggle import assert_checkbox_exists, get_audit_row_count, get_checkbox_state, wait_for_table
from soap_outconn import invoke_service_in_ide

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.as4.audit.' + CryptoManager.generate_hex_string(32) + '.'

_Audit_Source = 'as4'

_Audit_Log_Url_Prefix = '/zato/audit-log/'

# The section title for the AS4 source, compared lowercase because the heading is styled with CSS
_AS4_Title = 'as4 audit log'

# The pre-deployed fixture services this suite drives and routes to
_Invoker_Service  = 'test.as4.invoke'
_Receiver_Service = 'test.as4.receiver'

# What the events of one exchange are called
_Event_Message_Sent     = 'message-sent'
_Event_Receipt_Received = 'receipt-received'
_Event_Message_Received = 'message-received'
_Event_Receipt_Sent     = 'receipt-sent'

# One complete exchange records four events - message-sent and receipt-received on the sending
# side, message-received and receipt-sent on the receiving side
_Events_Per_Exchange = 4

# Column indexes: Time, CID, Event, Partner, Message id, Conversation id, Outcome, Size, Data preview
_Column_Time            = 0
_Column_CID             = 1
_Column_Event           = 2
_Column_Partner         = 3
_Column_Msg_ID          = 4
_Column_Conversation_ID = 5
_Column_Outcome         = 6

# What an event that went through says
_Outcome_Ok = 'ok'

# How long to keep retrying an invocation while a UI change propagates to the server
_Propagation_Timeout = 60

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# How long an edit needs before the channel runtime and the outgoing wrapper are rebuilt
_Rebuild_Delay = 5.0

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

def _new_exchange(
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
        'service': _Receiver_Service,
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

def _delete_exchange(page:'Page', exchange:'anydict') -> 'None':
    """ Takes down both sides of one loopback pair - both helpers find their own page first,
    so this works no matter where the browser was left.
    """

    delete_as4_outconn(page, exchange['outconn_id'])
    delete_as4_channel(page, exchange['channel_id'])

# ################################################################################################################################

def _get_rows(page:'Page') -> 'anylist':
    """ Returns all rows currently shown in the audit log table.
    """
    out = page.query_selector_all('#audit-log-table-body tr')
    return out

# ################################################################################################################################

def _get_row_cells(row:'any_') -> 'anylist':
    """ Returns the text of each cell in one audit log row.
    """
    out = [] # type: anylist

    for cell in row.query_selector_all('td'):
        out.append(cell.inner_text().strip())

    return out

# ################################################################################################################################

def _get_events_by_type(page:'Page') -> 'anydict':
    """ Returns the cells of every row currently shown, keyed by the event type of the row.
    """

    # Our response to produce
    out:'anydict' = {}

    for row in _get_rows(page):
        cells = _get_row_cells(row)
        out[cells[_Column_Event]] = cells

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

        _wait_for_invoker_service(page, base_url)

        # The parties are unique per run so only this test's events show up.
        suffix = CryptoManager.generate_hex_string()
        from_party = f'party-a-{suffix}'
        to_party = f'party-b-{suffix}'
        pair = f'{from_party}:{to_party}'

        name = _Test_Name_Prefix + 'columns'
        exchange = _new_exchange(page, base_url, server_port, name, from_party, to_party)

        try:
            payload = '<Document xmlns="urn:test"><Value>' + CryptoManager.generate_hex_string() + '</Value></Document>'
            result = _send_with_retry(page, base_url, name, payload)
            assert result['is_ok'], f'Expected a verified receipt, got: {result}'

            # The page pre-filtered to this party pair ..
            row_count = get_audit_row_count(page, base_url, _Audit_Source, pair)

            # .. shows all four events of the exchange, both halves of both sides ..
            assert row_count == _Events_Per_Exchange, \
                f'Expected {_Events_Per_Exchange} audit log rows, got {row_count}'

            # .. under a title naming the source, compared case-insensitively because of CSS styling ..
            title_text = page.inner_text('#detail-section-title')
            title_text = title_text.lower()
            assert title_text.startswith(_AS4_Title), \
                f'Expected the title to start with "{_AS4_Title}", got: "{title_text}"'

            # .. with the party pair in the title pill ..
            pill_text = page.inner_text('#detail-section-title .detail-component-pill')
            pill_text = pill_text.lower()
            assert pill_text == pair.lower(), f'Expected pair "{pair}" in the pill, got: "{pill_text}"'

            # .. and the AS4 columns in the header, compared case-insensitively
            # .. because the headers are uppercased with CSS.
            header_text = page.inner_text('#audit-log-table thead')
            header_text = header_text.lower()
            assert 'partner' in header_text, f'Expected a Partner column, got: "{header_text}"'
            assert 'message id' in header_text, f'Expected a Message id column, got: "{header_text}"'
            assert 'conversation id' in header_text, f'Expected a Conversation id column, got: "{header_text}"'

            events = _get_events_by_type(page)

            expected_events = {
                _Event_Message_Sent,
                _Event_Receipt_Received,
                _Event_Message_Received,
                _Event_Receipt_Sent,
            }

            assert set(events) == expected_events, f'Expected the four events of one exchange, got: {sorted(events)}'

            # Every event is filed under the pair and names the message it belongs to ..
            for event_type, cells in events.items():

                assert cells[_Column_Partner] == pair, \
                    f'Expected partner "{pair}" on {event_type}, got: "{cells[_Column_Partner]}"'

                assert cells[_Column_Msg_ID] == result['message_id'], \
                    f'Expected message id "{result["message_id"]}" on {event_type}, got: "{cells[_Column_Msg_ID]}"'

                assert cells[_Column_Outcome] == _Outcome_Ok, \
                    f'Expected outcome "{_Outcome_Ok}" on {event_type}, got: "{cells[_Column_Outcome]}"'

                assert cells[_Column_CID] != '', f'Expected a correlation id on {event_type}'

                # The times are shown in the browser's locale format, not as raw ISO strings.
                assert cells[_Column_Time] != '', f'Expected a non-empty event time on {event_type}'
                assert '+00:00' not in cells[_Column_Time], \
                    f'Expected a locale-formatted time on {event_type}, got: "{cells[_Column_Time]}"'

            # .. and the user message events carry the conversation their exchange belongs to.
            sent_cells = events[_Event_Message_Sent]
            received_cells = events[_Event_Message_Received]

            assert sent_cells[_Column_Conversation_ID] != '', 'Expected a conversation id on the sent message'
            assert sent_cells[_Column_Conversation_ID] == received_cells[_Column_Conversation_ID], \
                'Expected both sides of the exchange to record the same conversation id'

        finally:
            _delete_exchange(page, exchange)

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_AS4_Log_Patterns)
    def test_link_from_connection_list(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        _wait_for_invoker_service(page, base_url)

        suffix = CryptoManager.generate_hex_string()
        from_party = f'party-a-{suffix}'
        to_party = f'party-b-{suffix}'
        pair = f'{from_party}:{to_party}'

        name = _Test_Name_Prefix + 'link'
        exchange = _new_exchange(page, base_url, server_port, name, from_party, to_party)

        try:
            payload = '<Document xmlns="urn:test"><Value>linked</Value></Document>'
            result = _send_with_retry(page, base_url, name, payload)
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

            cells = events[_Event_Message_Sent]
            assert cells[_Column_Msg_ID] == result['message_id'], \
                f'Expected message id "{result["message_id"]}", got: "{cells[_Column_Msg_ID]}"'

        finally:
            _delete_exchange(page, exchange)

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

        _wait_for_invoker_service(page, base_url)

        suffix = CryptoManager.generate_hex_string()
        from_party = f'party-a-{suffix}'
        to_party = f'party-b-{suffix}'
        pair = f'{from_party}:{to_party}'

        name = _Test_Name_Prefix + 'toggle'
        exchange = _new_exchange(page, base_url, server_port, name, from_party, to_party)

        channel_id = exchange['channel_id']
        outconn_id = exchange['outconn_id']

        try:
            # One exchange with the toggle on, which is what a new pair starts with ..
            payload = '<Document xmlns="urn:test"><Value>toggle-on</Value></Document>'
            result = _send_with_retry(page, base_url, name, payload)
            assert result['is_ok'], f'Expected a verified receipt with the toggle on, got: {result}'

            baseline = get_audit_row_count(page, base_url, _Audit_Source, pair)
            assert baseline == _Events_Per_Exchange, \
                f'Expected {_Events_Per_Exchange} audit log rows with the toggle on, got {baseline}'

            # .. then turn the toggle off on both sides of the exchange and let the change reach the server ..
            open_as4_outconn_page(page, base_url, query=name)
            edit_as4_outconn(page, outconn_id, {'is_audit_log_active': False})

            open_as4_channel_page(page, base_url, query=name)
            edit_as4_channel(page, channel_id, {'is_audit_log_active': False})

            time.sleep(_Rebuild_Delay)

            # .. the message still travels end to end but nothing new is recorded ..
            result = _send_with_retry(page, base_url, name, payload)
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

            result = _send_with_retry(page, base_url, name, payload)
            assert result['is_ok'], f'Expected a verified receipt with the toggle back on, got: {result}'

            row_count = get_audit_row_count(page, base_url, _Audit_Source, pair)
            expected = baseline + _Events_Per_Exchange
            assert row_count == expected, \
                f'Expected {expected} audit log rows after turning the toggle back on, got {row_count}'

        finally:
            _delete_exchange(page, exchange)

# ################################################################################################################################
# ################################################################################################################################
