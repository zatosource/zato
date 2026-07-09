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

# Playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.soap.client import SOAPClient
from zato.common.soap.common import SOAPFault, SOAPVersion
from zato.common.soap.message import SOAPMessage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

from soap_channel import create_soap_channel, wait_for_channel_fixture_services
from soap_outconn import create_soap_outconn, invoke_soap_outconn_from_ide, open_soap_outconn_page, ping_soap_outconn, \
    wait_for_soap_invoker_service

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.soap.outconn.audit.' + CryptoManager.generate_hex_string(32) + '.'

# The fixture services behind the loopback channels, deployed during server boot
_Echo_Service   = 'test.soap.channel.echo'
_Faulty_Service = 'test.soap.channel.faulty'

# The SOAPAction the echo service's operation is invoked with
_Echo_Soap_Action = 'urn:cdc:iisb:2014:connectivityTest'
_Echo_Namespace   = 'urn:cdc:iisb:2014'
_Echo_Operation   = 'connectivityTest'

_Audit_Log_Url_Prefix = '/zato/audit-log/'
_Poll_Url_Path        = '/zato/audit-log/poll/'

_Event_Request_Sent      = 'request-sent'
_Event_Response_Received = 'response-received'

_Outcome_OK    = 'ok'
_Outcome_Error = 'error'

_No_Events_Text = 'No events found'

# The section title for the outgoing SOAP source, compared lowercase because the heading is styled with CSS
_SOAP_Outgoing_Title = 'outgoing soap audit log'

# Column indexes: Time, CID, Event, Endpoint, Outcome, Size, Data preview
_Column_Time     = 0
_Column_CID      = 1
_Column_Event    = 2
_Column_Endpoint = 3
_Column_Outcome  = 4
_Column_Size     = 5
_Column_Data     = 6

# A TCP port that nothing listens on, for connections that must fail
_Dead_Port = 1

# How long to keep retrying an invocation while a UI change propagates to the server
_Propagation_Timeout = 30

# How long to sleep between the attempts above
_Propagation_Poll_Interval = 1.0

# Log patterns produced when an invocation cannot reach its target
_Connection_Failure_Log_Patterns = ('Connection refused', 'NewConnectionError', 'Max retries exceeded', 'ConnectionError')

# ################################################################################################################################
# ################################################################################################################################

def _goto_audit_log(page:'Page', base_url:'str', outconn_name:'str') -> 'None':
    """ Navigates to the audit log page of one outgoing SOAP connection and waits for the first page of events to load.
    """

    # Build the per-object URL ..
    encoded_name = quote(outconn_name)
    url = f'{base_url}{_Audit_Log_Url_Prefix}?source=soap-outgoing&object_name={encoded_name}&cluster=1'

    # .. go there ..
    _ = page.goto(url)

    # .. and wait for the initial poll to replace the loading row.
    _wait_for_table(page)

# ################################################################################################################################

def _wait_for_table(page:'Page') -> 'None':
    """ Waits until the audit log table has finished loading its current page of events,
    i.e. until the table body exists, has rows and none of them is the loading placeholder.
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

def _attach_diagnostics(page:'Page') -> 'anydict':
    """ Captures everything the browser and Django report while a test runs - console messages,
    uncaught page errors, failed requests and the full body of each poll response.
    """

    # All the captured facts go here ..
    out = {
        'console': [],
        'page_errors': [],
        'failed_requests': [],
        'poll_responses': [],
    } # type: anydict

    # .. every console message is recorded with its severity ..
    def _on_console(message:'any_') -> 'None':
        out['console'].append(f'[console.{message.type}] {message.text}')

    # .. uncaught JavaScript exceptions are recorded in full ..
    def _on_page_error(error:'any_') -> 'None':
        out['page_errors'].append(f'[pageerror] {error}')

    # .. requests that never completed are recorded with their failure reason, except for
    # .. requests aborted by navigation, e.g. the session keepalive ping, which are not errors ..
    def _on_request_failed(request:'any_') -> 'None':
        if request.failure != 'net::ERR_ABORTED':
            out['failed_requests'].append(f'[requestfailed] {request.method} {request.url} -> {request.failure}')

    # .. and each poll response is recorded with its status and body, which is what Django returned.
    def _on_response(response:'any_') -> 'None':
        if _Poll_Url_Path in response.url:
            body = response.text()
            out['poll_responses'].append(f'[poll] {response.status} {response.url} -> {body}')

    page.on('console', _on_console)
    page.on('pageerror', _on_page_error)
    page.on('requestfailed', _on_request_failed)
    page.on('response', _on_response)

    return out

# ################################################################################################################################

def _format_diagnostics(diagnostics:'anydict') -> 'str':
    """ Turns the captured diagnostics into one readable block for assertion messages.
    """

    lines = [] # type: anylist

    for key in ('page_errors', 'failed_requests', 'console', 'poll_responses'):
        for entry in diagnostics[key]:
            lines.append(entry)

    out = '\n'.join(lines)
    return out

# ################################################################################################################################

def _search(page:'Page', query:'str') -> 'None':
    """ Types a query into the audit log search form and submits it with the search button.
    """

    # Fill in the query ..
    page.fill('#audit-log-search-input', query)

    # .. and submit the form.
    page.click('#audit-log-search-form button[type="submit"]')

# ################################################################################################################################

def _wait_for_row_count(page:'Page', count:'int', diagnostics:'anydictnone' = None) -> 'None':
    """ Waits until the audit log table shows exactly that many event rows. A SOAP envelope's
    preview never contains the payload markers - the envelope prefix alone exceeds the preview
    length - so search results are awaited by row count rather than by visible text.
    On timeout, the assertion message includes everything the browser and Django reported.
    """
    try:
        _ = page.wait_for_function(
            f'''() => {{
                let body = document.querySelector('#audit-log-table-body');
                let rows = body.querySelectorAll('tr');
                if (body.querySelector('tr.detail-loading-row')) return false;
                return rows.length === {count};
            }}''',
            timeout=10000)
    except PlaywrightTimeoutError:
        body_text = page.inner_text('#audit-log-table-body')
        details = _format_diagnostics(diagnostics) if diagnostics else '(no diagnostics attached)'
        pytest.fail(f'Timed out waiting for {count} rows, the table shows:\n{body_text}\n\nDiagnostics:\n{details}')

# ################################################################################################################################

def _wait_for_body_text(page:'Page', text:'str', diagnostics:'anydictnone' = None) -> 'None':
    """ Waits until the audit log table body contains the given text.
    On timeout, the assertion message includes everything the browser and Django reported.
    """
    try:
        _ = page.wait_for_function(
            f'document.querySelector("#audit-log-table-body").innerText.includes(\'{text}\')', timeout=10000)
    except PlaywrightTimeoutError:
        body_text = page.inner_text('#audit-log-table-body')
        details = _format_diagnostics(diagnostics) if diagnostics else '(no diagnostics attached)'
        pytest.fail(f'Timed out waiting for "{text}" in the table, the table shows:\n{body_text}\n\nDiagnostics:\n{details}')

# ################################################################################################################################

def _open_cid_overlay(page:'Page', row:'any_') -> 'str':
    """ Clicks the CID link of one row and returns the complete message the overlay shows,
    read through the Ace API because Ace renders only the visible part of the text into the DOM.
    """

    # Open the overlay ..
    cid_link = row.query_selector('a.audit-log-cid-link')
    assert cid_link is not None, 'Expected the CID cell to be a link'
    cid_link.click()
    _ = page.wait_for_selector('#zato-highlight-pane-overlay:not(.hidden)', state='visible', timeout=10000)

    # .. and read the editor's full contents.
    out = page.evaluate(
        '''() => {
            let element = document.querySelector('#zato-highlight-pane-overlay .zato-highlight-pane-editor');
            return ace.edit(element).getValue();
        }''')

    return out

# ################################################################################################################################

def _close_cid_overlay(page:'Page') -> 'None':
    """ Closes the complete message overlay and waits for it to disappear.
    """
    page.evaluate('$.fn.zato.highlight_pane.close_overlay()')
    _ = page.wait_for_selector('#zato-highlight-pane-overlay', state='hidden', timeout=5000)

# ################################################################################################################################

def _warm_up_channel(server_port:'int', url_path:'str', service_name:'str') -> 'None':
    """ Invokes a freshly created loopback channel directly, the way an external counterparty
    would, until it responds - so later invocations through the outgoing connection never hit
    a channel that has not propagated to the server yet. A channel of the faulty service is
    ready once it answers with its fault.
    """

    client_config = {
        'address': f'http://127.0.0.1:{server_port}{url_path}',
        'timeout': 10,
        'soap_version': SOAPVersion.V11,
        'soap_action': _Echo_Soap_Action,
    } # type: anydict

    client = SOAPClient(client_config)

    message = SOAPMessage()
    message.namespace = _Echo_Namespace
    message.echoBack = 'channel-warm-up'

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    try:
        while time.monotonic() < deadline:
            try:
                _ = client.invoke(_Echo_Operation, message)
            except SOAPFault:

                # A fault of the faulty service proves the channel is live.
                if service_name == _Faulty_Service:
                    return
                raise
            except Exception as invoke_error:
                last_error = invoke_error
                time.sleep(_Propagation_Poll_Interval)
            else:
                return

        raise Exception(f'Channel `{url_path}` did not propagate within {_Propagation_Timeout}s, last error: {last_error!r}')
    finally:
        client.close()

# ################################################################################################################################

def _create_ready_pair(
    page:'Page',
    base_url:'str',
    server_port:'int',
    name_suffix:'str',
    service_name:'str'=_Echo_Service,
    ) -> 'anydict':
    """ Creates a loopback pair - a SOAP channel on a fixture service and an outgoing
    connection pointed back at it - with the channel warmed up so invocations through
    the connection only ever meet a live endpoint.
    """

    name = _Test_Name_Prefix + name_suffix
    url_path = '/' + name

    # The channel comes first and is warmed up before the connection points at it ..
    _ = create_soap_channel(page, base_url, name, service_name, url_path, {
        'soap_action': _Echo_Soap_Action,
    })

    _warm_up_channel(server_port, url_path, service_name)

    # .. now the outgoing connection back at that channel.
    outconn_id = create_soap_outconn(page, base_url, name, f'http://127.0.0.1:{server_port}', {
        'url_path': url_path,
        'soap_action': _Echo_Soap_Action,
    })

    out = {
        'id': outconn_id,
        'name': name,
        'url_path': url_path,
        'address': f'http://127.0.0.1:{server_port}{url_path}',
    }

    return out

# ################################################################################################################################

def _invoke_echo_via_outconn(page:'Page', base_url:'str', outconn_name:'str', marker:'str') -> 'None':
    """ Invokes the loopback pair once through the pre-deployed invoker service, retrying
    while the freshly created connection propagates to the server. Until then the service
    reports the connection as unknown without ever reaching the wrapper, so the one
    invocation that succeeds is also the only one that is audited.
    """

    deadline = time.monotonic() + _Propagation_Timeout
    last_error = None

    while time.monotonic() < deadline:

        result = invoke_soap_outconn_from_ide(page, base_url, outconn_name, _Echo_Operation,
            namespace=_Echo_Namespace,
            fields={'echoBack': marker},
            response_fields=['echoed'],
        )

        if 'fields' in result:
            echoed = result['fields']['echoed']
            assert echoed == marker, f'Expected the echo back "{marker}", got: {result}'
            return

        last_error = result
        time.sleep(_Propagation_Poll_Interval)

    raise Exception(f'Could not invoke `{outconn_name}` within {_Propagation_Timeout}s, last error: {last_error}')

# ################################################################################################################################
# ################################################################################################################################

class TestSOAPOutconnAuditLog:
    """ Live tests for the outgoing SOAP connection audit log page - each connection is
    configured through the browser and exercised by real SOAP traffic against a loopback
    channel of the same server.
    """

    def test_invoke_creates_events(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Create a loopback pair and invoke it once ..
        outconn = _create_ready_pair(page, base_url, server_port, 'events')
        _invoke_echo_via_outconn(page, base_url, outconn['name'], 'single-invocation')

        # .. open the audit log page for that connection ..
        _goto_audit_log(page, base_url, outconn['name'])

        # .. the section title names the source, compared case-insensitively because of CSS styling ..
        title_text = page.inner_text('#detail-section-title')
        title_text = title_text.lower()
        assert title_text.startswith(_SOAP_Outgoing_Title), \
            f'Expected the title to start with "{_SOAP_Outgoing_Title}", got: "{title_text}"'

        # .. the section title pill shows the connection name, compared case-insensitively
        # .. because the pill is uppercased with CSS ..
        pill_text = page.inner_text('#detail-section-title .detail-component-pill')
        pill_text = pill_text.lower()
        assert pill_text == outconn['name'], f'Expected connection name "{outconn["name"]}" in the pill, got: "{pill_text}"'

        # .. the table shows the outgoing SOAP columns - there are Endpoint and Outcome columns
        # .. and no pub/sub Message id column, compared case-insensitively
        # .. because the headers are uppercased with CSS ..
        header_text = page.inner_text('#audit-log-table thead')
        header_text = header_text.lower()
        assert 'endpoint' in header_text, f'Expected an Endpoint column, got: "{header_text}"'
        assert 'outcome' in header_text, f'Expected an Outcome column, got: "{header_text}"'
        assert 'message id' not in header_text, f'Expected no Message id column, got: "{header_text}"'

        # .. one invocation produces exactly two events ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the newest event is the response, the older one is the request ..
        response_cells = _get_row_cells(rows[0])
        request_cells = _get_row_cells(rows[1])

        assert response_cells[_Column_Event] == _Event_Response_Received, \
            f'Expected event type "{_Event_Response_Received}", got: "{response_cells[_Column_Event]}"'
        assert request_cells[_Column_Event] == _Event_Request_Sent, \
            f'Expected event type "{_Event_Request_Sent}", got: "{request_cells[_Column_Event]}"'

        # .. both events carry the operation and the address invoked and completed fine ..
        expected_endpoint = f'{_Echo_Operation} {outconn["address"]}'

        for cells in (response_cells, request_cells):

            assert cells[_Column_Endpoint] == expected_endpoint, \
                f'Expected the endpoint "{expected_endpoint}", got: "{cells[_Column_Endpoint]}"'
            assert cells[_Column_Outcome] == _Outcome_OK, \
                f'Expected outcome "{_Outcome_OK}", got: "{cells[_Column_Outcome]}"'

            # .. the time is shown in the browser's locale format, not as a raw ISO string ..
            assert cells[_Column_Time] != '', 'Expected a non-empty event time'
            assert '+00:00' not in cells[_Column_Time], \
                f'Expected a locale-formatted time, got a raw ISO string: "{cells[_Column_Time]}"'

            size = int(cells[_Column_Size])
            assert size > 0, f'Expected a positive size, got {size}'

            # .. the preview holds the beginning of the raw envelope as it was on the wire.
            assert 'Envelope' in cells[_Column_Data], \
                f'Expected a SOAP envelope in the data preview, got: "{cells[_Column_Data]}"'

        # .. the request's CID opens the complete envelope, which carries the marker ..
        request_envelope = _open_cid_overlay(page, rows[1])
        assert 'single-invocation' in request_envelope, \
            f'Expected the marker in the complete request, got: "{request_envelope}"'
        _close_cid_overlay(page)

        # .. and so does the response's, echoed back by the loopback channel.
        response_envelope = _open_cid_overlay(page, rows[0])
        assert 'single-invocation' in response_envelope, \
            f'Expected the marker in the complete response, got: "{response_envelope}"'
        _close_cid_overlay(page)

# ################################################################################################################################

    def test_link_from_connection_list(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Create a loopback pair and invoke it once ..
        outconn = _create_ready_pair(page, base_url, server_port, 'from-list')
        _invoke_echo_via_outconn(page, base_url, outconn['name'], 'from-connection-list')

        # .. go back to the outgoing SOAP connections page ..
        open_soap_outconn_page(page, base_url)

        # .. click the audit log link in this connection's row ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{outconn["name"]}"))'
        page.click(f'{row_selector} a:text-is("Audit log")')

        # .. wait for the audit log page to load ..
        page.wait_for_url(f'**{_Audit_Log_Url_Prefix}**')
        _wait_for_table(page)

        # .. the URL points to the audit log page for this connection ..
        assert _Audit_Log_Url_Prefix in page.url, f'Expected an audit log URL, got: "{page.url}"'
        assert 'source=soap-outgoing' in page.url, f'Expected source=soap-outgoing in the URL, got: "{page.url}"'
        assert quote(outconn['name']) in page.url, f'Expected the connection name in the URL, got: "{page.url}"'

        # .. and the invocation's events are shown ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. carrying this invocation's marker in the complete request.
        request_envelope = _open_cid_overlay(page, rows[1])
        assert 'from-connection-list' in request_envelope, \
            f'Expected the marker in the complete request, got: "{request_envelope}"'
        _close_cid_overlay(page)

# ################################################################################################################################

    def test_events_share_cid_newest_first(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Create a loopback pair and invoke it twice, in a known order ..
        outconn = _create_ready_pair(page, base_url, server_port, 'ordering')
        _invoke_echo_via_outconn(page, base_url, outconn['name'], 'first-invocation')
        _invoke_echo_via_outconn(page, base_url, outconn['name'], 'second-invocation')

        # .. open the audit log page ..
        _goto_audit_log(page, base_url, outconn['name'])

        # .. both invocations are shown, two events each ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 4, f'Expected 4 audit log rows, got {row_count}'

        # .. the newest invocation comes first - the markers travel inside the envelopes,
        # .. which only the complete messages behind the CID links reveal ..
        first_row_cells = _get_row_cells(rows[0])
        second_row_cells = _get_row_cells(rows[1])
        last_row_cells = _get_row_cells(rows[3])

        newest_request_envelope = _open_cid_overlay(page, rows[1])
        assert 'second-invocation' in newest_request_envelope, \
            f'Expected the newest marker first, got: "{newest_request_envelope}"'
        _close_cid_overlay(page)

        oldest_request_envelope = _open_cid_overlay(page, rows[3])
        assert 'first-invocation' in oldest_request_envelope, \
            f'Expected the oldest marker last, got: "{oldest_request_envelope}"'
        _close_cid_overlay(page)

        # .. within one invocation the response comes before the request ..
        assert first_row_cells[_Column_Event] == _Event_Response_Received, \
            f'Expected event type "{_Event_Response_Received}", got: "{first_row_cells[_Column_Event]}"'
        assert second_row_cells[_Column_Event] == _Event_Request_Sent, \
            f'Expected event type "{_Event_Request_Sent}", got: "{second_row_cells[_Column_Event]}"'

        # .. the request and response of one invocation share the same CID ..
        assert first_row_cells[_Column_CID] == second_row_cells[_Column_CID], \
            f'Expected one shared CID, got: "{first_row_cells[_Column_CID]}" and "{second_row_cells[_Column_CID]}"'

        # .. and separate invocations carry separate CIDs.
        assert first_row_cells[_Column_CID] != last_row_cells[_Column_CID], \
            f'Expected distinct CIDs across invocations, got: "{first_row_cells[_Column_CID]}" twice'

# ################################################################################################################################

    def test_search_filters_rows(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Record everything the browser and Django report during this test ..
        diagnostics = _attach_diagnostics(page)

        # .. create a loopback pair and invoke it with three distinct markers - the echo
        # .. service sends each marker back, so both events of one call carry it ..
        outconn = _create_ready_pair(page, base_url, server_port, 'search')

        for marker in ('invoice-created', 'invoice-paid', 'invoice-cancelled'):
            _invoke_echo_via_outconn(page, base_url, outconn['name'], marker)

        # .. open the audit log page and confirm all six events are there ..
        _goto_audit_log(page, base_url, outconn['name'])

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 6, f'Expected 6 audit log rows, got {row_count}'

        # .. the search runs over the complete stored envelopes, so one marker matches
        # .. its invocation's request and response even though no preview shows it ..
        _search(page, 'invoice-paid')
        _wait_for_row_count(page, 2, diagnostics)

        # .. and the complete request behind the CID carries the matching marker ..
        rows = _get_rows(page)
        request_envelope = _open_cid_overlay(page, rows[1])
        assert 'invoice-paid' in request_envelope, \
            f'Expected the matching marker in the complete request, got: "{request_envelope}"'
        _close_cid_overlay(page)

        # .. a query matching nothing shows the empty placeholder ..
        _search(page, 'no-such-payload-anywhere')
        _wait_for_body_text(page, _No_Events_Text, diagnostics)

        # .. clearing the query brings all six events back ..
        _search(page, '')
        _wait_for_row_count(page, 6, diagnostics)

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{_format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{_format_diagnostics(diagnostics)}'

# ################################################################################################################################

    def test_cid_opens_complete_message(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Record everything the browser and Django report during this test ..
        diagnostics = _attach_diagnostics(page)

        # .. build a marker much longer than the 200-character preview shown in the table,
        # .. so it can never fit into the preview together with the envelope around it ..
        marker_parts:'strlist' = []

        for item_index in range(20):
            marker_parts.append(f'line-{item_index}-product-test-product-{item_index}-quantity-2')

        long_marker = 'order-test-order-1-' + '-'.join(marker_parts)

        # .. create a loopback pair and invoke it with that marker ..
        outconn = _create_ready_pair(page, base_url, server_port, 'complete')
        _invoke_echo_via_outconn(page, base_url, outconn['name'], long_marker)

        # .. open the audit log page ..
        _goto_audit_log(page, base_url, outconn['name'])

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the table shows only a truncated preview of the request envelope ..
        request_row = rows[1]
        cells = _get_row_cells(request_row)
        preview = cells[_Column_Data]
        assert long_marker not in preview, \
            f'Expected a truncated preview without the complete marker, got {len(preview)} characters'

        # .. while the overlay behind the request's CID holds the envelope in full.
        editor_value = _open_cid_overlay(page, request_row)

        assert long_marker in editor_value, \
            f'Expected the complete marker in the overlay, got: "{editor_value}"'
        assert 'Envelope' in editor_value, \
            f'Expected the complete envelope in the overlay, got: "{editor_value}"'

        _close_cid_overlay(page)

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{_format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{_format_diagnostics(diagnostics)}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*_Connection_Failure_Log_Patterns)
    def test_error_outcome(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A connection pointing at a closed port produces a response event
        with the error outcome and the connection error's details.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        wait_for_soap_invoker_service(page, base_url)

        outconn_name = _Test_Name_Prefix + 'error'
        url_path = '/' + outconn_name

        # Create a connection pointing at a port nothing listens on ..
        _ = create_soap_outconn(page, base_url, outconn_name, f'http://127.0.0.1:{_Dead_Port}', {
            'url_path': url_path,
            'soap_action': _Echo_Soap_Action,
        })

        # .. a dead connection cannot be warmed up, so the invocation is retried until
        # .. the connection error - rather than an unknown-connection one - arrives ..
        deadline = time.monotonic() + _Propagation_Timeout
        result = {} # type: anydict

        while time.monotonic() < deadline:

            result = invoke_soap_outconn_from_ide(page, base_url, outconn_name, _Echo_Operation,
                namespace=_Echo_Namespace,
                fields={'echoBack': 'error-outcome'},
            )

            if 'error' in result and 'Connection' in result['error']:
                break

            time.sleep(_Propagation_Poll_Interval)

        logger.info('[test_error_outcome] result=%s', result)

        assert 'Connection' in result['error'], f'Expected a connection error, got: {result}'

        # .. open the audit log page ..
        _goto_audit_log(page, base_url, outconn_name)

        # .. at least one invocation reached the wrapper, producing its two events ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count >= 2, f'Expected at least 2 audit log rows, got {row_count}'

        response_cells = _get_row_cells(rows[0])
        request_cells = _get_row_cells(rows[1])

        # .. the request itself was sent out fine ..
        assert request_cells[_Column_Event] == _Event_Request_Sent, \
            f'Expected event type "{_Event_Request_Sent}", got: "{request_cells[_Column_Event]}"'
        assert request_cells[_Column_Outcome] == _Outcome_OK, \
            f'Expected outcome "{_Outcome_OK}", got: "{request_cells[_Column_Outcome]}"'

        # .. while the response carries the error outcome with the connection error's details ..
        assert response_cells[_Column_Event] == _Event_Response_Received, \
            f'Expected event type "{_Event_Response_Received}", got: "{response_cells[_Column_Event]}"'
        assert response_cells[_Column_Outcome] == _Outcome_Error, \
            f'Expected outcome "{_Outcome_Error}", got: "{response_cells[_Column_Outcome]}"'
        assert 'Connection' in response_cells[_Column_Data], \
            f'Expected the connection error in the data preview, got: "{response_cells[_Column_Data]}"'

        # .. and both events share their invocation's CID.
        assert response_cells[_Column_CID] == request_cells[_Column_CID], \
            f'Expected one shared CID, got: "{response_cells[_Column_CID]}" and "{request_cells[_Column_CID]}"'

# ################################################################################################################################

    @pytest.mark.expect_log_errors('An internal detail that must never reach the wire')
    def test_fault_outcome(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A fault envelope arrives with an HTTP error status, so the response event
        carries the error outcome and the complete response shows the fault itself.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Create a loopback pair whose channel always answers with a Receiver fault ..
        outconn = _create_ready_pair(page, base_url, server_port, 'fault', _Faulty_Service)

        # .. invoke it, retrying while the connection propagates to the server ..
        deadline = time.monotonic() + _Propagation_Timeout
        result = {} # type: anydict

        while time.monotonic() < deadline:

            result = invoke_soap_outconn_from_ide(page, base_url, outconn['name'], _Echo_Operation,
                namespace=_Echo_Namespace,
                fields={'echoBack': 'fault-outcome'},
            )

            if 'fault_code' in result:
                break

            time.sleep(_Propagation_Poll_Interval)

        logger.info('[test_fault_outcome] result=%s', result)

        assert result['fault_code'] == 'Server', f'Expected a Server fault, got: {result}'

        # .. open the audit log page ..
        _goto_audit_log(page, base_url, outconn['name'])

        # .. the faulted invocation produced its two events ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        response_cells = _get_row_cells(rows[0])
        request_cells = _get_row_cells(rows[1])

        # .. the request itself was sent out fine ..
        assert request_cells[_Column_Event] == _Event_Request_Sent, \
            f'Expected event type "{_Event_Request_Sent}", got: "{request_cells[_Column_Event]}"'
        assert request_cells[_Column_Outcome] == _Outcome_OK, \
            f'Expected outcome "{_Outcome_OK}", got: "{request_cells[_Column_Outcome]}"'

        # .. while the response carries the error outcome ..
        assert response_cells[_Column_Event] == _Event_Response_Received, \
            f'Expected event type "{_Event_Response_Received}", got: "{response_cells[_Column_Event]}"'
        assert response_cells[_Column_Outcome] == _Outcome_Error, \
            f'Expected outcome "{_Outcome_Error}", got: "{response_cells[_Column_Outcome]}"'

        # .. and the complete response is the fault envelope as it arrived on the wire.
        response_envelope = _open_cid_overlay(page, rows[0])
        assert 'Fault' in response_envelope, \
            f'Expected a fault envelope in the complete response, got: "{response_envelope}"'
        _close_cid_overlay(page)

# ################################################################################################################################

    def test_ping_not_audited(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ Pings never write audit events - only actual invocations do.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        wait_for_channel_fixture_services(page, base_url)
        wait_for_soap_invoker_service(page, base_url)

        # Create a loopback pair and send real ping traffic through the connection ..
        outconn = _create_ready_pair(page, base_url, server_port, 'ping')

        open_soap_outconn_page(page, base_url)
        ping_result = ping_soap_outconn(page, outconn['name'])

        logger.info('[test_ping_not_audited] ping_result=%s', ping_result)

        # .. yet the audit log page shows no events at all ..
        _goto_audit_log(page, base_url, outconn['name'])

        body_text = page.inner_text('#audit-log-table-body')
        assert _No_Events_Text in body_text, f'Expected "{_No_Events_Text}" after pings only, got: "{body_text}"'

        # .. while one actual invocation produces its two events.
        _invoke_echo_via_outconn(page, base_url, outconn['name'], 'after-ping')

        _goto_audit_log(page, base_url, outconn['name'])

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows after one invocation, got {row_count}'

# ################################################################################################################################
# ################################################################################################################################
