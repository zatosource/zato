# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import os
import subprocess
import tempfile
import time
from urllib.parse import quote

# pytest
import pytest

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from client import ZatoClient
    from zato.common.typing_ import any_, anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

from audit_log_ui import No_Events_Text, attach_diagnostics, format_diagnostics, get_row_cid, get_row_event, \
    get_row_main_text, get_row_outcome, get_row_time_text, get_rows, goto_audit_log, close_cid_overlay, \
    open_cid_overlay, open_data, search, wait_for_empty, wait_for_payload_text, wait_for_row_count, wait_for_table

from http_test_server import HTTPTestServer
from rest_channel import deploy_service_file
from rest_outconn import Outconn_Invoker_Service_Source, create_outconn, get_outconn_id, invoke_outconn_from_service, \
    invoke_outconn_via_overlay, open_outconn_page, ping_outconn_until_success, wait_for_invoker_service, \
    wait_for_outconn_row

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.outconn.audit.' + rand_string() + '.'

_Audit_Log_URL_Prefix = '/zato/audit-log/'

_Source = 'rest-outgoing'

# How the events of one invocation read on their rows
_Event_Request_Sent_Label      = 'Request sent'
_Event_Response_Received_Label = 'Response received'

_Outcome_OK    = 'ok'
_Outcome_Error = 'error'

# The section title for the outgoing REST source, compared lowercase because the heading is styled with CSS
_REST_Outgoing_Title = 'outgoing rest audit log'

# A TCP port that nothing listens on, for connections that must fail
_Dead_Port = 1

# How long to keep invoking while a UI change propagates to the server
_Propagation_Timeout = 20

# How long to sleep between the invocations above
_Propagation_Poll_Interval = 0.5

# How long the enmasse import subprocess may run
_Enmasse_Import_Timeout = 120

# Log patterns produced when an invocation cannot reach its target
_Connection_Failure_Log_Patterns = ('Connection refused', 'NewConnectionError', 'Max retries exceeded', 'Connection error')

# Log patterns produced when an invocation runs before the connection propagates to the server
_Propagation_Log_Patterns = (
    'Outgoing REST connection wrapper',
    'invoke_outconn error',
    'Internal Server Error: /zato/http-soap/invoke-outconn',
)

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture()
def http_test_server() -> 'any_':
    """ A live recording HTTP server for the duration of a single test.
    """

    server = HTTPTestServer()
    server.start()

    yield server

    server.stop()

# ################################################################################################################################

@pytest.fixture(scope='module')
def invoker_service(zato_dashboard:'anydict', api_client:'ZatoClient') -> 'any_':
    """ Hot-deploys the outgoing connection invoker service for the duration of this module.
    """

    server_dir = zato_dashboard['server_dir']
    file_path = deploy_service_file(server_dir, 'test_rest_outconn_invoker.py', Outconn_Invoker_Service_Source)

    wait_for_invoker_service(api_client)

    yield

    os.remove(file_path)

# ################################################################################################################################
# ################################################################################################################################

def _create_ready_outconn(
    page:'Page',
    base_url:'str',
    name_suffix:'str',
    http_test_server:'HTTPTestServer',
    ) -> 'anydict':
    """ Creates an outgoing REST connection pointing at the recording server, waits for it
    to propagate to the server via ping and forgets the ping's recorded traffic.
    """

    outconn_name = _Test_Name_Prefix + name_suffix
    url_path = f'/test/outconn/audit-{name_suffix}/' + rand_string()

    outconn_id = create_outconn(page, base_url, outconn_name, http_test_server.address, {
        'url_path': url_path,
    })

    # The ping both proves the wrapper propagated and is itself the subject
    # of the ping-not-audited test, since pings never write audit events.
    _ = ping_outconn_until_success(page, outconn_name)
    http_test_server.clear_requests()

    out = {
        'id': outconn_id,
        'name': outconn_name,
        'url_path': url_path,
        'address': http_test_server.address + url_path,
    }

    return out

# ################################################################################################################################

def _invoke_via_overlay_until_response(
    page:'Page',
    outconn_id:'str',
    expected_fragment:'str',
    **invoke_kwargs:'any_',
    ) -> 'anydict':
    """ Keeps invoking a connection through the overlay until the expected fragment appears
    in the displayed response, which covers the propagation delay of freshly created connections.
    Returns the last result, letting the caller assert on it themselves.
    """

    deadline = time.monotonic() + _Propagation_Timeout

    while True:
        out = invoke_outconn_via_overlay(page, outconn_id, **invoke_kwargs)

        # Stop as soon as the expected response arrives ..
        if expected_fragment in out['response']:
            break

        # .. or when the deadline passes, in which case the caller's assertion fails with details.
        if time.monotonic() >= deadline:
            break

        time.sleep(_Propagation_Poll_Interval)

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRESTOutconnAuditLog:
    """ Live tests for the outgoing REST connection audit log page, driven by real HTTP traffic
    between the connections and a recording test server.
    """

    def test_invoke_creates_events(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a connection and invoke it once through the overlay ..
        outconn = _create_ready_outconn(page, base_url, 'events', http_test_server)

        server_response = '{"received": "single-invocation-response"}'
        http_test_server.set_response(outconn['url_path'], body=server_response)

        payload = '{"audit": "single-invocation"}'
        result = invoke_outconn_via_overlay(page, outconn['id'], request_body=payload, method='POST')

        assert 'single-invocation-response' in result['response'], f'Expected the server response, got: {result}'

        # .. open the audit log page for that connection ..
        goto_audit_log(page, base_url, _Source, outconn['name'])

        # .. the section title names the source, compared case-insensitively because of CSS styling ..
        title_text = page.inner_text('#detail-section-title')
        title_text = title_text.lower()
        assert title_text.startswith(_REST_Outgoing_Title), \
            f'Expected the title to start with "{_REST_Outgoing_Title}", got: "{title_text}"'

        # .. the section title pill shows the connection name, compared case-insensitively
        # .. because the pill is uppercased with CSS ..
        pill_text = page.inner_text('#detail-section-title .detail-component-pill')
        pill_text = pill_text.lower()
        assert pill_text == outconn['name'], f'Expected connection name "{outconn["name"]}" in the pill, got: "{pill_text}"'

        # .. one invocation produces exactly two events ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the newest event is the response, the older one is the request ..
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Response_Received_Label, \
            f'Expected event "{_Event_Response_Received_Label}", got: "{event_label}"'

        event_label = get_row_event(rows[1])
        assert event_label == _Event_Request_Sent_Label, \
            f'Expected event "{_Event_Request_Sent_Label}", got: "{event_label}"'

        # .. both events carry the address invoked and completed fine ..
        for row in rows:

            main_text = get_row_main_text(row)
            assert outconn['address'] in main_text, \
                f'Expected the address "{outconn["address"]}" on the row, got: "{main_text}"'

            # .. the time is shown in the browser's locale format, not as a raw ISO string ..
            time_text = get_row_time_text(row)
            assert time_text != '', 'Expected a non-empty event time'
            assert '+00:00' not in time_text, f'Expected a locale-formatted time, got a raw ISO string: "{time_text}"'

            outcome = get_row_outcome(page, row)
            assert outcome == _Outcome_OK, f'Expected outcome "{_Outcome_OK}", got: "{outcome}"'

        # .. the request event holds what was sent, read in the pane's Data tab ..
        open_data(page, rows[1])
        wait_for_payload_text(page, 'single-invocation')

        # .. and the response event holds what came back.
        open_data(page, rows[0])
        wait_for_payload_text(page, 'single-invocation-response')

# ################################################################################################################################

    def test_link_from_connection_list(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a connection and invoke it once through the overlay ..
        outconn = _create_ready_outconn(page, base_url, 'from-list', http_test_server)
        _ = invoke_outconn_via_overlay(page, outconn['id'], request_body='{"audit": "from-connection-list"}')

        # .. go back to the outgoing REST connections page ..
        open_outconn_page(page, base_url)

        # .. click the audit log link in this connection's row ..
        row_selector = f'#data-table tbody tr:has(span.name-value:text-is("{outconn["name"]}"))'
        page.click(f'{row_selector} a:text-is("Audit log")')

        # .. wait for the audit log page to load ..
        page.wait_for_url(f'**{_Audit_Log_URL_Prefix}**')
        wait_for_table(page)

        # .. the URL points to the audit log page for this connection ..
        assert _Audit_Log_URL_Prefix in page.url, f'Expected an audit log URL, got: "{page.url}"'
        assert 'source=rest-outgoing' in page.url, f'Expected source=rest-outgoing in the URL, got: "{page.url}"'
        assert quote(outconn['name']) in page.url, f'Expected the connection name in the URL, got: "{page.url}"'

        # .. and the invocation's events are shown, with the request payload in the Data tab.
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        open_data(page, rows[1])
        wait_for_payload_text(page, 'from-connection-list')

# ################################################################################################################################

    def test_events_share_cid_newest_first(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a connection and invoke it twice, in a known order ..
        outconn = _create_ready_outconn(page, base_url, 'ordering', http_test_server)
        _ = invoke_outconn_via_overlay(page, outconn['id'], request_body='{"order": "first-invocation"}')
        _ = invoke_outconn_via_overlay(page, outconn['id'], request_body='{"order": "second-invocation"}')

        # .. open the audit log page ..
        goto_audit_log(page, base_url, _Source, outconn['name'])

        # .. both invocations are shown, two events each ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 4, f'Expected 4 audit log rows, got {row_count}'

        # .. the newest invocation comes first - its request is the second row from the top,
        # .. which the payloads in the Data tab confirm ..
        open_data(page, rows[1])
        wait_for_payload_text(page, 'second-invocation')

        open_data(page, rows[3])
        wait_for_payload_text(page, 'first-invocation')

        # .. within one invocation the response comes before the request ..
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Response_Received_Label, \
            f'Expected event "{_Event_Response_Received_Label}", got: "{event_label}"'

        event_label = get_row_event(rows[1])
        assert event_label == _Event_Request_Sent_Label, \
            f'Expected event "{_Event_Request_Sent_Label}", got: "{event_label}"'

        # .. the request and response of one invocation share the same CID ..
        response_cid = get_row_cid(page, rows[0])
        request_cid = get_row_cid(page, rows[1])
        assert response_cid == request_cid, \
            f'Expected one shared CID, got: "{response_cid}" and "{request_cid}"'

        # .. and separate invocations carry separate CIDs.
        oldest_cid = get_row_cid(page, rows[3])
        assert response_cid != oldest_cid, f'Expected distinct CIDs across invocations, got: "{response_cid}" twice'

# ################################################################################################################################

    def test_service_call_creates_events(
        self,
        logged_in_page:'Page',
        zato_dashboard:'anydict',
        api_client:'ZatoClient',
        invoker_service:'any_',
        http_test_server:'HTTPTestServer',
        ) -> 'None':
        """ Calls the connection from inside a hot-deployed service, the same code path
        production services use, and verifies the audit events appear.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a connection ..
        outconn = _create_ready_outconn(page, base_url, 'service', http_test_server)

        # .. call it from inside the service ..
        payload = '{"audit": "from-inside-a-service"}'
        result = invoke_outconn_from_service(api_client, outconn['name'], method='POST', data=payload)

        logger.info('[test_service_call_creates_events] result=%s', result)

        # .. open the audit log page ..
        goto_audit_log(page, base_url, _Source, outconn['name'])

        # .. the call produced its two events ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the newest event is the response, the older one is the request ..
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Response_Received_Label, \
            f'Expected event "{_Event_Response_Received_Label}", got: "{event_label}"'

        event_label = get_row_event(rows[1])
        assert event_label == _Event_Request_Sent_Label, \
            f'Expected event "{_Event_Request_Sent_Label}", got: "{event_label}"'

        # .. both completed fine ..
        for row in rows:
            outcome = get_row_outcome(page, row)
            assert outcome == _Outcome_OK, f'Expected outcome "{_Outcome_OK}", got: "{outcome}"'

        # .. and the request event holds the payload the service sent.
        open_data(page, rows[1])
        wait_for_payload_text(page, 'from-inside-a-service')

# ################################################################################################################################

    def test_search_filters_rows(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Record everything the browser and Django report during this test ..
        diagnostics = attach_diagnostics(page)

        # .. create a connection and invoke it with three distinct payloads, changing
        # .. the server's response each time so both events of one call carry its marker ..
        outconn = _create_ready_outconn(page, base_url, 'search', http_test_server)

        for marker in ('invoice-created', 'invoice-paid', 'invoice-cancelled'):
            http_test_server.set_response(outconn['url_path'], body=f'{{"echo": "{marker}"}}')
            _ = invoke_outconn_via_overlay(page, outconn['id'], request_body=f'{{"event": "{marker}"}}')

        # .. open the audit log page and confirm all six events are there ..
        goto_audit_log(page, base_url, _Source, outconn['name'])

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 6, f'Expected 6 audit log rows, got {row_count}'

        # .. the search runs over the stored payloads, so one marker keeps one invocation's
        # .. request and response ..
        search(page, 'invoice-paid')
        wait_for_row_count(page, 2, diagnostics)

        rows = get_rows(page)

        open_data(page, rows[1])
        wait_for_payload_text(page, 'invoice-paid', diagnostics)

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

    def test_cid_opens_complete_message(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Record everything the browser and Django report during this test ..
        diagnostics = attach_diagnostics(page)

        # .. build a payload long enough that no row could ever show it whole ..
        line_items:'strlist' = []

        for item_index in range(20):
            line_items.append(f'{{"line": {item_index}, "product": "test-product-{item_index}", "quantity": 2}}')

        joined_items = ','.join(line_items)
        long_payload = f'{{"order": "test-order-1", "items": [{joined_items}]}}'

        # .. create a connection and invoke it with that payload ..
        outconn = _create_ready_outconn(page, base_url, 'complete', http_test_server)
        _ = invoke_outconn_via_overlay(page, outconn['id'], request_body=long_payload)

        # .. open the audit log page ..
        goto_audit_log(page, base_url, _Source, outconn['name'])

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the row itself carries no payload - the message is read in the pane ..
        request_row = rows[1]
        main_text = get_row_main_text(request_row)
        assert 'test-order-1' not in main_text, f'Expected no payload on the row, got: "{main_text}"'

        # .. while the overlay behind the request's CID holds the complete invocation
        # request - the payload in full, wrapped in the invoke form's own envelope.
        editor_value = open_cid_overlay(page, request_row)
        overlay_message = json.loads(editor_value)

        assert overlay_message['payload'] == long_payload, \
            f'Expected the complete payload in the overlay, got: "{editor_value}"'
        assert overlay_message['method'] == 'POST', \
            f'Expected the POST method in the overlay, got: "{editor_value}"'

        close_cid_overlay(page)

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{format_diagnostics(diagnostics)}'

# ################################################################################################################################

    @pytest.mark.expect_log_errors(*(_Connection_Failure_Log_Patterns + _Propagation_Log_Patterns))
    def test_error_outcome(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':
        """ A connection pointing at a closed port produces a response event
        with the error outcome and the connection error's details.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        outconn_name = _Test_Name_Prefix + 'error'
        url_path = '/test/outconn/audit-error/' + rand_string()

        # Create a connection pointing at a port nothing listens on ..
        outconn_id = create_outconn(page, base_url, outconn_name, f'http://127.0.0.1:{_Dead_Port}', {
            'url_path': url_path,
        })

        # .. a dead connection cannot be pinged to await propagation, so the overlay invocation
        # .. is retried until the connection error - rather than a wrapper-not-found one - arrives ..
        result = _invoke_via_overlay_until_response(
            page, outconn_id, 'Connection error', request_body='{"audit": "error-outcome"}')

        logger.info('[test_error_outcome] result=%s', result)

        assert 'Connection error' in result['response'], f'Expected a connection error, got: {result}'

        # .. open the audit log page ..
        goto_audit_log(page, base_url, _Source, outconn_name)

        # .. at least one invocation reached the wrapper, producing its two events ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count >= 2, f'Expected at least 2 audit log rows, got {row_count}'

        # .. the request itself was sent out fine ..
        event_label = get_row_event(rows[1])
        assert event_label == _Event_Request_Sent_Label, \
            f'Expected event "{_Event_Request_Sent_Label}", got: "{event_label}"'

        outcome = get_row_outcome(page, rows[1])
        assert outcome == _Outcome_OK, f'Expected outcome "{_Outcome_OK}", got: "{outcome}"'

        # .. while the response carries the error outcome with the connection error's details ..
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Response_Received_Label, \
            f'Expected event "{_Event_Response_Received_Label}", got: "{event_label}"'

        outcome = get_row_outcome(page, rows[0])
        assert outcome == _Outcome_Error, f'Expected outcome "{_Outcome_Error}", got: "{outcome}"'

        open_data(page, rows[0])
        wait_for_payload_text(page, 'Connection')

        # .. and both events share their invocation's CID.
        response_cid = get_row_cid(page, rows[0])
        request_cid = get_row_cid(page, rows[1])
        assert response_cid == request_cid, \
            f'Expected one shared CID, got: "{response_cid}" and "{request_cid}"'

# ################################################################################################################################

    def test_ping_not_audited(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ Pings never write audit events - only actual invocations do.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a connection - the helper already pings it until the ping succeeds,
        # so by now real ping traffic has flowed through the connection ..
        outconn = _create_ready_outconn(page, base_url, 'ping', http_test_server)

        # .. yet the audit log page shows no events at all ..
        goto_audit_log(page, base_url, _Source, outconn['name'])

        body_text = page.inner_text('#audit-log-table-body')
        assert No_Events_Text in body_text, f'Expected "{No_Events_Text}" after pings only, got: "{body_text}"'

        # .. while one actual invocation produces its two events - the overlay only exists
        # .. on the connections page, so that page must be opened again first.
        open_outconn_page(page, base_url)
        _ = invoke_outconn_via_overlay(page, outconn['id'], request_body='{"audit": "after-ping"}')

        goto_audit_log(page, base_url, _Source, outconn['name'])

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows after one invocation, got {row_count}'

# ################################################################################################################################

    def test_enmasse_import_is_audited(
        self, logged_in_page:'Page', zato_dashboard:'anydict', http_test_server:'HTTPTestServer') -> 'None':
        """ A connection imported through enmasse is audited exactly like a UI-created one.
        """

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_dir = zato_dashboard['server_dir']

        outconn_name = _Test_Name_Prefix + 'enmasse'
        url_path = '/test/outconn/audit-enmasse/' + rand_string()

        # Write the enmasse YAML with one outgoing REST connection ..
        yaml_content = f"""
outgoing_rest:
  - name: {outconn_name}
    host: {http_test_server.address}
    url_path: {url_path}
"""

        yaml_file = tempfile.NamedTemporaryFile(mode='w', suffix='-audit-enmasse.yaml', delete=False)
        _ = yaml_file.write(yaml_content)
        yaml_file.close()

        # .. import it with the enmasse CLI against the same environment the tests run in ..
        zato_base_dir = os.environ['ZATO_TEST_BASE_DIR']
        zato_bin = os.path.join(zato_base_dir, 'code', 'bin', 'zato')

        enmasse_env = os.environ.copy()
        _ = enmasse_env.pop('COVERAGE_PROCESS_START', None)

        try:
            import_command = [zato_bin, 'enmasse', server_dir, '--verbose', '--import', '--input', yaml_file.name]
            result = subprocess.run(
                import_command, capture_output=True, text=True, timeout=_Enmasse_Import_Timeout, env=enmasse_env)

            logger.info('[test_enmasse_import_is_audited] stdout=%s stderr=%s', result.stdout, result.stderr)

            assert result.returncode == 0, \
                f'enmasse import failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'
        finally:
            os.remove(yaml_file.name)

        # .. the imported connection appears in the UI ..
        open_outconn_page(page, base_url)
        _ = wait_for_outconn_row(page, outconn_name)
        outconn_id = get_outconn_id(page, outconn_name)

        # .. wait for the wrapper to propagate to the server ..
        ping_result = ping_outconn_until_success(page, outconn_name)
        assert ping_result['is_success'], f'Expected a successful ping, got: {ping_result}'
        http_test_server.clear_requests()

        # .. invoke it through the overlay ..
        payload = '{"audit": "created-through-enmasse"}'
        result = invoke_outconn_via_overlay(page, outconn_id, request_body=payload)

        # .. and its audit events appear exactly like for UI-created connections.
        goto_audit_log(page, base_url, _Source, outconn_name)

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        event_label = get_row_event(rows[0])
        assert event_label == _Event_Response_Received_Label, \
            f'Expected event "{_Event_Response_Received_Label}", got: "{event_label}"'

        event_label = get_row_event(rows[1])
        assert event_label == _Event_Request_Sent_Label, \
            f'Expected event "{_Event_Request_Sent_Label}", got: "{event_label}"'

        open_data(page, rows[1])
        wait_for_payload_text(page, 'created-through-enmasse')

# ################################################################################################################################
# ################################################################################################################################
