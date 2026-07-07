# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time
from urllib.parse import quote

# pytest
import pytest

# Playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# Zato
from zato.common.test import rand_string
from zato.common.test.client import PublishClient
from zato.common.test.playwright_pubsub import create_basic_auth, create_permission, create_topic, navigate_to_page, \
    open_publish_overlay, publish_via_overlay

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import any_, anydict, anydictnone, anylist, strlist

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.audit.' + rand_string() + '.'

_Topic_Page_Url       = '/zato/pubsub/topic/?cluster=1'
_Audit_Log_Url_Prefix = '/zato/audit-log/'
_Poll_Url_Path        = '/zato/audit-log/poll/'

_Event_Type_Published = 'published'
_No_Events_Text       = 'No events found'

# The section title for the pub/sub source, compared lowercase because the heading is styled with CSS
_PubSub_Title = 'pub/sub audit log'

# What the table shows for empty values, from the config object in audit_log.js
_Empty_Value = '---'

# How long a permission needs to reach the runtime pattern matcher after a form submission
_Config_Propagation_Delay = 1.0

# Column indexes: Time, CID, Event, Message id, Endpoint, Size, Data preview
_Object_Column_Time     = 0
_Object_Column_CID      = 1
_Object_Column_Event    = 2
_Object_Column_Msg_ID   = 3
_Object_Column_Endpoint = 4
_Object_Column_Size     = 5
_Object_Column_Data     = 6

# ################################################################################################################################
# ################################################################################################################################

def _goto_audit_log(page:'Page', base_url:'str', topic_name:'str') -> 'None':
    """ Navigates to the audit log page of one pub/sub topic and waits for the first page of events to load.
    """

    # Build the per-object URL ..
    encoded_name = quote(topic_name)
    url = f'{base_url}{_Audit_Log_Url_Prefix}?source=pubsub&object_name={encoded_name}&cluster=1'

    # .. go there ..
    _ = page.goto(url)

    # .. and wait for the initial poll to replace the loading row.
    _wait_for_table(page)

# ################################################################################################################################

def _wait_for_table(page:'Page') -> 'None':
    """ Waits until the audit log table has finished loading its current page of events,
    i.e. until the table body exists, has rows and none of them is the loading placeholder.
    """
    page.wait_for_function(
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

def _search_via_enter(page:'Page', query:'str') -> 'None':
    """ Types a query into the audit log search form and submits it by pressing Enter in the input.
    """

    # Fill in the query ..
    page.fill('#audit-log-search-input', query)

    # .. and submit the form by pressing Enter.
    page.press('#audit-log-search-input', 'Enter')

# ################################################################################################################################

def _wait_for_body_text(page:'Page', text:'str', diagnostics:'anydictnone' = None) -> 'None':
    """ Waits until the audit log table body contains the given text.
    On timeout, the assertion message includes everything the browser and Django reported.
    """
    try:
        page.wait_for_function(
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
        page.wait_for_function(
            f'!document.querySelector("#audit-log-table-body").innerText.includes(\'{text}\')', timeout=10000)
    except PlaywrightTimeoutError:
        body_text = page.inner_text('#audit-log-table-body')
        details = _format_diagnostics(diagnostics) if diagnostics else '(no diagnostics attached)'
        pytest.fail(
            f'Timed out waiting for "{text}" to disappear, the table shows:\n{body_text}\n\nDiagnostics:\n{details}')

# ################################################################################################################################

def _publish_messages(page:'Page', item_id:'str', payload_list:'strlist') -> 'None':
    """ Opens the publish overlay for a topic and publishes each payload in turn.
    """

    # Open the overlay once ..
    open_publish_overlay(page, item_id)

    # .. and publish all the payloads through it.
    for payload in payload_list:
        publish_via_overlay(page, payload)

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubAuditLog:
    """ Live tests for the pub/sub audit log page, driven by real publications through the dashboard.
    """

    def test_publish_creates_event(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic and publish one message to it ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'single')
        _publish_messages(page, topic['item_id'], ['{"audit":"single-event"}'])

        # .. open the audit log page for that topic ..
        _goto_audit_log(page, base_url, topic['name'])

        # .. the section title names the source, compared case-insensitively because of CSS styling ..
        title_text = page.inner_text('#detail-section-title')
        title_text = title_text.lower()
        assert title_text.startswith(_PubSub_Title), f'Expected the title to start with "{_PubSub_Title}", got: "{title_text}"'

        # .. the section title pill shows the topic name, compared case-insensitively
        # .. because the pill is uppercased with CSS ..
        pill_text = page.inner_text('#detail-section-title .detail-component-pill')
        pill_text = pill_text.lower()
        assert pill_text == topic['name'], f'Expected topic name "{topic["name"]}" in the pill, got: "{pill_text}"'

        # .. there are no tabs on the page because everything on it is an event ..
        tab_count = len(page.query_selector_all('.dashboard-tab'))
        assert tab_count == 0, f'Expected no tabs, got {tab_count}'

        # .. the table has no server column, compared case-insensitively
        # .. because the header is uppercased with CSS ..
        header_text = page.inner_text('#audit-log-table thead')
        header_text = header_text.lower()
        assert 'server' not in header_text, f'Expected no Server column, got: "{header_text}"'

        # .. exactly one event exists for this topic ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 1, f'Expected 1 audit log row, got {row_count}'

        # .. the row describes the publication ..
        cells = _get_row_cells(rows[0])

        # .. the time is shown in the browser's locale format, not as a raw ISO string ..
        assert cells[_Object_Column_Time] != '', 'Expected a non-empty event time'
        assert '+00:00' not in cells[_Object_Column_Time], \
            f'Expected a locale-formatted time, got a raw ISO string: "{cells[_Object_Column_Time]}"'

        assert cells[_Object_Column_Event] == _Event_Type_Published, \
            f'Expected event type "{_Event_Type_Published}", got: "{cells[_Object_Column_Event]}"'
        assert cells[_Object_Column_Msg_ID] != '', 'Expected a non-empty message id'

        # .. the endpoint is the publishing service since the message went out through the dashboard ..
        assert cells[_Object_Column_Endpoint] == 'zato.pubsub.topic.publish', \
            f'Expected the publishing service as the endpoint, got: "{cells[_Object_Column_Endpoint]}"'

        size = int(cells[_Object_Column_Size])
        assert size > 0, f'Expected a positive size, got {size}'

        assert 'single-event' in cells[_Object_Column_Data], \
            f'Expected the payload in the data preview, got: "{cells[_Object_Column_Data]}"'

        # .. and the CID cell is filled in because self-published messages carry the CID
        # .. of the publishing service, and it is a link that opens the complete message.
        assert cells[_Object_Column_CID] != _Empty_Value, \
            f'Expected a non-empty CID, got: "{cells[_Object_Column_CID]}"'

        cid_link = rows[0].query_selector('a.audit-log-cid-link')
        assert cid_link is not None, 'Expected the CID cell to be a link'

# ################################################################################################################################

    def test_link_from_topic_list(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic and publish one message to it ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'from-list')
        _publish_messages(page, topic['item_id'], ['{"audit":"from-topic-list"}'])

        # .. go back to the topic list ..
        navigate_to_page(page, base_url, _Topic_Page_Url)

        # .. click the audit log link in this topic's row ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{topic["name"]}"))'
        page.click(f'{row_selector} a:text-is("Audit log")')

        # .. wait for the audit log page to load ..
        page.wait_for_url(f'**{_Audit_Log_Url_Prefix}**')
        _wait_for_table(page)

        # .. the URL points to the audit log page for this topic ..
        assert _Audit_Log_Url_Prefix in page.url, f'Expected an audit log URL, got: "{page.url}"'
        assert 'source=pubsub' in page.url, f'Expected source=pubsub in the URL, got: "{page.url}"'
        assert quote(topic['name']) in page.url, f'Expected the topic name in the URL, got: "{page.url}"'

        # .. and the published event is shown.
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 1, f'Expected 1 audit log row, got {row_count}'

        cells = _get_row_cells(rows[0])
        assert 'from-topic-list' in cells[_Object_Column_Data], \
            f'Expected the payload in the data preview, got: "{cells[_Object_Column_Data]}"'

# ################################################################################################################################

    def test_multiple_publishes_newest_first(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic and publish three messages in a known order ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'ordering')
        _publish_messages(page, topic['item_id'], [
            '{"order":"first-message"}',
            '{"order":"second-message"}',
            '{"order":"third-message"}',
        ])

        # .. open the audit log page ..
        _goto_audit_log(page, base_url, topic['name'])

        # .. all three publications are shown ..
        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 3, f'Expected 3 audit log rows, got {row_count}'

        # .. and the newest one comes first.
        first_row_cells = _get_row_cells(rows[0])
        last_row_cells = _get_row_cells(rows[2])

        assert 'third-message' in first_row_cells[_Object_Column_Data], \
            f'Expected the newest payload first, got: "{first_row_cells[_Object_Column_Data]}"'
        assert 'first-message' in last_row_cells[_Object_Column_Data], \
            f'Expected the oldest payload last, got: "{last_row_cells[_Object_Column_Data]}"'

# ################################################################################################################################

    def test_search_filters_rows(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Record everything the browser and Django report during this test ..
        diagnostics = _attach_diagnostics(page)

        # .. create a topic and publish three messages with distinct payloads ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'search')
        _publish_messages(page, topic['item_id'], [
            '{"fruit":"apple"}',
            '{"fruit":"banana"}',
            '{"fruit":"cherry"}',
        ])

        # .. open the audit log page and confirm all three events are there ..
        _goto_audit_log(page, base_url, topic['name'])

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 3, f'Expected 3 audit log rows, got {row_count}'

        # .. search for one payload and wait for the others to disappear ..
        _search(page, 'banana')
        _wait_for_body_without_text(page, 'apple', diagnostics)

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 1, f'Expected 1 filtered row, got {row_count}'

        cells = _get_row_cells(rows[0])
        assert 'banana' in cells[_Object_Column_Data], \
            f'Expected the matching payload, got: "{cells[_Object_Column_Data]}"'

        # .. a query matching nothing shows the empty placeholder ..
        _search(page, 'no-such-payload-anywhere')
        _wait_for_body_text(page, _No_Events_Text, diagnostics)

        # .. clearing the query brings all three events back ..
        _search(page, '')
        _wait_for_body_text(page, 'apple', diagnostics)
        _wait_for_body_text(page, 'cherry', diagnostics)

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 3, f'Expected 3 rows after clearing the search, got {row_count}'

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{_format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{_format_diagnostics(diagnostics)}'

# ################################################################################################################################

    def test_search_via_enter_key(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Record everything the browser and Django report during this test ..
        diagnostics = _attach_diagnostics(page)

        # .. create a topic and publish two messages with distinct payloads ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'enter')
        _publish_messages(page, topic['item_id'], [
            '{"event":"invoice-created"}',
            '{"event":"invoice-paid"}',
        ])

        # .. open the audit log page and confirm both events are there ..
        _goto_audit_log(page, base_url, topic['name'])

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. pressing Enter in the input must filter the rows just like the button does ..
        _search_via_enter(page, 'invoice-created')
        _wait_for_body_without_text(page, 'invoice-paid', diagnostics)

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 1, f'Expected 1 filtered row, got {row_count}'

        cells = _get_row_cells(rows[0])
        assert 'invoice-created' in cells[_Object_Column_Data], \
            f'Expected the matching payload, got: "{cells[_Object_Column_Data]}"'

        # .. an Enter-submitted query matching nothing shows the empty placeholder ..
        _search_via_enter(page, 'no-such-payload-anywhere')
        _wait_for_body_text(page, _No_Events_Text, diagnostics)

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{_format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{_format_diagnostics(diagnostics)}'

# ################################################################################################################################

    def test_complete_message_overlay(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Record everything the browser and Django report during this test ..
        diagnostics = _attach_diagnostics(page)

        # .. build a payload much longer than the 200-character preview shown in the table ..
        line_items = [] # type: strlist

        for item_index in range(20):
            line_items.append(f'{{"line":{item_index},"product":"test-product-{item_index}","quantity":2}}')

        joined_items = ','.join(line_items)
        long_payload = f'{{"order":"test-order-1","items":[{joined_items}]}}'

        # .. create a topic and publish that payload ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'complete')
        _publish_messages(page, topic['item_id'], [long_payload])

        # .. open the audit log page ..
        _goto_audit_log(page, base_url, topic['name'])

        rows = _get_rows(page)
        row_count = len(rows)
        assert row_count == 1, f'Expected 1 audit log row, got {row_count}'

        # .. the table shows only a truncated preview of the payload ..
        cells = _get_row_cells(rows[0])
        preview = cells[_Object_Column_Data]
        assert len(preview) < len(long_payload), \
            f'Expected a truncated preview, got {len(preview)} characters for a {len(long_payload)}-character payload'

        # .. clicking the preview opens the overlay with the complete message ..
        page.click('.audit-log-preview-link')
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

    def test_cid_opens_complete_message(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']
        server_port = zato_dashboard['server_port']

        # Record everything the browser and Django report during this test ..
        diagnostics = _attach_diagnostics(page)

        # .. create a topic ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'cid-message')

        # .. an external publisher needs a security definition and a publisher permission ..
        sec_info = create_basic_auth(page, base_url, _Test_Name_Prefix, 'cid-message')
        _ = create_permission(page, base_url, sec_info['name'], 'publisher', 'pub', topic['name'])

        # .. let the permission reach the runtime pattern matcher ..
        time.sleep(_Config_Propagation_Delay)

        # .. publish through the pub/sub REST API so the CID in the audit log comes from an external request ..
        payload = '{"audit":"cid-complete-message"}'
        client = PublishClient(f'http://127.0.0.1:{server_port}', sec_info['username'], sec_info['password'])
        response = client.publish(topic['name'], payload)
        assert response['is_ok'] is True, f'Expected a successful publish, got: {response}'

        # .. open the audit log page for the topic ..
        _goto_audit_log(page, base_url, topic['name'])

        # .. the CID of the publication is filled in ..
        rows = _get_rows(page)
        cells = _get_row_cells(rows[0])

        cid = cells[_Object_Column_CID]
        assert cid != _Empty_Value, 'Expected a non-empty CID'

        # .. clicking the CID opens the complete message overlay with the CID in the title ..
        page.click('a.audit-log-cid-link')
        _ = page.wait_for_selector('#zato-highlight-pane-overlay:not(.hidden)', state='visible', timeout=10000)

        overlay_title = page.inner_text('#zato-highlight-pane-overlay .zato-highlight-pane-overlay-title')
        assert cid in overlay_title, f'Expected the CID "{cid}" in the overlay title, got: "{overlay_title}"'

        # .. the overlay editor holds the complete message, read through the Ace API
        # .. because Ace renders only the visible part of the text into the DOM ..
        editor_value = page.evaluate(
            '''() => {
                let element = document.querySelector('#zato-highlight-pane-overlay .zato-highlight-pane-editor');
                return ace.edit(element).getValue();
            }''')

        assert editor_value == payload, f'Expected the complete payload in the overlay, got: "{editor_value}"'

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{_format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{_format_diagnostics(diagnostics)}'

# ################################################################################################################################
# ################################################################################################################################
