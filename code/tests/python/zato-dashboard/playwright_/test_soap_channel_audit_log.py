# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import time
from urllib.parse import quote

# pytest
import pytest

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.soap.client import SOAPClient
from zato.common.soap.common import SOAPFault, SOAPVersion
from zato.common.soap.message import SOAPMessage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

from audit_log_ui import attach_diagnostics, format_diagnostics, get_row_cid, get_row_event, get_row_main_text, \
    get_row_outcome, get_row_time_text, get_rows, goto_audit_log, close_cid_overlay, open_cid_overlay, open_data, \
    search, wait_for_empty, wait_for_payload_text, wait_for_row_count, wait_for_table

from soap_channel import create_soap_channel, open_soap_channel_page, wait_for_channel_fixture_services

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.soap.audit.' + CryptoManager.generate_hex_string(32) + '.'

# The fixture services this suite's channels point to, deployed during server boot
_Echo_Service   = 'test.soap.channel.echo'
_Faulty_Service = 'test.soap.channel.faulty'

# The SOAPAction the echo service's operation is invoked with
_Echo_SOAP_Action = 'urn:cdc:iisb:2014:connectivityTest'
_Echo_Namespace   = 'urn:cdc:iisb:2014'
_Echo_Operation   = 'connectivityTest'

_Audit_Log_URL_Prefix = '/zato/audit-log/'

_Source = 'soap-channel'

# How the events of one invocation read on their rows
_Event_Request_Received_Label = 'Request received'
_Event_Response_Sent_Label    = 'Response sent'

_Outcome_OK    = 'ok'
_Outcome_Error = 'error'

# The section title for the SOAP channel source, compared lowercase because the heading is styled with CSS
_SOAP_Channel_Title = 'soap channel audit log'

# How long to keep retrying an invocation while a UI change propagates to the server
_Propagation_Timeout = 30

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# ################################################################################################################################
# ################################################################################################################################

def _new_channel_client(server_port:'int', url_path:'str') -> 'SOAPClient':
    """ Returns a SOAP client pointed at a channel of the server under test - exactly
    what an external SOAP counterparty is.
    """

    client_config = {
        'address': f'http://127.0.0.1:{server_port}{url_path}',
        'timeout': 10,
        'soap_version': SOAPVersion.V11,
        'soap_action': _Echo_SOAP_Action,
    } # type: anydict

    out = SOAPClient(client_config)
    return out

# ################################################################################################################################

def _invoke_with_retry(client:'SOAPClient', operation:'str', message:'SOAPMessage') -> 'any_':
    """ Invokes a channel, retrying while the configuration made a moment ago in the browser
    propagates to the server - until then the URL is unknown, so parse errors are retried.
    """

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            out = client.invoke(operation, message)
        except Exception as invoke_error:
            last_error = invoke_error
            time.sleep(_Propagation_Poll_Interval)
        else:
            return out

    raise Exception(f'Could not invoke `{client.address}` within {_Propagation_Timeout}s, last error: {last_error!r}')

# ################################################################################################################################

def _invoke_expecting_fault(client:'SOAPClient', operation:'str', message:'SOAPMessage') -> 'SOAPFault':
    """ Invokes a channel and returns the SOAP fault it answered with, retrying other errors
    while the channel configured a moment ago in the browser propagates to the server.
    """

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:
        try:
            response = client.invoke(operation, message)
        except SOAPFault as fault:
            return fault
        except Exception as invoke_error:
            last_error = invoke_error
            time.sleep(_Propagation_Poll_Interval)
        else:
            raise Exception(f'Expected a fault from `{client.address}`, got: {response!r}')

    raise Exception(f'No fault from `{client.address}` within {_Propagation_Timeout}s, last error: {last_error!r}')

# ################################################################################################################################

def _create_echo_channel(page:'Page', base_url:'str', name_suffix:'str') -> 'anydict':
    """ Creates a SOAP channel pointing at the echo service and returns its details.
    """

    channel_name = _Test_Name_Prefix + name_suffix
    url_path = '/' + channel_name

    channel_id = create_soap_channel(page, base_url, channel_name, _Echo_Service, url_path, {
        'soap_action': _Echo_SOAP_Action,
    })

    out = {
        'id': channel_id,
        'name': channel_name,
        'url_path': url_path,
    }

    return out

# ################################################################################################################################

def _invoke_echo(server_port:'int', url_path:'str', marker:'str') -> 'None':
    """ Invokes a SOAP channel with an echoBack marker, waiting out the short window
    between the channel's creation in the UI and its propagation to the server.
    The marker travels in both the request and the response envelope, which is
    what the audit log stores for each direction.
    """

    message = SOAPMessage()
    message.namespace = _Echo_Namespace
    message.echoBack = marker

    client = _new_channel_client(server_port, url_path)

    try:
        response = _invoke_with_retry(client, _Echo_Operation, message)
        echoed = response.connectivityTestResponse.echoed
        assert echoed == marker, f'Expected the echo back "{marker}", got: {echoed!r}'
    finally:
        client.close()

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPChannelAuditLog:
    """ Live tests for the SOAP channel audit log page, driven by real SOAP requests to real channels.
    """

    def test_invoke_creates_events(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)

        # Create a channel and invoke it once over live SOAP ..
        channel = _create_echo_channel(page, base_url, 'events')
        _invoke_echo(server_port, channel['url_path'], 'single-invocation')

        # .. open the audit log page for that channel ..
        goto_audit_log(page, base_url, _Source, channel['name'])

        # .. the section title names the source, compared case-insensitively because of CSS styling ..
        title_text = page.inner_text('#detail-section-title')
        title_text = title_text.lower()
        assert title_text.startswith(_SOAP_Channel_Title), \
            f'Expected the title to start with "{_SOAP_Channel_Title}", got: "{title_text}"'

        # .. the section title pill shows the channel name, compared case-insensitively
        # .. because the pill is uppercased with CSS ..
        pill_text = page.inner_text('#detail-section-title .detail-component-pill')
        pill_text = pill_text.lower()
        assert pill_text == channel['name'], f'Expected channel name "{channel["name"]}" in the pill, got: "{pill_text}"'

        # .. one invocation produces exactly two events ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the newest event is the response, the older one is the request ..
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Response_Sent_Label, \
            f'Expected event "{_Event_Response_Sent_Label}", got: "{event_label}"'

        event_label = get_row_event(rows[1])
        assert event_label == _Event_Request_Received_Label, \
            f'Expected event "{_Event_Request_Received_Label}", got: "{event_label}"'

        # .. both events point at the channel's service and completed fine ..
        for row in rows:

            main_text = get_row_main_text(row)
            assert _Echo_Service in main_text, f'Expected the service "{_Echo_Service}" on the row, got: "{main_text}"'

            # .. the time is shown in the browser's locale format, not as a raw ISO string ..
            time_text = get_row_time_text(row)
            assert time_text != '', 'Expected a non-empty event time'
            assert '+00:00' not in time_text, f'Expected a locale-formatted time, got a raw ISO string: "{time_text}"'

            outcome = get_row_outcome(page, row)
            assert outcome == _Outcome_OK, f'Expected outcome "{_Outcome_OK}", got: "{outcome}"'

            # .. the raw envelope as it was on the wire is read in the pane's Data tab ..
            open_data(page, row)
            wait_for_payload_text(page, 'Envelope')

        # .. the request's CID opens the complete envelope, which carries the marker ..
        request_envelope = open_cid_overlay(page, rows[1])
        assert 'single-invocation' in request_envelope, \
            f'Expected the marker in the complete request, got: "{request_envelope}"'
        close_cid_overlay(page)

        # .. and so does the response's.
        response_envelope = open_cid_overlay(page, rows[0])
        assert 'single-invocation' in response_envelope, \
            f'Expected the marker in the complete response, got: "{response_envelope}"'
        close_cid_overlay(page)

# ################################################################################################################################

    def test_link_from_channel_list(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)

        # Create a channel and invoke it once over live SOAP ..
        channel = _create_echo_channel(page, base_url, 'from-list')
        _invoke_echo(server_port, channel['url_path'], 'from-channel-list')

        # .. go back to the SOAP channels page ..
        open_soap_channel_page(page, base_url)

        # .. click the audit log link in this channel's row ..
        row_selector = f'#data-table tbody tr:has(span.name-value:text-is("{channel["name"]}"))'
        page.click(f'{row_selector} a:text-is("Audit log")')

        # .. wait for the audit log page to load ..
        page.wait_for_url(f'**{_Audit_Log_URL_Prefix}**')
        wait_for_table(page)

        # .. the URL points to the audit log page for this channel ..
        assert _Audit_Log_URL_Prefix in page.url, f'Expected an audit log URL, got: "{page.url}"'
        assert 'source=soap-channel' in page.url, f'Expected source=soap-channel in the URL, got: "{page.url}"'
        assert quote(channel['name']) in page.url, f'Expected the channel name in the URL, got: "{page.url}"'

        # .. and the invocation's events are shown ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. carrying this invocation's marker in the complete request.
        request_envelope = open_cid_overlay(page, rows[1])
        assert 'from-channel-list' in request_envelope, \
            f'Expected the marker in the complete request, got: "{request_envelope}"'
        close_cid_overlay(page)

# ################################################################################################################################

    def test_events_share_cid_newest_first(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)

        # Create a channel and invoke it twice, in a known order ..
        channel = _create_echo_channel(page, base_url, 'ordering')
        _invoke_echo(server_port, channel['url_path'], 'first-invocation')
        _invoke_echo(server_port, channel['url_path'], 'second-invocation')

        # .. open the audit log page ..
        goto_audit_log(page, base_url, _Source, channel['name'])

        # .. both invocations are shown, two events each ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 4, f'Expected 4 audit log rows, got {row_count}'

        # .. the newest invocation comes first - the markers travel inside the envelopes,
        # .. which only the complete messages behind the CID links reveal ..
        newest_request_envelope = open_cid_overlay(page, rows[1])
        assert 'second-invocation' in newest_request_envelope, \
            f'Expected the newest marker first, got: "{newest_request_envelope}"'
        close_cid_overlay(page)

        oldest_request_envelope = open_cid_overlay(page, rows[3])
        assert 'first-invocation' in oldest_request_envelope, \
            f'Expected the oldest marker last, got: "{oldest_request_envelope}"'
        close_cid_overlay(page)

        # .. within one invocation the response comes before the request ..
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Response_Sent_Label, \
            f'Expected event "{_Event_Response_Sent_Label}", got: "{event_label}"'

        event_label = get_row_event(rows[1])
        assert event_label == _Event_Request_Received_Label, \
            f'Expected event "{_Event_Request_Received_Label}", got: "{event_label}"'

        # .. the request and response of one invocation share the same CID ..
        response_cid = get_row_cid(page, rows[0])
        request_cid = get_row_cid(page, rows[1])
        assert response_cid == request_cid, \
            f'Expected one shared CID, got: "{response_cid}" and "{request_cid}"'

        # .. and separate invocations carry separate CIDs.
        oldest_cid = get_row_cid(page, rows[3])
        assert response_cid != oldest_cid, f'Expected distinct CIDs across invocations, got: "{response_cid}" twice'

# ################################################################################################################################

    def test_search_filters_rows(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)

        # Record everything the browser and Django report during this test ..
        diagnostics = attach_diagnostics(page)

        # .. create a channel and invoke it with three distinct markers ..
        channel = _create_echo_channel(page, base_url, 'search')
        _invoke_echo(server_port, channel['url_path'], 'invoice-created')
        _invoke_echo(server_port, channel['url_path'], 'invoice-paid')
        _invoke_echo(server_port, channel['url_path'], 'invoice-cancelled')

        # .. open the audit log page and confirm all six events are there ..
        goto_audit_log(page, base_url, _Source, channel['name'])

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 6, f'Expected 6 audit log rows, got {row_count}'

        # .. the search runs over the complete stored envelopes, so one marker matches
        # .. its invocation's request and response ..
        search(page, 'invoice-paid')
        wait_for_row_count(page, 2, diagnostics)

        # .. and the complete request behind the CID carries the matching marker ..
        rows = get_rows(page)
        request_envelope = open_cid_overlay(page, rows[1])
        assert 'invoice-paid' in request_envelope, \
            f'Expected the matching marker in the complete request, got: "{request_envelope}"'
        close_cid_overlay(page)

        # .. a query matching nothing shows the empty placeholder ..
        search(page, 'no-such-payload-anywhere')
        wait_for_empty(page, diagnostics)

        # .. clearing the query brings all six events back ..
        search(page, '')
        wait_for_row_count(page, 6, diagnostics)

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{format_diagnostics(diagnostics)}'

# ################################################################################################################################

    def test_cid_opens_complete_message(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)

        # Record everything the browser and Django report during this test ..
        diagnostics = attach_diagnostics(page)

        # .. build a marker long enough that no row could ever show it whole ..
        marker_parts:'strlist' = []

        for item_index in range(20):
            marker_parts.append(f'line-{item_index}-product-test-product-{item_index}-quantity-2')

        long_marker = 'order-test-order-1-' + '-'.join(marker_parts)

        # .. create a channel and invoke it with that marker ..
        channel = _create_echo_channel(page, base_url, 'complete')
        _invoke_echo(server_port, channel['url_path'], long_marker)

        # .. open the audit log page ..
        goto_audit_log(page, base_url, _Source, channel['name'])

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the row itself carries no envelope - the message is read in the pane ..
        request_row = rows[1]
        main_text = get_row_main_text(request_row)
        assert long_marker not in main_text, f'Expected no envelope on the row, got: "{main_text}"'

        # .. while the overlay behind the request's CID holds the envelope in full.
        editor_value = open_cid_overlay(page, request_row)

        assert long_marker in editor_value, \
            f'Expected the complete marker in the overlay, got: "{editor_value}"'
        assert 'Envelope' in editor_value, \
            f'Expected the complete envelope in the overlay, got: "{editor_value}"'

        close_cid_overlay(page)

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{format_diagnostics(diagnostics)}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors('An internal detail that must never reach the wire')
    def test_error_outcome(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)

        # Create a channel pointing at the always-raising fixture service ..
        channel_name = _Test_Name_Prefix + 'error'
        url_path = '/' + channel_name

        _ = create_soap_channel(page, base_url, channel_name, _Faulty_Service, url_path, {
            'soap_action': _Echo_SOAP_Action,
        })

        # .. invoke the channel and let the service raise, which the channel
        # .. turns into a Receiver fault on the wire ..
        message = SOAPMessage()
        message.namespace = _Echo_Namespace
        message.echoBack = 'error-outcome'

        client = _new_channel_client(server_port, url_path)

        try:
            fault = _invoke_expecting_fault(client, _Echo_Operation, message)
            assert fault.code == 'Server', f'Expected a Server fault, got: {fault.code} {fault.reason}'
        finally:
            client.close()

        # .. open the audit log page ..
        goto_audit_log(page, base_url, _Source, channel_name)

        # .. the invocation produced its two events ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the request itself was received fine ..
        event_label = get_row_event(rows[1])
        assert event_label == _Event_Request_Received_Label, \
            f'Expected event "{_Event_Request_Received_Label}", got: "{event_label}"'

        outcome = get_row_outcome(page, rows[1])
        assert outcome == _Outcome_OK, f'Expected outcome "{_Outcome_OK}", got: "{outcome}"'

        # .. while the response carries the error outcome ..
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Response_Sent_Label, \
            f'Expected event "{_Event_Response_Sent_Label}", got: "{event_label}"'

        outcome = get_row_outcome(page, rows[0])
        assert outcome == _Outcome_Error, f'Expected outcome "{_Outcome_Error}", got: "{outcome}"'

        # .. and the complete response is the fault envelope that went out on the wire.
        response_envelope = open_cid_overlay(page, rows[0])
        assert 'Fault' in response_envelope, \
            f'Expected a fault envelope in the complete response, got: "{response_envelope}"'
        close_cid_overlay(page)

# ################################################################################################################################
# ################################################################################################################################
