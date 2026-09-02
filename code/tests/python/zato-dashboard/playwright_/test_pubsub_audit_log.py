# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import time

# Zato
from zato.common.test import rand_string
from zato.common.test.client import PublishClient
from zato.common.test.playwright_pubsub import create_basic_auth, create_permission, create_topic, navigate_to_page, \
    open_publish_overlay, publish_via_overlay

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from playwright.sync_api import Page
    from zato.common.typing_ import anydict, strlist

# ################################################################################################################################
# ################################################################################################################################

from audit_log_ui import attach_diagnostics, format_diagnostics, get_details_value, get_pane_cid, get_row_event, \
    get_row_main_text, get_row_time_text, get_rows, goto_audit_log, click_pane_cid, open_data, open_details, \
    close_cid_overlay, read_overlay_text, search, search_via_enter, wait_for_empty, wait_for_payload_text, \
    wait_for_row_count

# ################################################################################################################################
# ################################################################################################################################

_Test_Name_Prefix = 'test.audit.' + rand_string() + '.'

_Topic_Page_URL = '/zato/pubsub/topic/?cluster=1'
_Audit_Log_URL_Prefix = '/zato/audit-log/'

_Source = 'pubsub'

# How the publication event reads on its row
_Event_Published_Label = 'Published'

# The service that publishes messages sent through the dashboard
_Publish_Service = 'zato.pubsub.topic.publish'

# The section title for the pub/sub source, compared lowercase because the heading is styled with CSS
_PubSub_Title = 'pub/sub audit log'

# How long a permission needs to reach the runtime pattern matcher after a form submission
_Config_Propagation_Delay = 1.0

# ################################################################################################################################
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
        goto_audit_log(page, base_url, _Source, topic['name'])

        # .. the section title names the source, compared case-insensitively because of CSS styling ..
        title_text = page.inner_text('#detail-section-title')
        title_text = title_text.lower()
        assert title_text.startswith(_PubSub_Title), f'Expected the title to start with "{_PubSub_Title}", got: "{title_text}"'

        # .. the section title pill shows the topic name, compared case-insensitively
        # .. because the pill is uppercased with CSS ..
        pill_text = page.inner_text('#detail-section-title .detail-component-pill')
        pill_text = pill_text.lower()
        assert pill_text == topic['name'], f'Expected topic name "{topic["name"]}" in the pill, got: "{pill_text}"'

        # .. exactly one event exists for this topic ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 1, f'Expected 1 audit log row, got {row_count}'

        # .. the row describes the publication ..
        event_label = get_row_event(rows[0])
        assert event_label == _Event_Published_Label, \
            f'Expected event "{_Event_Published_Label}", got: "{event_label}"'

        # .. the time is shown in the browser's locale format, not as a raw ISO string ..
        time_text = get_row_time_text(rows[0])
        assert time_text != '', 'Expected a non-empty event time'
        assert '+00:00' not in time_text, f'Expected a locale-formatted time, got a raw ISO string: "{time_text}"'

        # .. the endpoint is the publishing service since the message went out through the dashboard,
        # .. worn as a chip on the row ..
        main_text = get_row_main_text(rows[0])
        assert _Publish_Service in main_text, \
            f'Expected the publishing service "{_Publish_Service}" on the row, got: "{main_text}"'

        # .. the Details tab reads everything the event says ..
        open_details(page, rows[0])

        msg_id = get_details_value(page, 'Message id')
        assert msg_id != '', 'Expected a non-empty message id in the detail pane'

        endpoint = get_details_value(page, 'Endpoint')
        assert endpoint == _Publish_Service, \
            f'Expected the endpoint "{_Publish_Service}" in the detail pane, got: "{endpoint}"'

        # .. the CID is filled in because self-published messages carry the CID
        # .. of the publishing service, and it is a link that opens the complete message ..
        cid = get_pane_cid(page)
        assert cid.strip() != '', 'Expected a non-empty CID in the detail pane'

        # .. and the Data tab holds the payload itself.
        open_data(page, rows[0])
        wait_for_payload_text(page, 'single-event')

# ################################################################################################################################

    def test_link_from_topic_list(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Create a topic and publish one message to it ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'from-list')
        _publish_messages(page, topic['item_id'], ['{"audit":"from-topic-list"}'])

        # .. go back to the topic list ..
        navigate_to_page(page, base_url, _Topic_Page_URL)

        # .. click the audit log link in this topic's row ..
        row_selector = f'#data-table tbody tr:has(td:text-is("{topic["name"]}"))'
        page.click(f'{row_selector} a:text-is("Audit log")')

        # .. wait for the audit log page to load ..
        page.wait_for_url(f'**{_Audit_Log_URL_Prefix}**')
        wait_for_row_count(page, 1)

        # .. the URL points to the audit log page for this topic ..
        assert _Audit_Log_URL_Prefix in page.url, f'Expected an audit log URL, got: "{page.url}"'
        assert 'source=pubsub' in page.url, f'Expected source=pubsub in the URL, got: "{page.url}"'

        # .. and the published event is shown with its payload in the Data tab.
        rows = get_rows(page)

        open_data(page, rows[0])
        wait_for_payload_text(page, 'from-topic-list')

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
        goto_audit_log(page, base_url, _Source, topic['name'])

        # .. all three publications are shown ..
        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 3, f'Expected 3 audit log rows, got {row_count}'

        # .. and the newest one comes first, which the payloads in the Data tab confirm.
        open_data(page, rows[0])
        wait_for_payload_text(page, 'third-message')

        open_data(page, rows[2])
        wait_for_payload_text(page, 'first-message')

# ################################################################################################################################

    def test_search_filters_rows(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Record everything the browser and Django report during this test ..
        diagnostics = attach_diagnostics(page)

        # .. create a topic and publish three messages with distinct payloads ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'search')
        _publish_messages(page, topic['item_id'], [
            '{"fruit":"apple"}',
            '{"fruit":"banana"}',
            '{"fruit":"cherry"}',
        ])

        # .. open the audit log page and confirm all three events are there ..
        goto_audit_log(page, base_url, _Source, topic['name'])

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 3, f'Expected 3 audit log rows, got {row_count}'

        # .. the search runs over the stored payloads, so one term keeps one event ..
        search(page, 'banana')
        wait_for_row_count(page, 1, diagnostics)

        rows = get_rows(page)

        open_data(page, rows[0])
        wait_for_payload_text(page, 'banana', diagnostics)

        # .. a query matching nothing shows the empty placeholder ..
        search(page, 'no-such-payload-anywhere')
        wait_for_empty(page, diagnostics)

        # .. clearing the query brings all three events back ..
        search(page, '')
        wait_for_row_count(page, 3, diagnostics)

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{format_diagnostics(diagnostics)}'

# ################################################################################################################################

    def test_search_via_enter_key(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Record everything the browser and Django report during this test ..
        diagnostics = attach_diagnostics(page)

        # .. create a topic and publish two messages with distinct payloads ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'enter')
        _publish_messages(page, topic['item_id'], [
            '{"event":"invoice-created"}',
            '{"event":"invoice-paid"}',
        ])

        # .. open the audit log page and confirm both events are there ..
        goto_audit_log(page, base_url, _Source, topic['name'])

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 2, f'Expected 2 audit log rows, got {row_count}'

        # .. pressing Enter in the input must filter the rows just like the button does ..
        search_via_enter(page, 'invoice-created')
        wait_for_row_count(page, 1, diagnostics)

        rows = get_rows(page)

        open_data(page, rows[0])
        wait_for_payload_text(page, 'invoice-created', diagnostics)

        # .. an Enter-submitted query matching nothing shows the empty placeholder ..
        search_via_enter(page, 'no-such-payload-anywhere')
        wait_for_empty(page, diagnostics)

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{format_diagnostics(diagnostics)}'

# ################################################################################################################################

    def test_complete_message_overlay(self, logged_in_page:'Page', zato_dashboard:'anydict') -> 'None':

        page = logged_in_page
        base_url = zato_dashboard['dashboard_url']

        # Record everything the browser and Django report during this test ..
        diagnostics = attach_diagnostics(page)

        # .. build a payload long enough that no row could ever show it whole ..
        line_items = [] # type: strlist

        for item_index in range(20):
            line_items.append(f'{{"line":{item_index},"product":"test-product-{item_index}","quantity":2}}')

        joined_items = ','.join(line_items)
        long_payload = f'{{"order":"test-order-1","items":[{joined_items}]}}'

        # .. create a topic and publish that payload ..
        topic = create_topic(page, base_url, _Test_Name_Prefix, 'complete')
        _publish_messages(page, topic['item_id'], [long_payload])

        # .. open the audit log page ..
        goto_audit_log(page, base_url, _Source, topic['name'])

        rows = get_rows(page)
        row_count = len(rows)
        assert row_count == 1, f'Expected 1 audit log row, got {row_count}'

        # .. the row itself carries no payload - the message is read in the pane ..
        main_text = get_row_main_text(rows[0])
        assert 'test-order-1' not in main_text, f'Expected no payload on the row, got: "{main_text}"'

        # .. the overlay behind the CID holds the payload in full, read through the Ace API
        # .. because Ace renders only the visible part of the text into the DOM ..
        open_details(page, rows[0])
        click_pane_cid(page)

        editor_value = read_overlay_text(page)
        assert editor_value == long_payload, \
            f'Expected the complete payload in the overlay, got: "{editor_value}"'

        close_cid_overlay(page)

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
        goto_audit_log(page, base_url, _Source, topic['name'])

        # .. the CID of the publication is filled in ..
        rows = get_rows(page)

        open_details(page, rows[0])
        cid = get_pane_cid(page)
        assert cid.strip() != '', 'Expected a non-empty CID in the detail pane'

        # .. clicking the CID opens the complete message overlay with the CID in the title ..
        click_pane_cid(page)

        overlay_title = page.inner_text('#zato-highlight-pane-overlay .zato-highlight-pane-overlay-title')
        assert cid in overlay_title, f'Expected the CID "{cid}" in the overlay title, got: "{overlay_title}"'

        # .. the CID part of the title can be selected with a double click, e.g. to copy it manually ..
        page.dblclick('#zato-highlight-pane-overlay .zato-highlight-pane-overlay-title-detail')
        selected_text = page.evaluate('window.getSelection().toString()')
        assert selected_text == cid, f'Expected the CID "{cid}" to be selected, got: "{selected_text}"'

        # .. there is one button copying the CID and one copying the whole message,
        # .. read via textContent because CSS renders the labels uppercased ..
        copy_cid_label = page.text_content('#audit-log-copy-cid')
        assert copy_cid_label == 'Copy CID', f'Expected a "Copy CID" button, got: "{copy_cid_label}"'

        copy_message_label = page.text_content('#zato-highlight-pane-copy')
        assert copy_message_label == 'Copy message', f'Expected a "Copy message" button, got: "{copy_message_label}"'

        # .. clicking "Copy CID" puts the CID in the clipboard ..
        page.context.grant_permissions(['clipboard-read', 'clipboard-write'])
        page.click('#audit-log-copy-cid')

        clipboard_text = page.evaluate('navigator.clipboard.readText()')
        assert clipboard_text == cid, f'Expected the CID "{cid}" in the clipboard, got: "{clipboard_text}"'

        # .. the overlay editor holds the complete message, read through the Ace API
        # .. because Ace renders only the visible part of the text into the DOM ..
        editor_value = read_overlay_text(page)
        assert editor_value == payload, f'Expected the complete payload in the overlay, got: "{editor_value}"'

        # .. the JSON payload is highlighted as JSON ..
        editor_mode = page.evaluate(
            '''() => {
                let element = document.querySelector('#zato-highlight-pane-overlay .zato-highlight-pane-editor');
                return ace.edit(element).session.getMode().$id;
            }''')

        assert editor_mode == 'ace/mode/json', f'Expected JSON highlighting, got: "{editor_mode}"'

        # .. and no JavaScript errors or failed requests happened along the way.
        assert not diagnostics['page_errors'], f'Unexpected page errors:\n{format_diagnostics(diagnostics)}'
        assert not diagnostics['failed_requests'], f'Unexpected failed requests:\n{format_diagnostics(diagnostics)}'

# ################################################################################################################################
# ################################################################################################################################
