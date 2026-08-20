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

# Zato
from zato.common.test import rand_string

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

from audit_log_ui import attach_diagnostics, format_diagnostics, get_pane_cid, get_row_cid, get_row_event, \
    get_row_main_text, get_row_outcome, get_row_time_text, get_rows, goto_audit_log, close_cid_overlay, open_cid_overlay, \
    open_data, open_details, search, wait_for_empty, wait_for_payload_text, wait_for_row_count, wait_for_table

from rest_channel import create_channel, deploy_service_file, invoke_until_status, open_channel_page, \
    wait_for_service_in_dialog

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

_Test_Name_Prefix = 'test.rest.audit.' + rand_string() + '.'

_Echo_Service = 'demo.echo'

_Audit_Log_URL_Prefix = '/zato/audit-log/'

_Source = 'rest-channel'

# How the events of one invocation read on their rows
_Event_Request_Received_Label = 'Request received'
_Event_Response_Sent_Label    = 'Response sent'

_Outcome_OK    = 'ok'
_Outcome_Error = 'error'

# The section title for the REST channel source, compared lowercase because the heading is styled with CSS
_REST_Channel_Title = 'rest channel audit log'

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
        goto_audit_log(page, base_url, _Source, channel['name'])

        # .. the section title names the source, compared case-insensitively because of CSS styling ..
        title_text = page.inner_text('#detail-section-title')
        title_text = title_text.lower()
        assert title_text.startswith(_REST_Channel_Title), \
            f'Expected the title to start with "{_REST_Channel_Title}", got: "{title_text}"'

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

            # .. the echoed payload is read in the pane's Data tab ..
            open_data(page, row)
            wait_for_payload_text(page, 'single-invocation')

        # .. and each event's CID is a link in the Details tab that opens the complete message.
        open_details(page, rows[0])
        cid = get_pane_cid(page)
        assert cid.strip() != '', 'Expected a non-empty CID in the detail pane'

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
        page.wait_for_url(f'**{_Audit_Log_URL_Prefix}**')
        wait_for_table(page)

        # .. the URL points to the audit log page for this channel ..
        assert _Audit_Log_URL_Prefix in page.url, f'Expected an audit log URL, got: "{page.url}"'
        assert 'source=rest-channel' in page.url, f'Expected source=rest-channel in the URL, got: "{page.url}"'
        assert quote(channel['name']) in page.url, f'Expected the channel name in the URL, got: "{page.url}"'

        # .. and the invocation's events are shown, with the payload in the Data tab.
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        open_data(page, rows[0])
        wait_for_payload_text(page, 'from-channel-list')

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
        goto_audit_log(page, base_url, _Source, channel['name'])

        # .. both invocations are shown, two events each ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 4, f'Expected 4 audit log rows, got {row_count}'

        # .. the newest invocation comes first, which the payloads in the Data tab confirm ..
        open_data(page, rows[0])
        wait_for_payload_text(page, 'second-invocation')

        open_data(page, rows[3])
        wait_for_payload_text(page, 'first-invocation')

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

        # Record everything the browser and Django report during this test ..
        diagnostics = attach_diagnostics(page)

        # .. create a channel and invoke it with three distinct payloads ..
        channel = _create_echo_channel(page, base_url, 'search')
        _invoke_ok(server_port, channel['url_path'], '{"event":"invoice-created"}')
        _invoke_ok(server_port, channel['url_path'], '{"event":"invoice-paid"}')
        _invoke_ok(server_port, channel['url_path'], '{"event":"invoice-cancelled"}')

        # .. open the audit log page and confirm all six events are there ..
        goto_audit_log(page, base_url, _Source, channel['name'])

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 6, f'Expected 6 audit log rows, got {row_count}'

        # .. the search runs over the stored payloads, so one term keeps one invocation's
        # .. request and response ..
        search(page, 'invoice-paid')
        wait_for_row_count(page, 2, diagnostics)

        rows = get_rows(page)

        open_data(page, rows[0])
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

    def test_cid_opens_complete_message(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Record everything the browser and Django report during this test ..
        diagnostics = attach_diagnostics(page)

        # .. build a payload long enough that no row could ever show it whole ..
        line_items:'strlist' = []

        for item_index in range(20):
            line_items.append(f'{{"line":{item_index},"product":"test-product-{item_index}","quantity":2}}')

        joined_items = ','.join(line_items)
        long_payload = f'{{"order":"test-order-1","items":[{joined_items}]}}'

        # .. create a channel and invoke it with that payload ..
        channel = _create_echo_channel(page, base_url, 'complete')
        _invoke_ok(server_port, channel['url_path'], long_payload)

        # .. open the audit log page ..
        goto_audit_log(page, base_url, _Source, channel['name'])

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. the row itself carries no payload - the message is read in the pane ..
        request_row = rows[1]
        main_text = get_row_main_text(request_row)
        assert 'test-order-1' not in main_text, f'Expected no payload on the row, got: "{main_text}"'

        # .. while the overlay behind the request's CID holds the payload in full.
        editor_value = open_cid_overlay(page, request_row)
        assert editor_value == long_payload, \
            f'Expected the complete payload in the overlay, got: "{editor_value}"'

        close_cid_overlay(page)

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{format_diagnostics(diagnostics)}'

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

        # .. while the response carries the error outcome.
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Response_Sent_Label, \
            f'Expected event "{_Event_Response_Sent_Label}", got: "{event_label}"'

        outcome = get_row_outcome(page, rows[0])
        assert outcome == _Outcome_Error, f'Expected outcome "{_Outcome_Error}", got: "{outcome}"'

# ################################################################################################################################
# ################################################################################################################################
