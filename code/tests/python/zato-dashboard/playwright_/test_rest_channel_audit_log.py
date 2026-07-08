# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from http.client import INTERNAL_SERVER_ERROR, OK
from urllib.parse import quote

# pytest
import pytest

# Playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

from rest_channel import create_channel, deploy_service_file, invoke_until_status, open_channel_page, \
    wait_for_service_in_dialog

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.audit.' + rand_string() + '.'

_Echo_Service = 'demo.echo'

_Audit_Log_Url_Prefix = '/zato/audit-log/'
_Poll_Url_Path        = '/zato/audit-log/poll/'

_Event_Request_Received = 'request-received'
_Event_Response_Sent    = 'response-sent'

_Outcome_OK    = 'ok'
_Outcome_Error = 'error'

_No_Events_Text = 'No events found'

# The section title for the REST channel source, compared lowercase because the heading is styled with CSS
_Rest_Channel_Title = 'rest channel audit log'

# Column indexes: Time, CID, Event, Endpoint, Outcome, Size, Data preview
_Column_Time     = 0
_Column_CID      = 1
_Column_Event    = 2
_Column_Endpoint = 3
_Column_Outcome  = 4
_Column_Size     = 5
_Column_Data     = 6

# ################################################################################################################################
# ################################################################################################################################

# The error service always raises so channels pointing at it produce error responses
_Error_Service_Name = 'test.rest.audit.error'

_Error_Service_Source = '''
# -*- coding: utf-8 -*-

# Zato
from zato.server.service import Service

class RaiseAuditError(Service):
    """ Always raises so REST channel audit log tests can observe error outcomes.
    """

    name = 'test.rest.audit.error'

    def handle(self):
        raise Exception('Test audit log error')
'''.lstrip()

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def error_service(zato_dashboard:'anydict') -> 'any_':
    """ Hot-deploys the always-raising service for the duration of this module.
    """

    server_dir = zato_dashboard['server_dir']
    file_path = deploy_service_file(server_dir, 'test_rest_audit_error.py', _Error_Service_Source)

    yield _Error_Service_Name

    os.remove(file_path)

# ################################################################################################################################
# ################################################################################################################################

def _goto_audit_log(page:'Page', base_url:'str', channel_name:'str') -> 'None':
    """ Navigates to the audit log page of one REST channel and waits for the first page of events to load.
    """

    # Build the per-object URL ..
    encoded_name = quote(channel_name)
    url = f'{base_url}{_Audit_Log_Url_Prefix}?source=rest-channel&object_name={encoded_name}&cluster=1'

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

def _wait_for_body_without_text(page:'Page', text:'str', diagnostics:'anydictnone' = None) -> 'None':
    """ Waits until the audit log table body no longer contains the given text.
    On timeout, the assertion message includes everything the browser and Django reported.
    """
    try:
        _ = page.wait_for_function(
            f'!document.querySelector("#audit-log-table-body").innerText.includes(\'{text}\')', timeout=10000)
    except PlaywrightTimeoutError:
        body_text = page.inner_text('#audit-log-table-body')
        details = _format_diagnostics(diagnostics) if diagnostics else '(no diagnostics attached)'
        pytest.fail(
            f'Timed out waiting for "{text}" to disappear, the table shows:\n{body_text}\n\nDiagnostics:\n{details}')

# ################################################################################################################################

def _create_echo_channel(page:'Page', base_url:'str', name_suffix:'str') -> 'anydict':
    """ Creates a JSON REST channel pointing at the echo service and returns its details.
    """

    channel_name = _Test_Name_Prefix + name_suffix
    url_path = f'/test/rest/audit/{name_suffix}/' + rand_string()

    channel_id = create_channel(page, base_url, channel_name, _Echo_Service, url_path, {
        'data_format': 'json',
    })

    out = {
        'id': channel_id,
        'name': channel_name,
        'url_path': url_path,
    }

    return out

# ################################################################################################################################

def _invoke_ok(server_port:'int', url_path:'str', payload:'str') -> 'None':
    """ Invokes a REST channel with the given payload, waiting out the short window
    between the channel's creation in the UI and its propagation to the server.
    """
    response = invoke_until_status(server_port, url_path, OK, data=payload)
    assert response.status_code == OK, f'Expected OK, got {response.status_code}: {response.text}'

# ################################################################################################################################
# ################################################################################################################################

class TestRESTChannelAuditLog:
    """ Live tests for the REST channel audit log page, driven by real HTTP requests to real channels.
    """

    def test_invoke_creates_events(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Create a channel and invoke it once over live HTTP ..
        channel = _create_echo_channel(page, base_url, 'events')
        payload = '{"audit":"single-invocation"}'
        _invoke_ok(server_port, channel['url_path'], payload)

        # .. open the audit log page for that channel ..
        _goto_audit_log(page, base_url, channel['name'])

        # .. the section title names the source, compared case-insensitively because of CSS styling ..
        title_text = page.inner_text('#detail-section-title')
        title_text = title_text.lower()
        assert title_text.startswith(_Rest_Channel_Title), \
            f'Expected the title to start with "{_Rest_Channel_Title}", got: "{title_text}"'

        # .. the section title pill shows the channel name, compared case-insensitively
        # .. because the pill is uppercased with CSS ..
        pill_text = page.inner_text('#detail-section-title .detail-component-pill')
        pill_text = pill_text.lower()
        assert pill_text == channel['name'], f'Expected channel name "{channel["name"]}" in the pill, got: "{pill_text}"'

        # .. the table shows the REST channel columns - there is an Outcome column
        # .. and no pub/sub Message id column, compared case-insensitively
        # .. because the headers are uppercased with CSS ..
        header_text = page.inner_text('#audit-log-table thead')
        header_text = header_text.lower()
        assert 'outcome' in header_text, f'Expected an Outcome column, got: "{header_text}"'
        assert 'message id' not in header_text, f'Expected no Message id column, got: "{header_text}"'

        # .. one invocation produces exactly two events ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the newest event is the response, the older one is the request ..
        response_cells = _get_row_cells(rows[0])
        request_cells = _get_row_cells(rows[1])

        assert response_cells[_Column_Event] == _Event_Response_Sent, \
            f'Expected event type "{_Event_Response_Sent}", got: "{response_cells[_Column_Event]}"'
        assert request_cells[_Column_Event] == _Event_Request_Received, \
            f'Expected event type "{_Event_Request_Received}", got: "{request_cells[_Column_Event]}"'

        # .. both events point at the channel's service and completed fine ..
        for cells in (response_cells, request_cells):

            assert cells[_Column_Endpoint] == _Echo_Service, \
                f'Expected the endpoint "{_Echo_Service}", got: "{cells[_Column_Endpoint]}"'
            assert cells[_Column_Outcome] == _Outcome_OK, \
                f'Expected outcome "{_Outcome_OK}", got: "{cells[_Column_Outcome]}"'

            # .. the time is shown in the browser's locale format, not as a raw ISO string ..
            assert cells[_Column_Time] != '', 'Expected a non-empty event time'
            assert '+00:00' not in cells[_Column_Time], \
                f'Expected a locale-formatted time, got a raw ISO string: "{cells[_Column_Time]}"'

            size = int(cells[_Column_Size])
            assert size > 0, f'Expected a positive size, got {size}'

            assert 'single-invocation' in cells[_Column_Data], \
                f'Expected the payload in the data preview, got: "{cells[_Column_Data]}"'

        # .. and each row's CID is a link that opens the complete message.
        cid_link = rows[0].query_selector('a.audit-log-cid-link')
        assert cid_link is not None, 'Expected the CID cell to be a link'

# ################################################################################################################################

    def test_link_from_channel_list(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Create a channel and invoke it once over live HTTP ..
        channel = _create_echo_channel(page, base_url, 'from-list')
        _invoke_ok(server_port, channel['url_path'], '{"audit":"from-channel-list"}')

        # .. go back to the REST channels page ..
        open_channel_page(page, base_url)

        # .. click the audit log link in this channel's row ..
        row_selector = f'#data-table tbody tr:has(span.name-value:text-is("{channel["name"]}"))'
        page.click(f'{row_selector} a:text-is("Audit log")')

        # .. wait for the audit log page to load ..
        page.wait_for_url(f'**{_Audit_Log_Url_Prefix}**')
        _wait_for_table(page)

        # .. the URL points to the audit log page for this channel ..
        assert _Audit_Log_Url_Prefix in page.url, f'Expected an audit log URL, got: "{page.url}"'
        assert 'source=rest-channel' in page.url, f'Expected source=rest-channel in the URL, got: "{page.url}"'
        assert quote(channel['name']) in page.url, f'Expected the channel name in the URL, got: "{page.url}"'

        # .. and the invocation's events are shown.
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        cells = _get_row_cells(rows[0])
        assert 'from-channel-list' in cells[_Column_Data], \
            f'Expected the payload in the data preview, got: "{cells[_Column_Data]}"'

# ################################################################################################################################

    def test_events_share_cid_newest_first(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Create a channel and invoke it twice, in a known order ..
        channel = _create_echo_channel(page, base_url, 'ordering')
        _invoke_ok(server_port, channel['url_path'], '{"order":"first-invocation"}')
        _invoke_ok(server_port, channel['url_path'], '{"order":"second-invocation"}')

        # .. open the audit log page ..
        _goto_audit_log(page, base_url, channel['name'])

        # .. both invocations are shown, two events each ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 4, f'Expected 4 audit log rows, got {row_count}'

        # .. the newest invocation comes first ..
        first_row_cells = _get_row_cells(rows[0])
        last_row_cells = _get_row_cells(rows[3])

        assert 'second-invocation' in first_row_cells[_Column_Data], \
            f'Expected the newest payload first, got: "{first_row_cells[_Column_Data]}"'
        assert 'first-invocation' in last_row_cells[_Column_Data], \
            f'Expected the oldest payload last, got: "{last_row_cells[_Column_Data]}"'

        # .. within one invocation the response comes before the request ..
        second_row_cells = _get_row_cells(rows[1])

        assert first_row_cells[_Column_Event] == _Event_Response_Sent, \
            f'Expected event type "{_Event_Response_Sent}", got: "{first_row_cells[_Column_Event]}"'
        assert second_row_cells[_Column_Event] == _Event_Request_Received, \
            f'Expected event type "{_Event_Request_Received}", got: "{second_row_cells[_Column_Event]}"'

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

        # Record everything the browser and Django report during this test ..
        diagnostics = _attach_diagnostics(page)

        # .. create a channel and invoke it with three distinct payloads ..
        channel = _create_echo_channel(page, base_url, 'search')
        _invoke_ok(server_port, channel['url_path'], '{"event":"invoice-created"}')
        _invoke_ok(server_port, channel['url_path'], '{"event":"invoice-paid"}')
        _invoke_ok(server_port, channel['url_path'], '{"event":"invoice-cancelled"}')

        # .. open the audit log page and confirm all six events are there ..
        _goto_audit_log(page, base_url, channel['name'])

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 6, f'Expected 6 audit log rows, got {row_count}'

        # .. search for one payload and wait for the others to disappear ..
        _search(page, 'invoice-paid')
        _wait_for_body_without_text(page, 'invoice-created', diagnostics)

        # .. the request and the response of the matching invocation remain ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 filtered rows, got {row_count}'

        cells = _get_row_cells(rows[0])
        assert 'invoice-paid' in cells[_Column_Data], \
            f'Expected the matching payload, got: "{cells[_Column_Data]}"'

        # .. a query matching nothing shows the empty placeholder ..
        _search(page, 'no-such-payload-anywhere')
        _wait_for_body_text(page, _No_Events_Text, diagnostics)

        # .. clearing the query brings all six events back ..
        _search(page, '')
        _wait_for_body_text(page, 'invoice-created', diagnostics)
        _wait_for_body_text(page, 'invoice-cancelled', diagnostics)

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 6, f'Expected 6 rows after clearing the search, got {row_count}'

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{_format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{_format_diagnostics(diagnostics)}'

# ################################################################################################################################

    def test_cid_opens_complete_message(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Record everything the browser and Django report during this test ..
        diagnostics = _attach_diagnostics(page)

        # .. build a payload much longer than the 200-character preview shown in the table ..
        line_items:'strlist' = []

        for item_index in range(20):
            line_items.append(f'{{"line":{item_index},"product":"test-product-{item_index}","quantity":2}}')

        joined_items = ','.join(line_items)
        long_payload = f'{{"order":"test-order-1","items":[{joined_items}]}}'

        # .. create a channel and invoke it with that payload ..
        channel = _create_echo_channel(page, base_url, 'complete')
        _invoke_ok(server_port, channel['url_path'], long_payload)

        # .. open the audit log page ..
        _goto_audit_log(page, base_url, channel['name'])

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the table shows only a truncated preview of the request payload ..
        request_row = rows[1]
        cells = _get_row_cells(request_row)
        preview = cells[_Column_Data]
        assert len(preview) < len(long_payload), \
            f'Expected a truncated preview, got {len(preview)} characters for a {len(long_payload)}-character payload'

        # .. clicking the request's CID opens the overlay with the complete message ..
        cid_link = request_row.query_selector('a.audit-log-cid-link')
        cid_link.click()
        _ = page.wait_for_selector('#zato-highlight-pane-overlay:not(.hidden)', state='visible', timeout=10000)

        # .. the overlay editor holds the payload in full, read through the Ace API
        # .. because Ace renders only the visible part of the text into the DOM ..
        editor_value = page.evaluate(
            '''() => {
                let element = document.querySelector('#zato-highlight-pane-overlay .zato-highlight-pane-editor');
                return ace.edit(element).getValue();
            }''')

        assert editor_value == long_payload, \
            f'Expected the complete payload in the overlay, got: "{editor_value}"'

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{_format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{_format_diagnostics(diagnostics)}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors('Test audit log error')
    def test_error_outcome(
        self, logged_in_page:'Page', zato_dashboard:'anydict', error_service:'str') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Make sure the hot-deployed service is already selectable ..
        wait_for_service_in_dialog(page, base_url, error_service)

        # .. create a channel pointing at the always-raising service ..
        channel_name = _Test_Name_Prefix + 'error'
        url_path = '/test/rest/audit/error/' + rand_string()

        _ = create_channel(page, base_url, channel_name, error_service, url_path, {
            'data_format': 'json',
        })

        # .. invoke the channel and let the service raise ..
        response = invoke_until_status(server_port, url_path, INTERNAL_SERVER_ERROR, data='{"audit":"error-outcome"}')
        assert response.status_code == INTERNAL_SERVER_ERROR, \
            f'Expected INTERNAL_SERVER_ERROR, got {response.status_code}: {response.text}'

        # .. open the audit log page ..
        _goto_audit_log(page, base_url, channel_name)

        # .. the invocation produced its two events ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        response_cells = _get_row_cells(rows[0])
        request_cells = _get_row_cells(rows[1])

        # .. the request itself was received fine ..
        assert request_cells[_Column_Event] == _Event_Request_Received, \
            f'Expected event type "{_Event_Request_Received}", got: "{request_cells[_Column_Event]}"'
        assert request_cells[_Column_Outcome] == _Outcome_OK, \
            f'Expected outcome "{_Outcome_OK}", got: "{request_cells[_Column_Outcome]}"'

        # .. while the response carries the error outcome.
        assert response_cells[_Column_Event] == _Event_Response_Sent, \
            f'Expected event type "{_Event_Response_Sent}", got: "{response_cells[_Column_Event]}"'
        assert response_cells[_Column_Outcome] == _Outcome_Error, \
            f'Expected outcome "{_Outcome_Error}", got: "{response_cells[_Column_Outcome]}"'

# ################################################################################################################################
# ################################################################################################################################
